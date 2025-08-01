from google.adk.agents import Agent
from google.adk.models.lite_llm import LiteLlm
import os
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# Initialize the LiteLlm model with the Groq API key and base URL
model = LiteLlm(
    model="groq/llama3-8b-8192",
    api_key=os.getenv("GROQ_API_KEY"),
)

# Create the SentimentAgent with the LiteLlm model
agent = Agent(
    name="sentiment_agent",
    model=model,
    description="Sentiment Agent",
    instruction="Analyze the sentiment of text inputs and return a JSON object with fields: 'sentiment' (one of 'POS', 'NEG', 'NEU'). For example: {'sentiment': 'POS'}. Do not return any other text or explanation, just the JSON object.",
)

# Set the root agent - this is mandatory for the agent to be used in the ADK
root_agent = agent