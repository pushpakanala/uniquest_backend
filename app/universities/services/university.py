from fastapi import Depends, HTTPException,status
from typing import Annotated
from app.common.services.db_service import DBService
from app.common.collections import state_universities
from app.universities.models.university import StateUniversitySchema
from app.common.constants import Resources
from app.common.helpers import format_response
import bcrypt
class University:
    def __init__(
    self,
    db: Annotated[DBService, Depends(DBService)],
    ):
        self.db = db
        self.collection = state_universities
        self.model=StateUniversitySchema
    
    def process_string(self,s):
        return "".join(s.lower().split())

    async def get_universities_by_state(self,body):
        state=self.process_string(body)
        res = self.db.find_data(self.collection, self.model, {"state_name":state})
        return res

    
    async def get_all_universities(self):
        res = self.db.find_data(self.collection, self.model, {})
        return res
    
    async def post_state_university(self,body):
        body['state_name']=self.process_string(body['state_name'])
        inserted_details = self.db.insert_data(
            self.collection, self.model, body
        )
        return inserted_details
    
    # async def update_user(self,body):
    #     query = {"email": body["email"]}
    #     updated_details = self.db.upsert_data(
    #         self.collection, self.model, body, query, upsert=False
    #     )
    #     return updated_details
    
    # async def delete_user(self,body):
    #     query={"email":body}
    #     deleted_details=self.db.delete_one(self.collection,self.model,query)
    #     return deleted_details
        