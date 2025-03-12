from pydantic import BaseModel,Field
class User(BaseModel):#basemodel= crear una entidad pero sin el constructor usual
    #Path y Qwery
    id: str | None = Field(default=None, description="MongoDB ObjectID")
    username: str = Field(..., description="User name", max_length=50)
    disabled: bool =Field(...,description="Count valid")
    email: str = Field(..., description="Email Valid")

class user_db(User):
    password:str |None = Field(default=None, description="Password")
    token_version:int |None = Field(default=None, description="Token version")