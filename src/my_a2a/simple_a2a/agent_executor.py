from a2a.server.agent_execution import AgentExecutor
from a2a.server.agent_execution.context import RequestContext
from a2a.server.events.event_queue import EventQueue
from a2a.utils import new_agent_text_message
from pydantic import BaseModel
from google.adk.runners import Runner
from google.adk.sessions import InMemorySessionService
from google.genai import types

from my_adk.simple_agent.sentiment_agent.agent import agent as sentiment_agent

class SentimentAgentExecutor(AgentExecutor):
    """
    Custom executor for the sentiment analysis agent.
    This class extends AgentExecutor to handle sentiment analysis requests.
    """
    
    def __init__(self):
        self.agent = sentiment_agent
        self.session_service = InMemorySessionService()
        self.app_name = "sentiment_analysis_app"
        self.user_id = "default_user"
        self.session_id = "default_session"
        
    async def execute(self, context: RequestContext, event_queue: EventQueue):
        """
        Execute the sentiment analysis request.

        Args:
            context (RequestContext): The request context containing the input text.
            event_queue (EventQueue): The event queue for handling events during execution.
        """
        current_session = await self.session_service.create_session(app_name=self.app_name, user_id=self.user_id, session_id=self.session_id)

        print(f"Current session: {current_session}")

        user_input_text = context.get_user_input()

        content = types.Content(role="user", parts=[types.Part(text=user_input_text)])

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

        if final_response_text is not None:
            await event_queue.enqueue_event(new_agent_text_message(final_response_text))
        else:
            raise RuntimeError("No final response received from the agent.")


    async def cancel(self, context: RequestContext, event_queue: EventQueue):
        raise NotImplementedError("Cancellation is not supported for sentiment analysis agent.")