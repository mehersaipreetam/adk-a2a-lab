from google.adk.sessions import InMemorySessionService
from google.adk.runners import Runner
from my_adk.stateful_agent.expense_manager_agent import expense_manager_agent
from google.genai import types
import asyncio

async def main():
    session_service_stateful = InMemorySessionService()

    # Create a session service to manage expense tracking state
    expense_session = await session_service_stateful.create_session(
        app_name="expense_manager_app",
        user_id="example_user",
        session_id="session_1",  # Unique session ID for tracking
        state={
            "state": {
                "expenses": [],  # List to store expense records
                "categories": {  # Track totals by category
                    "food": 0.0,
                    "entertainment": 60.0,
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

    print("Session created with initial state:", expense_session.id)

    runner = Runner(
        agent=expense_manager_agent,
        app_name="expense_manager_app",
        session_service=session_service_stateful,
    )

    input_text = None

    while input_text != "exit":
        input_text = input("Enter your expense query (or type 'exit' to quit): ")
        if input_text.lower() == "exit":
            break

        # Process the input through the agent
        new_message = types.Content(
            role="user", parts=[types.Part(text=input_text)]
        )

        # Google adk suggests using run_async for to handle events in prod - run is for local alone
        async for event in runner.run_async(
            user_id="example_user",
            session_id="session_1",
            new_message=new_message,
        ):
            if event.is_final_response():
                if event.content and event.content.parts:
                    response_text = event.content.parts[0].text
                    print("Agent Response:", response_text)

if __name__ == "__main__":
    asyncio.run(main())
