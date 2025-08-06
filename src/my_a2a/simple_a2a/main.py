# Standard FastAPI-based server for A2A
import uvicorn

# Core A2A components for building agent servers
from a2a.server.apps import A2AStarletteApplication  # Base server application
from a2a.server.request_handlers import DefaultRequestHandler  # Handles incoming requests
from a2a.server.tasks import InMemoryTaskStore  # Stores task states temporarily

# A2A type definitions for agent capabilities and metadata
from a2a.types import AgentCapabilities, AgentCard, AgentSkill

# Our custom agent implementation
from my_a2a.simple_a2a.agent_executor import SentimentAgentExecutor


def main():
    """
    Sets up and runs an A2A-compliant sentiment analysis server.
    This server can:
    1. Accept text input from other agents
    2. Return sentiment analysis results
    3. Expose its capabilities via an agent card
    """
    # Define what this agent can do (its "skill")
    # This helps other agents understand how to interact with us
    skill = AgentSkill(
        id="sentiment",
        name="Sentiment Analysis",
        description="Return the sentiment of the input text",
        tags=["sentiment analysis", "text"],
        examples=["POS", "NEG", "NEU"],
    )

    # Create the agent's "business card"
    # This tells other agents everything they need to know about our capabilities
    agent_card = AgentCard(
        name="Sentiment Analysis Agent",  # Agent's name
        description="A simple agent that returns the sentiment of the input text.",
        url="http://localhost:9999/",     # Where to find this agent
        defaultInputModes=["text"],       # What input we accept
        defaultOutputModes=["text"],      # What output we provide
        skills=[skill],                   # What we can do
        version="1.0.0",                  # For compatibility checking
        capabilities=AgentCapabilities(), # Additional features (none needed here)
    )

    # Set up request handling
    # This connects incoming requests to our agent's logic
    request_handler = DefaultRequestHandler(
        agent_executor=SentimentAgentExecutor(),  # Our custom agent logic
        task_store=InMemoryTaskStore(),          # Temporary task storage
    )

    # Initialize the A2A server
    # This creates an API that other agents can interact with
    server = A2AStarletteApplication(
        http_handler=request_handler,  # Handles incoming requests
        agent_card=agent_card,        # Exposes our capabilities
    )

    uvicorn.run(server.build(), host="0.0.0.0", port=9999)


if __name__ == "__main__":
    main()