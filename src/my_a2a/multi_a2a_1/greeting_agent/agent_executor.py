# A2A components for agent execution
from a2a.server.agent_execution import AgentExecutor
from a2a.server.agent_execution.context import RequestContext
from a2a.server.events.event_queue import EventQueue
from a2a.utils import new_agent_text_message
from a2a.server.tasks import TaskUpdater
from a2a.types import TaskState

# ADK components
from google.adk.runners import Runner
from google.adk.sessions import InMemorySessionService
from google.genai import types

# Import our pre-configured greeting agent
from my_a2a.multi_a2a_1.greeting_agent import greeting_agent  

class GreetingAgentExecutor(AgentExecutor):
    """
    Bridges ADK and A2A for the Greeting Agent.
    This executor:
    - Receives greetings from other agents
    - Passes them to the ADK Greeting Agent
    - Returns the greeting response back in A2A format
    """
    
    def __init__(self):
        self.agent = greeting_agent
        self.session_service = InMemorySessionService()
        self.app_name = "greeting_app"
        self.user_id = "default_user"
        self.session_id = "default_session"

    async def execute(self, context: RequestContext, event_queue: EventQueue):
        # Always create a session (stateless, so same IDs)
        current_session = await self.session_service.create_session(
            app_name=self.app_name,
            user_id=self.user_id,
            session_id=self.session_id
        )
        updater = TaskUpdater(event_queue, context.task_id, context.context_id)
        if not context.current_task:
            await updater.update_status(TaskState.submitted)
        await updater.update_status(TaskState.working)
        # Extract user input from the incoming request
        user_input_text = context.get_user_input()

        # Wrap into ADK content structure
        content = types.Content(
            role="user",
            parts=[types.Part(text=user_input_text)]
        )

        # Create runner
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
                    final_response_text = event.content.parts[0].text
                break

        if final_response_text:
            await event_queue.enqueue_event(
                new_agent_text_message(final_response_text)
            )
            await updater.update_status(
                TaskState.completed, final=True
            )
        else:
            raise RuntimeError("No final response from Greeting Agent.")

    async def cancel(self, context: RequestContext, event_queue: EventQueue):
        raise NotImplementedError("Cancellation not supported for Greeting Agent.")
