from fastapi import FastAPI
from Routers import jwt_auth_users 

app=FastAPI()
app.include_router(jwt_auth_users.router)