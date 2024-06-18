from fastapi import APIRouter, Query, HTTPException, Depends
from fastapi.security import OAuth2PasswordBearer
from typing import List, Optional, Dict, Any
from pydantic import BaseModel
import datetime
from db_config import database

class LineaTiempo(BaseModel):
    id_linea_tiempo: int
    id_proyecto: int
    nombre_linea_tiempo: str
    descripcion_lineatiempo: str
    fecha_creacion: datetime.datetime
    fecha_modificacion: datetime.datetime

router = APIRouter(
    prefix="/api/escribdream",
    tags=["lineas_tiempo"]
)

oauth2_scheme = OAuth2PasswordBearer("/token")

#ENDPOINT PARA OBTENER TODAS LAS LINEAS DE TIEMPO O FILTRARLAS POR DIFERENTES CAMPOS DE LA TABLA
@router.get("/lineas_tiempo/", response_model=Dict[str, Any])
async def get_lineas_tiempo(
    token: str = Depends(oauth2_scheme),
    id_linea_tiempo: Optional[int] = Query(None),
    id_proyecto: Optional[int] = Query(None),
    nombre_linea_tiempo: Optional[str] = Query(None),
    descripcion_lineatiempo: Optional[str] = Query(None),
    fecha_creacion: Optional[str] = Query(None),
    fecha_modificacion: Optional[str] = Query(None)
):
    query = "SELECT * FROM lineas_de_tiempo WHERE 1=1"
    values = {}
    
    if fecha_creacion:
        query += " AND DATE(fecha_creacion) = :fecha_creacion"
        values["fecha_creacion"] = fecha_creacion
    if fecha_modificacion:
        query += " AND DATE(fecha_modificacion) = :fecha_modificacion"
        values["fecha_modificacion"] = fecha_modificacion
    
    lineas_tiempo = await database.fetch_all(query=query, values=values)
    if not lineas_tiempo:
        raise HTTPException(status_code=404, detail="No se encontraron líneas de tiempo con los filtros especificados")
    return {"ok": True, "content": [dict(linea_tiempo) for linea_tiempo in lineas_tiempo]}


#ENDPOINT PARA OBTENER UNA LINEA DE TIEMPO POR SU ID
@router.get("/lineas_tiempo/{id_linea_tiempo}", response_model=Dict[str, Any])
async def get_linea_tiempo(id_linea_tiempo: int, token: str = Depends(oauth2_scheme)):
    query = "SELECT * FROM lineas_de_tiempo WHERE id_linea_tiempo = :id_linea_tiempo"
    values = {"id_linea_tiempo": id_linea_tiempo}
    
    linea_tiempo = await database.fetch_one(query=query, values=values)
    if linea_tiempo is None:
        raise HTTPException(status_code=404, detail="La línea de tiempo no existe")
    return {"ok": True, "content": dict(linea_tiempo)}



#ENDPOINT PARA OBETENER LA LINEA DE TIEMPO DE UN PROYECTO POR ID DE PROYECTO
@router.get("/lineas_tiempo/proyecto/{id_proyecto}", response_model=Dict[str, Any])
async def get_lineas_tiempo_proyecto(id_proyecto: int, token: str = Depends(oauth2_scheme)):
    query = "SELECT * FROM lineas_de_tiempo WHERE id_proyecto = :id_proyecto"
    values = {"id_proyecto": id_proyecto}
    
    lineas_tiempo = await database.fetch_all(query=query, values=values)
    if not lineas_tiempo:
        raise HTTPException(status_code=404, detail="No se encontraron líneas de tiempo para el proyecto especificado")
    return {"ok": True, "content": [dict(linea_tiempo) for linea_tiempo in lineas_tiempo]}



#ENDPOINT PARA CREAR UNA LINEA DE TIEMPO
@router.post("/lineas_tiempo/", response_model=Dict[str, Any])
async def create_linea_tiempo(linea_tiempo: LineaTiempo, token: str = Depends(oauth2_scheme)):
    query = "INSERT INTO lineas_de_tiempo (id_proyecto, nombre_linea_tiempo, descripcion_lineatiempo) VALUES (:id_proyecto, :nombre_linea_tiempo, :descripcion_lineatiempo)"
    values = {
        "id_proyecto": linea_tiempo.id_proyecto,
        "nombre_linea_tiempo": linea_tiempo.nombre_linea_tiempo,
        "descripcion_lineatiempo": linea_tiempo.descripcion_lineatiempo
    }
    
    await database.execute(query=query, values=values)
    return {"message": "Línea de tiempo creada exitosamente"}

#ENDPOINT PARA ACTUALIZAR UNA LINEA DE TIEMPO
@router.put("/lineas_tiempo/{id_linea_tiempo}", response_model=Dict[str, Any])
async def update_linea_tiempo(id_linea_tiempo: int, linea_tiempo: LineaTiempo, token: str = Depends(oauth2_scheme)):
    query = "UPDATE lineas_de_tiempo SET nombre_linea_tiempo = :nombre_linea_tiempo, descripcion_lineatiempo = :descripcion_lineatiempo WHERE id_linea_tiempo = :id_linea_tiempo"
    values = {
        "id_linea_tiempo": id_linea_tiempo,
        "nombre_linea_tiempo": linea_tiempo.nombre_linea_tiempo,
        "descripcion_lineatiempo": linea_tiempo.descripcion_lineatiempo
    }
    
    await database.execute(query=query, values=values)
    return {"message": "Línea de tiempo actualizada exitosamente"}

#ENDPOINT PARA ELIMINAR UNA LINEA DE TIEMPO
@router.delete("/lineas_tiempo/{id_linea_tiempo}")
async def delete_linea_tiempo(id_linea_tiempo: int, token: str = Depends(oauth2_scheme)):
    query = "DELETE FROM lineas_de_tiempo WHERE id_linea_tiempo = :id_linea_tiempo"
    values = {"id_linea_tiempo": id_linea_tiempo}
    
    await database.execute(query=query, values=values)
    return {"message": "Línea de tiempo eliminada exitosamente"}


#ENDPOINT PARA CONTAR EL NUMERO DE EVENTOS QUE TIENE UNA LINEA DE TIEMPO
@router.get("/lineas_tiempo/{id_linea_tiempo}/eventos/count", response_model=Dict[str, Any])
async def count_eventos_linea_tiempo(id_linea_tiempo: int, token: str = Depends(oauth2_scheme)):
    query = "SELECT COUNT(*) FROM eventos WHERE id_linea_tiempo = :id_linea_tiempo"
    values = {"id_linea_tiempo": id_linea_tiempo}
    
    count = await database.fetch_val(query=query, values=values)
    return {"ok": True, "content": {"count": count}}



