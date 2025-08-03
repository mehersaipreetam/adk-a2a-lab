# Core ADK components for building stateful agents
from google.adk.sessions import InMemorySessionService  # Manages state persistence (in-memory for development)
from google.adk.runners import Runner  # Orchestrates agent execution and state management
from my_adk.stateful_agent.expense_manager_agent import expense_manager_agent  # Our custom expense tracking agent
from google.genai import types  # Structures for agent-user communication
import asyncio  # Required for ADK's async operations

async def main():
    """
    Main execution loop for the expense manager application.
    Handles:
    1. Session management (creation, retrieval)
    2. User interaction (input/output)
    3. Agent communication
    4. State persistence
    """
    # InMemorySessionService is suitable for development
    # For production: Replace with a persistent storage solution
    session_service_stateful = InMemorySessionService()
    input_text = None  # Controls the main interaction loop

    # Main interaction loop - continues until user types 'exit'
    while input_text != "exit":
        print("\n=== New Query ===")
        # Get session identifiers for each query
        # This allows users to switch between different expense tracking sessions
        query_user_id = input("Enter user ID: ").strip()
        query_session_id = input("Enter session ID: ").strip()

        # Validate required identifiers
        if not query_user_id or not query_session_id:
            print("\nError: User ID and Session ID cannot be empty")
            return

        try:
            # ADK session management:
            # 1. First try to retrieve existing session
            # 2. Create new session if none exists
            # This allows continuous expense tracking across multiple interactions
            if await session_service_stateful.get_session(
                app_name="expense_manager_app",  # Identifies this application
                user_id=query_user_id,          # Who owns this session
                session_id=query_session_id      # Unique session identifier
            ):
                print(f"\nSession already exists for User: {query_user_id}, Session: {query_session_id}")
            else:
                # Create new session with initial state structure
                expense_session = await session_service_stateful.create_session(
                    app_name="expense_manager_app",
                    user_id=query_user_id,
                    session_id=query_session_id,
                    # Initial state structure that our agent expects:
                    state={
                        "state": {  # Nested under 'state' key as per ADK conventions
                            "expenses": [],  # Chronological list of all transactions
                            "categories": {  # Pre-defined expense categories with running totals
                                "food": 0.0,
                                "entertainment": 0.0,
                                "transportation": 0.0,
                                "shopping": 0.0,
                                "utilities": 0.0,
                                "others": 0.0  # Catch-all for miscellaneous expenses
                            },
                            "total_expenses": 0.0,  # Aggregate total across all categories
                            "last_updated": None    # Tracks most recent transaction timestamp
                        }
                    }
                )
                print(f"\nSession- {expense_session.id} created successfully!")

        except Exception as e:
            print(f"\nError creating session: {str(e)}")
            return

        # Initialize ADK Runner:
        # - Manages the lifecycle of agent interactions
        # - Handles state updates automatically
        # - Processes messages between user and agent
        runner = Runner(
            agent=expense_manager_agent,          # Our custom ExpenseManagerAgent
            app_name="expense_manager_app",       # Must match session app_name
            session_service=session_service_stateful,  # For state persistence
        )

        # Get user's expense-related query
        input_text = input("Enter your expense query (or type 'exit' to quit): ")
        if input_text.lower() == "exit":
            break

        print(f"\nProcessing query for User: {query_user_id}, Session: {query_session_id}")

        # Create ADK message structure:
        # - role: Identifies message source (user/agent)
        # - parts: Contains actual message content
        new_message = types.Content(
            role="user",
            parts=[types.Part(text=input_text)]  # User's expense query
        )

        try:
            # run_async is ADK's recommended method for production use:
            # 1. Handles asynchronous processing
            # 2. Manages state updates
            # 3. Supports streaming responses
            async for event in runner.run_async(
                user_id=query_user_id,      # Links to specific user's context
                session_id=query_session_id, # Maintains conversation continuity
                new_message=new_message,     # The current query to process
            ):
                # ADK events can be intermediate or final
                # We only care about final responses here
                if event.is_final_response():
                    if event.content and event.content.parts:
                        response_text = event.content.parts[0].text
                        print("Agent Response:", response_text)
        except Exception as e:
            print(f"\nError processing query: {str(e)}")
            print("\nPlease try again with valid user and session IDs")

if __name__ == "__main__":
    asyncio.run(main())
