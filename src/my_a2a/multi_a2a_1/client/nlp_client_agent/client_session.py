# Import the root NLP agent
from my_a2a.multi_a2a_1.client.nlp_client_agent.agent import root_agent

# Core ADK components
from google.adk.sessions import InMemorySessionService
from google.adk.runners import Runner
from google.genai import types
import asyncio


async def main():
    """
    Main execution loop for the NLP Client Agent application.
    Handles:
    1. Session management (creation, retrieval)
    2. User interaction (input/output)
    3. Agent communication
    4. State persistence
    """
    session_service_stateful = InMemorySessionService()
    input_text = None

    while input_text != "exit":
        print("\n=== New NLP Query ===")
        query_user_id = input("Enter user ID: ").strip()
        query_session_id = input("Enter session ID: ").strip()

        if not query_user_id or not query_session_id:
            print("\nError: User ID and Session ID cannot be empty")
            return

        try:
            if await session_service_stateful.get_session(
                app_name="nlp_client_app",
                user_id=query_user_id,
                session_id=query_session_id
            ):
                print(f"\nSession already exists for User: {query_user_id}, Session: {query_session_id}")
            else:
                nlp_session = await session_service_stateful.create_session(
                    app_name="nlp_client_app",
                    user_id=query_user_id,
                    session_id=query_session_id,
                    state={"state": {}}  # NLP agent may not need pre-defined structure
                )
                print(f"\nSession- {nlp_session.id} created successfully!")

        except Exception as e:
            print(f"\nError creating session: {str(e)}")
            return

        # Runner for NLP agent
        runner = Runner(
            agent=root_agent,  # Import from your nlp_client_agent.agent
            app_name="nlp_client_app",
            session_service=session_service_stateful,
        )

        input_text = input("Enter your NLP query (or type 'exit' to quit): ")
        if input_text.lower() == "exit":
            break

        print(f"\nProcessing query for User: {query_user_id}, Session: {query_session_id}")

        new_message = types.Content(
            role="user",
            parts=[types.Part(text=input_text)]
        )

        try:
            async for event in runner.run_async(
                user_id=query_user_id,
                session_id=query_session_id,
                new_message=new_message,
            ):
                if event.is_final_response():
                    if event.content and event.content.parts:
                        response_text = event.content.parts[0].text
                        print("Agent Response:", response_text)
        except Exception as e:
            print(f"\nError processing query: {str(e)}")
            print("\nPlease try again with valid user and session IDs")


if __name__ == "__main__":
    asyncio.run(main())