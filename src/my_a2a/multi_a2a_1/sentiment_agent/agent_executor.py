# A2A components for agent execution
from a2a.server.agent_execution import AgentExecutor  # Base class for agent executors
from a2a.server.agent_execution.context import RequestContext  # Handles request data
from a2a.server.events.event_queue import EventQueue  # Manages message events
from a2a.utils import new_agent_text_message  # Helper for creating responses

# ADK components for running the sentiment agent
from google.adk.runners import Runner  # Executes agent logic
from google.adk.sessions import InMemorySessionService  # Manages agent state
from google.genai import types  # Structures for LLM communication

# Import our pre-configured sentiment analysis agent
from my_adk.simple_agent.sentiment_agent.agent import agent as sentiment_agent


class SentimentAgentExecutor(AgentExecutor):
    """
    Bridges ADK and A2A: Makes our sentiment analysis agent available to other agents.
    
    This executor:
    1. Receives requests from other agents via A2A protocol
    2. Processes them using our ADK-based sentiment agent
    3. Returns results in A2A-compatible format
    
    Key Components:
    - agent: Our ADK sentiment analysis agent
    - session_service: Manages conversation state (simple in this case)
    - app_name/user_id/session_id: Identifies this agent instance
    """
    
    def __init__(self):
        # Use our pre-configured sentiment analysis agent
        self.agent = sentiment_agent
        
        # Simple in-memory session (no persistence needed for stateless agent)
        self.session_service = InMemorySessionService()
        
        # Identifiers for this agent instance
        self.app_name = "sentiment_analysis_app"  # Application identifier
        self.user_id = "default_user"            # Single user for all requests
        self.session_id = "default_session"      # Single session (stateless)
        
    async def execute(self, context: RequestContext, event_queue: EventQueue):
        """
         Processes incoming A2A requests through our sentiment analysis agent.
        
        Flow:
        1. Create/get session for request handling
        2. Extract text from incoming request
        3. Process text through ADK agent
        4. Return sentiment analysis result
        
        Args:
            context: Contains the incoming request details (like input text)
            event_queue: For sending responses back to the requesting agent
        """
        # Initialize or get existing session
        # For our stateless agent, we create a new session each time
        current_session = await self.session_service.create_session(
            app_name=self.app_name,
            user_id=self.user_id,
            session_id=self.session_id
        )

        print(f"\n Session {current_session.id} created successfully.")

        # Extract the text to analyze from the A2A request
        user_input_text = context.get_user_input()

        # Format the input for our ADK agent
        # ADK expects a specific message structure
        content = types.Content(
            role="user",  # Message comes from another agent
            parts=[types.Part(text=user_input_text)]  # The text to analyze
        )

        # Set up the ADK runner to process our request
        runner = Runner(
            agent=self.agent,
            app_name=self.app_name,
            session_service=self.session_service,
        )

        # Will store the final sentiment result
        final_response_text = None

        # Process the request through our ADK agent
        # run_async yields a stream of events as processing happens
        async for event in runner.run_async(
            user_id=self.user_id,      # Who's making the request
            session_id=self.session_id, # Which conversation this belongs to
            new_message=content,        # The text to analyze
        ):
            # We only care about the final sentiment result
            # (could handle intermediate events for streaming responses)
            if event.is_final_response():
                if event.content and event.content.parts:
                    final_response_text = event.content.parts[0].text
                break

        # Handle the response
        if final_response_text is not None:
            # Create and send an A2A-compatible message with the result
            # This will be received by the requesting agent
            await event_queue.enqueue_event(
                new_agent_text_message(final_response_text)
            )
        else:
            raise RuntimeError("No final response received from the agent.")


    async def cancel(self, context: RequestContext, event_queue: EventQueue):
        raise NotImplementedError("Cancellation is not supported for sentiment analysis agent.")