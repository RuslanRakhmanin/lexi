# import asyncio
from google import genai
from google.genai import types
from google.api_core import exceptions as google_exceptions

async def get_llm_response(api_key: str, model_name: str, prompt: str) -> str:
    """
    Get response from Google's Gemini LLM API asynchronously.

    This function creates a client instance using the provided API key, then
    requests a response from the Gemini LLM API using the provided prompt.
    The response is returned as a string. If the request fails, an error message
    is returned instead.

    Args:
        api_key (str): Google API key for authentication
        model_name (str): The name of the LLM model to use
        prompt (str): The input prompt for the LLM

    Returns:
        str: The generated response or an error message if the request fails
    """
    client = genai.Client(api_key=api_key)
    
    print(f"Using model: {model_name}")
    config = types.GenerateContentConfig(
            thinking_config=types.ThinkingConfig(thinking_budget=0) # Disables thinking
        )
    
    try:
        # response = await asyncio.to_thread(client.models.generate_content, model=model_name, contents=prompt, config=config)
        response = await client.aio.models.generate_content(
                            model=model_name,
                            contents=prompt,
                            config=config
                        )
        # Return the generated text
        return response.text
    except google_exceptions.PermissionDenied as e:
        # Handle API key errors
        if "API key not valid" in str(e):
            return "Error: Invalid API key"
        return f"Error: {str(e)}"
    except google_exceptions.ResourceExhausted:
        # Handle quota exceeded errors
        return "Error: Quota exceeded for this API key"
    except ValueError as e:
        # Handle response blocked errors
        if "response blocked" in str(e).lower():
            return "Error: Response blocked by safety filters"
        return f"Error: {str(e)}"
    except Exception as e:
        # Handle any other errors
        return f"Error: {str(e)}"
