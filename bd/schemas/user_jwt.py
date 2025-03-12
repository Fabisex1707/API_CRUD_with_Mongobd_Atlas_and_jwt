from passlib.context import CryptContext
import bcrypt
bcrypt.__about__=bcrypt
crypt= CryptContext(schemes=["bcrypt"])
def user_schema(user) ->dict:
    return {"id":str(user["_id"]),
            "username":user["username"],
            "disabled":user["disabled"],
            "email":user["email"],
            "password":user["password"],
            "token_version":user["token_version"]
            }

def users_schema(users)->list:
    return[user_schema(user) for user in users]