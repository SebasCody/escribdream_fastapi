import os
import shutil
import uuid
from fastapi import APIRouter, File, Query, HTTPException, Depends, UploadFile
from typing import List, Optional, Dict, Any
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel
import datetime

import requests
from db_config import closeConnection, connectToDatabase, database
from fastapi.security import OAuth2PasswordBearer
from endpoint_login_register import get_user_by_id

router = APIRouter(
    prefix="/api/escribdream",
    tags=["usuarios"]
)

# Montar el directorio de almacenamiento de usuarios para servir archivos estáticos
router.mount("/user_storage", StaticFiles(directory="user_storage"), name="user_storage")


class Usuario(BaseModel):
    id_usuario: int
    nombre_usuario: str
    primer_apellido: str
    segundo_apellido: str
    seudonimo: str
    correo_electronico: str
    fecha_registro: datetime.datetime
    nombre_completo: str
    fecha_nacimiento: datetime.date
    biografia: Optional[str]
    imagen_perfil: Optional[str]
    proyectos_iniciados: int
    proyectos_finalizados: int
    ultima_conexion: Optional[datetime.datetime]



oauth2_scheme = OAuth2PasswordBearer("/token")

#ENDPOINT PARA OBTENER TODOS LOS USUARIOS O FILTRARLOS POR DIFERENTES CAMPOS DE LA TABLA
@router.get("/usuarios/", response_model=Dict[str, Any])
async def get_usuarios(
    token: str = Depends(oauth2_scheme),
    nombre_usuario: Optional[str] = Query(None),
    primer_apellido: Optional[str] = Query(None),
    segundo_apellido: Optional[str] = Query(None),
    seudonimo: Optional[str] = Query(None),
    correo_electronico: Optional[str] = Query(None),
    fecha_registro: Optional[str] = Query(None),
    fecha_nacimiento: Optional[str] = Query(None),
    proyectos_iniciados: Optional[int] = Query(None),
    proyectos_finalizados: Optional[int] = Query(None),
    ultima_conexion: Optional[str] = Query(None),
):
    
    query = "SELECT * FROM usuarios WHERE 1=1"
    values = {}

    if nombre_usuario:
        query += " AND nombre_usuario LIKE :nombre_usuario"
        values["nombre_usuario"] = f"%{nombre_usuario}%"
    if correo_electronico:
        query += " AND correo_electronico LIKE :correo_electronico"
        values["correo_electronico"] = f"%{correo_electronico}%"
    if primer_apellido:
        query += " AND primer_apellido LIKE :primer_apellido"
        values["primer_apellido"] = f"%{primer_apellido}%"
    if segundo_apellido:
        query += " AND segundo_apellido LIKE :segundo_apellido"
        values["segundo_apellido"] = f"%{segundo_apellido}%"
    if fecha_registro:
        query += " AND DATE(fecha_registro) = :fecha_registro"
        values["fecha_registro"] = fecha_registro
    if fecha_nacimiento:
        query += " AND fecha_nacimiento = :fecha_nacimiento"
        values["fecha_nacimiento"] = fecha_nacimiento
    if proyectos_iniciados is not None:
        query += " AND proyectos_iniciados = :proyectos_iniciados"
        values["proyectos_iniciados"] = proyectos_iniciados
    if proyectos_finalizados is not None:
        query += " AND proyectos_finalizados = :proyectos_finalizados"
        values["proyectos_finalizados"] = proyectos_finalizados
    if ultima_conexion:
        query += " AND DATE(ultima_conexion) = :ultima_conexion"
        values["ultima_conexion"] = ultima_conexion
    

    results = await database.fetch_all(query=query, values=values)
    if not results:
        raise HTTPException(status_code=404, detail="Ningún usuario coincide con los parámetros proporcionados.")
    return {"ok":True, "content": [dict(result) for result in results]}




#ENDPOINT PARA OBTENER UN USUARIO POR SU ID
@router.get("/usuarios/{id_usuario}", response_model=Dict[str, Any])
async def get_usuario(id_usuario: int, token: str = Depends(oauth2_scheme)):
    query = "SELECT id_usuario, nombre_usuario, primer_apellido, segundo_apellido, seudonimo, correo_electronico, fecha_registro, fecha_nacimiento, biografia, imagen_perfil, proyectos_iniciados, proyectos_finalizados, ultima_conexion FROM usuarios WHERE id_usuario = :id_usuario"
    
    values = {"id_usuario": id_usuario}
    result = await database.fetch_one(query=query, values=values)
    if not result:
        raise HTTPException(status_code=404, detail="Usuario no encontrado.")
    return {"ok":True, "content": [dict(result)]}



#ENDPOINT PARA ACTUALIZAR UN USUARIO POR SU ID
class UserUpdate(BaseModel):
    nombre_usuario: Optional[str] = None
    primer_apellido: Optional[str] = None
    segundo_apellido: Optional[str] = None
    correo_electronico: Optional[str] = None
    fecha_nacimiento: Optional[str] = None
    biografia: Optional[str] = None
    seudonimo: Optional[str] = None
    # imagen_perfil: Optional[str] = None
    

# Endpoint para actualizar uno o varios datos de un usuario
@router.put("/actualizar/usuario/{id_usuario}")
async def update_usuario(id_usuario: int, user_data: UserUpdate, token: str = Depends(oauth2_scheme)):
    user = get_user_by_id(id_usuario)
    if user is None:
        raise HTTPException(status_code=404, detail="Usuario no encontrado.")
    
    fields = []
    values = {"id_usuario": id_usuario}
    
    if user_data.nombre_usuario is not None:
        fields.append("nombre_usuario = :nombre_usuario")
        values["nombre_usuario"] = user_data.nombre_usuario
    if user_data.primer_apellido is not None:
        fields.append("primer_apellido = :primer_apellido")
        values["primer_apellido"] = user_data.primer_apellido
    if user_data.segundo_apellido is not None:
        fields.append("segundo_apellido = :segundo_apellido")
        values["segundo_apellido"] = user_data.segundo_apellido
    if user_data.correo_electronico is not None:    
        fields.append("correo_electronico = :correo_electronico")
        values["correo_electronico"] = user_data.correo_electronico
    if user_data.fecha_nacimiento is not None:
        fields.append("fecha_nacimiento = :fecha_nacimiento")
        values["fecha_nacimiento"] = user_data.fecha_nacimiento
    if user_data.biografia is not None:
        fields.append("biografia = :biografia")
        values["biografia"] = user_data.biografia
    if user_data.seudonimo is not None:
        fields.append("seudonimo = :seudonimo")
        values["seudonimo"] = user_data.seudonimo
    
    # if user_data.imagen_perfil is not None:
    #     image_base_url = "http://127.0.0.1:8001/user_storage/"
    #     image_url = f"{image_base_url}{user_data.imagen_perfil}" if user_data.imagen_perfil else None
    #     fields.append("imagen_perfil = :image_url")
    #     values["imagen_perfil"] = image_url
        
    if not fields:
        raise HTTPException(status_code=400, detail="No hay datos para actualizar.")
    
    query = f"UPDATE usuarios SET {', '.join(fields)} WHERE id_usuario = :id_usuario"
    
    #obtener el usuario actualizado
    # await database.fetch_one("SELECT * FROM usuarios WHERE id_usuario = :id_usuario", values={"id_usuario": id_usuario})
    await database.execute(query=query, values=values)
    
    return {
        "message": "Usuario actualizado exitosamente."
        # "image_url": updated_user["imagen_perfil"]
    }
    
    
    

# Endpoint para subir imágenes y asociarlas a un usuario
@router.post("/subir_imagen/{id_usuario}")
async def upload_image(id_usuario:int, file: UploadFile = File(...), token: str = Depends(oauth2_scheme)):
    
    user = get_user_by_id(id_usuario)
    if user is None:
        raise HTTPException(status_code=404, detail="Usuario no encontrado.")
    
    # if file.content_type not in ["image/jpeg", "image/png, image/jpg, image/gif, image/bmp, image/webp, image/tiff, image/svg+xml"]:
    #     raise HTTPException(status_code=400, detail="Tipo de archivo no soportado")
    
    file_extension = os.path.splitext(file.filename)[1]
    unique_filename = f"{uuid.uuid4()}{file_extension}"
    file_path = os.path.join("user_storage", unique_filename)

    with open(file_path, "wb") as buffer:
        shutil.copyfileobj(file.file, buffer)
        
    #Actualizar la imagen de perfil del usuario. Primero debemos eliminar la imagen anterior
    if user["imagen_perfil"]:
        old_image_path = os.path.join("user_storage", user["imagen_perfil"])
        if os.path.exists(old_image_path):
            os.remove(old_image_path)
            
    query = "UPDATE usuarios SET imagen_perfil = :imagen_perfil WHERE id_usuario = :id_usuario"
    values = {"id_usuario": id_usuario, "imagen_perfil": unique_filename}
    await database.execute(query=query, values=values)
    
    
    return {"message": "Imagen subida exitosamente.", "filename": unique_filename}


# Endpoint para obtener una imagen existente
STORAGE_PATH = "user_storage"

@router.get("/images/{image_name}")
async def get_image(image_name: str):
    file_path = os.path.join(STORAGE_PATH, image_name)
    if not os.path.exists(file_path):
        raise HTTPException(status_code=404, detail="Image not found")
    return FileResponse(file_path)



#ENDPOINT PARA ELIMINAR UN USUARIO POR SU ID
@router.delete("/usuarios/{id_usuario}")
async def delete_usuario(id_usuario: int, token: str = Depends(oauth2_scheme)):
    query = "DELETE FROM usuarios WHERE id_usuario = :id_usuario"
    values = {"id_usuario": id_usuario}
    await database.execute(query=query, values=values)
    return {"message": "Usuario eliminado exitosamente."}
    
    







class UserStats(BaseModel):
    totalProyectos: int
    totalLibros: int
    totalCapitulos: int
    totalPersonajes: int
    totalPalabras: int

@router.get("/usuarios/estadisticas/{user_id}", response_model=UserStats)
async def get_user_stats(user_id: int, token: str = Depends(oauth2_scheme)) :
    connection = None
    try:
        connection = connectToDatabase()
        cursor = connection.cursor(dictionary=True)
        
        # Obtener total de proyectos
        cursor.execute("SELECT COUNT(*) as totalProyectos FROM proyectos WHERE id_usuario = %s", (user_id,))
        totalProyectos = cursor.fetchone().get('totalProyectos', 0)
        
        # Obtener total de libros
        cursor.execute("""
            SELECT COUNT(*) as totalLibros 
            FROM libros 
            WHERE id_proyecto IN (
                SELECT id_proyecto 
                FROM proyectos 
                WHERE id_usuario = %s
            )
        """, (user_id,))
        totalLibros = cursor.fetchone().get('totalLibros', 0)
        
        # Obtener total de capítulos
        cursor.execute("""
            SELECT COUNT(*) as totalCapitulos 
            FROM capitulos 
            WHERE id_libro IN (
                SELECT id_libro 
                FROM libros 
                WHERE id_proyecto IN (
                    SELECT id_proyecto 
                    FROM proyectos 
                    WHERE id_usuario = %s
                )
            )
        """, (user_id,))
        totalCapitulos = cursor.fetchone().get('totalCapitulos', 0)
        
        # Obtener total de personajes
        cursor.execute("""
            SELECT COUNT(*) as totalPersonajes
            FROM personajes
            WHERE id_proyecto IN (
                SELECT id_proyecto 
                FROM proyectos 
                WHERE id_usuario = %s
            )
        """, (user_id,))
        totalPersonajes = cursor.fetchone().get('totalPersonajes', 0)
        
        # Obtener total de palabras
        cursor.execute("""
            SELECT COALESCE(SUM(LENGTH(contenido_capitulo) - LENGTH(REPLACE(contenido_capitulo, ' ', '')) + 1), 0) as totalPalabras 
            FROM capitulos 
            WHERE id_libro IN (
                SELECT id_libro 
                FROM libros 
                WHERE id_proyecto IN (
                    SELECT id_proyecto 
                    FROM proyectos 
                    WHERE id_usuario = %s
                )
            )
        """, (user_id,))
        totalPalabras = cursor.fetchone().get('totalPalabras', 0)

        return UserStats(
            totalProyectos=totalProyectos,
            totalLibros=totalLibros, 
            totalCapitulos=totalCapitulos, 
            totalPersonajes=totalPersonajes, 
            totalPalabras=totalPalabras
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error retrieving user stats: {str(e)}")
    finally:
        if connection:
            closeConnection(connection)


















# @router.put("/actualizarusuario/{id_usuario}")
# async def update_usuario(id_usuario: int, user_data: UserUpdate, token: str = Depends(oauth2_scheme)):
#     user = get_user_by_id(id_usuario)
#     if user is None:
#         raise HTTPException(status_code=404, detail="Usuario no encontrado.")
    
#     fields = []
#     values = {"id_usuario": id_usuario}
    
#     if user_data.nombre_usuario is not None:
#         fields.append("nombre_usuario = :nombre_usuario")
#         values["nombre_usuario"] = user_data.nombre_usuario
#     if user_data.primer_apellido is not None:
#         fields.append("primer_apellido = :primer_apellido")
#         values["primer_apellido"] = user_data.primer_apellido
#     if user_data.segundo_apellido is not None:
#         fields.append("segundo_apellido = :segundo_apellido")
#         values["segundo_apellido"] = user_data.segundo_apellido
#     if user_data.correo_electronico is not None:
#         fields.append("correo_electronico = :correo_electronico")
#         values["correo_electronico"] = user_data.correo_electronico
#     if user_data.fecha_nacimiento is not None:
#         fields.append("fecha_nacimiento = :fecha_nacimiento")
#         values["fecha_nacimiento"] = user_data.fecha_nacimiento
#     if user_data.biografia is not None:
#         fields.append("biografia = :biografia")
#         values["biografia"] = user_data.biografia
#     if user_data.seudonimo is not None:
#         fields.append("seudonimo = :seudonimo")
#         values["seudonimo"] = user_data.seudonimo
#     if user_data.imagen_perfil is not None:
#         fields.append("imagen_perfil = :imagen_perfil")
#         values["imagen_perfil"] = user_data.imagen_perfil
    
#     if not fields:
#         raise HTTPException(status_code=400, detail="No hay datos para actualizar.")
    
#     query = f"UPDATE usuarios SET {', '.join(fields)} WHERE id_usuario = :id_usuario"
    
#     await database.execute(query=query, values=values)
#     return {"message": "Usuario actualizado exitosamente."}






    
# @router.put("/actualizarusuario/{id_usuario}")
# async def update_usuario(id_usuario: int, user_data: UserUpdate, token: str = Depends(oauth2_scheme) ):
#     user = get_user_by_id(id_usuario)
#     if user is None:
#         raise HTTPException(status_code=404, detail="Usuario no encontrado.")
    
#     query = "UPDATE usuarios SET "
#     values = {}
#     if user_data.nombre_usuario:
#         query += "nombre_usuario = :nombre_usuario, "
#         values["nombre_usuario"] = user_data.nombre_usuario
#     if user_data.primer_apellido:
#         query += "primer_apellido = :primer_apellido, "
#         values["primer_apellido"] = user_data.primer_apellido
#     if user_data.segundo_apellido:
#         query += "segundo_apellido = :segundo_apellido, "
#         values["segundo_apellido"] = user_data.segundo_apellido
#     if user_data.correo_electronico:
#         query += "correo_electronico = :correo_electronico, "
#         values["correo_electronico"] = user_data.correo_electronico
#     if user_data.fecha_nacimiento:
#         query += "fecha_nacimiento = :fecha_nacimiento, "
#         values["fecha_nacimiento"] = user_data.fecha_nacimiento
#     if user_data.biografia:
#         query += "biografia = :biografia, "
#         values["biografia"] = user_data.biografia
#     if user_data.seudonimo:
#         query += "seudonimo = :seudonimo, "
#         values["seudonimo"] = user_data.seudonimo
#     if user_data.imagen_perfil:
#         query += "imagen_perfil = :imagen_perfil, "
#         values["imagen_perfil"] = user_data.imagen_perfil
    
#     query = query[:-2]
#     query += " WHERE id_usuario = :id_usuario"
#     values["id_usuario"] = user["id_usuario"]
#     await database.execute(query, values)
#     return {"message": "Usuario actualizado exitosamente."}
    

# @router.put("/usuarios/{id_usuario}", response_model=Usuario)
# async def update_usuario(id_usuario: int, usuario: Usuario, token: str = Depends(oauth2_scheme)):
#     query = """
#         UPDATE usuarios
#         SET nombre_usuario = :nombre_usuario, primer_apellido = :primer_apellido, segundo_apellido = :segundo_apellido, seudonimo = :seudonimo, correo_electronico = :correo_electronico, fecha_registro = :fecha_registro, fecha_nacimiento = :fecha_nacimiento, biografia = :biografia, imagen_perfil = :imagen_perfil, proyectos_iniciados = :proyectos_iniciados, proyectos_finalizados = :proyectos_finalizados, ultima_conexion = :ultima_conexion
#         WHERE id_usuario = :id_usuario
#     """
#     values = usuario.dict()
#     values["id_usuario"] = id_usuario
#     values["fecha_registro"] = datetime.datetime.now()
#     values["nombre_completo"] = f"{values['nombre_usuario']} {values['primer_apellido']} {values['segundo_apellido']}"
#     await database.execute(query=query, values=values)
#     return usuario









