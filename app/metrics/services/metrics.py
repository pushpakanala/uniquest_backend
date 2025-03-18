from fastapi import Depends, HTTPException,status
from typing import Annotated
from app.common.services.db_service import DBService
from app.common.collections import metrics
from app.metrics.models.metrics import MetricSchema
from app.common.constants import Resources
from app.common.helpers import format_response
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
class Metrics:
    def __init__(
    self,
    db: Annotated[DBService, Depends(DBService)],
    ):
        self.db = db
        self.collection = metrics
        self.model=MetricSchema
    
    async def get_log_event(self):
        res = self.db.find_data(self.collection, self.model, {})
        return res

    async def log_event(self,body):
        """Log any event with optional details"""
        log_entry = {
            "user_id": body['user_id'],
            "event": body['event'],
            "details": body['details'] if body['details'] else {},
        }
        inserted_details = self.db.insert_data(
                self.collection, self.model, log_entry
            )
        return inserted_details

    
    
        