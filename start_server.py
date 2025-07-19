#!/usr/bin/env python3
"""
Script para iniciar el servidor del Agente David Goggins
"""

import os
import sys
import subprocess
import time
from dotenv import load_dotenv

def verificar_configuracion():
    """Verifica que todas las variables de entorno estén configuradas"""
    load_dotenv()
    
    variables_requeridas = {
        "OPENAI_API_KEY": "API Key de OpenAI",
        "SUPABASE_URL": "URL de Supabase",
        "SUPABASE_KEY": "API Key de Supabase",
        "TWILIO_ACCOUNT_SID": "Account SID de Twilio",
        "TWILIO_AUTH_TOKEN": "Auth Token de Twilio",
        "TWILIO_PHONE_NUMBER": "Número de teléfono de Twilio"
    }
    
    faltantes = []
    
    for variable, descripcion in variables_requeridas.items():
        if not os.environ.get(variable):
            faltantes.append(f"  - {variable}: {descripcion}")
    
    if faltantes:
        print("❌ Variables de entorno faltantes:")
        for faltante in faltantes:
            print(faltante)
        print("\n💡 Agrega estas variables a tu archivo .env")
        return False
    
    print("✅ Todas las variables de entorno están configuradas")
    return True

def verificar_dependencias():
    """Verifica que todas las dependencias estén instaladas"""
    try:
        import fastapi
        import uvicorn
        import twilio
        import supabase
        print("✅ Todas las dependencias están instaladas")
        return True
    except ImportError as e:
        print(f"❌ Dependencia faltante: {e}")
        print("💡 Ejecuta: pip install -r requirements.txt")
        return False

def mostrar_instrucciones():
    """Muestra las instrucciones para configurar el webhook"""
    print("\n" + "="*60)
    print("🔥 CONFIGURACIÓN DEL WEBHOOK DE TWILIO 🔥")
    print("="*60)
    
    print("\n📋 Pasos para configurar:")
    print("1. Inicia el servidor (este script)")
    print("2. En otra terminal, ejecuta: ngrok http 8000")
    print("3. Copia la URL HTTPS de ngrok (ej: https://abc123.ngrok.io)")
    print("4. Ve a https://console.twilio.com/")
    print("5. Navega a Messaging > Settings > WhatsApp Sandbox")
    print("6. En 'When a message comes in', agrega: TU_URL_NGROK/webhook")
    print("7. Guarda la configuración")
    print("8. ¡Envía mensajes a tu número de Twilio!")
    
    print("\n🎯 Ejemplos de mensajes para probar:")
    print("- 'Hola, empecé mi entrenamiento'")
    print("- 'Bench press 3x8 @ 80kg'")
    print("- 'Squat 4x10 @ 100kg'")
    print("- 'Terminé mi entrenamiento'")
    
    print("\n🔗 URLs útiles:")
    print("- Servidor local: http://localhost:8000")
    print("- Documentación API: http://localhost:8000/docs")
    print("- Estado del servidor: http://localhost:8000/health")

def iniciar_servidor():
    """Inicia el servidor FastAPI"""
    print("\n🚀 Iniciando servidor del Agente David Goggins...")
    print("📍 Puerto: 8000")
    print("🌐 URL local: http://localhost:8000")
    print("📚 Documentación: http://localhost:8000/docs")
    print("\n⏹️  Presiona Ctrl+C para detener el servidor")
    print("="*60)
    
    try:
        # Importar y ejecutar el servidor
        import uvicorn
        uvicorn.run("server:app", host="0.0.0.0", port=8000, reload=True)
    except KeyboardInterrupt:
        print("\n\n🛑 Servidor detenido por el usuario")
    except Exception as e:
        print(f"\n❌ Error al iniciar el servidor: {e}")

def main():
    """Función principal"""
    print("🔥 AGENTE DAVID GOGGINS - SERVIDOR 🔥")
    print("="*40)
    
    # Verificar configuración
    if not verificar_configuracion():
        sys.exit(1)
    
    # Verificar dependencias
    if not verificar_dependencias():
        sys.exit(1)
    
    # Mostrar instrucciones
    mostrar_instrucciones()
    
    # Preguntar si continuar
    respuesta = input("\n¿Deseas iniciar el servidor ahora? (s/n): ").lower()
    if respuesta in ['s', 'si', 'sí', 'y', 'yes']:
        iniciar_servidor()
    else:
        print("👋 Servidor no iniciado. Ejecuta 'python start_server.py' cuando estés listo.")

if __name__ == "__main__":
    main() 