import os
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# from google.adk.models.lite_llm import LiteLlm
# Initialize the LiteLlm model with the Groq API key and base URL
# model = LiteLlm(
#     model="groq/llama3-8b-8192",
#     api_key=os.getenv("GROQ_API_KEY"),
# )

from google.adk.models.google_llm import Gemini
model = Gemini(
    model="gemini-2.0-flash",
    api_key=os.getenv("GEMINI_API_KEY")
)