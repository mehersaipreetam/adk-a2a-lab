from google.adk.agents import Agent
from my_adk.llm import model

# Create the SentimentAgent with the LiteLlm model
agent = Agent(
    name="sentiment_agent",
    model=model,
    description="Sentiment Agent",
    instruction="Analyze the sentiment of text inputs and return a JSON object with fields: 'sentiment' (one of 'POS', 'NEG', 'NEU'). For example: {'sentiment': 'POS'}. Do not return any other text or explanation, just the JSON object.",
)

# Set the root agent - this is mandatory for the agent to be used in the ADK
root_agent = agent