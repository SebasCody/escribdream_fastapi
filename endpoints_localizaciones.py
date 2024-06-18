from fastapi import APIRouter, Query, HTTPException, Depends
from fastapi.security import OAuth2PasswordBearer
from typing import List, Optional, Dict, Any
from pydantic import BaseModel
from enum import Enum
import datetime
from db_config import database

class TipoTerrenoEnum(str, Enum):
    Bosque = 'Bosque'
    Montaña = 'Montaña'
    Ciudad = 'Ciudad'
    Aldea = 'Aldea'
    Castillo = 'Castillo'
    Cueva = 'Cueva'
    Lago = 'Lago'
    Mar = 'Mar'
    Río = 'Río'
    Desierto = 'Desierto'
    Pradera = 'Pradera'
    Pantano = 'Pantano'
    Ruinas = 'Ruinas'
    Templo = 'Templo'
    Otros = 'Otros'
    
class ClimaEnum(str, Enum):
    Templado = 'Templado'
    Frio = 'Frío'
    Calido = 'Cálido'
    Tropical = 'Tropical'
    Desertico = 'Desértico'
    Montañoso = 'Montañoso'
    Lluvioso = 'Lluvioso'
    Neblinoso = 'Neblinoso'
    Ventoso = 'Ventoso'
    Nevado = 'Nevado'
    Otros = 'Otros'
    
class PoblacioEnum(str, Enum):
    Alto = 'Alto'
    Medio = 'Medio'
    Bajo = 'Bajo'
    Deshabitado = 'Deshabitado'
    

class Localizacion(BaseModel):
    id_localizacion: int
    id_mapa: int
    nombre_localizacion: str
    ciudad: Optional[str]
    provincia: Optional[str]
    pais: Optional[str]
    descripcion_localizacion: Optional[str]
    tipo_terreno: Optional[TipoTerrenoEnum]
    clima: Optional[ClimaEnum]
    poblacion: Optional[PoblacioEnum]
    flora_fauna: Optional[str]
    caracteristicas_destacadas: Optional[str]
    leyendas_historias: Optional[str]
    fecha_creacion: Optional[datetime.datetime]
    fecha_modificacion: Optional[datetime.datetime]
    
router = APIRouter(
    prefix="/api/escribdream",
    tags=["localizaciones"]
)

oauth2_scheme = OAuth2PasswordBearer("/token")

    
#ENDPOINT PARA OBTENER TODAS LAS LOCALIZACIONES DE LA BASE DE DATOS O FILTRARLAS POR LOS CAMPOS DE LA TABLA
@router.get("/localizaciones/", response_model=Dict[str, Any])
async def get_localizaciones(
    token: str = Depends(oauth2_scheme),
    ciudad: Optional[str] = Query(None),
    provincia: Optional[str] = Query(None),
    pais: Optional[str] = Query(None),
    tipo_terreno: Optional[TipoTerrenoEnum] = Query(None),
    clima: Optional[ClimaEnum] = Query(None),
    poblacion: Optional[PoblacioEnum] = Query(None),
    fecha_creacion: Optional[str] = Query(None),
    fecha_modificacion: Optional[str] = Query(None),
):
    
    
    query = "SELECT * FROM localizaciones WHERE 1=1"
    values = {}
    
    if ciudad:
        query += " AND ciudad = :ciudad"
        values["ciudad"] = ciudad
    if provincia:
        query += " AND provincia = :provincia"
        values["provincia"] = provincia
    if pais:
        query += " AND pais = :pais"
        values["pais"] = pais
    if tipo_terreno:
        query += " AND tipo_terreno = :tipo_terreno"
        values["tipo_terreno"] = tipo_terreno
    if clima:
        query += " AND clima = :clima"
        values["clima"] = clima
    if poblacion:
        query += " AND poblacion = :poblacion"
        values["poblacion"] = poblacion
    if fecha_creacion:
        query += " AND DATE(fecha_creacion) = :fecha_creacion"
        values["fecha_creacion"] = fecha_creacion
    if fecha_modificacion:
        query += " AND DATE(fecha_modificacion) = :fecha_modificacion"

        
    localizaciones = await database.fetch_all(query=query, values=values)
    if not localizaciones:
        raise HTTPException(status_code=404, detail="No se encontraron localizaciones con los filtros especificados")
    return {"ok": True, "content": [dict(localizacion) for localizacion in localizaciones]}



#Obtener todas las localizaciones de un mapa
@router.get("/localizaciones/mapa/{id_mapa}", response_model=Dict[str, Any])
async def get_localizaciones_by_mapa(id_mapa: int, token: str = Depends(oauth2_scheme)):
    query = "SELECT * FROM localizaciones WHERE id_mapa = :id_mapa"
    values = {"id_mapa": id_mapa}
    localizaciones = await database.fetch_all(query=query, values=values)
    if not localizaciones:
        raise HTTPException(status_code=404, detail="No se encontraron localizaciones con el id de mapa especificado")
    return {"ok": True, "content": [dict(localizacion) for localizacion in localizaciones]}


#Obtener una localizacion por su id
@router.get("/localizaciones/{id_localizacion}", response_model=Dict[str, Any])
async def get_localizacion_by_id(id_localizacion: int, token: str = Depends(oauth2_scheme)):
    query = "SELECT * FROM localizaciones WHERE id_localizacion = :id_localizacion"
    values = {"id_localizacion": id_localizacion}
    localizacion = await database.fetch_one(query=query, values=values)
    if not localizacion:
        raise HTTPException(status_code=404, detail="No se encontró la localización con el id especificado")
    return {"ok": True, "content": dict(localizacion)}


#Crear una nueva localizacion
@router.post("/localizaciones/", response_model=Dict[str, Any])
async def create_localizacion(localizacion: Localizacion, token: str = Depends(oauth2_scheme)):
    query = """
        INSERT INTO localizaciones (id_mapa, nombre_localizacion, ciudad, provincia, pais, descripcion_localizacion, tipo_terreno, clima, poblacion, flora_fauna, caracteristicas_destacadas, leyendas_historias, fecha_creacion, fecha_modificacion)
        VALUES (:id_mapa, :nombre_localizacion, :ciudad, :provincia, :pais, :descripcion_localizacion, :tipo_terreno, :clima, :poblacion, :flora_fauna, :caracteristicas_destacadas, :leyendas_historias, :fecha_creacion, :fecha_modificacion)
    """
    values = {
        "id_mapa": localizacion.id_mapa,
        "nombre_localizacion": localizacion.nombre_localizacion,
        "ciudad": localizacion.ciudad,
        "provincia": localizacion.provincia,
        "pais": localizacion.pais,
        "descripcion_localizacion": localizacion.descripcion_localizacion,
        "tipo_terreno": localizacion.tipo_terreno,
        "clima": localizacion.clima,
        "poblacion": localizacion.poblacion,
        "flora_fauna": localizacion.flora_fauna,
        "caracteristicas_destacadas": localizacion.caracteristicas_destacadas,
        "leyendas_historias": localizacion.leyendas_historias,
        "fecha_creacion": datetime.datetime.now(),
        "fecha_modificacion": datetime.datetime.now()
    }
    
    await database.execute(query=query, values=values)
    return {"message": "Localizacion creada exitosamente"}

#Actualizar una localizacion
@router.put("/localizaciones/{id_localizacion}", response_model=Dict[str, Any])
async def update_localizacion(id_localizacion: int, localizacion: Localizacion, token: str = Depends(oauth2_scheme)):
    query = """
        UPDATE localizaciones SET
        id_mapa = :id_mapa,
        nombre_localizacion = :nombre_localizacion,
        ciudad = :ciudad,
        provincia = :provincia,
        pais = :pais,
        descripcion_localizacion = :descripcion_localizacion,
        tipo_terreno = :tipo_terreno,
        clima = :clima,
        poblacion = :poblacion,
        flora_fauna = :flora_fauna,
        caracteristicas_destacadas = :caracteristicas_destacadas,
        leyendas_historias = :leyendas_historias,
        fecha_modificacion = :fecha_modificacion
        WHERE id_localizacion = :id_localizacion
    """
    values = {
        "id_localizacion": id_localizacion,
        "id_mapa": localizacion.id_mapa,
        "nombre_localizacion": localizacion.nombre_localizacion,
        "ciudad": localizacion.ciudad,
        "provincia": localizacion.provincia,
        "pais": localizacion.pais,
        "descripcion_localizacion": localizacion.descripcion_localizacion,
        "tipo_terreno": localizacion.tipo_terreno,
        "clima": localizacion.clima,
        "poblacion": localizacion.poblacion,
        "flora_fauna": localizacion.flora_fauna,
        "caracteristicas_destacadas": localizacion.caracteristicas_destacadas,
        "leyendas_historias": localizacion.leyendas_historias,
        "fecha_modificacion": datetime.datetime.now()
    }
    await database.execute(query=query, values=values)
    response = {
        "id_localizacion": id_localizacion,
        **values
    }
    return {"message": "Localizacion actualizada exitosamente", "content": response}

#Eliminar una localizacion
@router.delete("/localizaciones/{id_localizacion}", response_model=Dict[str, Any])
async def delete_localizacion(id_localizacion: int, token: str = Depends(oauth2_scheme)):
    query = "DELETE FROM localizaciones WHERE id_localizacion = :id_localizacion"
    values = {"id_localizacion": id_localizacion}
    await database.execute(query=query, values=values)
    return {"message": "Localizacion eliminada satisfactoriamente"}

