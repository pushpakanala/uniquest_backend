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
    

    async def chat_with_ai(self, request):
        API_KEY = self.gemini_API_KEY
        ai.configure(api_key=API_KEY)

        user_input = request.lower()

        if user_input == "bye":
            return {"response": "GoodBye! If you have more questions about universities, feel free to ask!"}

        # Identity related queries
        identity_queries = [
            "what is your name", "who are you", "who created you",
            "tell me about yourself", "what can you do", "who invented you"
        ]
        if any(query in user_input for query in identity_queries):
            return {
                "response": {
                    "name": "Uniquest Assistant",
                    "role": "Guide for exploring universities in the USA",
                    "capabilities": [
                        "Suggest universities",
                        "Explain admission requirements",
                        "List top courses",
                        "Provide fee details",
                        "Help with scholarships and living costs"
                    ]
                }
            }

        # Enhanced prompt with USA-only filter and satire for off-topic questions
        prompt = (
    "You are Uniquest Assistant, an expert in USA universities only.\n\n"
    "Rules:\n"
    "1. If the query is about universities outside the USA, respond only with a JSON like: {\"message\": \"I’d love to help, but my GPS only works within the borders of the USA — foreign universities are off the map!\"}\n"
    "2. If the query is unrelated to universities or education, respond in a funny, satirical tone, but still return the response as a JSON with only a 'message' key.\n"
    "3. If the query is about universities in the USA, respond in JSON format using keys like 'universities', 'courses', 'fees', 'requirements', 'scholarships', 'living_costs'. "
    "Each key should have an appropriate value (list or string).\n\n"
    "Avoid long paragraphs. Always respond in valid JSON format.\n\n"
    "Now answer: " + request
)



        response = self.gemini_chat.send_message(prompt)

        try:
            structured_output = json.loads(response.text)
        except json.JSONDecodeError:
            structured_output = response.text
        json_op = self.parse_gpt_json_response(structured_output)

        return {"response": json_op}



    
    def parse_json_response(self,response_text):
        """Extracts valid JSON from the AI response."""
        try:
            # Extract JSON content using regex (handles improperly formatted responses)
            match = re.search(r"\[.*\]", response_text, re.DOTALL)
            if match:
                json_data = json.loads(match.group(0))  # Convert matched JSON string
                return json_data
            else:
                raise HTTPException(status_code=500)
        except json.JSONDecodeError:
            raise HTTPException(status_code=500)
    
    def parse_gpt_json_response(self,response_text):
        """Extracts valid JSON from the AI response."""
        try:
            # Extract JSON content using regex (handles improperly formatted responses)
            match = re.search(r"\{.*\}|\[.*\]", response_text, re.DOTALL)
            if match:
                json_data = json.loads(match.group(0))  # Convert matched JSON string
                return json_data
            else:
                raise HTTPException(status_code=500)
        except json.JSONDecodeError:
            raise HTTPException(status_code=500)
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

    async def post_chatbot(self, request_body):
        session_id = request_body['session_id']
        user_message = request_body['user_message']

        if not session_id or not user_message:
            raise HTTPException(status_code=400, detail="Missing session_id or message")

        # Define Uniquest system prompt
        system_prompt = {
    "role": "system",
    "content": (
        "You are Uniquest Assistant, an expert in USA universities only.\n\n"
        "You must always respond using this exact JSON format:\n\n"
        "{\n"
        "  \"universities\": [\n"
        "    {\n"
        "      \"name\": \"University Name\",\n"
        "      \"courses\": [\"Course 1\", \"Course 2\"],\n"
        "      \"fees\": {\n"
        "        \"tuition\": \"string\",\n"
        "        \"additional_costs\": \"string\",\n"
        "        \"financial_aid\": \"string\"\n"
        "      },\n"
        "      \"requirements\": [\"Requirement 1\", \"Requirement 2\"],\n"
        "      \"scholarships\": [\"Scholarship 1\", \"Scholarship 2\"],\n"
        "      \"living_costs\": \"string\"\n"
        "    }\n"
        "  ],\n"
        "  \"message\": \"Optional general answer or summary.\"\n"
        "}\n\n"
        "Rules:\n"
        "1. If the query is about universities outside the USA, respond only with:\n"
        "{ \"universities\": [], \"message\": \"I’d love to help, but my GPS only works within the borders of the USA — foreign universities are off the map!\" }\n\n"
        "2. If the query is unrelated to universities or education, respond ONLY with a witty, clever, or satirical message. Do not attempt to answer seriously. Examples include:\n"
        "{ \"universities\": [], \"message\": \"I'm flattered, but I only flirt with facts about U.S. universities.\" }\n"
        "{ \"universities\": [], \"message\": \"I specialize in degrees, not dating advice — unless it's a PhD in awkward questions.\" }\n"
        "You can be playful, sarcastic, or humorous — but always use only the 'message' key and stay in character.\n\n"
        "3. If the query is a general educational question (e.g., 'What is a scholarship?'), return the explanation in the 'message' field and leave 'universities' empty.\n\n"
        "4. For valid questions about U.S. universities, fill the 'universities' list with as much structured data as possible. Use empty strings or arrays for missing fields.\n\n"
        "5. If asked about your identity or who created you, always reply with:\n"
        "{ \"universities\": [], \"message\": \"I am UNIQUEST Assistant, proudly created by the Uniquest team to guide you through the world of U.S. universities.\" }\n\n"
        "6. Do NOT use markdown, bullet points, asterisks, or any formatting.\n"
        "7. Do NOT include any greeting like 'Sure!', 'Of course!', or any text outside the JSON object.\n"
        "8. Your entire reply MUST be valid raw JSON. No extra characters or formatting. Just pure JSON.\n"
    )
}




        # Load existing conversation or initialize
        session = self.db.find_data(self.collection, self.model, {"session_id": session_id})
        if session:
            messages = session[0].messages
            # Always make sure system prompt is the first message
            if messages[0]["role"] != "system":
                messages.insert(0, system_prompt)
            else:
                messages[0] = system_prompt  # Replace if it already exists but might differ
        else:
            messages = [system_prompt]

        messages.append({"role": "user", "content": user_message})

        openai.api_key = self.gpt_API_KEY
        try:
            response = openai.chat.completions.create(
                model=self.gpt_model,
                messages=messages
            )
        except Exception as e:
            raise HTTPException(status_code=500, detail=str(e))

        assistant_reply = response.choices[0].message.content.strip()
        messages.append({"role": "assistant", "content": assistant_reply})

        # Save conversation history
        self.db.upsert_data(
            self.collection,
            self.model,
            {"messages": messages},
            {"session_id": session_id},
            upsert=True
        )

        # Parse response into JSON format
        try:
            structured_output = json.loads(assistant_reply)
        except Exception:
            structured_output = assistant_reply

        # json_op = self.parse_gpt_json_response(structured_output)

        return {"response": structured_output}

