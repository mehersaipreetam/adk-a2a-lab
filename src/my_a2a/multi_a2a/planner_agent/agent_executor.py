# A2A components for agent execution
import json
from a2a.server.agent_execution import AgentExecutor
from a2a.server.agent_execution.context import RequestContext
from a2a.server.events.event_queue import EventQueue
from a2a.utils import new_agent_parts_message
from a2a.server.tasks import TaskUpdater
from a2a.types import TaskState, Part, TextPart

# ADK components for running the sentiment agent
from google.adk.sessions import InMemorySessionService

from my_a2a.multi_a2a.planner_agent.agent import generate_plan

class PlannerAgentExecutor(AgentExecutor):
    def __init__(self):        
        self.session_service = InMemorySessionService()
        self.app_name = "planner_app"
        self.user_id = "default_user"
        self.session_id = "default_session"

    async def execute(self, context: RequestContext, event_queue: EventQueue):
        current_session = await self.session_service.create_session(
            app_name=self.app_name,
            user_id=self.user_id,
            session_id=self.session_id
        )
        print(f"\n Session {current_session.id} created successfully.")
        
        updater = TaskUpdater(event_queue, context.task_id, context.context_id)
        if not context.current_task:
            await updater.update_status(TaskState.submitted)
        await updater.update_status(TaskState.working)

        # Safely extract structured input from the A2A request
        user_input_string = context.get_user_input()
        print(f"Received user input: {user_input_string}")
        try:
            input_data = json.loads(user_input_string)
            user_input = input_data.get("user_input")
            available_agents = input_data.get("available_agents", [])
        except json.JSONDecodeError:
            # Handle malformed input gracefully
            await updater.update_status(TaskState.failed, final=True)
            raise ValueError("Input is not a valid JSON string.")

        # Process the input through our planner agent
        plan = await generate_plan(
            user_input=user_input,
            available_agents=available_agents
        )
        print(f"Generated plan: {plan}")
        
        if plan is not None:
            # Convert the Python dictionary into a JSON string
            json_plan_string = json.dumps(plan)
            
            # Wrap the JSON string into a TextPart and then into a Part object
            text_part = TextPart(text=json_plan_string)
            message_parts = [Part(root=text_part)]

            # Create and send an A2A-compatible message with the result
            await event_queue.enqueue_event(
                new_agent_parts_message(message_parts)
            )
            
            # Mark the task as completed
            await updater.update_status(TaskState.completed, final=True)
        else:
            await updater.update_status(TaskState.failed, final=True)
            raise RuntimeError("No final response received from the agent.")

    async def cancel(self, context: RequestContext, event_queue: EventQueue):
        raise NotImplementedError("Cancellation is not supported for planner agent.")