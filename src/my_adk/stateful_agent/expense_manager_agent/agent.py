from google.adk.agents import Agent
from my_adk.llm import model
from datetime import datetime
import pytz

def get_current_time():
    """Get the current time in IST timezone"""
    ist = pytz.timezone('Asia/Kolkata')
    current_time = datetime.now(ist)
    return current_time.strftime("%Y-%m-%d %H:%M:%S %Z")

class ExpenseManagerAgent(Agent):
    def process(self, request):
        # Add timestamp to every response
        response = super().process(request)
        if isinstance(response, dict):
            response['timestamp'] = get_current_time()
        return response

# Create the ExpenseManagerAgent with the LiteLlm model
expense_manager_agent = ExpenseManagerAgent(
    name="expense_manager_agent",
    model=model,
    description="Expense Manager Agent",
    instruction="""Process expense-related queries using state dictionary.

    For new expense: Return
    {
        "expenses": [{"amount": float, "category": "food|entertainment|transportation|shopping|utilities|others", "description": string, "date": current_time}],
        "categories": {"food": float, "entertainment": float, "transportation": float, "shopping": float, "utilities": float, "others": float},
        "total_expenses": float,
        "last_updated": string
    }

    For queries: Return matching expenses or category totals from state dictionary.

    Current state dictionary: {state}
    Return only the JSON object."""
    )
