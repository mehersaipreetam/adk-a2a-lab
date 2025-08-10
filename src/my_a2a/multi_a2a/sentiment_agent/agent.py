# Below is the code from the file src/my_adk/simple_agent/sentiment_agent/agent.py

from google.adk.agents import Agent
from my_adk.llm import model

# Initialize a simple sentiment analysis agent
# Unlike stateful agents, this one processes each input independently
# without maintaining conversation history or state
agent = Agent(
    name="sentiment_agent",
    model=model,
    description="Sentiment Agent",
    instruction="Analyze the sentiment of text inputs and return a JSON object with fields: 'sentiment' (one of 'POS', 'NEG', 'NEU'). For example: {'sentiment': 'POS'}. Do not return any other text or explanation, just the JSON object.",
)

# ADK requires a root_agent to be defined
# This is the entry point for message processing
# When ADK receives a message, it starts with the root_agent
root_agent = agent