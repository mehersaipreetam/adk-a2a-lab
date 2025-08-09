import os
from dotenv import load_dotenv
from google.adk.models.lite_llm import LiteLlm
from google.adk.models.llm_request import LlmRequest
from google.genai import types

# Load environment variables from .env file
load_dotenv()

# Initialize the LiteLlm model with the Groq API key and base URL
model = LiteLlm(
    model="groq/llama3-8b-8192",
    api_key=os.getenv("GROQ_API_KEY"),
)

async def litellm_complete(prompt: str):
    """
    Function to generate text using the initialized LiteLlm model.
    
    Args:
        prompt: The prompt to use with the model.
    
    Returns:
        The generated text response from the model.
    """
    content = ""
    async for chunk in model.generate_content_async(
        llm_request=LlmRequest(
            model="groq/llama3-8b-8192",
            contents=[types.Content(parts=[types.Part(text=prompt)], role="user")]
        )
    ):
        content += chunk.content.parts[0].text
    return content