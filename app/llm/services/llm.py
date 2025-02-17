from fastapi import Depends, HTTPException,status
from typing import Annotated
from app.common.services.db_service import DBService
from app.common.collections import llm
from app.llm.models.llm import LLMSchema
from app.common.constants import Resources
from app.common.helpers import format_response
import bcrypt,json,re
import google.generativeai as ai
import openai

class LLM:
    def __init__(
    self,
    db: Annotated[DBService, Depends(DBService)],
    ):
        self.db = db
        self.collection = llm
        self.model=LLMSchema
        self.gemini_API_KEY=Resources.API_KEY
        self.gemini_model = ai.GenerativeModel("gemini-pro")
        self.gemini_chat = self.gemini_model.start_chat()
        self.gpt_API_KEY=Resources.GPT_API_KEY
        self.gpt_model='gpt-4o'
    
    async def chat_with_ai(self,request):
        API_KEY = self.gemini_API_KEY
        ai.configure(api_key=API_KEY)
        if request.lower() == "bye":
            return {"response": "GoodBye!"}
    
        response = self.gemini_chat.send_message(request)
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
    
    def parse_gpt_json_response(self,response_text):
        """Extracts valid JSON from the AI response."""
        try:
            # Extract JSON content using regex (handles improperly formatted responses)
            match = re.search(r"\{.*\}|\[.*\]", response_text, re.DOTALL)
            if match:
                json_data = json.loads(match.group(0))  # Convert matched JSON string
                return json_data
            else:
                return {"status": {"code": 500, "message": "Failed to parse JSON"}}
        except json.JSONDecodeError:
            return {"status": {"code": 500, "message": "Invalid JSON format"}}
    
    async def get_top_universities(self,state):
        API_KEY = self.gemini_API_KEY
        ai.configure(api_key=API_KEY)
        query = f"Give me the top 10 universities in {state}, USA, in JSON format with fields: 'state_name' and 'university_name'."
        response = self.gemini_chat.send_message(query)
        return self.parse_json_response(response.text)
    
    async def get_gpt_top_universities(self,state):
        openai.api_key = self.gpt_API_KEY
        query = f"Give me the top 10 universities in {state}, USA, in JSON format with fields: 'state_name' and 'university_name'."

        response = openai.chat.completions.create(
            model=self.gpt_model,
            messages=[{"role": "user", "content": query}]
        )

        return self.parse_gpt_json_response(response.choices[0].message.content)
    
    async def get_gpt_universities_data(self,university_name):
        openai.api_key = self.gpt_API_KEY
        query = (
    f"Provide details for {university_name} in the USA in **strict JSON format** with the following fields: " 
    "'school': { 'zip', 'city', 'name', 'state', 'address', 'latitude', 'longitude', 'accreditor', 'school_url', "
    "'accreditor_code', 'us_ranking', 'school_programs', 'eligibility_addmission_exams', 'founded_in','cost_of_living_near_university(low or medium or high)','type(public or private)','contact_details','graduation_rate','acceptance_rate' }, "  
    "'programs': { 'undergrad_programs': [{'program_name', 'fees(total course fee usd)', 'program_duration','course_rank(us)'}], "  
    "'grad_programs': [{'program_name', 'fees(total course fee usd)', 'program_duration','course_rank(us)'}] }, "  
    "'students': { 'total_students', 'grad_students', 'men', 'women', 'race_ethnicity' }, "
    "'faculty': { 'men', 'women', 'race_ethnicity' } }, "
    "Ensure 'us_ranking' is a number. Include 'GRE', 'IELTS', 'TOEFL', and 'Duolingo' in eligibility_addmission_exams "
    "if the university accepts them, along with any other exams it recognizes. "
    "Retrieve all available programs (ensure at least 10) in both undergraduate and graduate categories. "
    "Display the **full name** of each program and ensure no majorly chosen program is omitted."
    "Strictly return a **valid JSON object** without any extra text or explanations."
    "For 'race_ethnicity' values, make sure to provide percentages even if data is not publicly available."

)

        response = openai.chat.completions.create(
        model=self.gpt_model,  # Ensure you are using a suitable model
        messages=[{"role": "user", "content": query}]
    )
        university_data = response.choices[0].message.content
        json_match = re.search(r'\{.*\}', university_data, re.DOTALL)

        if json_match:
            university_data = json_match.group(0)  # Get the JSON part
            try:
                university_json = json.loads(university_data)
                return university_json
            except json.JSONDecodeError:
                return {"error": "Malformed JSON response"}
        else:
            return {"error": "No JSON detected in response"}
