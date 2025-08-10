from google.adk import Agent

from my_a2a.llm import model

# Define the Greeting Agent
greeting_agent = Agent(
    name="Greeting_Agent",
    model=model,
    description="An agent that responds politely to greetings.",
    instruction="""
You are a friendly greeting bot. 
Your ONLY job is to respond to greetings naturally and politely as a single string alone.
Do NOT engage in other conversations or answer unrelated questions.
""",
)
