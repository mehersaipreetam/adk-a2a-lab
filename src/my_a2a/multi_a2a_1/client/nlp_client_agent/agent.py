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

    # async def send_message(self, agent_name: str, task: str):
    #     agent_card = self.agents_info[agent_name]
    #     message_payload = {
    #         "role": "user",
    #         "kind": "message",
    #         "message_id": str(uuid.uuid4()),
    #         "parts": [
    #             {
    #                 "kind": "text",
    #                 "text": task
    #             }
    #         ]
    #     }
    #     response = await self.send_message_payload(agent_card, message_payload)
    #     print(f"Response from {agent_name} agent: {response}")
    #     return response

    # async def send_message_payload(self, agent_card, message_payload):
    #     async with httpx.AsyncClient() as httpx_client:
    #         client = ClientFactory(config=ClientConfig(httpx_client=httpx_client)).create(agent_card)
            
    #         # Use a list to accumulate all text parts
    #         accumulated_text = []

    #         async for response in client.send_message(request=message_payload):
    #             json_content = response.model_dump(exclude_none=True)
    #             if json_content.get("kind", "") == "message":
    #                 for part in json_content.get("parts", []):
    #                     if part.get("kind", "") == "text":
    #                         accumulated_text.append(part["text"])

    #         # Join the list of strings into a single response
    #         return " ".join(accumulated_text)
    
    async def send_message(self, agent_name: str, task: str):
        agent_card = self.agents_info[agent_name]
        message_payload = {
            "role": "user",
            "kind": "message",
            "message_id": str(uuid.uuid4()),
            "parts": [
                {
                    "kind": "text",
                    "text": task
                }
            ]
        }
        
        # This now returns the full structured message
        response_content = await self.send_message_payload(agent_card, message_payload)

        # Process the structured response to extract useful information
        final_response_text = ""
        if response_content and response_content.get("kind") == "message":
            for part in response_content.get("parts", []):
                if part.get("kind") == "text":
                    final_response_text += part.get("text", "") + " "
        
        print(f"Response from {agent_name} agent: {final_response_text.strip()}")
        return final_response_text.strip()

    async def send_message_payload(self, agent_card, message_payload):
        async with httpx.AsyncClient() as httpx_client:
            client = ClientFactory(config=ClientConfig(httpx_client=httpx_client)).create(agent_card)
            
            # This variable will hold the final, complete message content
            final_response_content = None

            async for response in client.send_message(request=message_payload):
                # Update with the latest response in the stream
                final_response_content = response.model_dump(exclude_none=True)
            
            # Return the final structured message
            return final_response_content

    async def get_root_instruction(self, ctx):
        if self.agents_info is None:
            self.agents_info = await self.get_all_agent_cards()

        # ctx is a placeholder for context, not used here - mandatory for callable version of InstructionProvider and adk web cmd
        state_info = getattr(ctx, "state", None)

        prompt = f"""
        You are the Host Agent responsible for orchestrating NLP tasks by delegating them 
        to specialized sub-agents. You must perform all delegations using the `send_message` tool.  

        Rules for orchestration:
        1. If the query is a greeting (e.g., "hi", "hello", "good morning"), call `send_message` tool with:
        - `agent_name` = "greeting"
        - `content` = the original user query
        Respond to user with the greeting agent's response directly. This is the only case where you respond directly without further processing.
        2. Otherwise:
        a. First, call `send_message` tool with:
            - `agent_name` = "planner"
            - `content` = the original user query  
            This will return a structured plan containing subtasks.
        b. For each subtask in the returned plan, call `send_message` tool with:
            - `agent_name` = the agent specified for that subtask
            - `content` = the subtask's input text
        3. Aggregate all subtask results into a single coherent final response.
        4. Return this final aggregated response to the user.

        Available Agents: {self.agents_info}
        Current State: {state_info}

        Never invoke agents directly. Always route calls through the `send_message` tool with the correct `agent_name`.
        """
        return prompt.strip()


def main():
    """ADK async initializer for root agent."""
    client = Client()
    # instruction = await client.get_root_instruction()
    return Agent(
        model=model,
        name="nlp_client_agent",
        instruction=client.get_root_instruction,
        description="Host agent orchestrating NLP tasks and greetings.",
        tools=[client.send_message],
    )

root_agent = main()
