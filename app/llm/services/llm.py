from fastapi import Depends, HTTPException,status
from typing import Annotated
from app.common.services.db_service import DBService
from app.common.collections import llm
from app.llm.models.llm import LLMSchema
from app.common.constants import Resources
from app.common.helpers import format_response
import bcrypt,json,re
import google.generativeai as ai
import openai,os

class LLM:
    def __init__(
    self,
    db: Annotated[DBService, Depends(DBService)],
    ):
        self.db = db
        self.collection = llm
        self.model=LLMSchema
        self.gemini_API_KEY=os.getenv("API_KEY")
        self.gemini_model = ai.GenerativeModel("gemini-2.0-flash")
        self.gemini_chat = self.gemini_model.start_chat()
        self.gpt_API_KEY=os.getenv("GPT_API_KEY")
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
    f"First, check if {university_name} is a recognized university in the USA. "
    "If the university is not found in the USA, return: {'error': 'University Not Found'} and do not execute further queries. "
    "If the university is valid and located in the USA, provide details in **strict JSON format** with the following fields: "
    "'school': { 'zip', 'city', 'name', 'state', 'address', 'latitude', 'longitude', 'accreditor', 'school_url', "
    "'accreditor_code', 'us_ranking', 'school_programs': ['program_1', 'program_2', ...], 'eligibility_admission_exams', 'founded_in', "
    "'cost_of_living_near_university(low or medium or high)', 'type(public or private)', "
    "'contact_details': { 'mobile', 'email' }, "
    "'graduation_rate', 'acceptance_rate', "
    "'application_fee': { "
    "'undergraduate': { 'international_students', 'local_students', 'waivers_available', 'waiver_criteria' }, "
    "'graduate': { 'international_students', 'local_students', 'waivers_available', 'waiver_criteria' } }, "
    "'required_documents': { "
    "'international_students': ['Retrieve the **mandatory** documents required for international students from the university’s official website. "
    "Ensure required documents such as transcripts, test scores (GRE/TOEFL/IELTS/Duolingo), financial proof, "
    "application form, application fee receipt, and check if a **Statement of Purpose (SOP), Letters of Recommendation (LOR), "
    "and Passport Copy** are required. Include them only if mandatory.'], "
    "'local_students': ['Retrieve the **mandatory** documents required for local students from the university’s official website. "
    "Ensure required documents such as transcripts, standardized test scores (SAT/ACT/GRE if required), "
    "application form, application fee receipt, and check if a **Statement of Purpose (SOP) and Letters of Recommendation (LOR)** "
    "are required for graduate programs. Include them only if mandatory.'] }, "
    "'part_time_opportunities': { 'on_campus_jobs': ['job_1', 'job_2', ...], "
    "'internships': ['internship_1', 'internship_2', ...], "
    "'assistantships': ['research_assistant', 'teaching_assistant', ...], "
    "'availability_probability': { 'on_campus_jobs', 'internships', 'assistantships' } }, "
    "'admission_deadlines': { 'fall': { 'international_students': 'Month Day, Year', 'local_students': 'Month Day, Year' }, "
    "'spring': { 'international_students': 'Month Day, Year', 'local_students': 'Month Day, Year' }, "
    "'summer': { 'international_students': 'Month Day, Year', 'local_students': 'Month Day, Year' } }, "
    "'application_link', "
    "'programs': { 'undergrad_programs': [{'program_name', 'total_fees', 'program_duration', 'course_rank'}], "
    "'grad_programs': [{'program_name', 'total_fees', 'program_duration', 'course_rank'}] }, "
    "'students': { 'total_students', 'grad_students', 'men', 'women', 'race_ethnicity' }, "
    "'faculty': { 'men', 'women', 'race_ethnicity' } }, "
    "Ensure 'us_ranking' is a number. Include 'GRE', 'IELTS', 'TOEFL', and 'Duolingo' in eligibility_admission_exams "
    "if the university accepts them, along with any other exams it recognizes. "
    "Retrieve all available programs (make sure minimum 10 programs from trusted sources like official university website) for both undergrad_programs and grad_programs. "
    "Display the **full name** of each program and ensure no majorly chosen program is omitted. "
    "Strictly return a **valid JSON object** without any extra text or explanations. "
    "For 'race_ethnicity' values, make sure to provide percentages even if data is not publicly available. "
    "Ensure 'course_rank' is a number. "
    "Ensure 'admission_deadlines' are in 'Month Day, Year' format. "
    "For undergraduate and graduate fees, show only the total duration cost instead of yearly fees."
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
    
    async def get_compare_universities(self, universities):
        universities_list=universities.split(',')
        university_data = []
        for university in universities_list:
            res=await self.get_gpt_universities_data(university)
            university_data.append(res)
        return university_data
