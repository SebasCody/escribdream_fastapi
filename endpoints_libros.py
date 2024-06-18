from fastapi import APIRouter, Query, HTTPException, Depends
from fastapi.security import OAuth2PasswordBearer
from typing import List, Optional, Dict, Any
from pydantic import BaseModel
from enum import Enum
import datetime
from db_config import database, connectToDatabase, closeConnection, getAllUsers

class GeneroLibro(str, Enum):
    fantasia = 'fantasia'
    ciencia_ficcion = 'ciencia_ficcion'
    terror = 'terror'
    romance = 'romance'
    drama = 'drama'
    misterio = 'misterio'
    aventura = 'aventura'
    historico = 'historico'
    otros = 'otros'
    
class EstadoLibro(str, Enum):
    borrador = 'borrador'
    finalizado = 'finalizado'

class Libro(BaseModel):
    id_proyecto: int
    titulo_libro: str
    genero_libro: GeneroLibro
    descripcion_libro: Optional[str] = None
    imagen_portada: Optional[str] = None
    estado_libro: EstadoLibro = EstadoLibro.borrador
    fecha_creacion: Optional[datetime.datetime] = None
    fecha_modificacion: Optional[datetime.datetime] = None
    fecha_finalizacion: Optional[datetime.datetime] = None
    
router = APIRouter(
    prefix="/api/escribdream",
    tags=["libros"]
)

oauth2_scheme = OAuth2PasswordBearer("/token")

#ENDPOINT PARA OBTENER TODOS LOS LIBROS DE LA BASE DE DATOS O FILTRARLOS POR DIFERENTES CAMPOS DE LA TABLA
@router.get("/libros", response_model=Dict[str, Any])
async def get_libros(
    token: str = Depends(oauth2_scheme),
    genero_libro: Optional[GeneroLibro] = None,
    estado_libro: Optional[EstadoLibro] = None,
    fecha_creacion: Optional[datetime.datetime] = None,
    fecha_modificacion: Optional[datetime.datetime] = None,
    fecha_finalizacion: Optional[datetime.datetime] = None,
):
    query = "SELECT libros.id_libro, libros.id_proyecto, libros.titulo_libro, libros.genero_libro, libros.descripcion_libro, libros.imagen_portada, libros.estado_libro, libros.fecha_creacion, libros.fecha_modificacion, libros.fecha_finalizacion, proyectos.nombre_proyecto, proyectos.tipo_proyecto, usuarios.nombre_usuario as autor, usuarios.seudonimo FROM libros LEFT JOIN proyectos ON libros.id_proyecto = proyectos.id_proyecto LEFT JOIN usuarios ON proyectos.id_usuario = usuarios.id_usuario WHERE 1=1"
    values = {}
    
    if genero_libro:
        query += " AND genero_libro = :genero_libro"
        values['genero_libro'] = genero_libro
    if estado_libro:
        query += " AND estado_libro = :estado_libro"
        values['estado_libro'] = estado_libro
    if fecha_creacion:
        query += " AND fecha_creacion = :fecha_creacion"
        values['fecha_creacion'] = fecha_creacion
    if fecha_modificacion:
        query += " AND fecha_modificacion = :fecha_modificacion"
        values['fecha_modificacion'] = fecha_modificacion
    if fecha_finalizacion:
        query += " AND fecha_finalizacion = :fecha_finalizacion"
        values['fecha_finalizacion'] = fecha_finalizacion
    
    libros = await database.fetch_all(query=query, values=values)
    if not libros:
        raise HTTPException(status_code=404, detail="No se encontraron libros con los filtros especificados")
    return {"ok": True, "content": [dict(libro) for libro in libros]}



#----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------

#Obtener todos los libros de la bbdd por id_proyecto
@router.get("/libros/proyecto/{id_proyecto}", response_model=Dict[str, Any])
async def get_libros_by_id_proyecto(id_proyecto: int, token: str = Depends(oauth2_scheme)):
    query = "SELECT libros.id_libro, libros.id_proyecto, libros.titulo_libro, libros.genero_libro, libros.descripcion_libro, libros.imagen_portada, libros.estado_libro, libros.fecha_creacion, libros.fecha_modificacion, libros.fecha_finalizacion, proyectos.nombre_proyecto, proyectos.tipo_proyecto, usuarios.nombre_usuario as autor, usuarios.seudonimo FROM libros LEFT JOIN proyectos ON libros.id_proyecto = proyectos.id_proyecto LEFT JOIN usuarios ON proyectos.id_usuario = usuarios.id_usuario WHERE libros.id_proyecto = :id_proyecto"
    values = {"id_proyecto": id_proyecto}
    libros = await database.fetch_all(query=query, values=values)
    if not libros:
        raise HTTPException(status_code=404, detail="No se encontraron libros con el id_proyecto especificado")
    return {"ok": True, "content": [dict(libro) for libro in libros]}



#Obtener todos los libros de un proyecto por genero_libro
@router.get("/libros/proyecto/{id_proyecto}/genero/{genero_libro}", response_model=Dict[str, Any])
async def get_libros_by_id_proyecto_and_genero_libro(id_proyecto: int, genero_libro: GeneroLibro, token: str = Depends(oauth2_scheme)):
    query = "SELECT libros.id_libro, libros.id_proyecto, libros.titulo_libro, libros.genero_libro, libros.descripcion_libro, libros.imagen_portada, libros.estado_libro, libros.fecha_creacion, libros.fecha_modificacion, libros.fecha_finalizacion, proyectos.nombre_proyecto, proyectos.tipo_proyecto, usuarios.nombre_usuario as autor, usuarios.seudonimo FROM libros LEFT JOIN proyectos ON libros.id_proyecto = proyectos.id_proyecto LEFT JOIN usuarios ON proyectos.id_usuario = usuarios.id_usuario WHERE libros.id_proyecto = :id_proyecto AND genero_libro = :genero_libro"
    values = {"id_proyecto": id_proyecto, "genero_libro": genero_libro}
    libros = await database.fetch_all(query=query, values=values)
    if not libros:
        raise HTTPException(status_code=404, detail="No se encontraron libros con el id_proyecto y genero_libro especificados")
    return {"ok": True, "content": [dict(libro) for libro in libros]}


#Obtener todos los libros de un proyecto por estado_libro
@router.get("/libros/proyecto/{id_proyecto}/estado/{estado_libro}", response_model=Dict[str, Any])
async def get_libros_by_id_proyecto_and_estado_libro(id_proyecto: int, estado_libro: EstadoLibro, token: str = Depends(oauth2_scheme)):
    query = "SELECT  libros.id_libro, libros.id_proyecto, libros.titulo_libro, libros.genero_libro, libros.descripcion_libro, libros.imagen_portada, libros.estado_libro, libros.fecha_creacion, libros.fecha_modificacion, libros.fecha_finalizacion, proyectos.nombre_proyecto, proyectos.tipo_proyecto, usuarios.nombre_usuario as autor, usuarios.seudonimo FROM libros LEFT JOIN proyectos ON libros.id_proyecto = proyectos.id_proyecto  LEFT JOIN usuarios  ON proyectos.id_usuario = usuarios.id_usuario WHERE libros.id_proyecto = :id_proyecto AND estado_libro = :estado_libro"
    values = {"id_proyecto": id_proyecto, "estado_libro": estado_libro}
    libros = await database.fetch_all(query=query, values=values)
    if not libros:
        raise HTTPException(status_code=404, detail="No se encontraron libros con el id_proyecto y estado_libro especificados")
    return {"ok": True, "content": [dict(libro) for libro in libros]}



#Obtener todos los libros de un proyecto por fecha_creacion
@router.get("/libros/proyecto/{id_proyecto}/fecha_creacion/{fecha_creacion}", response_model=Dict[str, Any])
async def get_libros_by_id_proyecto_and_fecha_creacion(id_proyecto: int, fecha_creacion: datetime.datetime, token: str = Depends(oauth2_scheme)):
    query = "SELECT libros.id_libro, libros.id_proyecto, libros.titulo_libro, libros.genero_libro, libros.descripcion_libro, libros.imagen_portada, libros.estado_libro, libros.fecha_creacion, libros.fecha_modificacion, libros.fecha_finalizacion, proyectos.nombre_proyecto, proyectos.tipo_proyecto, usuarios.nombre_usuario as autor, usuarios.seudonimo FROM libros LEFT JOIN proyectos ON libros.id_proyecto = proyectos.id_proyecto LEFT JOIN usuarios ON proyectos.id_usuario = usuarios.id_usuario WHERE libros.id_proyecto = :id_proyecto AND fecha_creacion = :fecha_creacion"
    values = {"id_proyecto": id_proyecto, "fecha_creacion": fecha_creacion}
    libros = await database.fetch_all(query=query, values=values)
    if not libros:
        raise HTTPException(status_code=404, detail="No se encontraron libros con el id_proyecto y fecha_creacion especificados")
    return {"ok": True, "content": [dict(libro) for libro in libros]}


#Obtener todos los libros de un proyecto por fecha_modificacion
@router.get("/libros/proyecto/{id_proyecto}/fecha_modificacion/{fecha_modificacion}", response_model=Dict[str, Any])
async def get_libros_by_id_proyecto_and_fecha_modificacion(id_proyecto: int, fecha_modificacion: datetime.datetime, token: str = Depends(oauth2_scheme)):
    query = "SELECT libros.id_libro, libros.id_proyecto, libros.titulo_libro, libros.genero_libro, libros.descripcion_libro, libros.imagen_portada, libros.estado_libro, libros.fecha_creacion, libros.fecha_modificacion, libros.fecha_finalizacion, proyectos.nombre_proyecto, proyectos.tipo_proyecto, usuarios.nombre_usuario as autor, usuarios.seudonimo FROM libros LEFT JOIN proyectos ON libros.id_proyecto = proyectos.id_proyecto LEFT JOIN usuarios ON proyectos.id_usuario = usuarios.id_usuario WHERE libros.id_proyecto = :id_proyecto AND fecha_modificacion = :fecha_modificacion"
    values = {"id_proyecto": id_proyecto, "fecha_modificacion": fecha_modificacion}
    libros = await database.fetch_all(query=query, values=values)
    if not libros:
        raise HTTPException(status_code=404, detail="No se encontraron libros con el id_proyecto y fecha_modificacion especificados")
    return {"ok": True, "content": [dict(libro) for libro in libros]}


#Obtener todos los libros de un proyecto por fecha_finalizacion
@router.get("/libros/proyecto/{id_proyecto}/fecha_finalizacion/{fecha_finalizacion}", response_model=Dict[str, Any])
async def get_libros_by_id_proyecto_and_fecha_finalizacion(id_proyecto: int, fecha_finalizacion: datetime.datetime, token: str = Depends(oauth2_scheme)):
    query = "SELECT libros.id_libro, libros.id_proyecto, libros.titulo_libro, libros.genero_libro, libros.descripcion_libro, libros.imagen_portada, libros.estado_libro, libros.fecha_creacion, libros.fecha_modificacion, libros.fecha_finalizacion, proyectos.nombre_proyecto, proyectos.tipo_proyecto, usuarios.nombre_usuario as autor, usuarios.seudonimo FROM libros LEFT JOIN proyectos ON libros.id_proyecto = proyectos.id_proyecto LEFT JOIN usuarios ON proyectos.id_usuario = usuarios.id_usuario WHERE libros.id_proyecto = :id_proyecto AND fecha_finalizacion = :fecha_finalizacion"
    values = {"id_proyecto": id_proyecto, "fecha_finalizacion": fecha_finalizacion}
    libros = await database.fetch_all(query=query, values=values)
    if not libros:
        raise HTTPException(status_code=404, detail="No se encontraron libros con el id_proyecto y fecha_finalizacion especificados")
    return {"ok": True, "content": [dict(libro) for libro in libros]}


#----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------

#Obtener todos los libros de la bbdd por id_usuario
@router.get("/libros/usuario/{id_usuario}", response_model=Dict[str, Any])
async def get_libros_by_id_usuario(id_usuario: int, token: str = Depends(oauth2_scheme)):
    query = "SELECT libros.id_libro, libros.id_proyecto, libros.titulo_libro, libros.genero_libro, libros.descripcion_libro, libros.imagen_portada, libros.estado_libro, libros.fecha_creacion, libros.fecha_modificacion, libros.fecha_finalizacion, proyectos.nombre_proyecto, proyectos.tipo_proyecto, usuarios.nombre_usuario as autor, usuarios.seudonimo FROM libros LEFT JOIN proyectos ON libros.id_proyecto = proyectos.id_proyecto LEFT JOIN usuarios ON proyectos.id_usuario = usuarios.id_usuario WHERE usuarios.id_usuario = :id_usuario"
    values = {"id_usuario": id_usuario}
    libros = await database.fetch_all(query=query, values=values)
    if not libros:
        raise HTTPException(status_code=404, detail="No se encontraron libros con el id_usuario especificado")
    return {"ok": True, "content": [dict(libro) for libro in libros]}


#Obtener todos los libros de un usuario por genero_libro
@router.get("/libros/usuario/{id_usuario}/genero/{genero_libro}", response_model=Dict[str, Any])
async def get_libros_by_id_usuario_and_genero_libro(id_usuario: int, genero_libro: GeneroLibro, token: str = Depends(oauth2_scheme)):
    query = "SELECT libros.id_libro, libros.id_proyecto, libros.titulo_libro, libros.genero_libro, libros.descripcion_libro, libros.imagen_portada, libros.estado_libro, libros.fecha_creacion, libros.fecha_modificacion, libros.fecha_finalizacion, proyectos.nombre_proyecto, proyectos.tipo_proyecto, usuarios.nombre_usuario as autor, usuarios.seudonimo FROM libros LEFT JOIN proyectos ON libros.id_proyecto = proyectos.id_proyecto LEFT JOIN usuarios ON proyectos.id_usuario = usuarios.id_usuario WHERE usuarios.id_usuario = :id_usuario AND genero_libro = :genero_libro"
    values = {"id_usuario": id_usuario, "genero_libro": genero_libro}
    libros = await database.fetch_all(query=query, values=values)
    if not libros:
        raise HTTPException(status_code=404, detail="No se encontraron libros con el id_usuario y genero_libro especificados")
    return {"ok": True, "content": [dict(libro) for libro in libros]}


#Obtener todos los libros de un usuario por estado_libro
@router.get("/libros/usuario/{id_usuario}/estado/{estado_libro}", response_model=Dict[str, Any])
async def get_libros_by_id_usuario_and_estado_libro(id_usuario: int, estado_libro: EstadoLibro, token: str = Depends(oauth2_scheme)):
    query = "SELECT libros.id_libro, libros.id_proyecto, libros.titulo_libro, libros.genero_libro, libros.descripcion_libro, libros.imagen_portada, libros.estado_libro, libros.fecha_creacion, libros.fecha_modificacion, libros.fecha_finalizacion, proyectos.nombre_proyecto, proyectos.tipo_proyecto, usuarios.nombre_usuario as autor, usuarios.seudonimo FROM libros LEFT JOIN proyectos ON libros.id_proyecto = proyectos.id_proyecto LEFT JOIN usuarios ON proyectos.id_usuario = usuarios.id_usuario WHERE usuarios.id_usuario = :id_usuario AND estado_libro = :estado_libro"
    values = {"id_usuario": id_usuario, "estado_libro": estado_libro}
    libros = await database.fetch_all(query=query, values=values)
    if not libros:
        raise HTTPException(status_code=404, detail="No se encontraron libros con el id_usuario y estado_libro especificados")
    return {"ok": True, "content": [dict(libro) for libro in libros]}



#----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------


#Obtener un libro por id_libro
@router.get("/libros/{id_libro}", response_model=Dict[str, Any])
async def get_libro(id_libro: int, token: str = Depends(oauth2_scheme)):
    query = "SELECT libros.id_libro, libros.id_proyecto, libros.titulo_libro, libros.genero_libro, libros.descripcion_libro, libros.imagen_portada, libros.estado_libro, libros.fecha_creacion, libros.fecha_modificacion, libros.fecha_finalizacion, proyectos.nombre_proyecto, proyectos.tipo_proyecto, usuarios.nombre_usuario as autor, usuarios.seudonimo FROM libros LEFT JOIN proyectos ON libros.id_proyecto = proyectos.id_proyecto LEFT JOIN usuarios ON proyectos.id_usuario = usuarios.id_usuario WHERE libros.id_libro = :id_libro"
    values = {"id_libro": id_libro}
    libro = await database.fetch_one(query=query, values=values)
    if not libro:
        raise HTTPException(status_code=404, detail="No se encontró un libro con el id_libro especificado")
    return {"ok": True, "content": dict(libro)}



#Crear un libro
#Base model para CreateLibro
class NewLibro(BaseModel):
    id_proyecto: int
    titulo_libro: str
    genero_libro: GeneroLibro
    descripcion_libro: Optional[str] = None
    imagen_portada: Optional[str] = None

@router.post("/libros", response_model=Dict[str, Any])
async def create_libro(libro: NewLibro, token: str = Depends(oauth2_scheme)):
    query = """
        INSERT INTO libros (id_proyecto, titulo_libro, genero_libro, descripcion_libro, imagen_portada)
        VALUES (:id_proyecto, :titulo_libro, :genero_libro, :descripcion_libro, :imagen_portada)
    """
    values = {
        "id_proyecto": libro.id_proyecto,
        "titulo_libro": libro.titulo_libro,
        "genero_libro": libro.genero_libro,
        "descripcion_libro": libro.descripcion_libro,
        "imagen_portada": libro.imagen_portada,
    }
    
    id_libro = await database.execute(query=query, values=values)
    return {"message": "Libro creado exitosamente", "id_libro": id_libro}
    

#Actualizar un libro
def get_libro_by_id(id_libro):
    connection = connectToDatabase()
    cursor = connection.cursor(dictionary=True)
    cursor.execute("SELECT titulo_libro, genero_libro, descripcion_libro, estado_libro, imagen_portada FROM libros WHERE id_libro = %s", (id_libro,))
    result = cursor.fetchone()
    closeConnection(connection)
    return result

class UpdateLibro(BaseModel):
    titulo_libro: str
    genero_libro: Optional[GeneroLibro] = None
    descripcion_libro: Optional[str] = None
    imagen_portada: Optional[str] = None
    estado_libro: EstadoLibro = EstadoLibro.borrador

@router.put("/libros/{id_libro}")
async def update_libro(id_libro: int, libroToUpdate: UpdateLibro, token: str = Depends(oauth2_scheme)):
    libro = get_libro_by_id(id_libro)
    if libro is None:
        raise HTTPException(status_code=404, detail="Libro no encontrado.")
    
    fields = []
    values = {"id_libro": id_libro}
    
    if libroToUpdate.titulo_libro is not None:
        fields.append("titulo_libro = :titulo_libro")
        values["titulo_libro"] = libroToUpdate.titulo_libro
    if libroToUpdate.genero_libro is not None:
        fields.append("genero_libro = :genero_libro")
        values["genero_libro"] = libroToUpdate.genero_libro
    if libroToUpdate.descripcion_libro is not None:
        fields.append("descripcion_libro = :descripcion_libro")
        values["descripcion_libro"] = libroToUpdate.descripcion_libro
    if libroToUpdate.imagen_portada is not None:
        fields.append("imagen_portada = :imagen_portada")
        values["imagen_portada"] = libroToUpdate.imagen_portada
    if libroToUpdate.estado_libro is not None:
        fields.append("estado_libro = :estado_libro")
        values["estado_libro"] = libroToUpdate.estado_libro
        
    if not fields:
        raise HTTPException(status_code=400, detail="No hay datos para actualizar.")
    
    query = f"UPDATE libros SET {', '.join(fields)} WHERE id_libro = :id_libro"
    
    await database.execute(query=query, values=values)
    return {"message": "Libro actualizado exitosamente."}

#Eliminar un libro
@router.delete("/libros/{id_libro}")
async def delete_libro(id_libro: int, token: str = Depends(oauth2_scheme)):
    query = "DELETE FROM libros WHERE id_libro = :id_libro"
    values = {"id_libro": id_libro}
    await database.execute(query=query, values=values)
    return {"message": "Libro eliminado exitosamente"}

