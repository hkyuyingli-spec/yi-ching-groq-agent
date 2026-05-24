import os
from groq import Groq
from dotenv import load_dotenv
from prompts import SYSTEM_PROMPT, get_interpretation_prompt, get_direct_consultation_prompt

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
            
            return self._query_groq(prompt)
            
        except Exception as e:
            # Log the specific error for debugging if needed
            return f"❌ Error in Oracle: {str(e)}\n\nPlease ensure your GROQ_API_KEY is set correctly in the .env file."

    def get_direct_reading(self, question: str):
        try:
            prompt = get_direct_consultation_prompt(question)
            return self._query_groq(prompt)
        except Exception as e:
            return f"❌ Error in Direct Consultation: {str(e)}"

    def _query_groq(self, prompt: str):
        messages = [
            {"role": "system", "content": SYSTEM_PROMPT},
            {"role": "user", "content": prompt}
        ]
        
        response = self.client.chat.completions.create(
            model="llama-3.1-8b-instant",
            messages=messages
        )
        
        return response.choices[0].message.content.strip()
