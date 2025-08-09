import asyncio
import json
import uuid
import httpx
from a2a.client import ClientFactory, A2ACardResolver
from a2a.client.client import ClientConfig
from google.adk import Agent
from my_a2a.llm import model


class Client:
    def __init__(self):
        self.agent_registry = {
            "planner": "http://localhost:8001/",
            "greeting": "http://localhost:8002/",
            "sentiment": "http://localhost:8003/"
        }
        self.agents_info = None
    
    async def get_all_agent_cards(self):
        agent_cards = {}
        for agent_name, url in self.agent_registry.items():
            agent_card = await self.get_agent_card(url)
            agent_cards[agent_name] = agent_card
        return agent_cards

    async def get_agent_card(self, url):
        async with httpx.AsyncClient() as httpx_client:
            resolver = A2ACardResolver(httpx_client=httpx_client, base_url=url)
            return await resolver.get_agent_card()

    async def send_message(self, agent_name: str, task: str):
        agent_card = self.agents_info[agent_name]
        message_payload = {
            "role": "user",
            "messageId": str(uuid.uuid4()),
            "parts": [{"root": {"text": task}}]
        }
        return await self.send_message_payload(agent_card, message_payload)

    async def send_message_payload(self, agent_card, message_payload):
        async with httpx.AsyncClient() as httpx_client:
            client = ClientFactory(config=ClientConfig(httpx_client=httpx_client)).create(agent_card)
            send_response = await client.send_message(request=message_payload)
            json_content = json.loads(send_response.root.model_dump_json(exclude_none=True))
            resp = []
            if json_content.get("result", {}).get("artifacts"):
                for artifact in json_content["result"]["artifacts"]:
                    if artifact.get("parts"):
                        resp.extend(artifact["parts"])
            return resp

    async def get_root_instruction(self):
        if self.agents_info is None:
            self.agents_info = await self.get_all_agent_cards()
        prompt = f"""
        You are the Host Agent responsible for orchestrating NLP tasks by delegating them 
        to specialized sub-agents.

        1. If query is a greeting, send to Greeting Agent.
        2. Otherwise, send to Planner Agent to break into subtasks.
        3. Execute subtasks via appropriate agents.
        4. Return final aggregated response.

        Available Agents: {self.agents_info}
        """
        print(prompt)
        return prompt


async def __adk_init__():
    """ADK async initializer for root agent."""
    client = Client()
    instruction = await client.get_root_instruction()
    return Agent(
        model=model,
        name="nlp_client_agent",
        instruction=instruction,
        description="Host agent orchestrating NLP tasks and greetings.",
        tools=[client.send_message],
    )


# ADK expects root_agent to be assigned like this:
root_agent = asyncio.get_event_loop().run_until_complete(__adk_init__())
