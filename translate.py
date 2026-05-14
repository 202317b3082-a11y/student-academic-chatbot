import requests
import json
from typing import Optional

# Configuration
NVIDIA_API_ENDPOINT = "https://integrate.api.nvidia.com/v1/chat/completions"
NVIDIA_API_KEY = "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"
MODEL = "nvidia/nemotron-3-content-safety"



def translate_to_english(text: str, user_language: str = "auto", api_key: Optional[str] = None) -> dict:
    """
    Translate user's text to English using the NVIDIA API.
    
    Args:
        text (str): The text to translate
        user_language (str): The source language (default: "auto" for auto-detection)
        api_key (str, optional): API key. If not provided, uses default
    
    Returns:
        dict: JSON response with translation data
        {
            "success": bool,
            "translated_text": str,
            "source_language": str,
            "target_language": str,
            "error": str (only if success is False)
        }
    """
    try:
        # Use provided API key or default
        key = api_key if api_key else NVIDIA_API_KEY
        
        # Prepare the request headers
        headers = {
            "Authorization": f"Bearer {key}",
            "Accept": "application/json",
            "Content-Type": "application/json"
        }
        
        # Prepare the request body
        payload = {
            "model": MODEL,
            "messages": [
                {
                    "role": "user",
                    "content": f"Translate the following text from {user_language} to English. Only provide the translation, nothing else:\n\n{text}"
                }
            ],
            "max_tokens": 512,
            "temperature": 0.20,
            "top_p": 0.70,
            "stream": False
        }
        
        # Make the API request
        response = requests.post(
            NVIDIA_API_ENDPOINT,
            headers=headers,
            json=payload,
            timeout=30
        )
        
        # Check if request was successful
        response.raise_for_status()
        
        # Extract the translated text from response
        result = response.json()
        translated_text = result['choices'][0]['message']['content'].strip()
        
        return {
            "success": True,
            "translated_text": translated_text,
            "source_language": user_language,
            "target_language": "English"
        }
    
    except requests.exceptions.RequestException as e:
        return {
            "success": False,
            "translated_text": None,
            "source_language": user_language,
            "target_language": "English",
            "error": f"API request failed: {str(e)}"
        }
    except (KeyError, IndexError) as e:
        return {
            "success": False,
            "translated_text": None,
            "source_language": user_language,
            "target_language": "English",
            "error": f"Failed to parse API response: {str(e)}"
        }


def translate_from_english(text: str, target_language: str, api_key: Optional[str] = None) -> dict:
    """
    Translate English text to user's target language using the NVIDIA API.
    
    Args:
        text (str): The English text to translate
        target_language (str): The target language to translate to
        api_key (str, optional): API key. If not provided, uses default
    
    Returns:
        dict: JSON response with translation data
        {
            "success": bool,
            "translated_text": str,
            "source_language": str,
            "target_language": str,
            "error": str (only if success is False)
        }
    """
    try:
        # Use provided API key or default
        key = api_key if api_key else NVIDIA_API_KEY
        
        # Prepare the request headers
        headers = {
            "Authorization": f"Bearer {key}",
            "Accept": "application/json",
            "Content-Type": "application/json"
        }
        
        # Prepare the request body
        payload = {
            "model": MODEL,
            "messages": [
                {
                    "role": "user",
                    "content": f"Translate the following English text to {target_language}. Only provide the translation, nothing else:\n\n{text}"
                }
            ],
            "max_tokens": 512,
            "temperature": 0.20,
            "top_p": 0.70,
            "stream": False
        }
        
        # Make the API request
        response = requests.post(
            NVIDIA_API_ENDPOINT,
            headers=headers,
            json=payload,
            timeout=30
        )
        
        # Check if request was successful
        response.raise_for_status()
        
        # Extract the translated text from response
        result = response.json()
        translated_text = result['choices'][0]['message']['content'].strip()
        
        return {
            "success": True,
            "translated_text": translated_text,
            "source_language": "English",
            "target_language": target_language
        }
    
    except requests.exceptions.RequestException as e:
        return {
            "success": False,
            "translated_text": None,
            "source_language": "English",
            "target_language": target_language,
            "error": f"API request failed: {str(e)}"
        }
    except (KeyError, IndexError) as e:
        return {
            "success": False,
            "translated_text": None,
            "source_language": "English",
            "target_language": target_language,
            "error": f"Failed to parse API response: {str(e)}"
        }


# Example usage
if __name__ == "__main__":
    # Example: Translate Spanish to English
    spanish_text = "¿Cuál es React?"
    print(f"Original (Spanish): {spanish_text}")
    english_response = translate_to_english(spanish_text, "Spanish")
    print(f"Response: {json.dumps(english_response, indent=2)}")
    
    # Example: Translate English back to Spanish
    english_text = "What is React?"
    print(f"\nOriginal (English): {english_text}")
    spanish_response = translate_from_english(english_text, "Spanish")
    print(f"Response: {json.dumps(spanish_response, indent=2)}")
