import os
import sys
from dotenv import load_dotenv
from langchain.llms import OpenAI
from langchain.agents import initialize_agent, AgentType
from langchain.tools import Tool
from langchain.memory import ConversationBufferMemory

# Cargar variables de entorno
load_dotenv()

def configurar_agente():
    """
    Configura y retorna un agente de LangChain con GPT-4
    """
    # Verificar que la API key esté configurada
    if "OPENAI_API_KEY" not in os.environ:
        raise ValueError("OPENAI_API_KEY no está configurada en el archivo .env")
    
    # Inicializar el modelo de lenguaje (GPT-4)
    llm = OpenAI(
        model_name="gpt-4",  # Usar GPT-4
        temperature=0.7,     # Controlar la creatividad (0.0 = muy conservador, 1.0 = muy creativo)
        max_tokens=1000      # Máximo número de tokens en la respuesta
    )
    
    # Configurar memoria para mantener contexto de la conversación
    memory = ConversationBufferMemory(
        memory_key="chat_history",
        return_messages=True
    )
    
    # Definir herramientas que el agente puede usar
    herramientas = [
        Tool(
            name="Calculadora",
            func=lambda x: str(eval(x)),
            description="Útil para realizar cálculos matemáticos. Ejemplo: '2 + 2' o '10 * 5'"
        ),
        Tool(
            name="Información_del_Sistema",
            func=lambda x: f"Información del sistema: {os.name}, Python {sys.version}",
            description="Proporciona información sobre el sistema operativo y Python"
        )
    ]
    
    # Inicializar el agente
    agente = initialize_agent(
        tools=herramientas,
        llm=llm,
        agent=AgentType.CONVERSATIONAL_REACT_DESCRIPTION,
        memory=memory,
        verbose=True,  # Mostrar el proceso de pensamiento del agente
        handle_parsing_errors=True
    )
    
    return agente

def ejecutar_agente(agente, pregunta):
    """
    Ejecuta el agente con una pregunta específica
    """
    try:
        respuesta = agente.run(pregunta)
        return respuesta
    except Exception as e:
        return f"Error al ejecutar el agente: {str(e)}"

def main():
    """
    Función principal para demostrar el uso del agente
    """
    print("🤖 Configurando agente con LangChain y GPT-4...")
    
    try:
        # Configurar el agente
        agente = configurar_agente()
        print("✅ Agente configurado exitosamente!")
        
        # Ejemplo de uso
        print("\n" + "="*50)
        print("EJEMPLOS DE USO DEL AGENTE")
        print("="*50)
        
        # Ejemplo 1: Cálculo matemático
        pregunta1 = "¿Cuánto es 15 * 23?"
        print(f"\n❓ Pregunta: {pregunta1}")
        respuesta1 = ejecutar_agente(agente, pregunta1)
        print(f"🤖 Respuesta: {respuesta1}")
        
        # Ejemplo 2: Pregunta general
        pregunta2 = "¿Puedes explicarme qué es la inteligencia artificial?"
        print(f"\n❓ Pregunta: {pregunta2}")
        respuesta2 = ejecutar_agente(agente, pregunta2)
        print(f"🤖 Respuesta: {respuesta2}")
        
        # Ejemplo 3: Información del sistema
        pregunta3 = "¿Qué información tienes sobre el sistema?"
        print(f"\n❓ Pregunta: {pregunta3}")
        respuesta3 = ejecutar_agente(agente, pregunta3)
        print(f"🤖 Respuesta: {respuesta3}")
        
        print("\n" + "="*50)
        print("🎉 ¡Agente funcionando correctamente!")
        print("="*50)
        
    except Exception as e:
        print(f"❌ Error al configurar el agente: {str(e)}")
        print("\n💡 Asegúrate de:")
        print("   1. Tener instalado: pip install -r requirements.txt")
        print("   2. Tener configurada OPENAI_API_KEY en tu archivo .env")
        print("   3. Tener saldo en tu cuenta de OpenAI")
        print(f"\n🔍 Error detallado: {type(e).__name__}: {str(e)}")

if __name__ == "__main__":
    main() 