from fastapi import APIRouter, Query, HTTPException, Depends
from fastapi.security import OAuth2PasswordBearer
from typing import List, Optional, Dict, Any
from pydantic import BaseModel
from enum import Enum
import datetime
from db_config import database

router = APIRouter(
    prefix="/api/escribdream",
    tags=["escaletas"]
)

oauth2_scheme = OAuth2PasswordBearer("/token")


class EstadoEscaleta(str, Enum):
    borrador = "borrador"
    finalizado = "finalizado"

class Escaleta(BaseModel):
    id_escaleta: Optional[int]
    id_libro: int
    nombre_escaleta: str
    descripcion_escaleta: Optional[str]
    contenido_escaleta: str
    notas_escaleta: Optional[str]
    estado_escaleta: EstadoEscaleta = EstadoEscaleta.borrador
    fecha_creacion: Optional[datetime.datetime]
    fecha_modificacion: Optional[datetime.datetime]
    
    

#ENDPOINT PARA OBTENER TODAS LAS ESCALETAS DE LA BASE DE DATOS O FILTRARLAS POR LOS CAMPOS DE LA TABLA
@router.get("/escaletas", response_model=Dict[str, Any])
async def get_escaletas(
    token: str = Depends(oauth2_scheme),
    estado_escaleta: Optional[EstadoEscaleta] = Query(None),
    fecha_creacion: Optional[str] = Query(None),
    fecha_modificacion: Optional[str] = Query(None)
):
    
    query = "SELECT * FROM escaletas WHERE 1=1"
    values = {}
    

    if estado_escaleta:
        query += " AND estado_escaleta = :estado_escaleta"
        values["estado_escaleta"] = estado_escaleta
    if fecha_creacion:
        query += " AND DATE(fecha_creacion) = :fecha_creacion"
        values["fecha_creacion"] = fecha_creacion
    if fecha_modificacion:
        query += " AND DATE(fecha_modificacion) = :fecha_modificacion"
        values["fecha_modificacion"] = fecha_modificacion
    
    escaletas = await database.fetch_all(query=query, values=values)
    if not escaletas:
        raise HTTPException(status_code=404, detail="No se encontraron escaletas")
    return {"ok": True, "content": [dict(escaleta) for escaleta in escaletas]}




#Obtener todas las escaletas de un libro por id_libro
@router.get("/escaletas/libro/{id_libro}", response_model=Dict[str, Any])
async def get_escaletas_by_id_libro(id_libro: int, token: str = Depends(oauth2_scheme)):
    query = "SELECT * FROM escaletas WHERE id_libro = :id_libro"
    values = {"id_libro": id_libro}
    escaletas = await database.fetch_all(query=query, values=values)
    if not escaletas:
        raise HTTPException(status_code=404, detail="No se encontraron escaletas")
    return {"ok": True, "content": [dict(escaleta) for escaleta in escaletas]}




#Obtener todas las escaletas de un libro por fecha_creacion
@router.get("/escaletas/libro/{id_libro}/fecha_creacion/{fecha_creacion}", response_model=Dict[str, Any])
async def get_escaletas_by_fecha_creacion(id_libro: int, fecha_creacion: str, token: str = Depends(oauth2_scheme)):
    query = "SELECT * FROM escaletas WHERE id_libro = :id_libro AND DATE(fecha_creacion) = :fecha_creacion"
    values = {"id_libro": id_libro, "fecha_creacion": fecha_creacion}
    escaletas = await database.fetch_all(query=query, values=values)
    if not escaletas:
        raise HTTPException(status_code=404, detail="No se encontraron escaletas")
    return {"ok": True, "content": [dict(escaleta) for escaleta in escaletas]}




#Obtener todas las escaletas de un libro por fecha de modificacion
@router.get("/escaletas/libro/{id_libro}/fecha_modificacion/{fecha_modificacion}", response_model=Dict[str, Any])
async def get_escaletas_by_fecha_modificacion(id_libro: int, fecha_modificacion: str, token: str = Depends(oauth2_scheme)):
    query = "SELECT * FROM escaletas WHERE id_libro = :id_libro AND DATE(fecha_modificacion) = :fecha_modificacion"
    values = {"id_libro": id_libro, "fecha_modificacion": fecha_modificacion}
    escaletas = await database.fetch_all(query=query, values=values)
    if not escaletas:
        raise HTTPException(status_code=404, detail="No se encontraron escaletas")
    return {"ok": True, "content": [dict(escaleta) for escaleta in escaletas]}



#Obtener todas las escaletas de un libro por estado_escaleta
@router.get("/escaletas/libro/{id_libro}/estado/{estado_escaleta}", response_model=Dict[str, Any])
async def get_escaletas_by_estado(id_libro: int, estado_escaleta: EstadoEscaleta, token: str = Depends(oauth2_scheme)):
    query = "SELECT * FROM escaletas WHERE id_libro = :id_libro AND estado_escaleta = :estado_escaleta"
    values = {"id_libro": id_libro, "estado_escaleta": estado_escaleta}
    escaletas = await database.fetch_all(query=query, values=values)
    if not escaletas:
        raise HTTPException(status_code=404, detail="No se encontraron escaletas")
    return {"ok": True, "content": [dict(escaleta) for escaleta in escaletas]}




#Obtener una escaleta por id_escaleta
@router.get("/escaletas/{id_escaleta}", response_model=Dict[str, Any])
async def get_escaleta_by_id(id_escaleta: int, token: str = Depends(oauth2_scheme)):
    query = "SELECT * FROM escaletas WHERE id_escaleta = :id_escaleta"
    values = {"id_escaleta": id_escaleta}
    escaleta = await database.fetch_one(query=query, values=values)
    if not escaleta:
        raise HTTPException(status_code=404, detail="No se encontro la escaleta")
    return {"ok": True, "content": dict(escaleta)}



#Crear una escaleta
@router.post("/escaletas")
async def create_escaleta(escaleta: Escaleta, token: str = Depends(oauth2_scheme)):
    query = "INSERT INTO escaletas (id_libro, nombre_escaleta, descripcion_escaleta, contenido_escaleta, notas_escaleta, estado_escaleta) VALUES (:id_libro, :nombre_escaleta, :descripcion_escaleta, :contenido_escaleta, :notas_escaleta, :estado_escaleta)"
    values = escaleta.dict()
    await database.execute(query=query, values=values)
    return {"message": "Escaleta creada exitosamente"}

#Actualizar una escaleta
@router.put("/escaletas/{id_escaleta}")
async def update_escaleta(id_escaleta: int, escaleta: Escaleta, token: str = Depends(oauth2_scheme)):
    query = "UPDATE escaletas SET id_libro = :id_libro, nombre_escaleta = :nombre_escaleta, descripcion_escaleta = :descripcion_escaleta, contenido_escaleta = :contenido_escaleta, notas_escaleta = :notas_escaleta, estado_escaleta = :estado_escaleta WHERE id_escaleta = :id_escaleta"
    values = escaleta.dict()
    values["id_escaleta"] = id_escaleta
    await database.execute(query=query, values=values)
    return {"message": "Escaleta actualizada"}

#Eliminar una escaleta
@router.delete("/escaletas/{id_escaleta}")
async def delete_escaleta(id_escaleta: int, token: str = Depends(oauth2_scheme)):
    query = "DELETE FROM escaletas WHERE id_escaleta = :id_escaleta"
    values = {"id_escaleta": id_escaleta}
    await database.execute(query=query, values=values)
    return {"message": "Escaleta eliminada"}

#Eliminar todas las escaletas de un libro
@router.delete("/escaletas/libro/{id_libro}")
async def delete_escaletas_by_id_libro(id_libro: int, token: str = Depends(oauth2_scheme)):
    query = "DELETE FROM escaletas WHERE id_libro = :id_libro"
    values = {"id_libro": id_libro}
    await database.execute(query=query, values=values)
    return {"message": "Varias escaletas eliminadas"}

