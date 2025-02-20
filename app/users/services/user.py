from fastapi import Depends, HTTPException,status
from typing import Annotated
from app.common.services.db_service import DBService
from app.common.collections import users
from app.users.models.user import UserSchema
from app.common.constants import Resources
from app.common.helpers import format_response
import bcrypt
import random
import string
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
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
    
    def generate_password(self):
        # Define the core password segment
        core = "Uniquest"
        symbol = "@"
    
        # Generate random numbers for the suffix
        random_numbers = ''.join(random.choices(string.digits, k=random.randint(3, 5)))
    
        # Combine the parts to create the password
        password = f"{core}{symbol}{random_numbers}"
    
        return password
    
    
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
    
    def generate_otp(self,length=6):
        digits = string.digits  # Use only numeric characters
        otp = ''.join(random.choices(digits, k=length))
        return otp
    
    def send_pwd_reset_email(self,recipient_email,otp):
        sender_email = "uniquestservicesystem@gmail.com"
        sender_password = "hmdzizsxynygmitz"  # Use an app password if 2FA is enabled
        recipient_email = recipient_email
        url="uniquest-d9hk.onrender.com"
        # Email content
        subject = "Password Reset Request"
        body = f"""
<html>
<body style="font-family: Arial, sans-serif; line-height: 1.6; background-color: #f4f4f9; padding: 20px;">
  <div style="max-width: 600px; margin: auto; background: #ffffff; padding: 20px; border-radius: 8px; box-shadow: 0 4px 8px rgba(0, 0, 0, 0.1);">
    <h2 style="color: #333;">Password Reset Request - Uniquest</h2>
    <p style="color: #555;">Hello,</p>
    <p style="color: #555;">We received a request to reset your password for your <strong>Uniquest</strong> account. Please use the OTP below to update your password:</p>
    <p style="font-size: 18px; font-weight: bold; color: #2a9d8f;">{otp}</p>
    <p style="color: #555;">This OTP is valid for a limited time. If you did not request this change, please ignore this email.</p>
    <p style="margin-top: 20px; color: #888;">Best regards,<br>The Uniquest Team</p>
    <p style="margin-top: 10px; color: #555; text-align: center; font-style: italic;">Thanks for using Uniquest!</p>
  </div>
</body>
</html>
"""



        # Create the email message
        message = MIMEMultipart()
        message["From"] = sender_email
        message["To"] = recipient_email
        # Gmail account credentials
        message["Subject"] = subject

        # Attach the body to the email
        message.attach(MIMEText(body, "html"))
        # Connect to the Gmail SMTP server and send the email
        try:
            server = smtplib.SMTP("smtp.gmail.com", 587)
            server.starttls()  # Secure the connection
            server.login(sender_email, sender_password)
            server.sendmail(sender_email, recipient_email, message.as_string())
            print("Email sent successfully!")
        except Exception as e:
            print(f"Error: {e}")
        finally:
            server.quit()

    
    async def get_user_verify_by_email(self,email):
        res = self.db.find_data(self.collection, self.model, {"email":email})
        if res:
            otp=self.generate_otp()
            query = {"email": email}
            body={"otp":otp}
            updated_details = self.db.upsert_data(
                self.collection, self.model, body, query, upsert=False
            )
            try:
                self.send_pwd_reset_email(email,otp)
            except Exception as e:
                print(f"Error: {e}")
        return res
    
    def hash_password(self,password: str) -> str:
        return bcrypt.hashpw(password.encode("utf-8"), bcrypt.gensalt()).decode("utf-8")
    
    def send_email(self,recipient_email,password):
        sender_email = "uniquestservicesystem@gmail.com"
        sender_password = "hmdzizsxynygmitz"  # Use an app password if 2FA is enabled
        recipient_email = recipient_email
        url="uniquest-d9hk.onrender.com"
        # Email content
        subject = "User Credentials"
        body = f"""
<html>
<body style="font-family: Arial, sans-serif; line-height: 1.6; background-color: #f4f4f9; padding: 20px;">
  <div style="max-width: 600px; margin: auto; background: #ffffff; padding: 20px; border-radius: 8px; box-shadow: 0 4px 8px rgba(0, 0, 0, 0.1);">
    <h2 style="color: #333;">Welcome to Uniquest!</h2>
    <p style="color: #555;">Hello,</p>
    <p style="color: #555;">Thank you for joining <strong>Uniquest</strong>. Below is your login password for accessing our platform:</p>
    <p style="font-size: 18px; font-weight: bold; color: #2a9d8f;">{password}</p>
    <p style="color: #555;">You can log in using the following link: <a href="{url}" style="color: #2a9d8f; text-decoration: none;">{url}</a></p>
    <p style="color: #555;">Once you log in with these credentials, we recommend changing your password for security purposes.</p>
    <p style="color: #555;">Please keep this password secure and do not share it with anyone.</p>
    <p style="margin-top: 20px; color: #888;">Best regards,<br>The Uniquest Team</p>
    <p style="margin-top: 10px; color: #555; text-align: center; font-style: italic;">Thanks for using Uniquest!</p>
  </div>
</body>
</html>
"""


        # Create the email message
        message = MIMEMultipart()
        message["From"] = sender_email
        message["To"] = recipient_email
        # Gmail account credentials
        message["Subject"] = subject

        # Attach the body to the email
        message.attach(MIMEText(body, "html"))
        # Connect to the Gmail SMTP server and send the email
        try:
            server = smtplib.SMTP("smtp.gmail.com", 587)
            server.starttls()  # Secure the connection
            server.login(sender_email, sender_password)
            server.sendmail(sender_email, recipient_email, message.as_string())
            print("Email sent successfully!")
        except Exception as e:
            print(f"Error: {e}")
        finally:
            server.quit()
    
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
            pwd=self.generate_password()
            hashed_password = self.hash_password(pwd)
            body["password"]=hashed_password
            inserted_details = self.db.insert_data(
                self.collection, self.model, body
            )
            try:
                self.send_email(email,pwd)
            except Exception as e:
                print(f"Error: {e}")
            return inserted_details
    
    async def update_user(self,body):
        query = {"email": body["email"]}
        updated_details = self.db.upsert_data(
            self.collection, self.model, body, query, upsert=False
        )
        return updated_details
    
    async def update_user_pwd(self,body):
        query = {"email": body["email"]}
        res = self.db.find_data(self.collection, self.model, query)
        otp=res[0].otp
        if otp==body['otp']:
            pwd=self.hash_password(body['password'])
            new_body={"password":pwd}
            updated_details = self.db.upsert_data(
                self.collection, self.model, new_body, query, upsert=False
            )
            return updated_details
        else:
            raise HTTPException(
                status.HTTP_400_BAD_REQUEST,
                Resources.NOT_MATCHED,
            )   
    
    async def delete_user(self,body):
        query={"email":body}
        deleted_details=self.db.delete_one(self.collection,self.model,query)
        return deleted_details
        