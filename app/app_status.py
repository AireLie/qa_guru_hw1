from pydantic import BaseModel


class AppStatus(BaseModel):
    users: bool
    db_connected: bool = False
