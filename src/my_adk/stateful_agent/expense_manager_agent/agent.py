from google.adk.agents import Agent
from my_adk.llm import model
from datetime import datetime
import pytz

def get_current_time():
    """Get the current time in IST timezone for consistent timestamp tracking"""
    ist = pytz.timezone('Asia/Kolkata')
    current_time = datetime.now(ist)
    return current_time.strftime("%Y-%m-%d %H:%M:%S %Z")

class ExpenseManagerAgent(Agent):
    """
    Custom Agent for managing expenses. Extends ADK's Agent class to:
    1. Process expense-related queries
    2. Maintain state across conversations
    3. Add timestamps to responses
    """
    def process(self, request):
        # Call parent class's process method to handle the core LLM interaction
        response = super().process(request)
        # Add timestamps only to dictionary responses (not to error messages)
        if isinstance(response, dict):
            response['timestamp'] = get_current_time()
        return response

# Initialize our ExpenseManagerAgent
# The agent needs four key components:
# 1. name: Unique identifier for this agent instance
# 2. model: The LLM model to use for processing queries
# 3. description: Brief description of the agent's purpose
# 4. instruction: Detailed instructions for how the agent should process inputs and format outputs
agent = ExpenseManagerAgent(
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