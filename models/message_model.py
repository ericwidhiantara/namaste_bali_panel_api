from pydantic import BaseModel
class MessageModel(BaseModel):
    sender_id: str
    recipient_id: str
    message: str
    is_read: bool = False
    
