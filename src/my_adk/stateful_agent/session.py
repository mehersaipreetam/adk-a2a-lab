from google.adk.sessions import InMemorySessionService
from google.adk.runners import Runner
from my_adk.stateful_agent.expense_manager_agent import expense_manager_agent
from google.genai import types
import asyncio

async def main():
    # Backend store can be updated for persistent storage
    # For now, we use an in-memory session service for simplicity
    session_service_stateful = InMemorySessionService()
    input_text = None

    while input_text != "exit":
        print("\n=== New Query ===")
        query_user_id = input("Enter user ID: ").strip()
        query_session_id = input("Enter session ID: ").strip()

        if not query_user_id or not query_session_id:
            print("Error: User ID and Session ID cannot be empty")
            return


        try:
            # Check if session already exists
            if await session_service_stateful.get_session(app_name="expense_manager_app", user_id=query_user_id, session_id=query_session_id):
                print(f"Session already exists for User: {query_user_id}, Session: {query_session_id}")
            else:
                expense_session = await session_service_stateful.create_session(
                    app_name="expense_manager_app",
                    user_id=query_user_id,
                    session_id=query_session_id,
                    state={
                        "state": {
                            "expenses": [],  # List to store expense records
                            "categories": {  # Track totals by category
                                "food": 0.0,
                                "entertainment": 0.0,
                                "transportation": 0.0,
                                "shopping": 0.0,
                                "utilities": 0.0,
                                "others": 0.0
                            },
                            "total_expenses": 0.0,  # Running total of all expenses
                            "last_updated": None  # Timestamp of last transaction
                        }
                    }
                )
                print(f"\nSession- {expense_session.id} created successfully!")

        except Exception as e:
            print(f"Error creating session: {str(e)}")
            return

        runner = Runner(
            agent=expense_manager_agent,
            app_name="expense_manager_app",
            session_service=session_service_stateful,
        )

        input_text = input("Enter your expense query (or type 'exit' to quit): ")
        if input_text.lower() == "exit":
            break

        print(f"\nProcessing query for User: {query_user_id}, Session: {query_session_id}")

        # Process the input through the agent
        new_message = types.Content(
            role="user", parts=[types.Part(text=input_text)]
        )

        try:
            # Google adk suggests using run_async for to handle events in prod - run is for local alone
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
            print(f"Error processing query: {str(e)}")
            print("Please try again with valid user and session IDs")

if __name__ == "__main__":
    asyncio.run(main())
