from fastapi import FastAPI, Depends
from databases import Database
import mysql.connector

# Configuración de la conexión a la base de datos escribdream_prueba_5 en localhost
db_config = {
    'host': 'db5015971926.hosting-data.io',
    'user': 'dbu5608856',
    'password': 'EscribSueno87',
    # 'database': 'proyect_escribdream'
    'database': 'dbs13013259'
}

DATABASE_URL = f"mysql://{db_config['user']}:{db_config['password']}@{db_config['host']}/{db_config['database']}"
database = Database(DATABASE_URL)

def connectToDatabase():
    connection = mysql.connector.connect(
        host=db_config['host'],
        user=db_config['user'],
        password=db_config['password'],
        database=db_config['database']
    )

    return connection

def closeConnection(connection):
    connection.close()

def getAllUsers(connection):
    cursor = connection.cursor(dictionary=True)
    cursor.execute("SELECT * FROM usuarios")
    result = cursor.fetchall()
    cursor.close()

    return result

# app nos permitirá definir los eventos de inicio y finalización de la aplicación
app = FastAPI()

# Función que se ejecutará al iniciar la aplicación
@app.on_event("startup")
async def startup():
    await database.connect()
    
# Función que se ejecutará al finalizar la aplicación
@app.on_event("shutdown")
async def shutdown():
    await database.disconnect()

