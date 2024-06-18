from fastapi import APIRouter, Query, HTTPException, Depends
from fastapi.security import OAuth2PasswordBearer
from typing import List, Optional, Dict, Any
from pydantic import BaseModel
from enum import Enum
import datetime
from db_config import database
from fastapi.middleware.cors import CORSMiddleware



class Mapa(BaseModel):
    id_mapa: int
    id_libro: int
    nombre_mapa: str
    descripcion_mapa: Optional[str]
    detalles_mapa: Optional[str]
    imagen_mapa: Optional[str]
    fecha_creacion: datetime.datetime
    fecha_modificacion: datetime.datetime


router = APIRouter(
    prefix="/api/escribdream",
    tags=["mapas"]
)

oauth2_scheme = OAuth2PasswordBearer("/token")


#ENDPOINT PARA OBTENER TODOS LOS MAPAS DE LA BASE DE DATOS O FILTRARLOS POR LOS CAMPOS DE LA TABLA
@router.get("/mapas/", response_model=Dict[str, Any])
async def get_mapas(
    token: str = Depends(oauth2_scheme),
    fecha_creacion: Optional[datetime.datetime] = None,
    fecha_modificacion: Optional[datetime.datetime] = None
):
    query = "SELECT * FROM mapas WHERE 1=1"
    values = {}

    if fecha_creacion:
        query += f" WHERE fecha_creacion = '{fecha_creacion}'"
    if fecha_modificacion:
        query += f" WHERE fecha_modificacion = '{fecha_modificacion}'"

    mapas = await database.fetch_all(query=query, values=values)
    if not mapas:
        raise HTTPException(status_code=404, detail="No se encontraron mapas con los filtros especificados")
    return {"ok": True, "content": [dict(mapa) for mapa in mapas]}



#Obtener el mapa de un libro por id_libro
@router.get("/mapa/libro/{id_libro}", response_model=Dict[str, Any])
async def get_mapas_by_id_libro(id_libro: int, token: str = Depends(oauth2_scheme)):
    query = "SELECT * FROM mapas WHERE id_libro = :id_libro"
    values = {"id_libro": id_libro}
    mapas = await database.fetch_all(query=query, values=values)
    if not mapas:
        raise HTTPException(status_code=404, detail="No se encontraron mapas con el id_libro especificado")
    return {"ok": True, "content": [dict(mapa) for mapa in mapas]}



#Obtener un mapa por id_mapa
@router.get("/mapa/{id_mapa}", response_model=Dict[str, Any])
async def get_mapa(id_mapa: int, token: str = Depends(oauth2_scheme)):
    query = "SELECT * FROM mapas WHERE id_mapa = :id_mapa"
    values = {"id_mapa": id_mapa}
    mapa = await database.fetch_one(query=query, values=values)
    if not mapa:
        raise HTTPException(status_code=404, detail="No se encontró un mapa con el id_mapa especificado")
    return {"ok": True, "content": dict(mapa)}


#ENDPOINT PARA CREAR UN MAPA
@router.post("/mapa/")
async def create_mapa(mapa: Mapa, token: str = Depends(oauth2_scheme)):
    query = "INSERT INTO mapas (id_libro, nombre_mapa, descripcion_mapa, detalles_mapa, imagen_mapa) VALUES (:id_libro, :nombre_mapa, :descripcion_mapa, :detalles_mapa, :imagen_mapa)"
    values = {
        "id_libro": mapa.id_libro,
        "nombre_mapa": mapa.nombre_mapa,
        "descripcion_mapa": mapa.descripcion_mapa,
        "detalles_mapa": mapa.detalles_mapa,
        "imagen_mapa": mapa.imagen_mapa
    }
    await database.execute(query=query, values=values)
    return {"message": "Mapa creado exitosamente"  }

#ENDPOINT PARA ACTUALIZAR UN MAPA
@router.put("/mapa/{id_mapa}")
async def update_mapa(id_mapa: int, mapa: Mapa, token: str = Depends(oauth2_scheme)):
    query = "UPDATE mapas SET id_libro = :id_libro, nombre_mapa = :nombre_mapa, descripcion_mapa = :descripcion_mapa, detalles_mapa = :detalles_mapa, imagen_mapa = :imagen_mapa WHERE id_mapa = :id_mapa"
    values = {
        "id_libro": mapa.id_libro,
        "nombre_mapa": mapa.nombre_mapa,
        "descripcion_mapa": mapa.descripcion_mapa,
        "detalles_mapa": mapa.detalles_mapa,
        "imagen_mapa": mapa.imagen_mapa,
        "id_mapa": id_mapa
    }
    await database.execute(query=query, values=values)
    return {"message": "Mapa actualizado exitosamente"}


#ENDPOINT PARA ELIMINAR UN MAPA
@router.delete("/mapa/{id_mapa}")
async def delete_mapa(id_mapa: int, token: str = Depends(oauth2_scheme)):
    query = "DELETE FROM mapas WHERE id_mapa = :id_mapa"
    values = {"id_mapa": id_mapa}
    await database.execute(query=query, values=values)
    return {"message": "Mapa eliminado exitosamente"}


