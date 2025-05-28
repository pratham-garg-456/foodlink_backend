from beanie import Document
from typing import Optional

class Contact(Document):
    name: str
    email: str
    phone: str
    subject: str
    message: Optional[str]
    
    class Settings:
        collection = "contacts"