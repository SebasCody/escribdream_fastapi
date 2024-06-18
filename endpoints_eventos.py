from fastapi import APIRouter, Query, HTTPException, Depends
from fastapi.security import OAuth2PasswordBearer
from typing import List, Optional, Dict, Any
from datetime import datetime
from pydantic import BaseModel
from db_config import database

class Evento(BaseModel):
    id_evento: int
    id_linea_tiempo: int
    nombre_evento: str
    descripcion_evento: str
    fecha_creacion: datetime
    fecha_modificacion: datetime
    
    
router = APIRouter(
    prefix="/api/escribdream",
    tags=["eventos"]
)

oauth2_scheme = OAuth2PasswordBearer("/token")

#ENDPOINT PARA OBTENER TODOS LOS EVENTOS O FILTRARLOS POR DIFERENTES CAMPOS DE LA TABLA
@router.get("/eventos", response_model=Dict[str, Any])
async def get_eventos(
    token: str = Depends(oauth2_scheme),
    fecha_creacion: Optional[str] = None,
    fecha_modificacion: Optional[str] = None
):
    query = "SELECT * FROM eventos WHERE 1=1"
    values = {}

    if fecha_creacion:
        query += " AND DATE(fecha_creacion) = :fecha_creacion"
        values["fecha_creacion"] = fecha_creacion
    if fecha_modificacion:
        query += " AND DATE(fecha_modificacion) = :fecha_modificacion"
        values["fecha_modificacion"] = fecha_modificacion

    eventos = await database.fetch_all(query=query, values=values)
    return {"ok": True, "content": [dict(evento) for evento in eventos]}


#ENDPOINT PARA OBTENER UN EVENTO POR SU ID
@router.get("/eventos/{id_evento}", response_model=Dict[str, Any])
async def get_evento(id_evento: int, token: str = Depends(oauth2_scheme)):
    query = "SELECT * FROM eventos WHERE id_evento = :id_evento"
    values = {"id_evento": id_evento}
    
    evento = await database.fetch_one(query=query, values=values)
    if evento is None:
        raise HTTPException(status_code=404, detail="El evento no existe")
    return {"ok": True, "content": [dict(evento)]}



#ENDPOINT PARA OBTENER LOS EVENTOS DE UNA LINEA DE TIEMPO POR ID DE LINEA DE TIEMPO
@router.get("/eventos/linea_tiempo/{id_linea_tiempo}", response_model=Dict[str, Any])
async def get_eventos_linea_tiempo(id_linea_tiempo: int, token: str = Depends(oauth2_scheme)):
    query = "SELECT * FROM eventos WHERE id_linea_tiempo = :id_linea_tiempo"
    values = {"id_linea_tiempo": id_linea_tiempo}
    
    eventos = await database.fetch_all(query=query, values=values)
    if not eventos:
        raise HTTPException(status_code=404, detail="No hay eventos en la línea de tiempo")
    return {"ok": True, "content": [dict(evento) for evento in eventos]}



#ENDPOINT PARA CREAR UN EVENTO
@router.post("/eventos", response_model=Evento)
async def create_evento(evento: Evento, token: str = Depends(oauth2_scheme)):
    query = "INSERT INTO eventos (id_linea_tiempo, nombre_evento, descripcion_evento) VALUES (:id_linea_tiempo, :nombre_evento, :descripcion_evento)"
    values = {
        "id_linea_tiempo": evento.id_linea_tiempo,
        "nombre_evento": evento.nombre_evento,
        "descripcion_evento": evento.descripcion_evento
        
    }
    
    evento.id_evento = await database.execute(query=query, values=values)
    return evento

#ENDPOINT PARA ACTUALIZAR UN EVENTO
@router.put("/eventos/{id_evento}", response_model=Dict[str, Any])
async def update_evento(id_evento: int, evento: Evento, token: str = Depends(oauth2_scheme)):
    query = "UPDATE eventos SET nombre_evento = :nombre_evento, descripcion_evento = :descripcion_evento WHERE id_evento = :id_evento"
    values = {
        "id_evento": id_evento,
        "nombre_evento": evento.nombre_evento,
        "descripcion_evento": evento.descripcion_evento
    }
    
    await database.execute(query=query, values=values)
    return {"message": "Evento actualizado"}

#ENDPOINT PARA ELIMINAR UN EVENTO
@router.delete("/eventos/{id_evento}")
async def delete_evento(id_evento: int, token: str = Depends(oauth2_scheme)):
    query = "DELETE FROM eventos WHERE id_evento = :id_evento"
    values = {"id_evento": id_evento}
    
    await database.execute(query=query, values=values)
    return {"message": "Evento eliminado"}

