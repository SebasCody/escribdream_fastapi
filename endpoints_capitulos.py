from io import BytesIO
from fastapi import APIRouter, Query, HTTPException, Depends
from fastapi.responses import FileResponse
from fastapi.security import OAuth2PasswordBearer
from typing import List, Optional, Dict, Any
from pydantic import BaseModel
from enum import Enum
import datetime
from db_config import database
import pdfkit
import tempfile
import os
import json
import subprocess


router = APIRouter(
    prefix="/api/escribdream",
    tags=["capitulos"]
)

oauth2_scheme = OAuth2PasswordBearer("/token")


class EstadoCapituloEnum(str, Enum):
    Primer_borrador = "Primer borrador"
    Segundo_borrador = "Segundo borrador"
    Tercer_borrador = "Tercer borrador"
    Cuarto_borrador = "Cuarto borrador"
    Quinto_borrador = "Quinto borrador"
    Finalizado = "Finalizado"
    

class Capitulo(BaseModel):
    id_capitulo: Optional[int]
    id_libro: int
    numero_capitulo: int
    titulo_capitulo: str
    contenido_capitulo: Optional[str]
    estado_capitulo: Optional[EstadoCapituloEnum]
    fecha_creacion: Optional[datetime.datetime]
    fecha_modificacion: Optional[datetime.datetime]
    

#ENDPOINT PARA OBTENER TODOS LOS CAPITULOS DE LA BASE DE DATOS
@router.get("/capitulos", response_model=Dict[str, Any])
async def get_capitulos(
    token: str = Depends(oauth2_scheme),
    estado_capitulo: Optional[EstadoCapituloEnum] = Query(None),
    fecha_creacion: Optional[str] = Query(None),
    fecha_modificacion: Optional[str] = Query(None)
):
    query = "SELECT * FROM capitulos WHERE 1=1"
    values = {}

    if estado_capitulo:
        query += " AND estado_capitulo = :estado_capitulo"
        values.update({"estado_capitulo": estado_capitulo})
    if fecha_creacion:
        query += " AND DATE(fecha_creacion) = :fecha_creacion"
        values.update({"fecha_creacion": fecha_creacion})
    if fecha_modificacion:
        query += " AND DATE(fecha_modificacion) = :fecha_modificacion"
        values.update({"fecha_modificacion": fecha_modificacion})

    capitulos = await database.fetch_all(query=query, values=values)
    if not capitulos:
        raise HTTPException(status_code=404, detail="No se encontraron capitulos")
    return {"ok": True, "content": [dict(capitulo) for capitulo in capitulos]}



#Obtener todos los capítulos de un libro por id_libro
@router.get("/capitulos/libro/{id_libro}", response_model=Dict[str, Any])
async def get_capitulos_libro(id_libro: int, token: str = Depends(oauth2_scheme)):
    query = "SELECT * FROM capitulos WHERE id_libro = :id_libro"
    values = {"id_libro": id_libro}
    capitulos = await database.fetch_all(query=query, values=values)
    if not capitulos:
        raise HTTPException(status_code=404, detail="No se encontraron capitulos")
    return {"ok": True, "content": [dict(capitulo) for capitulo in capitulos]}


#Obtener todos los capítulos de un libro por estado_capitulo
@router.get("/capitulos/libro/{id_libro}/estado/{estado_capitulo}", response_model=Dict[str, Any])
async def get_capitulos_libro_estado(id_libro: int, estado_capitulo: EstadoCapituloEnum, token: str = Depends(oauth2_scheme)):
    query = "SELECT * FROM capitulos WHERE id_libro = :id_libro AND estado_capitulo = :estado_capitulo"
    values = {"id_libro": id_libro, "estado_capitulo": estado_capitulo}
    capitulos = await database.fetch_all(query=query, values=values)
    if not capitulos:
        raise HTTPException(status_code=404, detail="No se encontraron capitulos")
    return {"ok": True, "content": [dict(capitulo) for capitulo in capitulos]}


#Obtener todos los capítulos de un libro por numero_capitulo
@router.get("/capitulos/libro/{id_libro}/numero/{numero_capitulo}", response_model=Dict[str, Any])
async def get_capitulos_libro_numero(id_libro: int, numero_capitulo: int, token: str = Depends(oauth2_scheme)):
    query = "SELECT * FROM capitulos WHERE id_libro = :id_libro AND numero_capitulo = :numero_capitulo"
    values = {"id_libro": id_libro, "numero_capitulo": numero_capitulo}
    capitulos = await database.fetch_all(query=query, values=values)
    if not capitulos:
        raise HTTPException(status_code=404, detail="No se encontraron capitulos")
    return {"ok": True, "content": [dict(capitulo) for capitulo in capitulos]}


#Obtener todos los capítulos de un libro por fecha_creacion
@router.get("/capitulos/libro/{id_libro}/fecha_creacion/{fecha_creacion}", response_model=Dict[str, Any])
async def get_capitulos_libro_fecha_creacion(id_libro: int, fecha_creacion: str, token: str = Depends(oauth2_scheme)):
    query = "SELECT * FROM capitulos WHERE id_libro = :id_libro AND DATE(fecha_creacion) = :fecha_creacion"
    values = {"id_libro": id_libro, "fecha_creacion": fecha_creacion}
    capitulos = await database.fetch_all(query=query, values=values)
    if not capitulos:
        raise HTTPException(status_code=404, detail="No se encontraron capitulos")
    return {"ok": True, "content": [dict(capitulo) for capitulo in capitulos]}


#Obtener todos los capítulos de un libro por fecha_modificacion
@router.get("/capitulos/libro/{id_libro}/fecha_modificacion/{fecha_modificacion}", response_model=Dict[str, Any])
async def get_capitulos_libro_fecha_modificacion(id_libro: int, fecha_modificacion: str, token: str = Depends(oauth2_scheme)):
    query = "SELECT * FROM capitulos WHERE id_libro = :id_libro AND DATE(fecha_modificacion) = :fecha_modificacion"
    values = {"id_libro": id_libro, "fecha_modificacion": fecha_modificacion}
    capitulos = await database.fetch_all(query=query, values=values)
    if not capitulos:
        raise HTTPException(status_code=404, detail="No se encontraron capitulos")
    return {"ok": True, "content": [dict(capitulo) for capitulo in capitulos]}


#Obtener un capítulo por id_capitulo
@router.get("/capitulos/{id_capitulo}", response_model=Dict[str, Any])
async def get_capitulo(id_capitulo: int, token: str = Depends(oauth2_scheme)):
    query = "SELECT * FROM capitulos WHERE id_capitulo = :id_capitulo"
    values = {"id_capitulo": id_capitulo}
    capitulo = await database.fetch_one(query=query, values=values)
    if not capitulo:
        raise HTTPException(status_code=404, detail="No se encontró el capítulo")
    return {"ok": True, "content": dict(capitulo)}



#ENDPOINT PARA CREAR UN NUEVO CAPITULO

#Base model para crear un capítulo
class CreateCapitulo(BaseModel):
    id_libro: int
    numero_capitulo: int
    titulo_capitulo: str



@router.post("/capitulos", response_model=Dict[str, Any])
async def create_capitulo(capitulo: CreateCapitulo, token: str = Depends(oauth2_scheme)):
    query = """
        INSERT INTO capitulos (id_libro, numero_capitulo, titulo_capitulo)
        VALUES (:id_libro, :numero_capitulo, :titulo_capitulo)
    """
    values = {
        "id_libro": capitulo.id_libro,
        "numero_capitulo": capitulo.numero_capitulo,
        "titulo_capitulo": capitulo.titulo_capitulo
    }
    id_capitulo = await database.execute(query=query, values=values)
    return {"message": "Capítulo creado correctamente"}



#ENDPOINT PARA ACTUALIZAR UN CAPITULO
class UpdateCapitulo(BaseModel):
    id_libro: Optional[int] = None
    numero_capitulo: Optional[int] = None
    titulo_capitulo: Optional[str] = None
    contenido_capitulo: Optional[str] = None
    estado_capitulo: Optional[EstadoCapituloEnum] = None

#ENDPOINT PARA ACTUALIZAR UNO O VARIOS DATOS D UN CAPITULO
@router.put("/capitulos/{id_capitulo}", response_model=Dict[str, Any])
async def update_capitulo(id_capitulo: int, capitulo: UpdateCapitulo, token: str = Depends(oauth2_scheme)):
    
    #Verificar si el capítulo existe
    capitulo_db = await database.fetch_one(query="SELECT * FROM capitulos WHERE id_capitulo = :id_capitulo", values={"id_capitulo": id_capitulo})
    if not capitulo_db:
        raise HTTPException(status_code=404, detail="El capítulo no existe")
    
    #Actualizar los datos del capítulo
    fields = []
    values = {"id_capitulo": id_capitulo}
    
    if capitulo.id_libro is not None:
        fields.append("id_libro = :id_libro")
        values.update({"id_libro": capitulo.id_libro})
    if capitulo.numero_capitulo is not None:
        fields.append("numero_capitulo = :numero_capitulo")
        values.update({"numero_capitulo": capitulo.numero_capitulo})
    if capitulo.titulo_capitulo is not None:
        fields.append("titulo_capitulo = :titulo_capitulo")
        values.update({"titulo_capitulo": capitulo.titulo_capitulo})
    if capitulo.contenido_capitulo is not None:
        fields.append("contenido_capitulo = :contenido_capitulo")
        values.update({"contenido_capitulo": capitulo.contenido_capitulo})
    if capitulo.estado_capitulo is not None:
        fields.append("estado_capitulo = :estado_capitulo")
        values.update({"estado_capitulo": capitulo.estado_capitulo})
        
    if not fields:
        raise HTTPException(status_code=400, detail="No se especificaron campos a actualizar")
    
    query = f"UPDATE capitulos SET {', '.join(fields)} WHERE id_capitulo = :id_capitulo"
    
    await database.execute(query=query, values=values)
    return {"message": "Capítulo actualizado correctamente"}
    
    







#ENDPOINT PARA ELIMINAR UN CAPITULO
@router.delete("/capitulos/{id_capitulo}")
async def delete_capitulo(id_capitulo: int, token: str = Depends(oauth2_scheme)):
    query = "DELETE FROM capitulos WHERE id_capitulo = :id_capitulo"
    values = {"id_capitulo": id_capitulo}
    await database.execute(query=query, values=values)
    return {"message": "Capítulo eliminado correctamente"}

#ENDPOINT PARA ELIMINAR TODOS LOS CAPITULOS DE UN LIBRO
@router.delete("/capitulos/libro/{id_libro}")
async def delete_capitulos_libro(id_libro: int, token: str = Depends(oauth2_scheme)):
    query = "DELETE FROM capitulos WHERE id_libro = :id_libro"
    values = {"id_libro": id_libro}
    await database.execute(query=query, values=values)
    return {"message": "Capítulos eliminados correctamente"}





def convert_delta_to_html(delta_json):
    process = subprocess.Popen(
        ['node', 'node_scripts/convertDeltaToHtml.js', json.dumps(delta_json)],
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE
    )
    stdout, stderr = process.communicate()
    if process.returncode != 0:
        raise Exception(f"Node.js script error: {stderr.decode('utf-8')}")
    return stdout.decode('utf-8')


@router.get("/capitulos/libro/{id_libro}/pdf", response_class=FileResponse)
async def get_capitulos_libro_pdf(id_libro: int, token: str = Depends(oauth2_scheme)):
    # Obtener los capítulos del libro desde la base de datos
    query = "SELECT * FROM capitulos WHERE id_libro = :id_libro"
    values = {"id_libro": id_libro}
    capitulos = await database.fetch_all(query=query, values=values)
    
    if not capitulos:
        raise HTTPException(status_code=404, detail="No se encontraron capítulos para este libro")
    
    # Obtener información del libro desde la base de datos
    query_libro = """
        SELECT libros.titulo_libro, usuarios.nombre_usuario
        FROM libros
        LEFT JOIN proyectos ON libros.id_proyecto = proyectos.id_proyecto
        LEFT JOIN usuarios ON proyectos.id_usuario = usuarios.id_usuario
        WHERE libros.id_libro = :id_libro
    """
    libro_info = await database.fetch_one(query=query_libro, values={"id_libro": id_libro})
    if not libro_info:
        raise HTTPException(status_code=404, detail="No se encontró el libro")
    
    titulo_libro = libro_info['titulo_libro']
    autor_libro = libro_info['nombre_usuario']
    
    # Plantilla HTML para el contenido del PDF
    html_template = """
        <!DOCTYPE html>
        <html lang="es">

        <head>
            <meta charset="UTF-8">
            <title>{titulo_libro}</title>
            <style>
                body {{
                    font-family: Arial, sans-serif;
                    margin: 40px;
                    line-height: 1.6;
                }}

                h1, h2, h3, h4 {{
                    text-align: center;
                    page-break-after: avoid;
                }}

                h1 {{
                    font-size: 2.5em;
                    margin-bottom: 0.5em;
                }}

                h2 {{
                    font-size: 2em;
                    margin-top: 2em;
                    margin-bottom: 0.5em;
                }}

                h3 {{
                    font-size: 1.75em;
                    margin-top: 1.5em;
                    margin-bottom: 0.5em;
                }}

                p {{
                    text-align: justify;
                }}

                .chapter {{
                    page-break-before: always;
                    page-break-inside: avoid;
                }}
            </style>
        </head>

        <body>
            <h1>{titulo_libro}</h1>
            <h3>Por {autor_libro}</h3>
            <hr>
            {contenido}
        </body>

        </html>
        """
    
    # Generar el contenido HTML para el PDF
    html_content = html_template.format(titulo_libro=titulo_libro, autor_libro=autor_libro, contenido="")
    
    for capitulo in capitulos:
        delta = json.loads(capitulo['contenido_capitulo'])
        html_fragment = convert_delta_to_html(delta)

        html_content += f"<div class='chapter'>"
        html_content += f"<h2>Capítulo {capitulo['numero_capitulo']}: {capitulo['titulo_capitulo']}</h2>"
        html_content += html_fragment
        html_content += f"</div>"
    
    # Guardar el contenido HTML en un archivo para depuración (opcional)
    with open("debug.html", "w", encoding="utf-8") as f:
        f.write(html_content)
    
    # Configurar pdfkit con la ruta de wkhtmltopdf si es necesario
    config = pdfkit.configuration(wkhtmltopdf=r"C:\Program Files\wkhtmltopdf\bin\wkhtmltopdf.exe")

    # Crear un archivo temporal para el PDF
    with tempfile.NamedTemporaryFile(delete=False, suffix=".pdf") as tmp_file:
        tmp_file_path = tmp_file.name
        pdfkit.from_string(html_content, tmp_file_path, configuration=config)
    
    # Enviar el archivo PDF como respuesta
    return FileResponse(tmp_file_path, filename=f"libro_{id_libro}_capitulos.pdf", media_type='application/pdf')

    # Limpieza del archivo temporal después de enviarlo (opcional)
    os.remove(tmp_file_path)