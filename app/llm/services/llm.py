from fastapi import Depends, HTTPException,status
from typing import Annotated
from app.common.services.db_service import DBService
from app.common.collections import llm
from app.llm.models.llm import LLMSchema
from app.common.constants import Resources
from app.common.helpers import format_response
import bcrypt,json,re
import google.generativeai as ai

class LLM:
    def __init__(
    self,
    db: Annotated[DBService, Depends(DBService)],
    ):
        self.db = db
        self.collection = llm
        self.model=LLMSchema
        self.API_KEY=Resources.API_KEY
        self.model = ai.GenerativeModel("gemini-pro")
        self.chat = self.model.start_chat()
    
    async def chat_with_ai(self,request):
        API_KEY = self.API_KEY
        ai.configure(api_key=API_KEY)
        if request.lower() == "bye":
            return {"response": "GoodBye!"}
    
        response = self.chat.send_message(request)
        return {"response": response.text}
    
    def parse_json_response(self,response_text):
        """Extracts valid JSON from the AI response."""
        try:
            # Extract JSON content using regex (handles improperly formatted responses)
            match = re.search(r"\[.*\]", response_text, re.DOTALL)
            if match:
                json_data = json.loads(match.group(0))  # Convert matched JSON string
                return json_data
            else:
                return {"status": {"code": 500, "message": "Failed to parse JSON"}}
        except json.JSONDecodeError:
            return {"status": {"code": 500, "message": "Invalid JSON format"}}
    
    async def get_top_universities(self,state):
        API_KEY = self.API_KEY
        ai.configure(api_key=API_KEY)
        query = f"Give me the top 10 universities in {state}, USA, in JSON format with fields: 'state_name' and 'university_name'."
        response = self.chat.send_message(query)
        return self.parse_json_response(response.text)
