import uuid

import httpx
from a2a.client import A2ACardResolver
from a2a.client.client_factory import ClientFactory
from a2a.types import (
    AgentCard,
    Message,
    MessageSendParams,
    Part,
    Role,
    SendMessageRequest,
    TextPart,
)
from a2a.client.client import ClientConfig

PUBLIC_AGENT_CARD_PATH = "/.well-known/agent.json"
BASE_URL = "http://localhost:9999"


async def main() -> None:
    async with httpx.AsyncClient() as httpx_client:
        # Initialize A2ACardResolver
        resolver = A2ACardResolver(
            httpx_client=httpx_client,
            base_url=BASE_URL,
        )

        final_agent_card_to_use: AgentCard | None = None

        try:
            print(
                f"Fetching public agent card from: {BASE_URL}{PUBLIC_AGENT_CARD_PATH}"
            )
            _public_card = await resolver.get_agent_card()
            print("Fetched public agent card")
            print(_public_card.model_dump_json(indent=2))

            final_agent_card_to_use = _public_card

        except Exception as e:
            print(f"Error fetching public agent card: {e}")
            raise RuntimeError("Failed to fetch public agent card")
        
        client = ClientFactory(config=ClientConfig(httpx_client=httpx_client)).create(final_agent_card_to_use)
        print("A2AClient initialized")

        message_payload = Message(
            role=Role.user,
            messageId=str(uuid.uuid4()),
            parts=[Part(root=TextPart(text="The movie was amazing!"))],
        )

        print("Sending message")

        # Process messages as they arrive from the async generator
        async for response in client.send_message(request=message_payload):
            print("Response:")
            print(response.model_dump_json(indent=2))


if __name__ == "__main__":
    import asyncio

    asyncio.run(main())