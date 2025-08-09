import uvicorn
from a2a.server.apps import A2AStarletteApplication
from a2a.server.request_handlers import DefaultRequestHandler
from a2a.server.tasks import InMemoryTaskStore
from a2a.types import AgentCapabilities, AgentCard, AgentSkill
from my_a2a.multi_a2a_1.greeting_agent.agent_executor import GreetingAgentExecutor

def main():
    skill = AgentSkill(
        id="greeting",
        name="Greetings",
        description="Respond with a friendly greeting based on the input text",
        tags=["greeting", "conversation"],
        examples=["Hello!", "Good morning!", "Hi there!"],
    )

    agent_card = AgentCard(
        name="Greetings Agent",
        description="An agent that returns a friendly greeting.",
        url="http://localhost:8002/",
        defaultInputModes=["text"],
        defaultOutputModes=["text"],
        skills=[skill],
        version="1.0.0",
        capabilities=AgentCapabilities(),
    )

    request_handler = DefaultRequestHandler(
        agent_executor=GreetingAgentExecutor(),
        task_store=InMemoryTaskStore(),
    )

    server = A2AStarletteApplication(
        http_handler=request_handler,
        agent_card=agent_card,
    )

    uvicorn.run(server.build(), host="0.0.0.0", port=8002)

if __name__ == "__main__":
    main()
