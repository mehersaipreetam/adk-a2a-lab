from google.adk.agents import Agent
from my_adk.llm import model
from google.adk.sessions import InMemorySessionService, Session

# Create a session service to manage expense tracking state
session_service = InMemorySessionService()
expense_session = session_service.create_session(
    app_name="expense_manager_app",
    user_id="example_user",
    state={
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
)

# Create the ExpenseManagerAgent with the LiteLlm model
agent = Agent(
    name="expense_manager_agent",
    model=model,
    description="Expense Manager Agent",
    instruction="Manage expenses by analyzing text inputs and returning a JSON object with fields: 'expense' (a float representing the expense amount), 'category' (a string representing the category of the expense). If the question asks for a specific expense, return the relevant information in the JSON object. For example: [{'expense': 100.0, 'category': 'food', 'detailed_description': 'Restaurant Name'}, {'expense': 120.0, 'category': 'entertainment', 'detailed_description': 'Iron Man Movie'}]. If the question asks for a summary of expenses, return a JSON object with the total expenses and a breakdown by category. For example: {'total_expenses': 220.0, 'breakdown': {'food': 100.0, 'entertainment': 120.0}}}. Do not return any other text or explanation, just the JSON object properly indented.",
    )

# Set the root agent - this is mandatory for the agent to be used in the ADK
root_agent = agent

