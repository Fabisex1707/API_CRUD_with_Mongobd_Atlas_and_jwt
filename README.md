
# API REST CRUD - FastAPI + MongoDB Atlas

Este proyecto es una API RESTful desarrollada con FastAPI y MongoDB Atlas, que implementa operaciones básicas CRUD (Create, Read, Update, Delete) y cuenta con autenticación JWT para proteger las rutas privadas.

---

## Tecnologías utilizadas

- **Python 3.11**
- **FastAPI** - Framework web moderno para crear APIs rápidas.
- **MongoDB Atlas** - Base de datos NoSQL en la nube.
- **Pydantic** - Validación de datos.
- **JWT (JSON Web Token)** - Autenticación segura.
- **Render** - Despliegue del proyecto.
- **Postman** - Pruebas de endpoints.
- **Git** - Control de versiones.

---

## Funcionalidades principales

- Operaciones CRUD (Create, Read, Update, Delete).
- Autenticación con JWT para proteger rutas privadas.
- Cifrado de contraseñas con hashing.
- Modelado de esquemas con Pydantic.
- Conexión remota a MongoDB Atlas.
- Despliegue en Render.

---

## Rutas principales

```http
POST    /register       → Crear un nuevo usuario
POST    /login          → Iniciar sesión y obtener token JWT
GET     /users/me          → Obtener al usario por medio del token (protegida)
PUT     /update     → Actualizar un usario mandando un json con por lo menos nombre de usario y correo (protegida)
DELETE  /borrar     → Eliminar un usario por medio del token (protegida)
```

---

## Pruebas

- Se realizaron pruebas manuales con **Postman**.
- Las cabeceras incluyen el token JWT para acceder a rutas protegidas.
- Se utilizaron datos de prueba para validar registros, login y operaciones CRUD.

---

## Estructura del proyecto 

```
📁 app/
 ┣ 📄 main.py
 ┣ 📄 requirements.txt
 ┣ 📄 README.md

    📁 bd
     ┣ 📄 client.py
        📁 models
         ┣ 📄 models.py
        📁 schemas 
         ┣ 📄 schemas.py

    📁 routers
    ┣ 📄 jwt_auth_users.py
```

---

## 🧑‍💻 Autor

**Fabian Castro Dolores**  
📧 kamicami1707@gmail.com  
🔗 [GitHub](https://github.com/Fabisex1707)

---

## ✅ Estado del proyecto

🚧 En desarrollo activo | Se planean mejoras como validación avanzada y la asignacion de roles.
