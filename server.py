import os
import logging
from fastapi import FastAPI, Request, Form, HTTPException
from fastapi.responses import HTMLResponse
from fastapi.middleware.cors import CORSMiddleware
from twilio.rest import Client
from twilio.twiml.messaging_response import MessagingResponse
from dotenv import load_dotenv
from agente import GogginsFitnessAgent
from web_agent import GogginsFitnessWebAgent
from pydantic import BaseModel
from typing import Literal

# Configurar logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Cargar variables de entorno
load_dotenv()

# Configurar Twilio
twilio_account_sid = os.environ.get("TWILIO_ACCOUNT_SID")
twilio_auth_token = os.environ.get("TWILIO_AUTH_TOKEN")
twilio_phone_number = os.environ.get("TWILIO_PHONE_NUMBER")

# Verificar configuración de Twilio
if not all([twilio_account_sid, twilio_auth_token, twilio_phone_number]):
    raise ValueError("TWILIO_ACCOUNT_SID, TWILIO_AUTH_TOKEN y TWILIO_PHONE_NUMBER deben estar configuradas en .env")

# Inicializar cliente de Twilio
twilio_client = Client(twilio_account_sid, twilio_auth_token)

# Crear aplicación FastAPI
app = FastAPI(
    title="Agente de Fitness David Goggins",
    description="API para procesar mensajes de WhatsApp con el agente de fitness",
    version="1.0.0"
)

# Configurar CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Permite todos los orígenes
    allow_credentials=True,
    allow_methods=["*"],  # Permite todos los métodos
    allow_headers=["*"],  # Permite todos los headers
)

# Inicializar agente de Goggins
goggins_agent = GogginsFitnessAgent()

# Inicializar agente web de Goggins
goggins_web_agent = GogginsFitnessWebAgent()

class ConsultaRequest(BaseModel):
    tipo_consulta: Literal["progreso", "estadisticas", "recomendaciones"]

@app.get("/", response_class=HTMLResponse)
async def root():
    """Página de inicio con información del webhook"""
    return """
    <html>
        <head>
            <title>🔥 Agente David Goggins - Webhook</title>
            <style>
                body { font-family: Arial, sans-serif; margin: 40px; background-color: #1a1a1a; color: #ffffff; }
                .container { max-width: 800px; margin: 0 auto; }
                .header { text-align: center; margin-bottom: 40px; }
                .status { background-color: #2d2d2d; padding: 20px; border-radius: 10px; margin: 20px 0; }
                .endpoint { background-color: #3d3d3d; padding: 15px; border-radius: 5px; font-family: monospace; }
                .warning { background-color: #ff4444; color: white; padding: 15px; border-radius: 5px; margin: 20px 0; }
                .success { background-color: #44ff44; color: black; padding: 15px; border-radius: 5px; margin: 20px 0; }
            </style>
        </head>
        <body>
            <div class="container">
                <div class="header">
                    <h1>🔥 AGENTE DAVID GOGGINS 🔥</h1>
                    <h2>Webhook para WhatsApp</h2>
                </div>
                
                <div class="status">
                    <h3>✅ Estado del Servidor</h3>
                    <p>El servidor está funcionando correctamente.</p>
                    <p>Agente de Goggins: <strong>ACTIVO</strong></p>
                </div>
                
                <div class="endpoint">
                    <h3>📡 Endpoint del Webhook</h3>
                    <p><strong>POST /webhook</strong></p>
                    <p>URL completa: <code>https://tu-ngrok-url.ngrok.io/webhook</code></p>
                </div>
                
                <div class="warning">
                    <h3>⚠️ Configuración Requerida</h3>
                    <p>1. Ejecuta ngrok: <code>ngrok http 8000</code></p>
                    <p>2. Copia la URL de ngrok</p>
                    <p>3. Configura el webhook en Twilio Console</p>
                    <p>4. Agrega la URL + /webhook en la configuración</p>
                </div>
                
                <div class="success">
                    <h3>🎯 Próximos Pasos</h3>
                    <p>1. Inicia el servidor: <code>uvicorn server:app --reload --port 8000</code></p>
                    <p>2. Ejecuta ngrok en otra terminal</p>
                    <p>3. Configura el webhook en Twilio</p>
                    <p>4. ¡Envía mensajes a tu número de Twilio!</p>
                </div>
            </div>
        </body>
    </html>
    """

@app.post("/webhook")
async def webhook(request: Request):
    """Endpoint para recibir mensajes de WhatsApp desde Twilio"""
    try:
        # Obtener datos del formulario
        form_data = await request.form()
        
        # Extraer información del mensaje
        from_number = form_data.get("From", "")
        body = form_data.get("Body", "")
        message_sid = form_data.get("MessageSid", "")
        
        logger.info(f"Mensaje recibido de {from_number}: {body}")
        
        # Validar que tenemos un mensaje válido
        if not body or not from_number:
            logger.error("Mensaje o número de teléfono vacío")
            raise HTTPException(status_code=400, detail="Mensaje o número de teléfono vacío")
        
        # Procesar mensaje con el agente de Goggins
        respuesta_goggins = goggins_agent.procesar_mensaje_whatsapp(body, from_number)
        
        logger.info(f"Respuesta de Goggins: {respuesta_goggins}")
        
        # Crear respuesta TwiML
        resp = MessagingResponse()
        resp.message(respuesta_goggins)
        
        return HTMLResponse(content=str(resp), media_type="text/html")
        
    except Exception as e:
        logger.error(f"Error procesando mensaje: {str(e)}")
        
        # Respuesta de error con personalidad de Goggins
        resp = MessagingResponse()
        resp.message("¡ERROR EN EL SISTEMA, PENDEJO! ¡PERO ESO NO ES EXCUSA PARA NO ENTRENAR! 🔥")
        
        return HTMLResponse(content=str(resp), media_type="text/html")

@app.post("/web-consult")
async def web_consultation(consulta: ConsultaRequest):
    """Endpoint para consultas web del agente Goggins"""
    try:
        # Procesar consulta web
        respuesta = goggins_web_agent.procesar_consulta_web(consulta.tipo_consulta)
        
        return {
            "success": True,
            "message": respuesta
        }
        
    except Exception as e:
        logger.error(f"Error en consulta web: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail="¡ERROR EN EL SISTEMA, PEDAZO DE MIERDA! ¡PERO ESO NO ES EXCUSA PARA SER UN VAGO!"
        )

@app.get("/health")
async def health_check():
    """Endpoint para verificar el estado del servidor"""
    return {
        "status": "healthy",
        "agent": "David Goggins Fitness Agent",
        "version": "1.0.0",
        "twilio_configured": bool(twilio_account_sid and twilio_auth_token)
    }

@app.post("/test-message")
async def test_message(
    phone_number: str = Form(...),
    message: str = Form(...)
):
    """Endpoint para probar el envío de mensajes (solo para desarrollo)"""
    try:
        # Procesar mensaje con el agente
        respuesta = goggins_agent.procesar_mensaje_whatsapp(message, phone_number)
        
        return {
            "success": True,
            "original_message": message,
            "goggins_response": respuesta,
            "phone_number": phone_number
        }
        
    except Exception as e:
        return {
            "success": False,
            "error": str(e)
        }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000) 