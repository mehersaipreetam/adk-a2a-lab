import uvicorn
from a2a.server.apps import A2AStarletteApplication
from a2a.server.request_handlers import DefaultRequestHandler
from a2a.server.tasks import InMemoryTaskStore
from a2a.types import AgentCapabilities, AgentCard, AgentSkill
from my_a2a.simple_a2a.agent_executor import SentimentAgentExecutor


def main():
    skill = AgentSkill(
        id="sentiment",
        name="Sentiment Analysis",
        description="Return the sentiment of the input text",
        tags=["sentiment analysis", "text"],
        examples=["POS", "NEG", "NEU"],
    )

    agent_card = AgentCard(
        name="Sentiment Analysis Agent",
        description="A simple agent that returns the sentiment of the input text.",
        url="http://localhost:9999/",
        defaultInputModes=["text"],
        defaultOutputModes=["text"],
        skills=[skill],
        version="1.0.0",
        capabilities=AgentCapabilities(),
    )

    request_handler = DefaultRequestHandler(
        agent_executor=SentimentAgentExecutor(),
        task_store=InMemoryTaskStore(),
    )

    server = A2AStarletteApplication(
        http_handler=request_handler,
        agent_card=agent_card,
    )

    uvicorn.run(server.build(), host="0.0.0.0", port=9999)


if __name__ == "__main__":
    main()