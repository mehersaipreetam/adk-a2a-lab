import json
from a2a.server.agent_execution import AgentExecutor
from a2a.server.agent_execution.context import RequestContext
from a2a.server.events.event_queue import EventQueue
from a2a.server.tasks import TaskUpdater
from a2a.utils import new_agent_parts_message
from a2a.types import TaskState, Part, TextPart
from typing import TypedDict, List
from my_a2a.multi_a2a.pos_tag_agent.agent import app

class AgentState(TypedDict):
    """Represents the state of our graph."""
    text_input: str
    pos_tags: List[List[str]]

class PosTagAgentExecutor(AgentExecutor):
    def __init__(self):
        # We don't need a session service for this stateless agent
        pass

    async def execute(self, context: RequestContext, event_queue: EventQueue):
        # Create a task updater to manage the task's state
        updater = TaskUpdater(event_queue, context.task_id, context.context_id)
        if not context.current_task:
            await updater.update_status(TaskState.submitted)
        await updater.update_status(TaskState.working)

        try:
            # Safely get the input text from the A2A request
            user_input_text = context.get_user_input()
            if not user_input_text:
                raise ValueError("No text input provided for tagging.")
            
            # Create the initial state for the LangGraph
            initial_state: AgentState = {"text_input": user_input_text, "pos_tags": []}

            # Run the compiled LangGraph app to get the final state
            # The app itself is now an async runnable because it contains async nodes
            final_state = await app.ainvoke(initial_state)

            # Extract the result from the final state
            pos_tags = final_state['pos_tags']
            
            # Serialize the list of lists to a JSON string
            json_response = json.dumps(pos_tags)
            
            # Wrap the JSON string into a TextPart and then into a Part object
            text_part = TextPart(text=json_response)
            parts = [Part(root=text_part)]

            # Send the structured result back via A2A
            await event_queue.enqueue_event(
                new_agent_parts_message(parts)
            )
            
            # Mark the task as completed
            await updater.update_status(TaskState.completed, final=True)
            
        except Exception as e:
            await updater.update_status(TaskState.failed, final=True)
            raise RuntimeError(f"An error occurred during POS tagging: {e}")

    async def cancel(self, context: RequestContext, event_queue: EventQueue):
        raise NotImplementedError("Cancellation is not supported for this agent.")
