import os
from groq import Groq
from dotenv import load_dotenv
from utils.prompts import SYSTEM_PROMPT, get_interpretation_prompt, get_direct_consultation_prompt

# Load environment variables from .env file
load_dotenv()

class IChingInterpreter:
    def __init__(self):
        self.client = Groq(api_key=os.getenv("GROQ_API_KEY"))
    
    def get_reading(self, question: str, primary_hex: dict, transformed_hex: dict = None, changing_lines: list = None, primary_num: int = None, transformed_num: int = None):
        try:
            # Pass original numbers to handle cases where hexagram data is missing in JSON
            prompt = get_interpretation_prompt(
                question, 
                primary_hex, 
                transformed_hex, 
                changing_lines, 
                primary_num=primary_num, 
                transformed_num=transformed_num
            )
            
            return self._query_groq([
                {"role": "system", "content": SYSTEM_PROMPT},
                {"role": "user", "content": prompt}
            ])
            
        except Exception as e:
            # Log the specific error for debugging if needed
            return f"❌ Error in Oracle: {str(e)}\n\nPlease ensure your GROQ_API_KEY is set correctly in the .env file."

    def get_direct_reading(self, question: str):
        try:
            prompt = get_direct_consultation_prompt(question)
            return self._query_groq([
                {"role": "system", "content": SYSTEM_PROMPT},
                {"role": "user", "content": prompt}
            ])
        except Exception as e:
            return f"❌ Error in Direct Consultation: {str(e)}"

    def chat(self, messages: list):
        try:
            # Create a copy to avoid modifying session state and ensure system prompt is present
            api_messages = []
            if not any(m.get("role") == "system" for m in messages):
                api_messages.append({"role": "system", "content": SYSTEM_PROMPT})
            
            api_messages.extend(messages)
            
            return self._query_groq(api_messages)
        except Exception as e:
            return f"❌ Error in Chat: {str(e)}"

    def _query_groq(self, messages: list):
        # Additional safety check for messages structure
        filtered_messages = [
            {"role": m["role"], "content": m["content"]}
            for m in messages if m["role"] in ["system", "user", "assistant"]
        ]
        
        response = self.client.chat.completions.create(
            model="openai/gpt-oss-20b",
            messages=filtered_messages
        )
        
        return response.choices[0].message.content.strip()
