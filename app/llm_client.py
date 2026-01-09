"""
Client for interacting with Google's Gemini API.
"""
import os
import google.generativeai as genai

# Setup API Key
API_KEY = os.environ.get("GEMINI_API_KEY")
if API_KEY:
    genai.configure(api_key=API_KEY)
else:
    # In a real app, we might raise an error, but for now we'll just log
    print("WARNING: GEMINI_API_KEY not found in environment variables.")

def call_gemini(system_prompt: str, user_message: str) -> str:
    """
    Calls the Gemini API with the given system and user prompts.
    """
    model = genai.GenerativeModel('gemini-2.5-flash', system_instruction=system_prompt)
    
    response = model.generate_content(user_message)
    return response.text
