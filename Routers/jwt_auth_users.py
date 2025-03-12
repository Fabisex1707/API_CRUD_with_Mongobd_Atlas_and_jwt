from typing import Annotated
from fastapi import APIRouter, Depends, HTTPException,status
from bd.schemas.user_jwt import user_schema
from bd.models.user import User,user_db
from bd.client import db_cliente
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from jose import jwt, JWTError
from passlib.context import CryptContext
from datetime import datetime, timedelta, timezone
from bson import ObjectId
ALGORITHM="HS256" #Este numero lo saque de la pagina jwt debugger: https://jwt.io 
acces_token_duration_minute=50 #Establecemos el tiempo en el que el token sera valido 1min
SECRET="57eaf25cee2d3a4f00e8cac2c284a144327d17699014d9bbff04f1ca44bfca0e" #Esto se genera a traves del comando "openssl rand -hex 32"
crypt= CryptContext(schemes=["bcrypt"])

router=APIRouter()
outh2= OAuth2PasswordBearer(tokenUrl='login')


#En principio os datos se ven asi pues solo es un ajemplo, pero a futuro hay que usar un "hash"
#Base de datos falsa
users_db={
}
#Funciones
    
def search_user_db(field:str,value):
    try:
        user=db_cliente.userdb.find_one({field:value})#Busamos dentro de la bd un campo x y un valor y
        return user_db(**user_schema(user))
    except:
        return {"Error":"No se encontro el usario v:p"}
    
def search_user(field:str,value):
    try:
        user=db_cliente.userdb.find_one({field:value})#Busamos dentro de la bd un campo x y un valor y
        return User(**user_schema(user))
    except:
        return None
    
async def auth_user(token:Annotated[str, Depends(outh2)]):
    exception=HTTPException(status_code=401,
                      detail='Credenciales invalidas',
                      headers={'www-Authenticte':' bearer'})
    try:
        payl= jwt.decode(token,SECRET,algorithms=[ALGORITHM])
        username=payl.get("sub")
        if username is None:
            raise exception
        
        user = search_user("username",username)
        if user is None:
            raise exception
    except JWTError:
        raise exception
    
    return user

async def auth_user_db(token:Annotated[str, Depends(outh2)]):
    exception=HTTPException(status_code=401,
                      detail='Credenciales invalidas',
                      headers={'www-Authenticte':' bearer'})
    try:
        payl= jwt.decode(token,SECRET,algorithms=[ALGORITHM])
        username=payl.get("sub")
        token_version=payl.get("token_version")
        if username is None:
            raise exception
        
        user = search_user_db("username",username)
        if user is None:
            raise exception
        
        if token_version != user.token_version:
            raise HTTPException(status_code=401, detail="Token inválido o desactualizado")
    except JWTError:
        raise exception
    
    return user

async def current_user(user:Annotated[User,Depends(auth_user)]):
    if user.disabled:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST,
                      detail='Usario inactivo')
    
    return user


def current_user_db(user:Annotated[user_db,Depends(auth_user_db)]):
    if user.disabled:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST,
                      detail='Usario inactivo')
    return user

   

#Operacion get
@router.post('/login')
async def login(form:Annotated[OAuth2PasswordRequestForm,Depends()]):
    userdb=db_cliente.userdb.find_one({"username":form.username})
    print(type(userdb))
    if userdb is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND)

    if not userdb:
        raise HTTPException(status_code=400,detail='El usario no es correcto')
    
    user=search_user_db("username",form.username)
    if not crypt.verify(form.password,user.password):
        raise HTTPException(status_code=400,detail='La contrasena no es correcta')
    
    
    #acces_token_expiration=timedelta(minutes=acces_token_duration) #aqui le decimos la diferencia de tiempo que queremos que pase para que expire el token 
    
    #expire=datetime.now(timezone.utc) + timedelta(minutes=acces_token_duration) Eliminamos estas variables pq podemos poner todo esto en el lugar que lo necesitemos

    acces_token={"sub":user.username, 
                 "exp":datetime.now(timezone.utc) + timedelta(minutes=acces_token_duration_minute),
                 "token_version":user.token_version
                 }
    
    return {'acces_token': jwt.encode(acces_token,SECRET,algorithm=ALGORITHM),'token_type':'bearer'} 
                        #  aqui estamos encriptando la informacion que nos devuelve el login, en este caso un Json con datos como: 
                        # username 
                        # fecha de expiracion 
                        # tipo de token que envia 
                        # la llave para dar permiso 

@router.get('/users/me')
async def me(user: Annotated[User,Depends(current_user)]): #al poner criterios de dependencia le decimos al back que la unica form ade realizar esa opracion es primero validando que ese susario si esta registrado
    if search_user("username",user.username) is None:
        return {"Error":"Usario no econtrado"}
    else:
        return search_user("username",user.username)


'''''
Esto es lo que devuelve la operacion de login, es un Json mucho mas comlejo, pero esto no es un token y no sirve para que queremos :v
{
  "acces_token": {
    "sub": "Fabisex",
    "exp": "2025-01-04T04:35:17.714561+00:00"
  },
  "token_type": "bearer"
}
'''''


@router.post('/register', response_model=user_db, status_code=status.HTTP_201_CREATED)
async def register(user: user_db):
    if type(search_user_db("username",user.username))==user_db:
        raise HTTPException(
            status_code=400,
            detail='El usuario ya está registrado'
        )
    
    if type(search_user_db("email",user.email))==user_db:
        raise HTTPException(
            status_code=400,
            detail='El emial ya está registrado'
        )
    
    user_dict=dict(user)
    del(user_dict["id"])
    user_dict["password"]=crypt.hash(user.password)
    user_dict["token_version"]=1
    id=db_cliente.userdb.insert_one(user_dict).inserted_id
    new_user=user_schema(db_cliente.userdb.find_one({"_id":id}))
    return user_db(**new_user)

@router.put('/update',response_model=user_db,status_code=status.HTTP_200_OK)
async def update(token: Annotated[str, Depends(outh2)],user_update: user_db):
    exception=HTTPException(status_code=401,
                      detail='Credenciales invalidas',
                      headers={'www-Authenticte':' bearer'})
    try:
        payl= jwt.decode(token,SECRET,algorithms=[ALGORITHM])
        username=payl.get("sub")
        token_version=payl.get("token_version")
        if username is None:
            raise exception
        
        stored_user=search_user_db("username",username)
        dict_stored_user=dict(stored_user)
        
        user = db_cliente.userdb.find_one({"username":username})
        if user is None:
            raise exception
        print(type(stored_user))
        if token_version != dict_stored_user["token_version"]:
            raise HTTPException(status_code=401, detail="Token desactualizado o inválido")
    except JWTError:
        raise exception

   
    if type(stored_user) != user_db:
        raise HTTPException(status_code=404, detail="Usuario no encontrado:v")
    
    dict_user=dict(user_update)
    del dict_user["id"]

    dict_user["password"]=crypt.hash(user_update.password) if user_update.password else dict_stored_user["password"]
    dict_user["token_version"]=dict_stored_user["token_version"] + 1

    try:
        correo_repetido=db_cliente.userdb.find_one({"email":user_update.email,"_id":{"$ne":ObjectId(user_update.id)}})
        if correo_repetido:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail={"El email ya esta registrado en otro usario:v"}) 
    except:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,detail={"Error":"No se encontro el usario o el email ya esta registrado en otro usario:"})

    try:
        usario_repetido=db_cliente.userdb.find_one({"username":user_update.username,"_id":{"$ne":ObjectId(user_update.id)}})
        if usario_repetido:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail={"El nombre de usario ya esta registrado en otra cuenta:v"}) 
    except:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,detail={"Error":"No se encontro el usario o el nombre de usario ya esta registrado en otra cuenta:"})
    

    try:
        db_cliente.userdb.find_one_and_replace({"_id":ObjectId(user_update.id)},dict_user)
    except:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,detail={"Error":"No se encontro el usario o el nombre de usario ya esta registrado en otra cuenta:"})
    
    update_user=user_schema(db_cliente.userdb.find_one({"_id":ObjectId(user_update.id)}))
    return user_db(**update_user)

@router.delete('/borrar',status_code=status.HTTP_200_OK)
async def vanish(token: Annotated[str, Depends(outh2)]):
    exception=HTTPException(status_code=401,
                      detail='Credenciales invalidas',
                      headers={'www-Authenticte':' bearer'})
    try:
        payl= jwt.decode(token,SECRET,algorithms=[ALGORITHM])
        username=payl.get("sub")
        
        if username is None:
            raise exception
        
        user = db_cliente.userdb.find_one({"username":username})
        if user is None:
            raise exception
    except JWTError:
        raise exception

    found=db_cliente.userdb.find_one_and_delete({"username":username})
    if not found:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,detail='No se encontro el usario')
    
# Pendientes: 
# revisar la relacion del token de auth_user y auth_user_db
# problema al actualizar, creo que no se actualiza porque no tiene un token valido, ya que usamos auth_user_db y este no genera un token propio
# Los datos de user_db no se actualizan debido a que las funciones que desencriptan los datos del token, solo retornan datos del usario y eso tiene influencia en los datos
# #
# Soluciones: 
# dejar de usar current_user_db y auth_user_db, ya que cada uno solo nos devolvia los datos de un usario, cosa que relacionabamos con user(la varaible que usaria la clase User y serian los espacios que rellenariamos con el json) y lo que ocacionaba que no se pudieran actalizar lo datos
# usamos directamnete la variable outh2, ya que contenia el token que tenia el nombre del usario y la version del token que usaba, asi solo para hacer los cambios en el usario que tenia el toekn de iniico de sesion y cambiar la version para que caduque y tenga que hacer login de nuevo
# 
# # 