import os
import sys
import json
import re
from datetime import datetime
from dotenv import load_dotenv
from langchain.llms import OpenAI
from langchain.agents import initialize_agent, AgentType
from langchain.tools import Tool
from langchain.memory import ConversationBufferMemory
from supabase import create_client, Client

# Cargar variables de entorno
load_dotenv()

# Configurar Supabase
supabase_url = os.environ.get("SUPABASE_URL")
supabase_key = os.environ.get("SUPABASE_KEY")
supabase: Client = create_client(supabase_url, supabase_key)

class GogginsFitnessAgent:
    def __init__(self):
        self.llm = OpenAI(
            model_name="gpt-4",
            temperature=0.9,  # Más creativo para la personalidad de Goggins
            max_tokens=500
        )
        
        self.memory = ConversationBufferMemory(
            memory_key="chat_history",
            return_messages=True
        )
        
        # Configurar herramientas
        self.herramientas = [
            Tool(
                name="registrar_entrenamiento",
                func=self.registrar_entrenamiento,
                description="Registra un entrenamiento en la base de datos. Parámetros: user_phone, exercise, sets, reps, weight_kg"
            ),
            Tool(
                name="obtener_ultimo_record",
                func=self.obtener_ultimo_record,
                description="Obtiene el último record del usuario para un ejercicio específico. Parámetros: user_phone, exercise"
            ),
            Tool(
                name="obtener_historial_entrenamientos",
                func=self.obtener_historial_entrenamientos,
                description="Obtiene el historial de entrenamientos del usuario. Parámetros: user_phone, limit"
            )
        ]
        
        # Configurar el agente
        self.agente = initialize_agent(
            tools=self.herramientas,
            llm=self.llm,
            agent=AgentType.CONVERSATIONAL_REACT_DESCRIPTION,
            memory=self.memory,
            verbose=True,
            handle_parsing_errors=True
        )

    def registrar_entrenamiento(self, user_phone: str, exercise: str, sets: int, reps: int, weight_kg: float):
        """Registra un entrenamiento en Supabase"""
        try:
            # Verificar si hay progreso comparando con el último record
            ultimo_record = self.obtener_ultimo_record(user_phone, exercise)
            is_progress = False
            
            if ultimo_record:
                # Calcular si hay progreso (más peso, más reps, o más sets)
                progreso_peso = weight_kg > ultimo_record['weight_kg']
                progreso_reps = reps > ultimo_record['reps']
                progreso_sets = sets > ultimo_record['sets']
                is_progress = progreso_peso or progreso_reps or progreso_sets
            
            # Insertar en Supabase
            data = {
                'user_phone': user_phone,
                'exercise': exercise,
                'sets': sets,
                'reps': reps,
                'weight_kg': weight_kg,
                'is_progress': is_progress
            }
            
            result = supabase.table('workouts').insert(data).execute()
            return f"Entrenamiento registrado: {exercise} - {sets} series x {reps} reps @ {weight_kg}kg. Progreso: {is_progress}"
            
        except Exception as e:
            return f"Error al registrar entrenamiento: {str(e)}"

    def obtener_ultimo_record(self, user_phone: str, exercise: str):
        """Obtiene el último record del usuario para un ejercicio específico"""
        try:
            result = supabase.table('workouts')\
                .select('*')\
                .eq('user_phone', user_phone)\
                .eq('exercise', exercise)\
                .order('created_at', desc=True)\
                .limit(1)\
                .execute()
            
            if result.data:
                return result.data[0]
            return None
            
        except Exception as e:
            print(f"Error al obtener último record: {str(e)}")
            return None

    def obtener_historial_entrenamientos(self, user_phone: str, limit: int = 10):
        """Obtiene el historial de entrenamientos del usuario"""
        try:
            result = supabase.table('workouts')\
                .select('*')\
                .eq('user_phone', user_phone)\
                .order('created_at', desc=True)\
                .limit(limit)\
                .execute()
            
            return result.data
            
        except Exception as e:
            print(f"Error al obtener historial: {str(e)}")
            return []

    def parsear_mensaje_entrenamiento(self, mensaje: str):
        """Extrae información de entrenamiento del mensaje del usuario"""
        # Patrones para detectar ejercicios, pesos, reps y series
        patrones = {
            'bench_press': r'bench|press|pecho|pectoral',
            'squat': r'squat|sentadilla|pierna',
            'deadlift': r'deadlift|peso muerto|muerto',
            'pull_up': r'pull.?up|dominada|dominadas',
            'push_up': r'push.?up|flexion|flexiones',
            'curl': r'curl|bicep|bíceps',
            'overhead_press': r'overhead|press|hombro|militar'
        }
        
        # Buscar ejercicio
        ejercicio_encontrado = None
        for ejercicio, patron in patrones.items():
            if re.search(patron, mensaje.lower()):
                ejercicio_encontrado = ejercicio
                break
        
        # Extraer números (peso, reps, series)
        numeros = re.findall(r'\d+', mensaje)
        
        if len(numeros) >= 3 and ejercicio_encontrado:
            # Asumir formato: series x reps @ peso
            series = int(numeros[0])
            reps = int(numeros[1])
            peso = float(numeros[2])
            
            return {
                'exercise': ejercicio_encontrado,
                'sets': series,
                'reps': reps,
                'weight_kg': peso
            }
        
        return None

    def generar_respuesta_goggins(self, mensaje_usuario: str, user_phone: str):
        """Genera una respuesta con la personalidad de David Goggins"""
        
        # Verificar si es un mensaje de entrenamiento
        datos_entrenamiento = self.parsear_mensaje_entrenamiento(mensaje_usuario)
        
        if datos_entrenamiento:
            # Es un registro de entrenamiento
            ejercicio = datos_entrenamiento['exercise']
            series = datos_entrenamiento['sets']
            reps = datos_entrenamiento['reps']
            peso = datos_entrenamiento['weight_kg']
            
            # Obtener último record para comparar
            ultimo_record = self.obtener_ultimo_record(user_phone, ejercicio)
            
            # Registrar el entrenamiento
            self.registrar_entrenamiento(user_phone, ejercicio, series, reps, peso)
            
            # Generar respuesta motivacional
            if ultimo_record:
                # Comparar con el record anterior
                progreso_peso = peso > ultimo_record['weight_kg']
                progreso_reps = reps > ultimo_record['reps']
                progreso_sets = series > ultimo_record['sets']
                
                if progreso_peso or progreso_reps or progreso_sets:
                    return f"¡BIEN! ¡Finalmente estás dejando de ser un puto perdedor! {ejercicio.upper()}: {series}x{reps} @ {peso}kg. ¡Has superado tu debilidad anterior! Pero no te pongas cómodo, pendejo. El récord de hoy es el calentamiento de mañana. ¡SIGUE ADELANTE Y DESTRUYE TUS LÍMITES! 💪🔥"
                else:
                    return f"¡¿ESTO ES UNA BROMA?! ¡Tu último {ejercicio.upper()} se está riendo de ti ahora mismo! {series}x{reps} @ {peso}kg - ¡Estás robando oxígeno! ¡Vuelve a intentarlo y deja de ser un puto cobarde! ¡LA SOBRECARGA PROGRESIVA NO ES UNA SUGERENCIA, ES UNA ORDEN! 🔥💀"
            else:
                return f"¡PRIMER ENTRENAMIENTO REGISTRADO! {ejercicio.upper()}: {series}x{reps} @ {peso}kg. ¡Bienvenido al infierno, pendejo! Ahora el verdadero trabajo comienza. ¡NO HAY VUELTA ATRÁS! 💪🔥"
        
        else:
            # Es un mensaje general
            if any(palabra in mensaje_usuario.lower() for palabra in ['hola', 'hello', 'hey']):
                return "¡¿QUÉ CARAJO QUIERES?! ¡No tengo tiempo para saludos de mierda! ¡Dime qué ejercicio vas a hacer y cuánto peso vas a levantar, pendejo! ¡LA VIDA NO ESPERA A LOS DÉBILES! 💪🔥"
            
            elif any(palabra in mensaje_usuario.lower() for palabra in ['terminé', 'acabé', 'finish', 'done']):
                return "¡¿TERMINASTE?! ¡NO HAY 'TERMINAR' EN ESTE INFIERNO! ¡El trabajo nunca termina, pendejo! ¡Mañana vuelves más fuerte o te rindes como el cobarde que eres! ¡LA EXCELENCIA ES UN HÁBITO, NO UN ACTO! 🔥💀"
            
            elif any(palabra in mensaje_usuario.lower() for palabra in ['cansado', 'tired', 'fatiga']):
                return "¡¿CANSADO?! ¡LA FATIGA ES UNA MENTIRA! ¡Tu mente te está engañando, pendejo! ¡Empuja más allá de tus límites imaginarios! ¡EL DOLOR TEMPORAL ES MEJOR QUE EL DOLOR PERMANENTE DE LA MEDIOCRIDAD! 💪🔥"
            
            else:
                return "¡HABLA CLARO, PENDEJO! ¡No entiendo tu mierda! ¡Dime qué ejercicio hiciste, cuántas series, repeticiones y peso! ¡O mejor aún, ¡VE A ENTRENAR EN LUGAR DE PERDER MI TIEMPO! 🔥💀"

    def procesar_mensaje_whatsapp(self, mensaje: str, user_phone: str):
        """Procesa un mensaje de WhatsApp y retorna la respuesta de Goggins"""
        try:
            # Generar respuesta con personalidad de Goggins
            respuesta = self.generar_respuesta_goggins(mensaje, user_phone)
            
            # Guardar en memoria para contexto
            self.memory.save_context(
                {"input": mensaje},
                {"output": respuesta}
            )
            
            return respuesta
            
        except Exception as e:
            return f"¡ERROR EN EL SISTEMA, PENDEJO! {str(e)} ¡PERO ESO NO ES EXCUSA PARA NO ENTRENAR! 🔥"

def main():
    """Función principal para probar el agente"""
    print("🔥 INICIANDO AGENTE DE FITNESS DAVID GOGGINS 🔥")
    
    try:
        # Verificar configuración
        if not supabase_url or not supabase_key:
            raise ValueError("SUPABASE_URL y SUPABASE_KEY deben estar configuradas en .env")
        
        # Crear agente
        agente = GogginsFitnessAgent()
        print("✅ ¡AGENTE GOGGINS CONFIGURADO EXITOSAMENTE!")
        
        # Simular mensajes de WhatsApp
        user_phone = "+1234567890"
        
        print("\n" + "="*60)
        print("🔥 SIMULACIÓN DE MENSAJES DE WHATSAPP 🔥")
        print("="*60)
        
        # Mensaje 1: Saludo
        mensaje1 = "Hola, empecé mi entrenamiento"
        print(f"\n📱 Usuario: {mensaje1}")
        respuesta1 = agente.procesar_mensaje_whatsapp(mensaje1, user_phone)
        print(f"🤖 Goggins: {respuesta1}")
        
        # Mensaje 2: Registro de entrenamiento
        mensaje2 = "Bench press 3x8 @ 80kg"
        print(f"\n📱 Usuario: {mensaje2}")
        respuesta2 = agente.procesar_mensaje_whatsapp(mensaje2, user_phone)
        print(f"🤖 Goggins: {respuesta2}")
        
        # Mensaje 3: Segundo entrenamiento (sin progreso)
        mensaje3 = "Bench press 3x8 @ 80kg"
        print(f"\n📱 Usuario: {mensaje3}")
        respuesta3 = agente.procesar_mensaje_whatsapp(mensaje3, user_phone)
        print(f"🤖 Goggins: {respuesta3}")
        
        # Mensaje 4: Con progreso
        mensaje4 = "Bench press 3x8 @ 85kg"
        print(f"\n📱 Usuario: {mensaje4}")
        respuesta4 = agente.procesar_mensaje_whatsapp(mensaje4, user_phone)
        print(f"🤖 Goggins: {respuesta4}")
        
        print("\n" + "="*60)
        print("🎉 ¡AGENTE GOGGINS FUNCIONANDO PERFECTAMENTE! 🎉")
        print("="*60)
        
    except Exception as e:
        print(f"❌ Error al configurar el agente: {str(e)}")
        print("\n💡 Asegúrate de:")
        print("   1. Tener instalado: pip install -r requirements.txt")
        print("   2. Tener configuradas las variables en .env:")
        print("      - OPENAI_API_KEY")
        print("      - SUPABASE_URL")
        print("      - SUPABASE_KEY")
        print("   3. Tener saldo en tu cuenta de OpenAI")
        print(f"\n🔍 Error detallado: {type(e).__name__}: {str(e)}")

if __name__ == "__main__":
    main() 