import os
from dotenv import load_dotenv
from google.genai import types

# Load environment variables from .env file
load_dotenv()

from google.adk.models.lite_llm import LiteLlm
from google.adk.models.llm_request import LlmRequest
# model = LiteLlm(
#     model="groq/llama-3.1-8b-instant",
#     api_key=os.getenv("GROQ_API_KEY"),
# )

# async def llm_complete(prompt: str):
#     """
#     Function to generate text using the initialized LiteLlm model.
    
#     Args:
#         prompt: The prompt to use with the model.
    
#     Returns:
#         The generated text response from the model.
#     """
#     content = ""
#     async for chunk in model.generate_content_async(
#         llm_request=LlmRequest(
#             model="groq/llama3-8b-8192",
#             contents=[types.Content(parts=[types.Part(text=prompt)], role="user")]
#         )
#     ):
#         content += chunk.content.parts[0].text
#     return content


from google.adk.models.google_llm import Gemini
from google.adk.models.llm_request import LlmRequest
model = Gemini(
    model="gemini-2.0-flash",
    api_key=os.getenv("GEMINI_API_KEY")
)

async def llm_complete(prompt: str):
    """
    Function to generate text using the initialized gemini model.
    
    Args:
        prompt: The prompt to use with the model.
    
    Returns:
        The generated text response from the model.
    """
    content = ""
    async for chunk in model.generate_content_async(
        llm_request=LlmRequest(
            model=model.model,
            contents=[
                types.Content(
                    parts=[types.Part(text=prompt)],
                    role="user"
                )
            ]
        )
    ):
        if hasattr(chunk, "content") and chunk.content.parts:
            for part in chunk.content.parts:
                if hasattr(part, "text") and part.text:
                    content += part.text
    return content