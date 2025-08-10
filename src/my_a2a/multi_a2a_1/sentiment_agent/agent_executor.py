# A2A components for agent execution
import re
from a2a.server.agent_execution import AgentExecutor
from a2a.server.agent_execution.context import RequestContext
from a2a.server.events.event_queue import EventQueue
from a2a.utils import new_agent_parts_message
from a2a.server.tasks import TaskUpdater
from a2a.types import TaskState, Part, TextPart # Import new types

# ADK components for running the sentiment agent
from google.adk.runners import Runner
from google.adk.sessions import InMemorySessionService
from google.genai import types

# Import our pre-configured sentiment analysis agent
from my_adk.simple_agent.sentiment_agent.agent import agent as sentiment_agent


class SentimentAgentExecutor(AgentExecutor):
    """
    Bridges ADK and A2A: Makes our sentiment analysis agent available to other agents.
    
    This executor:
    1. Receives requests from other agents via A2A protocol
    2. Processes them using our ADK-based sentiment agent
    3. Returns results in A2A-compatible format
    """
    
    def __init__(self):
        # Use our pre-configured sentiment analysis agent
        self.agent = sentiment_agent
        
        # Simple in-memory session (no persistence needed for stateless agent)
        self.session_service = InMemorySessionService()
        
        # Identifiers for this agent instance
        self.app_name = "sentiment_analysis_app"
        self.user_id = "default_user"
        self.session_id = "default_session"
        
    async def execute(self, context: RequestContext, event_queue: EventQueue):
        """
         Processes incoming A2A requests through our sentiment analysis agent.
        """
        # Create a task updater to manage the task's state
        updater = TaskUpdater(event_queue, context.task_id, context.context_id)

        # Update the task status to reflect the current state
        if not context.current_task:
            await updater.update_status(TaskState.submitted)
        await updater.update_status(TaskState.working)

        # Initialize or get existing session
        current_session = await self.session_service.create_session(
            app_name=self.app_name,
            user_id=self.user_id,
            session_id=self.session_id
        )

        print(f"\n Session {current_session.id} created successfully.")

        # Extract the text to analyze from the A2A request
        user_input_text = context.get_user_input()

        # Format the input for our ADK agent
        content = types.Content(
            role="user",
            parts=[types.Part(text=user_input_text)]
        )

        # Set up the ADK runner to process our request
        runner = Runner(
            agent=self.agent,
            app_name=self.app_name,
            session_service=self.session_service,
        )

        final_response_text = None

        async for event in runner.run_async(
            user_id=self.user_id,
            session_id=self.session_id,
            new_message=content,
        ):
            if event.is_final_response():
                if event.content and event.content.parts:
                    # Capture the full response text, which might include markdown fences
                    final_response_text = event.content.parts[0].text
                break

        # Handle the response
        if final_response_text is not None:
            # Use a regex to clean the text from any JSON markdown fences
            pattern = r"^```json\n|```$"
            cleaned_json_string = re.sub(pattern, "", final_response_text, flags=re.MULTILINE).strip()

            # Create a structured message using A2A parts
            # Since the response is expected to be a JSON string, we create a TextPart
            # and wrap it in a Part object to conform to the A2A message structure.
            text_part = TextPart(text=cleaned_json_string)
            parts = [Part(root=text_part)]

            await event_queue.enqueue_event(
                new_agent_parts_message(parts)
            )
            
            # Mark the task as completed
            await updater.update_status(TaskState.completed, final=True)
        else:
            await updater.update_status(TaskState.failed, final=True)
            raise RuntimeError("No final response received from the agent.")


    async def cancel(self, context: RequestContext, event_queue: EventQueue):
        raise NotImplementedError("Cancellation is not supported for sentiment analysis agent.")
