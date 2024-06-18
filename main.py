import uvicorn
from db_config import app
from fastapi.middleware.cors import CORSMiddleware
from endpoints_usuarios import router as usuarios_router
from endpoints_proyectos import router as proyectos_router
from endpoints_lineas_tiempo import router as lineas_tiempo_router
from endpoints_eventos import router as eventos_router
from endpoints_personajes import router as personajes_router
from endpoints_libros import router as libros_router
from endpoints_capitulos import router as capitulos_router
from endpoints_mapas import router as mapas_router
from endpoints_localizaciones import router as localizaciones_router
from endpoints_notas import router as notas_router
from endpoints_escaletas import router as escaletas_router
from endpoints_secciones_escaleta import router as secciones_escaleta_router
from endpoint_login_register import router as login_router

# origins = [
#     "http://127.0.0.1:57628",  
#     "http://localhost:60369",
#     "http://127.0.0.1:60369",
#     "http://localhost:57628",
#     "http://localhost"
    
# ]

app.include_router(usuarios_router)
app.include_router(proyectos_router)
app.include_router(lineas_tiempo_router)
app.include_router(eventos_router)
app.include_router(personajes_router)
app.include_router(libros_router)
app.include_router(capitulos_router)
app.include_router(mapas_router)
app.include_router(localizaciones_router)
app.include_router(notas_router)
app.include_router(escaletas_router)
app.include_router(secciones_escaleta_router)
app.include_router(login_router)


origins = [
    "http://localhost",
    "http://127.0.0.1",
    "*"
]
    
app.add_middleware(
    CORSMiddleware,
    # allow_origins=["*"],  
    allow_origins=origins,  
    allow_credentials=True,
    allow_methods=["*"],  
    allow_headers=["*"],  
)

if __name__ == "__main__":
    
    uvicorn.run("main:app", host="0.0.0.0", port=4000, log_level="info")