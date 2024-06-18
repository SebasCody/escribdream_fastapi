import os
import shutil
import uuid
from fastapi import APIRouter, File, Query, HTTPException, Depends, UploadFile
from fastapi.responses import FileResponse
from fastapi.security import OAuth2PasswordBearer
from typing import List, Optional, Dict, Any
from pydantic import BaseModel
from enum import Enum
import datetime
from db_config import database, connectToDatabase, closeConnection
from endpoint_login_register import get_user_by_id



#HAY QUE TENER EN CUENTA QUE GENERO ES UN ENUMERADO Y QUE ROL_PERSONAJE Y ESTADO_VITAL SON ENUMERADOS TAMBIÉN
#POR LO QUE SE DEBE INGRESAR UNO DE LOS VALORES PERMITIDOS PARA CADA CAMPO

# Definición de los enumerados
class GeneroEnum(str, Enum):
    masculino = 'masculino'
    femenino = 'femenino'
    no_binario = 'no_binario'
    otro = 'otro'

class RolPersonajeEnum(str, Enum):
    protagonista = 'protagonista'
    antagonista = 'antagonista'
    secundario = 'secundario'
    principal = 'principal'
    recurrente = 'recurrente'
    invitado = 'invitado'
    otro = 'otro'
    sin_rol = 'sin_rol'

class EstadoVitalEnum(str, Enum):
    vivo = 'vivo'
    muerto = 'muerto'
    desconocido = 'desconocido'

class Personaje(BaseModel):
    id_personaje: int
    id_proyecto: int
    nombre_personaje: str
    descripcion_personaje: str
    genero: GeneroEnum
    rol_personaje: RolPersonajeEnum
    estado_vital: EstadoVitalEnum
    imagen_personaje: Optional[str]
    fecha_creacion: Optional[datetime.datetime]
    fecha_modificacion: Optional[datetime.datetime]


router = APIRouter(
    prefix="/api/escribdream",
    tags=["personajes"]
)

oauth2_scheme = OAuth2PasswordBearer("/token")

#ENDPOINT PARA OBTENER TODOS LOS PERSONAJES DE LA BASE DE DATOS O FILTRARLOS POR DIFERENTES CAMPOS DE LA TABLA
@router.get("/personajes/", response_model=Dict[str, Any])
async def get_personajes(
    token: str = Depends(oauth2_scheme),
    id_personaje: Optional[int] = Query(None),
    id_proyecto: Optional[int] = Query(None),
    nombre_personaje: Optional[str] = Query(None),
    genero: Optional[GeneroEnum] = Query(None),
    rol_personaje: Optional[RolPersonajeEnum] = Query(None),
    estado_vital: Optional[EstadoVitalEnum] = Query(None),
    fecha_creacion: Optional[str] = Query(None),
    fecha_modificacion: Optional[str] = Query(None),
):
    query = "SELECT * FROM personajes WHERE 1=1"
    values = {}

    if genero:
        query += " AND genero = :genero"
        values["genero"] = genero
    if rol_personaje:
        query += " AND rol_personaje = :rol_personaje"
        values["rol_personaje"] = rol_personaje
    if estado_vital:
        query += " AND estado_vital = :estado_vital"
        values["estado_vital"] = estado_vital
    if fecha_creacion:
        query += " AND DATE(fecha_creacion) = :fecha_creacion"
        values["fecha_creacion"] = fecha_creacion
    if fecha_modificacion:
        query += " AND DATE(fecha_modificacion) = :fecha_modificacion"
        values["fecha_modificacion"] = fecha_modificacion

    personajes = await database.fetch_all(query=query, values=values)
    if not personajes:
        raise HTTPException(status_code=404, detail="No se encontraron personajes con los filtros especificados")
    return {"ok": True, "content": [dict(personaje) for personaje in personajes]}




#ENDPOINT PARA OBTENER UN PERSONAJE ESPECÍFICO DE LA BASE DE DATOS POR SU ID_PERSONAJE
@router.get("/personajes/{id_personaje}", response_model=Dict[str, Any])
async def get_personaje(id_personaje: int, token: str = Depends(oauth2_scheme)):
    query = "SELECT * FROM personajes WHERE id_personaje = :id_personaje"
    values = {"id_personaje": id_personaje}
    personaje = await database.fetch_one(query=query, values=values)
    if not personaje:
        raise HTTPException(status_code=404, detail="No se encontró un personaje con ese ID")
    return {"ok": True, "content": [dict(personaje)]}



#ENDPOINT PARA OBTENER TODOS LOS PERSONAJES DE UN PROYECTO POR ID_PROYECTO
@router.get("/personajes/proyecto/{id_proyecto}", response_model=Dict[str, Any])
async def get_personaje(id_proyecto: int, token: str = Depends(oauth2_scheme)):
    query = "SELECT * FROM personajes WHERE id_proyecto = :id_proyecto"
    values = {"id_proyecto": id_proyecto}
    personajes = await database.fetch_all(query=query, values=values)
    if not personajes:
        raise HTTPException(status_code=404, detail="No se encontraron personajes asociados a ese proyecto")
    return {"ok": True, "content": [dict(personaje) for personaje in personajes]}
    
    
    
    # query = "SELECT * FROM personajes WHERE id_proyecto = :id_proyecto"
    # values = {"id_proyecto": id_proyecto}
    # personaje = await database.fetch_one(query=query, values=values)
    # if not personaje:
    #     raise HTTPException(status_code=404, detail="No se encontraron personajes asociados a ese proyecto.")
    # return {"ok": True, "content": [dict(personaje)]}




#Obtener todos los personajes de la bbdd por id_usuario
@router.get("/personajes/usuario/{id_usuario}", response_model=Dict[str, Any])
async def get_personajes_usuario(id_usuario: int, token: str = Depends(oauth2_scheme)):
    query = "SELECT personajes.* FROM personajes JOIN proyectos ON personajes.id_proyecto = proyectos.id_proyecto WHERE proyectos.id_usuario = :id_usuario"
    values = {"id_usuario": id_usuario}
    personajes = await database.fetch_all(query=query, values=values)
    if not personajes:
        raise HTTPException(status_code=404, detail="No se encontraron personajes asociados a proyectos del usuario con ese ID")
    return {"ok": True, "content": [dict(personaje) for personaje in personajes]}




#Obtener todos los personajes de un proyecto por id_usuario
@router.get("/personajes/usuario/{id_usuario}/proyecto/{id_proyecto}", response_model=Dict[str, Any])
async def get_personajes_usuario_proyecto(id_usuario: int, id_proyecto: int, token: str = Depends(oauth2_scheme)):
    query = "SELECT personajes.* FROM personajes JOIN proyectos ON personajes.id_proyecto = proyectos.id_proyecto WHERE proyectos.id_usuario = :id_usuario AND proyectos.id_proyecto = :id_proyecto"
    values = {"id_usuario": id_usuario, "id_proyecto": id_proyecto}
    personajes = await database.fetch_all(query=query, values=values)
    if not personajes:
        raise HTTPException(status_code=404, detail="No se encontraron personajes asociados a ese proyecto del usuario con ese ID")
    return {"ok": True, "content": [dict(personaje) for personaje in personajes]}




#OBTENER TODOS LOS PERSONAJES DE UN PROYECTO ESPECIFICO POR GENERO
@router.get("/personajes/proyecto/{id_proyecto}/genero/{genero}", response_model=Dict[str, Any])
async def get_personajes_proyecto_genero(id_proyecto: int, genero: GeneroEnum, token: str = Depends(oauth2_scheme)):
    query = "SELECT * FROM personajes WHERE id_proyecto = :id_proyecto AND genero = :genero"
    values = {"id_proyecto": id_proyecto, "genero": genero}
    personajes = await database.fetch_all(query=query, values=values)
    if not personajes:
        raise HTTPException(status_code=404, detail="No se encontraron personajes asociados a ese proyecto con ese género")
    return {"ok": True, "content": [dict(personaje) for personaje in personajes]}




#OBTENER TODOS LOS PERSONAJES DE UN PROYECTO ESPECIFICO POR ROL
@router.get("/personajes/proyecto/{id_proyecto}/rol/{rol_personaje}", response_model=Dict[str, Any])
async def get_personajes_proyecto_rol(id_proyecto: int, rol_personaje: RolPersonajeEnum, token: str = Depends(oauth2_scheme)):
    query = "SELECT * FROM personajes WHERE id_proyecto = :id_proyecto AND rol_personaje = :rol_personaje"
    values = {"id_proyecto": id_proyecto, "rol_personaje": rol_personaje}
    personajes = await database.fetch_all(query=query, values=values)
    if not personajes:
        raise HTTPException(status_code=404, detail="No se encontraron personajes asociados a ese proyecto con ese rol")
    return {"ok": True, "content": [dict(personaje) for personaje in personajes]}




#OBTENER TODOS LOS PERSONAJES DE UN PROYECTO ESPECIFICO POR ESTADO VITAL
@router.get("/personajes/proyecto/{id_proyecto}/estado/{estado_vital}", response_model=Dict[str, Any])
async def get_personajes_proyecto_estado(id_proyecto: int, estado_vital: EstadoVitalEnum, token: str = Depends(oauth2_scheme)):
    query = "SELECT * FROM personajes WHERE id_proyecto = :id_proyecto AND estado_vital = :estado_vital"
    values = {"id_proyecto": id_proyecto, "estado_vital": estado_vital}
    personajes = await database.fetch_all(query=query, values=values)
    if not personajes:
        raise HTTPException(status_code=404, detail="No se encontraron personajes asociados a ese proyecto con ese estado vital")
    return {"ok": True, "content": [dict(personaje) for personaje in personajes]}




#OBTENER TODOS LOS PERSONAJES DE UN PROYECTO ESPECIFICO POR FECHA DE CREACION
@router.get("/personajes/proyecto/{id_proyecto}/fecha_creacion/{fecha_creacion}", response_model=Dict[str, Any])
async def get_personajes_proyecto_fecha_creacion(id_proyecto: int, fecha_creacion: str, token: str = Depends(oauth2_scheme)):
    query = "SELECT * FROM personajes WHERE id_proyecto = :id_proyecto AND DATE(fecha_creacion) = :fecha_creacion"
    values = {"id_proyecto": id_proyecto, "fecha_creacion": fecha_creacion}
    personajes = await database.fetch_all(query=query, values=values)
    if not personajes:
        raise HTTPException(status_code=404, detail="No se encontraron personajes asociados a ese proyecto con esa fecha de creación")
    return {"ok": True, "content": [dict(personaje) for personaje in personajes]}




#OBTENER TODOS LOS PERSONAJES DE UN PROYECTO ESPECIFICO POR FECHA DE MODIFICACION
@router.get("/personajes/proyecto/{id_proyecto}/fecha_modificacion/{fecha_modificacion}", response_model=Dict[str, Any])
async def get_personajes_proyecto_fecha_modificacion(id_proyecto: int, fecha_modificacion: str, token: str = Depends(oauth2_scheme)):
    query = "SELECT * FROM personajes WHERE id_proyecto = :id_proyecto AND DATE(fecha_modificacion) = :fecha_modificacion"
    values = {"id_proyecto": id_proyecto, "fecha_modificacion": fecha_modificacion}
    personajes = await database.fetch_all(query=query, values=values)
    if not personajes:
        raise HTTPException(status_code=404, detail="No se encontraron personajes asociados a ese proyecto con esa fecha de modificación")
    return {"ok": True, "content": [dict(personaje) for personaje in personajes]}





#ENDPOINT PARA OBTENER TODOS LOS PERSONAJES DE UN LIBRO POR ID_LIBRO
@router.get("/personajes/libro/{id_libro}", response_model=Dict[str, Any])
async def get_personajes_libro(id_libro: int, token: str = Depends(oauth2_scheme)):
    query = "SELECT personajes.* FROM personajes JOIN personajes_libros ON personajes.id_personaje = personajes_libros.id_personaje WHERE personajes_libros.id_libro = :id_libro"
    values = {"id_libro": id_libro}
    personajes = await database.fetch_all(query=query, values=values)
    if not personajes:
        raise HTTPException(status_code=404, detail="No se encontraron personajes asociados a ese libro")
    return {"ok": True, "content": [dict(personaje) for personaje in personajes]}



#ENDPOINT PARA OBTENER TODOS LOS PERSONAJES DE UN LIBRO POR ID_LIBRO Y GENERO
@router.get("/personajes/libro/{id_libro}/genero/{genero}", response_model=Dict[str, Any])
async def get_personajes_libro_genero(id_libro: int, genero: GeneroEnum, token: str = Depends(oauth2_scheme)):
    query = "SELECT personajes.* FROM personajes JOIN personajes_libros ON personajes.id_personaje = personajes_libros.id_personaje WHERE personajes_libros.id_libro = :id_libro AND genero = :genero"
    values = {"id_libro": id_libro, "genero": genero}
    personajes = await database.fetch_all(query=query, values=values)
    if not personajes:
        raise HTTPException(status_code=404, detail="No se encontraron personajes asociados a ese libro con ese género")
    return {"ok": True, "content": [dict(personaje) for personaje in personajes]}


#ENDPOINT PARA OBTENER TODOS LOS PERSONAJES DE UN LIBRO POR ID_LIBRO Y ROL
@router.get("/personajes/libro/{id_libro}/rol/{rol_personaje}", response_model=Dict[str, Any])
async def get_personajes_libro_rol(id_libro: int, rol_personaje: RolPersonajeEnum, token: str = Depends(oauth2_scheme)):
    query = "SELECT personajes.* FROM personajes JOIN personajes_libros ON personajes.id_personaje = personajes_libros.id_personaje WHERE personajes_libros.id_libro = :id_libro AND rol_personaje = :rol_personaje"
    values = {"id_libro": id_libro, "rol_personaje": rol_personaje}
    personajes = await database.fetch_all(query=query, values=values)
    if not personajes:
        raise HTTPException(status_code=404, detail="No se encontraron personajes asociados a ese libro con ese rol")
    return {"ok": True, "content": [dict(personaje) for personaje in personajes]}


#ENDPOINT PARA OBTENER TODOS LOS PERSONAJES DE UN LIBRO POR ID_LIBRO Y ESTADO VITAL
@router.get("/personajes/libro/{id_libro}/estado/{estado_vital}", response_model=Dict[str, Any])
async def get_personajes_libro_estado(id_libro: int, estado_vital: EstadoVitalEnum, token: str = Depends(oauth2_scheme)):
    query = "SELECT personajes.* FROM personajes JOIN personajes_libros ON personajes.id_personaje = personajes_libros.id_personaje WHERE personajes_libros.id_libro = :id_libro AND estado_vital = :estado_vital"
    values = {"id_libro": id_libro, "estado_vital": estado_vital}
    personajes = await database.fetch_all(query=query, values=values)
    if not personajes:
        raise HTTPException(status_code=404, detail="No se encontraron personajes asociados a ese libro con ese estado vital")
    return {"ok": True, "content": [dict(personaje) for personaje in personajes]}



#ENDPOINT PARA OBTENER TODOS LOS PERSONAJES DE UN LIBRO POR ID_LIBRO Y FECHA DE CREACION
@router.get("/personajes/libro/{id_libro}/fecha_creacion/{fecha_creacion}", response_model=Dict[str, Any])
async def get_personajes_libro_fecha_creacion(id_libro: int, fecha_creacion: str, token: str = Depends(oauth2_scheme)):
    query = "SELECT personajes.* FROM personajes JOIN personajes_libros ON personajes.id_personaje = personajes_libros.id_personaje WHERE personajes_libros.id_libro = :id_libro AND DATE(fecha_creacion) = :fecha_creacion"
    values = {"id_libro": id_libro, "fecha_creacion": fecha_creacion}
    personajes = await database.fetch_all(query=query, values=values)
    if not personajes:
        raise HTTPException(status_code=404, detail="No se encontraron personajes asociados a ese libro con esa fecha de creación")
    return {"ok": True, "content": [dict(personaje) for personaje in personajes]}


#ENDPOINT PARA OBTENER TODOS LOS PERSONAJES DE UN LIBRO POR ID_LIBRO Y FECHA DE MODIFICACION
@router.get("/personajes/libro/{id_libro}/fecha_modificacion/{fecha_modificacion}", response_model=Dict[str, Any])
async def get_personajes_libro_fecha_modificacion(id_libro: int, fecha_modificacion: str, token: str = Depends(oauth2_scheme)):
    query = "SELECT personajes.* FROM personajes JOIN personajes_libros ON personajes.id_personaje = personajes_libros.id_personaje WHERE personajes_libros.id_libro = :id_libro AND DATE(fecha_modificacion) = :fecha_modificacion"
    values = {"id_libro": id_libro, "fecha_modificacion": fecha_modificacion}
    personajes = await database.fetch_all(query=query, values=values)
    if not personajes:
        raise HTTPException(status_code=404, detail="No se encontraron personajes asociados a ese libro con esa fecha de modificación")
    return {"ok": True, "content": [dict(personaje) for personaje in personajes]}




#--------------------------------------------------------------------------------------------------------

#ENDPOINT PARA CREAR UN NUEVO PERSONAJE EN LA BASE DE DATOS
#Base model para la creación de un personaje
class NewPersonaje(BaseModel):
    id_proyecto: int
    nombre_personaje: str
    descripcion_personaje: Optional[str]
    genero: GeneroEnum
    rol_personaje: RolPersonajeEnum
    estado_vital: EstadoVitalEnum
    imagen_personaje: Optional[str]


@router.post("/personajes/", response_model=Dict[str, Any])
async def create_personaje(personaje: NewPersonaje, token: str = Depends(oauth2_scheme)):
    query = """
        INSERT INTO personajes (id_proyecto, nombre_personaje, descripcion_personaje, genero, rol_personaje, estado_vital, imagen_personaje)
        VALUES (:id_proyecto, :nombre_personaje, :descripcion_personaje, :genero, :rol_personaje, :estado_vital, :imagen_personaje)
    """
    values = {
        "id_proyecto": personaje.id_proyecto,
        "nombre_personaje": personaje.nombre_personaje,
        "descripcion_personaje": personaje.descripcion_personaje,
        "genero": personaje.genero,
        "rol_personaje": personaje.rol_personaje,
        "estado_vital": personaje.estado_vital,
        "imagen_personaje": personaje.imagen_personaje
    }
    id_personaje = await database.execute(query=query, values=values)
    return {"message": "Personaje creado exitosamente", "id_personaje": id_personaje}


#ENDPOINT PARA ACTUALIZAR UN PERSONAJE POR SU ID_PERSONAJE

def get_personaje_by_id(id_personaje):
    connection = connectToDatabase()
    cursor = connection.cursor(dictionary=True)
    cursor.execute("SELECT nombre_personaje, descripcion_personaje, genero, rol_personaje, estado_vital, imagen_personaje FROM personajes WHERE id_personaje = %s", (id_personaje,))
    result = cursor.fetchone()
    closeConnection(connection)
    return result



class UpdatePersonaje(BaseModel):
    nombre_personaje: Optional[str] = None
    descripcion_personaje: Optional[str] = None
    genero: Optional[GeneroEnum] = None
    rol_personaje: Optional[RolPersonajeEnum] = None
    estado_vital: Optional[EstadoVitalEnum] = None
    imagen_personaje: Optional[str] = None
    
    
@router.put("/personajes/{id_personaje}")
async def update_personaje(id_personaje: int, personajeToUpdate: UpdatePersonaje, token: str = Depends(oauth2_scheme)):
    personaje = get_personaje_by_id(id_personaje)
    if personaje is None:
        raise HTTPException(status_code=404, detail="Personaje no encontrado.")
    
    fields = []
    values = {"id_personaje": id_personaje}
    
    if personajeToUpdate.nombre_personaje is not None:
        fields.append("nombre_personaje = :nombre_personaje")
        values["nombre_personaje"] = personajeToUpdate.nombre_personaje
    if personajeToUpdate.descripcion_personaje is not None:
        fields.append("descripcion_personaje = :descripcion_personaje")
        values["descripcion_personaje"] = personajeToUpdate.descripcion_personaje
    if personajeToUpdate.genero is not None:
        fields.append("genero = :genero")
        values["genero"] = personajeToUpdate.genero
    if personajeToUpdate.rol_personaje is not None:
        fields.append("rol_personaje = :rol_personaje")
        values["rol_personaje"] = personajeToUpdate.rol_personaje
    if personajeToUpdate.estado_vital is not None:
        fields.append("estado_vital = :estado_vital")
        values["estado_vital"] = personajeToUpdate.estado_vital
    if personajeToUpdate.imagen_personaje is not None:
        fields.append("imagen_personaje = :imagen_personaje")
        values["imagen_personaje"] = personajeToUpdate.imagen_personaje
        
    if not fields:
        raise HTTPException(status_code=400, detail="No hay datos para actualizar.")
        
    query = f"UPDATE personajes SET {', '.join(fields)} WHERE id_personaje = :id_personaje"
    
    await database.execute(query=query, values=values)
    return {"message": "Personaje actualizado exitosamente."}



#ENDPOINT PARA ELIMINAR UN PERSONAJE DE LA BASE DE DATOS POR SU ID_PERSONAJE
@router.delete("/personajes/{id_personaje}")
async def delete_personaje(id_personaje: int, token: str = Depends(oauth2_scheme)):
    query = "DELETE FROM personajes WHERE id_personaje = :id_personaje"
    values = {"id_personaje": id_personaje}
    await database.execute(query=query, values=values)
    return {"message": "Personaje eliminado exitosamente"}



#ENDPOINT PARA ELIMINAR TODOS LOS PERSONAJES DE UN PROYECTO POR SU ID_PROYECTO
@router.delete("/personajes/proyecto/{id_proyecto}")
async def delete_personajes_proyecto(id_proyecto: int, token: str = Depends(oauth2_scheme)):
    query = "DELETE FROM personajes WHERE id_proyecto = :id_proyecto"
    values = {"id_proyecto": id_proyecto}
    await database.execute(query=query, values=values)
    return {"message": "Personajes asociados al proyecto eliminados exitosamente"}



#ENDPOINT PARA ELIMINAR TODOS LOS PERSONAJES DE UN USUARIO POR SU ID_USUARIO
@router.delete("/personajes/usuario/{id_usuario}")
async def delete_personajes_usuario(id_usuario: int, token: str = Depends(oauth2_scheme)):
    query = "DELETE personajes FROM personajes JOIN proyectos ON personajes.id_proyecto = proyectos.id_proyecto WHERE proyectos.id_usuario = :id_usuario"
    values = {"id_usuario": id_usuario}
    await database.execute(query=query, values=values)
    return {"message": "Personajes asociados a proyectos del usuario eliminados exitosamente"}




#ENDPOINT PARA ELIMINAR TODOS LOS PERSONAJES ASOCIADOS A UN LIBRO
@router.delete("/personajes/libro/{id_libro}")
async def delete_personajes_libro(id_libro: int, token: str = Depends(oauth2_scheme)):
    query = "DELETE FROM personajes_libros WHERE id_libro = :id_libro"
    values = {"id_libro": id_libro}
    await database.execute(query=query, values=values)
    return {"message": "Personajes asociados al libro eliminados exitosamente"}


#ENDPOINT PARA ASOCIAR UN PERSONAJE A UN LIBRO
@router.post("/personajes/libro/")
async def create_personaje_libro(id_personaje: int, id_libro: int, token: str = Depends(oauth2_scheme)):
    query = "INSERT INTO personajes_libros (id_personaje, id_libro) VALUES (:id_personaje, :id_libro)"
    values = {"id_personaje": id_personaje, "id_libro": id_libro}
    await database.execute(query=query, values=values)
    return {"message": "Personaje asociado al libro exitosamente"}


#ENDPOINT PARA DESASOCIAR UN PERSONAJE DE UN LIBRO
@router.delete("/personajes/libro/")
async def delete_personaje_libro(id_personaje: int, id_libro: int, token: str = Depends(oauth2_scheme)):
    query = "DELETE FROM personajes_libros WHERE id_personaje = :id_personaje AND id_libro = :id_libro"
    values = {"id_personaje": id_personaje, "id_libro": id_libro}
    await database.execute(query=query, values=values)
    return {"message": "Personaje desasociado del libro exitosamente"}



# Endpoint para subir imágenes y asociarlas a un personaje
@router.post("/subir_imagen/personaje/{id_personaje}")
async def upload_image(id_personaje:int, file: UploadFile = File(...), token: str = Depends(oauth2_scheme)):
    
    personaje = get_personaje_by_id(id_personaje)
    
    if personaje is None:
        raise HTTPException(status_code=404, detail="Personaje no encontrado.")
    
    # if file.content_type not in ["image/jpeg", "image/png, image/jpg, image/gif, image/bmp, image/webp, image/tiff, image/svg+xml"]:
    #     raise HTTPException(status_code=400, detail="Tipo de archivo no soportado")
    
    file_extension = os.path.splitext(file.filename)[1]
    unique_filename = f"{uuid.uuid4()}{file_extension}"
    file_path = os.path.join("user_storage", unique_filename)

    with open(file_path, "wb") as buffer:
        shutil.copyfileobj(file.file, buffer)
        
    #Actualizar la imagen de perfil del personaje. Primero debemos eliminar la imagen anterior
    if personaje["imagen_personaje"]:
        old_image_path = os.path.join("user_storage", personaje["imagen_personaje"])
        if os.path.exists(old_image_path):
            os.remove(old_image_path)
            
    query = "UPDATE personajes SET imagen_personaje = :imagen_personaje WHERE id_personaje = :id_personaje"
    values = {"id_personaje": id_personaje, "imagen_personaje": unique_filename}
    await database.execute(query=query, values=values)
    
    
    return {"message": "Imagen subida exitosamente.", "filename": unique_filename}

