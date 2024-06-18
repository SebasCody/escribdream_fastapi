from fastapi import APIRouter, Query, HTTPException, Depends
from fastapi.security import OAuth2PasswordBearer
from typing import List, Optional, Dict, Any
from pydantic import BaseModel
from enum import Enum
import datetime
from db_config import database

class Nota(BaseModel):
    id_nota: int
    id_libro: int
    titulo_nota: str
    contenido: str
    fecha_creacion: datetime.datetime
    fecha_modificacion: datetime.datetime

router = APIRouter(
    prefix="/api/escribdream",
    tags=["notas"]
)

oauth2_scheme = OAuth2PasswordBearer("/token")


#ENDPOINT PARA OBTENER TODAS LAS NOTAS DE LA BASE DE DATOS Y FILTRARLAS POR LOS CAMPOS DE LA TABLA NOTAS
@router.get("/notas/", response_model=Dict[str, Any])
async def get_notas(
    token: str = Depends(oauth2_scheme),
    fecha_creacion: Optional[str] = Query(None),
    fecha_modificacion: Optional[str] = Query(None),
):
    query = "SELECT * FROM notas WHERE 1=1"
    values = {}

    if fecha_creacion:
        query += " AND DATE(fecha_creacion) = :fecha_creacion"
        values["fecha_creacion"] = fecha_creacion
    if fecha_modificacion:
        query += " AND DATE(fecha_modificacion) = :fecha_modificacion"
        values["fecha_modificacion"] = fecha_modificacion
    
    notas = await database.fetch_all(query=query, values=values)
    if not notas:
        raise HTTPException(status_code=404, detail="No se encontraron notas con los parametros proporcionados")
    return {"ok": True, "content": [dict(nota) for nota in notas]}





#Obtener todas las notas de un libro
@router.get("/notas/libro/{id_libro}", response_model=Dict[str, Any])
async def get_notas_by_libro(id_libro: int, token: str = Depends(oauth2_scheme)):
    query = "SELECT * FROM notas WHERE id_libro = :id_libro"
    values = {"id_libro": id_libro}
    notas = await database.fetch_all(query=query, values=values)
    if not notas:
        raise HTTPException(status_code=404, detail="No se encontraron notas para el libro especificado")
    return {"ok": True, "content": [dict(nota) for nota in notas]}


#Obtener todas las notas de un libro por fecha_creacion
@router.get("/notas/libro/{id_libro}/fecha_creacion/{fecha_creacion}", response_model=Dict[str, Any])
async def get_notas_by_libro_fecha_creacion(id_libro: int, fecha_creacion: str, token: str = Depends(oauth2_scheme)):
    query = "SELECT * FROM notas WHERE id_libro = :id_libro AND DATE(fecha_creacion) = :fecha_creacion"
    values = {"id_libro": id_libro, "fecha_creacion": fecha_creacion}
    notas = await database.fetch_all(query=query, values=values)
    if not notas:
        raise HTTPException(status_code=404, detail="No se encontraron notas para el libro especificado y la fecha de creación proporcionada")
    return {"ok": True, "content": [dict(nota) for nota in notas]}


#Obtener todas las notas de un libro por fecha_modificacion
@router.get("/notas/libro/{id_libro}/fecha_modificacion/{fecha_modificacion}", response_model=Dict[str, Any])
async def get_notas_by_libro_fecha_modificacion(id_libro: int, fecha_modificacion: str, token: str = Depends(oauth2_scheme)):
    query = "SELECT * FROM notas WHERE id_libro = :id_libro AND DATE(fecha_modificacion) = :fecha_modificacion"
    values = {"id_libro": id_libro, "fecha_modificacion": fecha_modificacion}
    notas = await database.fetch_all(query=query, values=values)
    if not notas:
        raise HTTPException(status_code=404, detail="No se encontraron notas para el libro especificado y la fecha de modificación proporcionada")
    return {"ok": True, "content": [dict(nota) for nota in notas]}


#Obtener una nota por id_nota
@router.get("/nota/{id_nota}", response_model=Dict[str, Any])
async def get_nota_by_id(id_nota: int, token: str = Depends(oauth2_scheme)):
    query = "SELECT * FROM notas WHERE id_nota = :id_nota"
    values = {"id_nota": id_nota}
    nota = await database.fetch_one(query=query, values=values)
    if not nota:
        raise HTTPException(status_code=404, detail="No se encontró la nota con el id especificado")
    return {"ok": True, "content": [dict(nota)]}


#Crear una nota
@router.post("/notas/", response_model=Dict[str, Any])
async def create_nota(nota: Nota, token: str = Depends(oauth2_scheme)):
    query = "INSERT INTO notas (id_libro, titulo_nota, contenido) VALUES (:id_libro, :titulo_nota, :contenido)"
    values = {
        "id_libro": nota.id_libro,
        "titulo_nota": nota.titulo_nota,
        "contenido": nota.contenido
    }
    nota.id_nota = await database.execute(query=query, values=values)
    return {"message": "Nota creada exitosamente"}

#Actualizar una nota
@router.put("/notas/{id_nota}", response_model=Dict[str, Any])
async def update_nota(id_nota: int, nota: Nota, token: str = Depends(oauth2_scheme)):
    query = "UPDATE notas SET id_libro = :id_libro, titulo_nota = :titulo_nota, contenido = :contenido WHERE id_nota = :id_nota"
    values = {
        "id_nota": id_nota,
        "id_libro": nota.id_libro,
        "titulo_nota": nota.titulo_nota,
        "contenido": nota.contenido
    }
    await database.execute(query=query, values=values)
    return {"message: Nota actualizada exitosamente"}

#Eliminar una nota
@router.delete("/notas/{id_nota}")
async def delete_nota(id_nota: int, token: str = Depends(oauth2_scheme)):
    query = "DELETE FROM notas WHERE id_nota = :id_nota"
    values = {"id_nota": id_nota}
    await database.execute(query=query, values=values)
    return {"message": "Nota eliminada exitosamente"}

#Eliminar todas las notas de un libro
@router.delete("/notas/libro/{id_libro}")
async def delete_notas_by_libro(id_libro: int, token: str = Depends(oauth2_scheme)):
    query = "DELETE FROM notas WHERE id_libro = :id_libro"
    values = {"id_libro": id_libro}
    await database.execute(query=query, values=values)
    return {"message": "Notas eliminadas exitosamente"}

