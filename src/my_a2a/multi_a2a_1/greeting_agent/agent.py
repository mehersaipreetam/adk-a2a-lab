from google.adk import Agent

# Define the Greeting Agent
greeting_agent = Agent(
    name="Greeting_Agent",
    description="An agent that responds politely to greetings.",
    instruction="""
You are a friendly greeting bot. 
Your ONLY job is to respond to greetings naturally and politely.
Do NOT engage in other conversations or answer unrelated questions.
""",
)
