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


def translate_from_english(content: any, target_lang: str) -> dict:
    """
    Translate English content to the target language.
    Supports:
    - Plain string input (original behavior).
    - Dictionary input containing a 'response' key (list or string) typically returned from the NLP call.
    The function preserves the original structure and returns a dictionary matching the original format,
    adding or replacing the translated text under the 'translated_text' key.
    """
    # Helper to perform actual translation via SarvamAI client
    def _translate_text(text: str) -> str:
        try:
            resp = client.text.translate(
                input=text.strip(),
                source_language_code="en-IN",
                target_language_code=get_language_code(target_lang),
                speaker_gender="Male",
                mode="formal",
                model="mayura:v1",
                numerals_format="native",
            )
            return extract_translated_text(resp)
        except Exception as e:
            # Propagate error message for higher-level handling
            raise RuntimeError(f"Translation error: {str(e)}")

    # Case 1: content is a string – keep original simple behavior
    if isinstance(content, str):
        if not content or not content.strip():
            return {
                "success": False,
                "translated_text": content,
                "source_language": "English",
                "target_language": target_lang,
                "error": "Empty text cannot be translated",
            }
        try:
            translated = _translate_text(content)
            if not translated:
                return {
                    "success": False,
                    "translated_text": content,
                    "source_language": "English",
                    "target_language": target_lang,
                    "error": "No translation returned from API",
                }
            return {
                "success": True,
                "translated_text": translated,
                "source_language": "English",
                "target_language": target_lang,
            }
        except Exception as e:
            return {
                "success": False,
                "translated_text": content,
                "source_language": "English",
                "target_language": target_lang,
                "error": f"Translation error: {str(e)}",
            }

    # Case 2: content is a dict (expected format from nlpcall)
    if isinstance(content, dict):
        # Preserve original fields (e.g., confidence) in the result
        result = dict(content)
        response = content.get("response")
        if response is None:
            # Nothing to translate; return original dict unchanged but indicate failure
            result.update({
                "success": False,
                "error": "No 'response' field to translate",
                "source_language": "English",
                "target_language": target_lang,
            })
            return result
        # Normalise response to a string for translation
        if isinstance(response, list):
            # Join list items with newline to keep separations after translation
            response_text = "\n".join(map(str, response))
        else:
            response_text = str(response)
        try:
            translated_text = _translate_text(response_text)
            if not translated_text:
                result.update({
                    "success": False,
                    "error": "No translation returned from API",
                    "source_language": "English",
                    "target_language": target_lang,
                })
                return result
            # If original response was a list, split back on newline to preserve list shape
            if isinstance(response, list):
                translated_list = translated_text.split("\n")
                result["response"] = translated_list
            else:
                result["response"] = translated_text
            result.update({
                "success": True,
                "source_language": "English",
                "target_language": target_lang,
                "translated_text": translated_text,
            })
            return result
        except Exception as e:
            result.update({
                "success": False,
                "error": f"Translation error: {str(e)}",
                "source_language": "English",
                "target_language": target_lang,
            })
            return result

    # Fallback for unexpected types
    return {
        "success": False,
        "translated_text": "",
        "source_language": "English",
        "target_language": target_lang,
        "error": "Unsupported input type for translation",
    }

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
