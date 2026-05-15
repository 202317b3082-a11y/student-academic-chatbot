from sarvamai import SarvamAI

# Initialize client
client = SarvamAI(
    api_subscription_key="sk_fm3qm7nr_fRfha3W00NIXikJR80tdK65V",
)

# Language mapping - from friendly names/codes to API language codes
LANGUAGE_MAP = {
    # Friendly names (from UI)
    "english": "en-IN",
    "hindi": "hi-IN",
    "tamil": "ta-IN",
    "telugu": "te-IN",
    "kannada": "kn-IN",
    "malayalam": "ml-IN",
    "marathi": "mr-IN",
    "gujarati": "gu-IN",
    "bengali": "bn-IN",
    "punjabi": "pa-IN",
    "odia": "od-IN",
    "assamese": "as-IN",
    "urdu": "ur-IN",
    # API codes (direct passthrough)
    "en-in": "en-IN",
    "hi-in": "hi-IN",
    "ta-in": "ta-IN",
    "te-in": "te-IN",
    "kn-in": "kn-IN",
    "ml-in": "ml-IN",
    "mr-in": "mr-IN",
    "gu-in": "gu-IN",
    "bn-in": "bn-IN",
    "pa-in": "pa-IN",
    "od-in": "od-IN",
    "as-in": "as-IN",
    "ur-in": "ur-IN",
    # Uppercase variants
    "EN-IN": "en-IN",
    "HI-IN": "hi-IN",
    "TA-IN": "ta-IN",
    "TE-IN": "te-IN",
    "KN-IN": "kn-IN",
    "ML-IN": "ml-IN",
    "MR-IN": "mr-IN",
    "GU-IN": "gu-IN",
    "BN-IN": "bn-IN",
    "PA-IN": "pa-IN",
    "OD-IN": "od-IN",
    "AS-IN": "as-IN",
    "UR-IN": "ur-IN",
    "auto": "auto",
    "AUTO": "auto",
    "Auto": "auto",
}

def get_language_code(lang: str) -> str:
    """
    Convert language name or code to API language code.
    Defaults to 'auto' if language not found.
    """
    if not lang:
        return "auto"
    
    normalized = lang.strip().lower()
    return LANGUAGE_MAP.get(normalized, "auto")


def extract_translated_text(response) -> str:
    """
    Extract translated text from API response.
    Handles TranslationResponse object, dict, and string formats.
    """
    if response is None:
        return ""
    
    # If it's a string, return as-is
    if isinstance(response, str):
        return response
    
    # If it's a dict, extract from known fields
    if isinstance(response, dict):
        return response.get("output") or response.get("translated_text") or response.get("text") or str(response)
    
    # Try to access as TranslationResponse object with common attributes
    try:
        # Try common attribute names (TranslationResponse from SarvamAI has 'translated_text')
        if hasattr(response, "translated_text"):
            return str(response.translated_text)
        if hasattr(response, "output"):
            return str(response.output)
        if hasattr(response, "text"):
            return str(response.text)
        if hasattr(response, "data"):
            return str(response.data)
        # Fallback to string representation
        return str(response)
    except Exception:
        return str(response)


def translate_to_english(text: str, source_lang: str = "auto") -> dict:
    """
    Translate text from user-selected language to English.
    """
    if not text or not text.strip():
        return {
            "success": False,
            "translated_text": text,
            "source_language": source_lang,
            "target_language": "English",
            "error": "Empty text cannot be translated"
        }
    
    try:
        # Convert language name/code to API format
        api_source_lang = get_language_code(source_lang)
        
        response = client.text.translate(
            input=text.strip(),
            source_language_code=api_source_lang,
            target_language_code="en-IN",   # English (India)
            speaker_gender="Male",
            mode="formal",
            model="mayura:v1",
            numerals_format="native"
        )
        
        # Extract translated text from response (handles TranslationResponse object)
        translated_text = extract_translated_text(response)
        
        if not translated_text:
            return {
                "success": False,
                "translated_text": text,
                "source_language": source_lang,
                "target_language": "English",
                "error": "No translation returned from API"
            }
        
        return {
            "success": True,
            "translated_text": translated_text,
            "source_language": source_lang,
            "target_language": "English"
        }
    except Exception as e:
        return {
            "success": False,
            "translated_text": text,
            "source_language": source_lang,
            "target_language": "English",
            "error": f"Translation error: {str(e)}"
        }


def translate_from_english(text: str, target_lang: str) -> dict:
    """
    Translate text from English to user-selected language.
    """
    if not text or not text.strip():
        return {
            "success": False,
            "translated_text": text,
            "source_language": "English",
            "target_language": target_lang,
            "error": "Empty text cannot be translated"
        }
    
    try:
        # Convert language name/code to API format
        api_target_lang = get_language_code(target_lang)
        
        # Ensure target language is not 'auto'
        if api_target_lang == "auto":
            return {
                "success": False,
                "translated_text": text,
                "source_language": "English",
                "target_language": target_lang,
                "error": "Target language must be specified (cannot be 'auto')"
            }
        
        response = client.text.translate(
            input=text.strip(),
            source_language_code="en-IN",
            target_language_code=api_target_lang,
            speaker_gender="Male",
            mode="formal",
            model="mayura:v1",
            numerals_format="native"
        )
        
        # Extract translated text from response (handles TranslationResponse object)
        translated_text = extract_translated_text(response)
        
        if not translated_text:
            return {
                "success": False,
                "translated_text": text,
                "source_language": "English",
                "target_language": target_lang,
                "error": "No translation returned from API"
            }
        
        return {
            "success": True,
            "translated_text": translated_text,
            "source_language": "English",
            "target_language": target_lang
        }
    except Exception as e:
        return {
            "success": False,
            "translated_text": text,
            "source_language": "English",
            "target_language": target_lang,
            "error": f"Translation error: {str(e)}"
        }


# Example usage
if __name__ == "__main__":
    # Hindi → English
    result1 = translate_to_english("तितली मुस्कुराते हुए बोली, 'मैं जानती हूँ कि तुम कितनी ताकतवर हो, लेकिन मेरी ताकत कहीं और है। मैं जो कर सकती हूँ, वह तुम नहीं कर सकती।'", "Hindi")
    print("Hindi → English:", result1)

    # English → Hindi
    result2 = translate_from_english("What is React?", "Hindi")
    print("English → Hindi:", result2)
