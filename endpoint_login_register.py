import base64
import json
from fastapi import FastAPI, HTTPException, status, Depends, APIRouter, Query
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from typing import Optional
from httplib2 import Credentials
import jwt
from passlib.context import CryptContext
from datetime import datetime, timedelta
import os
from db_config import connectToDatabase, closeConnection, getAllUsers
from dotenv import load_dotenv
from pydantic import BaseModel, EmailStr
import smtplib
from email.mime.text import MIMEText
from google.oauth2.credentials import Credentials
from googleapiclient.discovery import build
from google.auth.transport.requests import Request
from google_auth_oauthlib.flow import InstalledAppFlow


load_dotenv()

router = APIRouter(
    #prefix="/token",
    tags=["autenticación y registro"]
)


SECRET_KEY = os.getenv("SECRET_KEY")
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 60

SECRET_KEY2 = os.getenv("SECRET_KEY2")
ALGORITHM2 = "RS256"

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
oauth2_scheme = OAuth2PasswordBearer("/token")


#Verificar contraseña con hash
def verify_password(password, password_hash):
    return pwd_context.verify(password, password_hash)


#Obtener el usuario en caso de que este en la bbdd
def get_user(email):
    connection = connectToDatabase()
    result = getAllUsers(connection)
    closeConnection(connection)

    for user in result:
        if user["correo_electronico"] == email:
            return user
    return None  


#Obtener el usuario en caso de que este en la bbdd por id
def get_user_by_id(id_usuario):
    connection = connectToDatabase()
    result = getAllUsers(connection)
    closeConnection(connection)

    for user in result:
        if user["id_usuario"] == id_usuario:
            return user
    return None


#Comprobacion final para autenticar el usuario
def authenticate_user(username, password):
    user = get_user(username)
    if not user:
        return None 
    if not verify_password(password, user['clave_acceso']):
        return None  
    return user


#Crear el token de acceso
def create_access_token(data: str, expires_delta: timedelta):
    payload = {
        "exp": datetime.utcnow() + expires_delta,
        "sub": data
    }
    return jwt.encode(payload, SECRET_KEY, algorithm=ALGORITHM)


def decode_jwt(token: str) -> dict:
    #Separar el token en sus tres partes (header, payload, signature)
    base64_url = token.split('.')[1]

    #Reemplazar '-' con '+' y '_' con '/'
    base64_url = base64_url.replace('-', '+').replace('_', '/')

    #Añadir padding si es necesario
    padding = '=' * (4 - len(base64_url) % 4)
    base64_url += padding

    #Decodificar Base64
    base64_bytes = base64.b64decode(base64_url)

    #Convertir bytes a string
    json_payload = base64_bytes.decode('utf-8')

    #Convertir JSON a diccionario
    return json.loads(json_payload)



#------------------------------------------------------------------------------------------------------------

#Ruta para el token cuando un usuario inicie sesion
@router.post('/token')
async def login_for_access_token(form_data: OAuth2PasswordRequestForm = Depends()):
    user = authenticate_user(form_data.username, form_data.password)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="El nombre de usuario o la contraseña son incorrectos",
            headers={"WWW-Authenticate": "Bearer"}
        )
    
    access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        data=user['id_usuario'],  
        expires_delta=access_token_expires
    )

    return {'ok':True, 'access_token': access_token, 'token_type': 'bearer'}

#Ruta para desencriptar el token y devolver el id del usuario
@router.get("/token/data")
async def read_users_me(token: str = Depends(oauth2_scheme)):
    
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        id_usuario: str = payload.get("sub")
        
        #si falla usaremos la funcion decode_jwt
        try:
            payload = decode_jwt(token)
            id_usuario = payload.get("sub")
        except:
            raise HTTPException(status_code=403, detail="Token google inválido")
        
        
        if id_usuario is None:
            raise HTTPException(status_code=403, detail="Se requiere autenticación")
        return {"ok":True, "id_usuario": id_usuario}
    
    except jwt.ExpiredSignatureError:
        raise HTTPException(status_code=403, detail="Token expirado")
    except jwt.InvalidTokenError:
        raise HTTPException(status_code=403, detail="Token normal inválido")


#Funcion para cifrar la contraseña
def get_password_hash(password):
    return pwd_context.hash(password)



#Funcion para obtener el correo electrónico de un usuario de la base de datos
def get_correo_electronico(email):
    connection = connectToDatabase()
    result = getAllUsers(connection)
    closeConnection(connection)

    for user in result:
        if user["correo_electronico"] == email:
            return user["correo_electronico"]
    return None

#Funcion para verificar si un seudónimo ya está en uso
def get_seudonimo(apodo):
    connection = connectToDatabase()
    result = getAllUsers(connection)
    closeConnection(connection)

    for user in result:
        if user["seudonimo"] == apodo:
            return user["seudonimo"]
    return None

#Ruta para registrar un usuario

class UserRegistration(BaseModel):
    nombre: str
    primer_apellido: Optional[str] = None
    segundo_apellido: Optional[str] = None
    email: str
    password: str
    seudonimo: Optional[str] = None
    fecha_nacimiento: Optional[str] = None


@router.post("/register")
async def register_user(user_data: UserRegistration):
    
    nombre = user_data.nombre
    primer_apellido = user_data.primer_apellido
    segundo_apellido = user_data.segundo_apellido
    email = user_data.email
    password = user_data.password
    seudonimo = user_data.seudonimo
    fecha_nacimiento = user_data.fecha_nacimiento
    
    #Debemos comprobar que el formato de la fecha sea el adecuado, siempre que exista fecha
    if fecha_nacimiento != '':
        try:
            fecha_nacimiento = datetime.strptime(fecha_nacimiento, '%Y-%m-%d')
        except ValueError:
            raise HTTPException(status_code=400, detail="El formato de la fecha de nacimiento no es válido.")
    
    #Debemos comprobar que el correo electrónico no exista ya en la base de datos
    if get_correo_electronico(email) is not None:
        raise HTTPException(status_code=400, detail="El correo electrónico ya está en uso.")
    
    #El seudónimo tampoco puede estar en uso
    #if get_seudonimo(seudonimo) is not None:
    #   raise HTTPException(status_code=400, detail="El seudónimo ya está en uso.")
    
    
    connection = connectToDatabase()
    cursor = connection.cursor(dictionary=True)
    query = "INSERT INTO usuarios (nombre_usuario, primer_apellido, segundo_apellido, seudonimo, correo_electronico, clave_acceso, fecha_nacimiento) VALUES (%s, %s, %s, %s, %s, %s, %s)"
    values = (nombre, primer_apellido, segundo_apellido, seudonimo, email, get_password_hash(password), fecha_nacimiento)

    cursor.execute(query, values)
    connection.commit()
    closeConnection(connection)
    return {"message":"Usuario registrado con éxito."}



#Registro de usuarios con Google
class GoogleUser(BaseModel):
    name: str
    email: str
    picture: Optional[str] = None



@router.post("/verification/account/google")
async def register_google_user(user: GoogleUser):
    email = user.email
    
    #Verificar si el usuario ya existe
    connection = connectToDatabase()
    cursor = connection.cursor(dictionary=True)
    query = "SELECT * FROM usuarios WHERE correo_electronico = %s"
    cursor.execute(query, (email,))
    existing_user = cursor.fetchone()
    
    if existing_user:
        closeConnection(connection)
        #Crear token de acceso
        access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
        access_token = create_access_token(data=existing_user['id_usuario'], expires_delta=access_token_expires)
        return {"message": "Usuario autenticado con éxito.", "access_token": access_token, "token_type": "bearer"}    
    #El usuario no eciste
    query = """
    INSERT INTO usuarios (nombre_usuario, correo_electronico, imagen_perfil) 
    VALUES (%s, %s, %s)
    """
    cursor.execute(query, (user.name, email, user.picture))
    connection.commit()
    
    cursor.execute("SELECT * FROM usuarios WHERE correo_electronico = %s", (email,))
    new_user = cursor.fetchone()
    
    closeConnection(connection)
    
    #Crear token de acceso
    access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(data=new_user['id_usuario'], expires_delta=access_token_expires)
    
    return {"message": "Usuario registrado con éxito.", "access_token": access_token, "token_type": "bearer"} 
    
    
    
    
#Envio de correo con contraseña temporal
class EmailSchema(BaseModel):
    email: EmailStr
    temp_password: str

# Cargar las credenciales de OAuth 2.0
def load_credentials():
    creds = None
    if os.path.exists('token.json'):
        creds = Credentials.from_authorized_user_file('token.json', ['https://www.googleapis.com/auth/gmail.send'])
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file('credentials.json', ['https://www.googleapis.com/auth/gmail.send'], redirect_uri='http://localhost/htdocs/frontend_escribdream_javascript_alpha/views/login.html')
            creds = flow.run_local_server(port=0)
        with open('token.json', 'w') as token:
            token.write(creds.to_json())
    return creds

def send_email_via_gmail(email, temp_password):
    creds = load_credentials()
    service = build('gmail', 'v1', credentials=creds)
    
    message = MIMEText(f"Bienvenido a Escribdream. Su contraseña temporal es: --> {temp_password} <--. Asegúrese de cambiarla lo antes posible.")
    message['to'] = email
    message['from'] = os.getenv("EMAIL")
    message['subject'] = "Contraseña temporal"
    
    raw_message = base64.urlsafe_b64encode(message.as_bytes()).decode()
    body = {'raw': raw_message}
    
    try:
        message = service.users().messages().send(userId='me', body=body).execute()
        print(f'Message Id: {message["id"]}')
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error al enviar el correo: {str(e)}")

@router.post("/send/email")
async def send_email(email_data: EmailSchema):
    email = email_data.email
    temp_password = email_data.temp_password

    try:
        send_email_via_gmail(email, temp_password)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error al enviar el correo: {str(e)}")
    
    return {"message": "Correo enviado con éxito."}