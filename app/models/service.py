from beanie import Document

class Service(Document):
    title: str
    description: str

    class Settings:
        collection="services"