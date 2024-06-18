from fastapi import APIRouter, Query, HTTPException, Depends
from fastapi.security import OAuth2PasswordBearer
from typing import List, Optional, Dict, Any
from pydantic import BaseModel
import datetime
from db_config import database

class Proyecto(BaseModel):
    id_proyecto: int
    id_usuario: int
    nombre_proyecto: str
    tipo_proyecto: str
    descripcion_proyecto: str
    estado_proyecto: str
    libros_asociados: int
    fecha_creacion: datetime.datetime
    fecha_modificacion: datetime.datetime
    fecha_finalizacion: Optional[datetime.datetime]
    etiquetas_proyecto: Optional[str]
    imagen_portada: Optional[str]

router = APIRouter(
    prefix="/api/escribdream",
    tags=["proyectos"]
)

oauth2_scheme = OAuth2PasswordBearer("/token")

#ENDPOINT PARA OBTENER TODOS LOS PROYECTOS O FILTRARLOS POR DIFERENTES CAMPOS DE LA TABLA
@router.get("/proyectos/", response_model=Dict[str, Any])
async def get_proyectos(
    token: str = Depends(oauth2_scheme),
    id_proyecto: Optional[int] = Query(None),
    id_usuario: Optional[int] = Query(None),
    nombre_proyecto: Optional[str] = Query(None),
    tipo_proyecto: Optional[str] = Query(None),
    descripcion_proyecto: Optional[str] = Query(None),
    estado_proyecto: Optional[str] = Query(None),
    libros_asociados: Optional[int] = Query(None),
    fecha_creacion: Optional[str] = Query(None),
    fecha_modificacion: Optional[str] = Query(None),
    fecha_finalizacion: Optional[str] = Query(None),
    etiquetas_proyecto: Optional[str] = Query(None),
    imagen_portada: Optional[str] = Query(None),
):
    query = "SELECT * FROM proyectos WHERE 1=1"
    values = {}
    
    if nombre_proyecto:
        query += " AND nombre_proyecto LIKE :nombre_proyecto"
        values["nombre_proyecto"] = f"%{nombre_proyecto}%"
    if tipo_proyecto:
        query += " AND tipo_proyecto = :tipo_proyecto"
        values["tipo_proyecto"] = tipo_proyecto
    if descripcion_proyecto:
        query += " AND descripcion_proyecto LIKE :descripcion_proyecto"
        values["descripcion_proyecto"] = f"%{descripcion_proyecto}%"
    if estado_proyecto:
        query += " AND estado_proyecto = :estado_proyecto"
        values["estado_proyecto"] = estado_proyecto
    if libros_asociados is not None:
        query += " AND libros_asociados = :libros_asociados"
        values["libros_asociados"] = libros_asociados
    if fecha_creacion:
        query += " AND DATE(fecha_creacion) = :fecha_creacion"
        values["fecha_creacion"] = fecha_creacion
    if fecha_modificacion:
        query += " AND DATE(fecha_modificacion) = :fecha_modificacion"
        values["fecha_modificacion"] = fecha_modificacion
    if fecha_finalizacion:
        query += " AND DATE(fecha_finalizacion) = :fecha_finalizacion"
        values["fecha_finalizacion"] = fecha_finalizacion
    if etiquetas_proyecto:
        query += " AND etiquetas_proyecto LIKE :etiquetas_proyecto"
        values["etiquetas_proyecto"] = f"%{etiquetas_proyecto}%"
    if imagen_portada:  
        query += " AND imagen_portada = :imagen_portada"
        values["imagen_portada"] = imagen_portada

    proyectos = await database.fetch_all(query=query, values=values)
    if not proyectos:
        raise HTTPException(status_code=404, detail="No se encontraron proyectos con los filtros especificados")
    return {"ok": True, "content": [dict(proyecto) for proyecto in proyectos]}


#ENDPOINT PARA OBTENER UN PROYECTO POR SU ID
@router.get("/proyectos/{id_proyecto}", response_model=Dict[str, Any])
async def get_proyecto(id_proyecto: int, token: str = Depends(oauth2_scheme)):
    query = "SELECT * FROM proyectos WHERE id_proyecto = :id_proyecto"
    values = {"id_proyecto": id_proyecto}
    proyecto = await database.fetch_one(query=query, values=values)
    if not proyecto:
        raise HTTPException(status_code=404, detail="No se encontró un proyecto con el id proporcionado")
    return {"ok": True, "content": dict(proyecto)}


#ENDPOINT PARA OBTENER TODOS LOS PROYECTOS DE UN USUARIO
@router.get("/proyectos/usuario/{id_usuario}", response_model=Dict[str, Any])
async def get_proyectos_usuario(id_usuario: int, token: str = Depends(oauth2_scheme)):
    query = "SELECT * FROM proyectos WHERE id_usuario = :id_usuario"
    values = {"id_usuario": id_usuario}
    proyectos = await database.fetch_all(query=query, values=values)
    if not proyectos:
        raise HTTPException(status_code=404, detail="El usuario no tiene proyectos asociados")
    return {"ok": True, "content": [dict(proyecto) for proyecto in proyectos]}


#ENDPOINT PARA OBTENER LOS PROYECTOS DE UN USUARIO POR SU TIPO DE PROYECTO
@router.get("/proyectos/usuario/{id_usuario}/tipo_proyecto/{tipo_proyecto}", response_model=Dict[str, Any])
async def get_proyectos_usuario_tipo(id_usuario: int, tipo_proyecto: str, token: str = Depends(oauth2_scheme)):
    query = "SELECT * FROM proyectos WHERE id_usuario = :id_usuario AND tipo_proyecto = :tipo_proyecto"
    values = {"id_usuario": id_usuario, "tipo_proyecto": tipo_proyecto}
    proyectos = await database.fetch_all(query=query, values=values)
    if not proyectos:
        raise HTTPException(status_code=404, detail="El usuario no tiene proyectos asociados con el tipo especificado")
    return {"ok": True, "content": [dict(proyecto) for proyecto in proyectos]}


#ENDPOINT PARA OBTENER LOS PROYECTOS DE UN USUARIO POR SU ESTADO
@router.get("/proyectos/usuario/{id_usuario}/estado/{estado_proyecto}", response_model=Dict[str, Any])
async def get_proyectos_usuario_estado(id_usuario: int, estado_proyecto: str, token: str = Depends(oauth2_scheme)):
    query = "SELECT * FROM proyectos WHERE id_usuario = :id_usuario AND estado_proyecto = :estado_proyecto"
    values = {"id_usuario": id_usuario, "estado_proyecto": estado_proyecto}
    proyectos = await database.fetch_all(query=query, values=values)
    if not proyectos:
        raise HTTPException(status_code=404, detail="El usuario no tiene proyectos asociados con el estado especificado")
    return {"ok": True, "content": [dict(proyecto) for proyecto in proyectos]}


# ENDPOINT PARA OBTENER LOS PROYECTOS DE UN USUARIO POR LIBROS ASOCIADOS
@router.get("/proyectos/usuario/{id_usuario}/libros_asociados/{libros_asociados}", response_model=Dict[str, Any])
async def get_proyectos_usuario_libros_asociados(id_usuario: int, libros_asociados: int, token: str = Depends(oauth2_scheme)):
    query = "SELECT * FROM proyectos WHERE id_usuario = :id_usuario AND libros_asociados = :libros_asociados"
    values = {"id_usuario": id_usuario, "libros_asociados": libros_asociados}
    proyectos = await database.fetch_all(query=query, values=values)
    if not proyectos:
        raise HTTPException(status_code=404, detail="El usuario no tiene proyectos con el número de libros asociados especificado")
    return {"ok": True, "content": [dict(proyecto) for proyecto in proyectos]}


#ENDPOINT PARA CREAR UN PROYECTO
# @router.post("/proyectos/")
# async def create_proyecto(proyecto: Proyecto, token: str = Depends(oauth2_scheme)):
#     query = """
#         INSERT INTO proyectos (id_usuario, nombre_proyecto, tipo_proyecto, descripcion_proyecto, estado_proyecto, libros_asociados, fecha_creacion, fecha_modificacion, fecha_finalizacion, etiquetas_proyecto, imagen_portada)
#         VALUES (:id_usuario, :nombre_proyecto, :tipo_proyecto, :descripcion_proyecto, :estado_proyecto, :libros_asociados, :fecha_creacion, :fecha_modificacion, :fecha_finalizacion, :etiquetas_proyecto, :imagen_portada)
#     """
#     values = proyecto.dict()
#     await database.execute(query=query, values=values)
#     return {"message": "Proyecto creado exitosamente"}

class NewProyecto(BaseModel):
    id_usuario: int
    nombre_proyecto: str
    tipo_proyecto: str
    descripcion_proyecto: str
    etiquetas_proyecto: Optional[str]
    imagen_portada: Optional[str]

@router.post("/proyectos/")
async def create_proyecto(proyecto: NewProyecto, token: str = Depends(oauth2_scheme)):
    query = """
        INSERT INTO proyectos (id_usuario, nombre_proyecto, tipo_proyecto, descripcion_proyecto, etiquetas_proyecto, imagen_portada)
        VALUES (:id_usuario, :nombre_proyecto, :tipo_proyecto, :descripcion_proyecto, :etiquetas_proyecto, :imagen_portada)
    """
    values = proyecto.dict()
    await database.execute(query=query, values=values)
    return {"message": "Proyecto creado exitosamente"}




#ENDPOINT PARA ELIMINAR UN PROYECTO
@router.delete("/proyectos/{id_proyecto}")
async def delete_proyecto(id_proyecto: int, token: str = Depends(oauth2_scheme)):
    query = "DELETE FROM proyectos WHERE id_proyecto = :id_proyecto"
    values = {"id_proyecto": id_proyecto}
    await database.execute(query=query, values=values)
    return {"message": "Proyecto eliminado exitosamente"}


#ENDPOINT PARA ACTUALIZAR UN PROYECTO POR SU ID CON LOS DATOS PROPORCIONADOS QUE SON OPCIONALES
class UpdateProyecto(BaseModel):
    nombre_proyecto: Optional[str]
    tipo_proyecto: Optional[str]
    descripcion_proyecto: Optional[str]
    estado_proyecto: Optional[str]
    etiquetas_proyecto: Optional[str]
    imagen_portada: Optional[str]
    
    
@router.put("/proyectos/{id_proyecto}")
async def update_proyecto(id_proyecto: int, proyecto: UpdateProyecto, token: str = Depends(oauth2_scheme)):
    query = "UPDATE proyectos SET "
    values = {}
    if proyecto.nombre_proyecto:
        query += "nombre_proyecto = :nombre_proyecto, "
        values["nombre_proyecto"] = proyecto.nombre_proyecto
    if proyecto.tipo_proyecto:
        query += "tipo_proyecto = :tipo_proyecto, "
        values["tipo_proyecto"] = proyecto.tipo_proyecto
    if proyecto.descripcion_proyecto:
        query += "descripcion_proyecto = :descripcion_proyecto, "
        values["descripcion_proyecto"] = proyecto.descripcion_proyecto
    if proyecto.estado_proyecto:
        query += "estado_proyecto = :estado_proyecto, "
        values["estado_proyecto"] = proyecto.estado_proyecto
    if proyecto.etiquetas_proyecto:
        query += "etiquetas_proyecto = :etiquetas_proyecto, "
        values["etiquetas_proyecto"] = proyecto.etiquetas_proyecto
    if proyecto.imagen_portada:
        query += "imagen_portada = :imagen_portada, "
        values["imagen_portada"] = proyecto.imagen_portada
    query = query[:-2] + " WHERE id_proyecto = :id_proyecto"
    values["id_proyecto"] = id_proyecto
    await database.execute(query=query, values=values)
    return {"message": "Proyecto actualizado exitosamente"}