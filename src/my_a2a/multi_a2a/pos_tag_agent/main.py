# Standard FastAPI-based server for A2A
import uvicorn

# Core A2A components for building agent servers
from a2a.server.apps import A2AStarletteApplication
from a2a.server.request_handlers import DefaultRequestHandler
from a2a.server.tasks import InMemoryTaskStore

# A2A type definitions for agent capabilities and metadata
from a2a.types import AgentCapabilities, AgentCard, AgentSkill

# Our custom agent implementation
from my_a2a.multi_a2a.pos_tag_agent.agent_executor import PosTagAgentExecutor


def main():
    """
    Sets up and runs an A2A-compliant POS tagging server.
    This server can:
    1. Accept text input from other agents
    2. Return a list of part-of-speech tags
    3. Expose its capabilities via an agent card
    """
    # Define what this agent can do (its "skill")
    skill = AgentSkill(
        id="pos_tagger",
        name="POS Tagger Agent",
        description="Returns the part-of-speech tags for a given text.",
        tags=["pos", "nlp", "tagging", "text"],
        examples=[
            "tag the sentence 'The cat sat on the mat'",
            "What are the POS tags for 'I am running'",
        ],
    )

    # Create the agent's "business card"
    agent_card = AgentCard(
        name="POS Tagger Agent",
        description="An agent that performs part-of-speech tagging on text.",
        url="http://localhost:8004/",
        defaultInputModes=["text"],
        defaultOutputModes=["json"],
        skills=[skill],
        version="1.0.0",
        capabilities=AgentCapabilities(),
    )

    # Set up request handling
    request_handler = DefaultRequestHandler(
        agent_executor=PosTagAgentExecutor(),
        task_store=InMemoryTaskStore(),
    )

    # Initialize the A2A server
    server = A2AStarletteApplication(
        http_handler=request_handler,
        agent_card=agent_card,
    )

    uvicorn.run(server.build(), host="0.0.0.0", port=8004)


if __name__ == "__main__":
    main()
