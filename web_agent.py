import os
import json
from datetime import datetime, timedelta
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

# Usuario hardcodeado para consultas
HARDCODED_USER = "+51998555878"

class GogginsFitnessWebAgent:
    def __init__(self):
        self.llm = OpenAI(
            model_name="gpt-4",
            temperature=0.9,
            max_tokens=750
        )
        
        self.memory = ConversationBufferMemory(
            memory_key="chat_history",
            return_messages=True
        )
        
        # Configurar herramientas
        self.herramientas = [
            Tool(
                name="analizar_progreso",
                func=self.analizar_progreso,
                description="Analiza el progreso del usuario en los últimos días"
            ),
            Tool(
                name="obtener_estadisticas",
                func=self.obtener_estadisticas,
                description="Obtiene estadísticas generales del entrenamiento del usuario"
            ),
            Tool(
                name="generar_recomendaciones",
                func=self.generar_recomendaciones,
                description="Genera recomendaciones personalizadas basadas en el historial"
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

    def analizar_progreso(self):
        """Analiza el progreso del usuario en los últimos 30 días"""
        try:
            # Obtener fecha de hace 30 días
            fecha_inicio = (datetime.now() - timedelta(days=30)).isoformat()
            
            result = supabase.table('workouts')\
                .select('*')\
                .eq('user_phone', HARDCODED_USER)\
                .gte('created_at', fecha_inicio)\
                .order('created_at', desc=True)\
                .execute()
            
            if not result.data:
                return "NO HAY DATOS DE ENTRENAMIENTO, ¡MALDITO VAGO!"
            
            # Agrupar por ejercicio
            ejercicios = {}
            for workout in result.data:
                ejercicio = workout['exercise']
                if ejercicio not in ejercicios:
                    ejercicios[ejercicio] = []
                ejercicios[ejercicio].append(workout)
            
            # Analizar progreso por ejercicio
            analisis = []
            for ejercicio, workouts in ejercicios.items():
                if len(workouts) > 1:
                    primer_workout = workouts[-1]
                    ultimo_workout = workouts[0]
                    
                    diferencia_peso = ultimo_workout['weight_kg'] - primer_workout['weight_kg']
                    diferencia_reps = ultimo_workout['reps'] - primer_workout['reps']
                    
                    analisis.append({
                        'ejercicio': ejercicio,
                        'diferencia_peso': diferencia_peso,
                        'diferencia_reps': diferencia_reps,
                        'sesiones': len(workouts)
                    })
            
            return json.dumps(analisis)
            
        except Exception as e:
            return f"Error analizando progreso: {str(e)}"

    def obtener_estadisticas(self):
        """Obtiene estadísticas generales del entrenamiento"""
        try:
            result = supabase.table('workouts')\
                .select('*')\
                .eq('user_phone', HARDCODED_USER)\
                .execute()
            
            if not result.data:
                return "NO HAY DATOS DE ENTRENAMIENTO, ¡PEDAZO DE VAGO!"
            
            # Calcular estadísticas
            total_workouts = len(result.data)
            ejercicios_unicos = len(set(w['exercise'] for w in result.data))
            max_peso = max(w['weight_kg'] for w in result.data)
            progreso_count = len([w for w in result.data if w.get('is_progress', False)])
            
            stats = {
                'total_workouts': total_workouts,
                'ejercicios_unicos': ejercicios_unicos,
                'max_peso': max_peso,
                'total_progresos': progreso_count
            }
            
            return json.dumps(stats)
            
        except Exception as e:
            return f"Error obteniendo estadísticas: {str(e)}"

    def generar_recomendaciones(self):
        """Genera recomendaciones basadas en el historial"""
        try:
            # Obtener datos de progreso y estadísticas
            progreso = json.loads(self.analizar_progreso())
            stats = json.loads(self.obtener_estadisticas())
            
            # Generar prompt para recomendaciones
            prompt = f"""
            Actúa como David Goggins, el ex-Navy SEAL ultra motivador y extremadamente ofensivo.
            
            Analiza estos datos de entrenamiento:
            - Total entrenamientos: {stats['total_workouts']}
            - Ejercicios diferentes: {stats['ejercicios_unicos']}
            - Máximo peso levantado: {stats['max_peso']}kg
            - Veces que ha progresado: {stats['total_progresos']}
            
            Progreso por ejercicio:
            {json.dumps(progreso, indent=2)}
            
            Genera 3-4 recomendaciones EXTREMADAMENTE AGRESIVAS Y OFENSIVAS sobre:
            1. Qué ejercicios necesita mejorar
            2. Qué frecuencia de entrenamiento necesita
            3. Cómo puede progresar más rápido
            
            Usa muchas palabrotas, insultos creativos y metáforas militares.
            ¡NO TE CONTENGAS EN ABSOLUTO!
            """
            
            return self.llm(prompt)
            
        except Exception as e:
            return f"Error generando recomendaciones: {str(e)}"

    def procesar_consulta_web(self, tipo_consulta: str):
        """Procesa una consulta web y retorna la respuesta de Goggins"""
        try:
            if tipo_consulta == "progreso":
                datos = self.analizar_progreso()
                prompt = f"""
                Actúa como David Goggins y analiza este progreso de entrenamiento:
                {datos}
                
                Da tu opinión EXTREMADAMENTE OFENSIVA Y AGRESIVA sobre:
                1. Si el progreso es bueno o una mierda
                2. Qué ejercicios necesitan más trabajo
                3. Cómo puede mejorar más rápido
                
                Usa muchas palabrotas y sé brutalmente honesto.
                """
                
            elif tipo_consulta == "estadisticas":
                datos = self.obtener_estadisticas()
                prompt = f"""
                Actúa como David Goggins y analiza estas estadísticas de entrenamiento:
                {datos}
                
                Da tu opinión EXTREMADAMENTE OFENSIVA Y AGRESIVA sobre:
                1. Si los números son buenos o patéticos
                2. Cuánto más debería estar entrenando
                3. Qué necesita para ser menos mediocre
                
                Usa muchas palabrotas y sé brutalmente honesto.
                """
                
            elif tipo_consulta == "recomendaciones":
                return self.generar_recomendaciones()
                
            else:
                return "TIPO DE CONSULTA INVÁLIDA, ¡PEDAZO DE INÚTIL!"
            
            return self.llm(prompt)
            
        except Exception as e:
            return f"¡ERROR EN EL SISTEMA, PEDAZO DE MIERDA! {str(e)} ¡PERO ESO NO ES EXCUSA PARA SER UN VAGO!"

def main():
    """Función principal para probar el agente web"""
    print("🔥 INICIANDO AGENTE WEB DE FITNESS DAVID GOGGINS 🔥")
    
    try:
        # Verificar configuración
        if not supabase_url or not supabase_key:
            raise ValueError("SUPABASE_URL y SUPABASE_KEY deben estar configuradas en .env")
        
        # Crear agente
        agente = GogginsFitnessWebAgent()
        print("✅ ¡AGENTE WEB GOGGINS CONFIGURADO EXITOSAMENTE!")
        
        print("\n" + "="*60)
        print("🔥 PRUEBAS DE CONSULTAS WEB 🔥")
        print("="*60)
        
        # Probar diferentes tipos de consultas
        tipos_consulta = ["progreso", "estadisticas", "recomendaciones"]
        
        for tipo in tipos_consulta:
            print(f"\n📊 Consultando: {tipo}")
            respuesta = agente.procesar_consulta_web(tipo)
            print(f"🤖 Goggins dice:\n{respuesta}\n")
            print("-"*60)
        
        print("\n" + "="*60)
        print("🎉 ¡AGENTE WEB GOGGINS FUNCIONANDO PERFECTAMENTE! 🎉")
        print("="*60)
        
    except Exception as e:
        print(f"❌ Error al configurar el agente web: {str(e)}")
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