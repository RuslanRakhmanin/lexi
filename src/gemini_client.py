import asyncio
import google.generativeai as genai
from google.api_core import exceptions as google_exceptions

async def get_llm_response(api_key: str, prompt: str) -> str:
    """
    Get response from Google's Gemini LLM API asynchronously.
    
    Args:
        api_key: Google API key for authentication
        prompt: The input prompt for the LLM
        
    Returns:
        str: The generated response or an error message if the request fails
    """
    genai.configure(api_key=api_key)
    model = genai.GenerativeModel('gemini-pro')
    
    try:
        response = await asyncio.to_thread(model.generate_content, prompt)
        return response.text
    except google_exceptions.PermissionDenied as e:
        if "API key not valid" in str(e):
            return "Error: Invalid API key"
        return f"Error: {str(e)}"
    except google_exceptions.ResourceExhausted:
        return "Error: Quota exceeded for this API key"
    except ValueError as e:
        if "response blocked" in str(e).lower():
            return "Error: Response blocked by safety filters"
        return f"Error: {str(e)}"
    except Exception as e:
        return f"Error: {str(e)}"