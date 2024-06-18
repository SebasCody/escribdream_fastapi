from fastapi import APIRouter, Query, HTTPException, Depends
from fastapi.security import OAuth2PasswordBearer
from typing import List, Optional, Dict, Any
from pydantic import BaseModel
from enum import Enum
import datetime
from db_config import database

router = APIRouter(
    prefix="/api/escribdream",
    tags=["secciones escaleta"]
)
oauth2_scheme = OAuth2PasswordBearer("/token")

class Seccion(BaseModel):
    id_seccion: Optional[int]
    id_escaleta: int
    nombre_seccion: str
    descripcion_seccion: Optional[str]
    fecha_creacion: Optional[datetime.datetime]
    fecha_modificacion: Optional[datetime.datetime]
    

#ENDPOINT PARA OBTENER TODAS LAS SECCIONES DE ESCALETAS DE LA BASE DE DATOS
@router.get("/secciones", response_model=Dict[str, Any])
async def get_secciones(
    token: str = Depends(oauth2_scheme),
    fecha_creacion: Optional[str] = Query(None),
    fecha_modificacion: Optional[str] = Query(None)

):
    query = "SELECT * FROM secciones_escaleta WHERE 1=1"
    values = {}
    if fecha_creacion:
        query += " AND DATE(fecha_creacion) = :fecha_creacion"
        values.update({"fecha_creacion": fecha_creacion})
    if fecha_modificacion:
        query += " AND DATE(fecha_modificacion) = :fecha_modificacion"
        values.update({"fecha_modificacion": fecha_modificacion})

    secciones = await database.fetch_all(query=query, values=values)
    if not secciones:
        raise HTTPException(status_code=404, detail="No se encontraron secciones de escaleta")
    #Devolvemos ok:True y un diccionario
    return {"ok": True, "content": [dict(seccion) for seccion in secciones]} 


#ENDPOINT PARA OBTENER UNA SECCION DE ESCALETAS POR SU ID
@router.get("/secciones/{id_seccion}", response_model=Dict[str, Any])
async def get_seccion(id_seccion: int, token: str = Depends(oauth2_scheme)):
    query = "SELECT * FROM secciones_escaleta WHERE id_seccion = :id_seccion"
    seccion = await database.fetch_one(query=query, values={"id_seccion": id_seccion})
    if not seccion:
        raise HTTPException(status_code=404, detail="La seccion de escaleta no existe")
    return {"ok": True, "content": dict(seccion)}


#ENDPOINT PARA CREAR UNA SECCION DE ESCALETAS
@router.post("/secciones")
async def create_seccion(seccion: Seccion, token: str = Depends(oauth2_scheme)):
    query = "INSERT INTO secciones_escaleta (id_escaleta, nombre_seccion, descripcion_seccion) VALUES (:id_escaleta, :nombre_seccion, :descripcion_seccion)"
    values = {
        "id_escaleta": seccion.id_escaleta,
        "nombre_seccion": seccion.nombre_seccion,
        "descripcion_seccion": seccion.descripcion_seccion
    }
    seccion.id_seccion = await database.execute(query=query, values=values)
    return seccion


#ENDPOINT PARA ACTUALIZAR UNA SECCION DE ESCALETAS
@router.put("/secciones/{id_seccion}")
async def update_seccion(id_seccion: int, seccion: Seccion, token: str = Depends(oauth2_scheme)):
    query = "UPDATE secciones_escaleta SET id_escaleta = :id_escaleta, nombre_seccion = :nombre_seccion, descripcion_seccion = :descripcion_seccion WHERE id_seccion = :id_seccion"
    values = {
        "id_seccion": id_seccion,
        "id_escaleta": seccion.id_escaleta,
        "nombre_seccion": seccion.nombre_seccion,
        "descripcion_seccion": seccion.descripcion_seccion
    }
    seccion.id_seccion = await database.execute(query=query, values=values)
    return seccion


#ENDPOINT PARA ELIMINAR UNA SECCION DE ESCALETAS
@router.delete("/secciones/{id_seccion}")
async def delete_seccion(id_seccion: int, token: str = Depends(oauth2_scheme)):
    query = "DELETE FROM secciones_escaleta WHERE id_seccion = :id_seccion"
    values = {"id_seccion": id_seccion}
    await database.execute(query=query, values=values)
    return {"message": "Seccion de escaleta eliminada correctamente"}


#ENDPOINT PARA OBTENER TODAS LAS SECCIONES DE ESCALETAS DE UNA ESCALETA POR SU ID
@router.get("/secciones/escaleta/{id_escaleta}", response_model=Dict[str, Any])
async def get_secciones_by_escaleta(id_escaleta: int, token: str = Depends(oauth2_scheme)):
    query = "SELECT * FROM secciones_escaleta WHERE id_escaleta = :id_escaleta"
    values = {"id_escaleta": id_escaleta}
    secciones = await database.fetch_all(query=query, values=values)
    return {"ok": True, "content": [dict(seccion) for seccion in secciones]}

#ENDPOINT PARA obtener todas las secciones de escaletas de una escaleta por fecha de creacion
@router.get("/secciones/escaleta/{id_escaleta}/fecha_creacion", response_model=Dict[str, Any])
async def get_secciones_by_escaleta_fecha_creacion(id_escaleta: int, fecha_creacion: str, token: str = Depends(oauth2_scheme)):
    query = "SELECT * FROM secciones_escaleta WHERE id_escaleta = :id_escaleta AND DATE(fecha_creacion) = :fecha_creacion"
    values = {"id_escaleta": id_escaleta, "fecha_creacion": fecha_creacion}
    secciones = await database.fetch_all(query=query, values=values)
    return {"ok": True, "content": [dict(seccion) for seccion in secciones]}


#ENDPOINT PARA obtener todas las secciones de escaletas de una escaleta por fecha de modificacion
@router.get("/secciones/escaleta/{id_escaleta}/fecha_modificacion", response_model=Dict[str, Any])
async def get_secciones_by_escaleta_fecha_modificacion(id_escaleta: int, fecha_modificacion: str, token: str = Depends(oauth2_scheme)):
    query = "SELECT * FROM secciones_escaleta WHERE id_escaleta = :id_escaleta AND DATE(fecha_modificacion) = :fecha_modificacion"
    values = {"id_escaleta": id_escaleta, "fecha_modificacion": fecha_modificacion}
    secciones = await database.fetch_all(query=query, values=values)
    return {"ok": True, "content": [dict(seccion) for seccion in secciones]}



#ENDPOINT PARA ELIMINAR TODAS LAS SECCIONES DE ESCALETAS DE UNA ESCALETA POR SU ID
@router.delete("/secciones/escaleta/{id_escaleta}")
async def delete_secciones_by_escaleta(id_escaleta: int, token: str = Depends(oauth2_scheme)):
    query = "DELETE FROM secciones_escaleta WHERE id_escaleta = :id_escaleta"
    values = {"id_escaleta": id_escaleta}
    await database.execute(query=query, values=values)
    return {"message": "Secciones de escaleta eliminadas correctamente"}