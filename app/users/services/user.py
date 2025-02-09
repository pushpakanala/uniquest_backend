from fastapi import Depends, HTTPException,status
from typing import Annotated
from app.common.services.db_service import DBService
from app.common.collections import users
from app.users.models.user import UserSchema
from app.common.constants import Resources
from app.common.helpers import format_response
import bcrypt
class User:
    def __init__(
    self,
    db: Annotated[DBService, Depends(DBService)],
    ):
        self.db = db
        self.collection = users
        self.model=UserSchema

    #get user by emails
    async def get_user_by_email(self,body):
        email=body
        res = self.db.find_data(self.collection, self.model, {"email":email})
        return res
    
    
    def verify_password(self,password: str, hashed_password: str) -> bool:
        return bcrypt.checkpw(password.encode("utf-8"), hashed_password.encode("utf-8"))

    
    async def login(self, email, password):
        res=self.db.find_data(self.collection, self.model, {"email":email})
        result=""
        if len(res):
            response=self.verify_password(password,res[0].password)
            if response:
                # result={'name':res[0].name,
                #  'email':res[0].email,
                #  'role':res[0].role}
                result = res[0].model_dump()
                del result["password"]
        return result
    
    async def get_all_users(self):
        res = self.db.find_data(self.collection, self.model, {})
        return res
    
    def hash_password(self,password: str) -> str:
        return bcrypt.hashpw(password.encode("utf-8"), bcrypt.gensalt()).decode("utf-8")
    
    async def post_user(self,body):
        email = body["email"]
        existing = self.db.find_data(
            self.collection, self.model, {"email": email}
        )
        if len(existing):
            raise HTTPException(
                status.HTTP_409_CONFLICT,
                Resources.EXISTS,
            )   
        else:
            hashed_password = self.hash_password(body["password"])
            body["password"]=hashed_password
            inserted_details = self.db.insert_data(
                self.collection, self.model, body
            )
            return inserted_details
    
    async def update_user(self,body):
        query = {"email": body["email"]}
        updated_details = self.db.upsert_data(
            self.collection, self.model, body, query, upsert=False
        )
        return updated_details
    
    async def delete_user(self,body):
        query={"email":body}
        deleted_details=self.db.delete_one(self.collection,self.model,query)
        return deleted_details
        