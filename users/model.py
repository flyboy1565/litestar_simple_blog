from pydantic import BaseModel, UUID4


class User(BaseModel):
    id: UUID4
    username: str
    first_name: str
    last_name: str
