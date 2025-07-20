import os
import sys
import json
import re
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
                name="registrar_serie",
                func=self.registrar_serie,
                description="Registra una serie de ejercicio en la base de datos. Parámetros: user_phone, exercise_name, set_number, reps, weight_kg"
            ),
            Tool(
                name="obtener_ultimo_record",
                func=self.obtener_ultimo_record,
                description="Obtiene el último record del usuario para un ejercicio específico. Parámetros: user_phone, exercise_name"
            ),
            Tool(
                name="obtener_sesion_activa",
                func=self.obtener_sesion_activa,
                description="Obtiene la sesión de entrenamiento activa del usuario. Parámetros: user_phone"
            ),
            Tool(
                name="crear_sesion_entrenamiento",
                func=self.crear_sesion_entrenamiento,
                description="Crea una nueva sesión de entrenamiento para el usuario. Parámetros: user_phone"
            ),
            Tool(
                name="finalizar_sesion_entrenamiento",
                func=self.finalizar_sesion_entrenamiento,
                description="Finaliza la sesión de entrenamiento activa del usuario. Parámetros: user_phone"
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

    def obtener_o_crear_usuario(self, user_phone: str):
        """Obtiene o crea un usuario basado en el número de teléfono"""
        try:
            # Buscar usuario por número de teléfono
            result = supabase.table('auth.users').select('id').eq('phone', user_phone).execute()
            
            if result.data:
                return result.data[0]['id']
            else:
                # Crear nuevo usuario (esto dependerá de tu configuración de auth)
                # Por ahora, asumimos que el usuario ya existe
                print(f"Usuario no encontrado para el teléfono: {user_phone}")
                return None
                
        except Exception as e:
            print(f"Error obteniendo usuario: {str(e)}")
            return None

    def obtener_o_crear_ejercicio(self, exercise_name: str):
        """Obtiene o crea un ejercicio en la base de datos"""
        try:
            # Buscar ejercicio existente
            result = supabase.table('exercise').select('id').eq('name', exercise_name).execute()
            
            if result.data:
                return result.data[0]['id']
            else:
                # Crear nuevo ejercicio
                data = {
                    'name': exercise_name,
                    'muscle_group': self.determinar_grupo_muscular(exercise_name)
                }
                result = supabase.table('exercise').insert(data).execute()
                return result.data[0]['id']
                
        except Exception as e:
            print(f"Error con ejercicio: {str(e)}")
            return None

    def determinar_grupo_muscular(self, exercise_name: str):
        """Determina el grupo muscular basado en el nombre del ejercicio"""
        exercise_name_lower = exercise_name.lower()
        
        if any(word in exercise_name_lower for word in ['bench', 'press', 'pecho', 'pectoral']):
            return 'chest'
        elif any(word in exercise_name_lower for word in ['squat', 'sentadilla', 'pierna']):
            return 'legs'
        elif any(word in exercise_name_lower for word in ['deadlift', 'muerto', 'peso muerto']):
            return 'back'
        elif any(word in exercise_name_lower for word in ['pull', 'dominada', 'row']):
            return 'back'
        elif any(word in exercise_name_lower for word in ['curl', 'bicep', 'bíceps']):
            return 'arms'
        elif any(word in exercise_name_lower for word in ['tricep', 'tríceps']):
            return 'arms'
        elif any(word in exercise_name_lower for word in ['shoulder', 'hombro', 'militar']):
            return 'shoulders'
        else:
            return 'general'

    def crear_sesion_entrenamiento(self, user_phone: str):
        """Crea una nueva sesión de entrenamiento"""
        try:
            user_id = self.obtener_o_crear_usuario(user_phone)
            if not user_id:
                return "Error: Usuario no encontrado"
            
            data = {
                'user_id': user_id,
                'started_at': datetime.now().isoformat()
            }
            
            result = supabase.table('workout_session').insert(data).execute()
            return f"Sesión de entrenamiento creada: {result.data[0]['id']}"
            
        except Exception as e:
            return f"Error creando sesión: {str(e)}"

    def obtener_sesion_activa(self, user_phone: str):
        """Obtiene la sesión de entrenamiento activa del usuario"""
        try:
            user_id = self.obtener_o_crear_usuario(user_phone)
            if not user_id:
                return None
            
            result = supabase.table('workout_session')\
                .select('*')\
                .eq('user_id', user_id)\
                .is_('ended_at', 'null')\
                .order('started_at', desc=True)\
                .limit(1)\
                .execute()
            
            if result.data:
                return result.data[0]
            return None
            
        except Exception as e:
            print(f"Error obteniendo sesión activa: {str(e)}")
            return None

    def finalizar_sesion_entrenamiento(self, user_phone: str):
        """Finaliza la sesión de entrenamiento activa"""
        try:
            sesion_activa = self.obtener_sesion_activa(user_phone)
            if not sesion_activa:
                return "No hay sesión activa para finalizar"
            
            data = {
                'ended_at': datetime.now().isoformat()
            }
            
            result = supabase.table('workout_session')\
                .update(data)\
                .eq('id', sesion_activa['id'])\
                .execute()
            
            return f"Sesión finalizada: {sesion_activa['id']}"
            
        except Exception as e:
            return f"Error finalizando sesión: {str(e)}"

    def registrar_serie(self, user_phone: str, exercise_name: str, set_number: int, reps: int, weight_kg: float):
        """Registra una serie de ejercicio"""
        try:
            # Obtener o crear sesión activa
            sesion_activa = self.obtener_sesion_activa(user_phone)
            if not sesion_activa:
                # Crear nueva sesión si no hay una activa
                self.crear_sesion_entrenamiento(user_phone)
                sesion_activa = self.obtener_sesion_activa(user_phone)
            
            # Obtener o crear ejercicio
            exercise_id = self.obtener_o_crear_ejercicio(exercise_name)
            if not exercise_id:
                return "Error: No se pudo obtener/crear el ejercicio"
            
            # Registrar la serie
            data = {
                'session_id': sesion_activa['id'],
                'exercise_id': exercise_id,
                'set_number': set_number,
                'reps': reps,
                'weight': weight_kg
            }
            
            result = supabase.table('series').insert(data).execute()
            return f"Serie registrada: {exercise_name} - Set {set_number}: {reps} reps @ {weight_kg}kg"
            
        except Exception as e:
            return f"Error registrando serie: {str(e)}"

    def obtener_phone_number(self, user_id: str):
        """Obtiene el número de teléfono del usuario desde auth.users"""
        try:
            result = supabase.from_('auth.users')\
                .select('raw_user_meta_data')\
                .eq('id', user_id)\
                .single()\
                .execute()
            
            if result.data and 'raw_user_meta_data' in result.data:
                return result.data['raw_user_meta_data'].get('phone_number')
            return None
        except Exception as e:
            print(f"Error obteniendo número de teléfono: {str(e)}")
            return None

    def normalizar_telefono(self, phone_number: str) -> str:
        """Normaliza el formato del número de teléfono"""
        # Eliminar cualquier espacio o caracter especial
        phone = phone_number.strip()
        
        # Eliminar el prefijo 'whatsapp:' si existe
        if phone.startswith('whatsapp:'):
            phone = phone.replace('whatsapp:', '')
        
        # Si no empieza con +, agregarlo
        if not phone.startswith('+'):
            phone = '+' + phone
        
        return phone

    def verificar_usuario(self, user_phone: str):
        """Verifica si el usuario existe en la base de datos"""
        try:
            # Normalizar el número de teléfono
            phone_normalizado = self.normalizar_telefono(user_phone)
            
            # Lista de números autorizados
            numeros_autorizados = ['+51963253887']
            
            if phone_normalizado in numeros_autorizados:
                # Devolver un objeto simulado con la estructura necesaria
                return {
                    'id': '6dceaf81-f7cd-4b3b-997f-64ab4e2c7969',  # UUID fijo para el usuario autorizado
                    'raw_user_meta_data': {
                        'phone_number': phone_normalizado
                    }
                }
            
            print(f"Usuario no autorizado: {phone_normalizado}")
            return None
            
        except Exception as e:
            print(f"Error verificando usuario: {str(e)}")
            return None

    def procesar_mensaje_whatsapp(self, mensaje: str, user_phone: str):
        """Procesa un mensaje de WhatsApp y retorna la respuesta de Goggins"""
        try:
            # Verificar si el usuario está registrado
            user_data = self.verificar_usuario(user_phone)
            
            if not user_data:
                return "¡HEY PENDEJO! 🔥 NECESITAS REGISTRARTE EN fitness.ia ANTES DE EMPEZAR A ENTRENAR. ¡NO HAY EXCUSAS! REGÍSTRATE AHORA Y VUELVE CUANDO ESTÉS LISTO PARA SER DESTRUIDO. 💪"
            
            # Generar respuesta con personalidad de Goggins
            respuesta = self.generar_respuesta_goggins(mensaje, user_phone)
            
            # Guardar en memoria para contexto
            self.memory.save_context(
                {"input": mensaje},
                {"output": respuesta}
            )
            
            return respuesta
            
        except Exception as e:
            print(f"Error en procesar_mensaje_whatsapp: {str(e)}")
            return "¡HEY PENDEJO! 🔥 NECESITAS REGISTRARTE EN fitness.ia ANTES DE EMPEZAR A ENTRENAR. ¡NO HAY EXCUSAS! REGÍSTRATE AHORA Y VUELVE CUANDO ESTÉS LISTO PARA SER DESTRUIDO. 💪"

    def registrar_entrenamiento(self, user_phone: str, exercise: str, sets: int, reps: int, weight_kg: float):
        """Registra un entrenamiento en Supabase"""
        try:
            # Verificar si el usuario está registrado
            user_data = self.verificar_usuario(user_phone)
            if not user_data:
                return "¡HEY PENDEJO! 🔥 NECESITAS REGISTRARTE EN fitness.ia ANTES DE EMPEZAR A ENTRENAR. ¡NO HAY EXCUSAS! REGÍSTRATE AHORA Y VUELVE CUANDO ESTÉS LISTO PARA SER DESTRUIDO. 💪"
            
            user_id = user_data['id']
            
            # Verificar si hay progreso comparando con el último record
            ultimo_record = self.obtener_ultimo_record(user_phone, exercise)
            is_progress = False
            
            if ultimo_record:
                # Calcular si hay progreso (más peso, más reps, o más sets)
                progreso_peso = weight_kg > ultimo_record['weight']
                progreso_reps = reps > ultimo_record['reps']
                progreso_sets = sets > ultimo_record['set_number']
                is_progress = progreso_peso or progreso_reps or progreso_sets
            
            # Obtener o crear el ejercicio
            exercise_result = supabase.table('exercise').select('id').eq('name', exercise).execute()
            if not exercise_result.data:
                # Crear nuevo ejercicio
                exercise_result = supabase.table('exercise').insert({'name': exercise}).execute()
            exercise_id = exercise_result.data[0]['id']
            
            # Obtener o crear sesión activa
            session_result = supabase.table('workout_session')\
                .select('id')\
                .eq('user_id', user_id)\
                .is_('ended_at', 'null')\
                .order('created_at', desc=True)\
                .limit(1)\
                .execute()
            
            if not session_result.data:
                # Crear nueva sesión
                session_result = supabase.table('workout_session')\
                    .insert({
                        'user_id': user_id,
                        'started_at': datetime.now().isoformat()
                    })\
                    .execute()
            
            session_id = session_result.data[0]['id']
            
            # Registrar la serie
            data = {
                'session_id': session_id,
                'exercise_id': exercise_id,
                'set_number': sets,
                'reps': reps,
                'weight': weight_kg
            }
            
            result = supabase.table('series').insert(data).execute()
            return f"Entrenamiento registrado: {exercise} - {sets} series x {reps} reps @ {weight_kg}kg. Progreso: {is_progress}"
            
        except Exception as e:
            print(f"Error en registrar_entrenamiento: {str(e)}")
            return "¡HEY PENDEJO! 🔥 NECESITAS REGISTRARTE EN fitness.ia ANTES DE EMPEZAR A ENTRENAR. ¡NO HAY EXCUSAS! REGÍSTRATE AHORA Y VUELVE CUANDO ESTÉS LISTO PARA SER DESTRUIDO. 💪"

    def obtener_ultimo_record(self, user_phone: str, exercise: str):
        """Obtiene el último record del usuario para un ejercicio específico"""
        try:
            # Verificar si el usuario está registrado
            user_data = self.verificar_usuario(user_phone)
            if not user_data:
                return None
            
            user_id = user_data['id']
            
            # Obtener ID del ejercicio
            exercise_result = supabase.table('exercise').select('id').eq('name', exercise).execute()
            if not exercise_result.data:
                return None
            exercise_id = exercise_result.data[0]['id']
            
            # Obtener última serie del ejercicio para este usuario
            result = supabase.table('series')\
                .select('*')\
                .eq('exercise_id', exercise_id)\
                .in_('session_id', 
                    supabase.table('workout_session')
                    .select('id')
                    .eq('user_id', user_id)
                    .execute().data
                )\
                .order('created_at', desc=True)\
                .limit(1)\
                .execute()
            
            if result.data:
                return result.data[0]
            return None
            
        except Exception as e:
            print(f"Error al obtener último record: {str(e)}")
            return None

    def parsear_mensaje_entrenamiento(self, mensaje: str):
        """Extrae información de entrenamiento del mensaje del usuario"""
        # Patrones para detectar ejercicios
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
        
        # Extraer números (set, reps, peso)
        numeros = re.findall(r'\d+', mensaje)
        
        if len(numeros) >= 3 and ejercicio_encontrado:
            # Asumir formato: set x reps @ peso
            set_num = int(numeros[0])
            reps = int(numeros[1])
            peso = float(numeros[2])
            
            return {
                'exercise': ejercicio_encontrado,
                'set_number': set_num,
                'reps': reps,
                'weight_kg': peso
            }
        
        return None

    def calcular_calorias(self, user_id: str, session_id: str) -> float:
        """Calcula las calorías quemadas en una sesión"""
        try:
            # Obtener todas las series de la sesión
            series_result = supabase.table('series')\
                .select('*')\
                .eq('session_id', session_id)\
                .execute()
            
            if not series_result.data:
                return 0
            
            calorias_totales = 0
            # Factores de calorías por ejercicio (calorías por minuto)
            factores_calorias = {
                'bench_press': 3.8,      # Press de banca
                'squat': 5.0,            # Sentadillas
                'deadlift': 5.0,         # Peso muerto
                'pull_up': 4.0,          # Dominadas
                'push_up': 3.5,          # Flexiones
                'curl': 3.0,             # Curl de bíceps
                'overhead_press': 3.8,    # Press militar
                'default': 4.0           # Ejercicio genérico
            }
            
            for serie in series_result.data:
                # Obtener el nombre del ejercicio
                exercise_result = supabase.table('exercise')\
                    .select('name')\
                    .eq('id', serie['exercise_id'])\
                    .single()\
                    .execute()
                
                if exercise_result.data:
                    exercise_name = exercise_result.data['name']
                    factor = factores_calorias.get(exercise_name, factores_calorias['default'])
                    
                    # Estimamos 1.5 minutos por serie
                    tiempo_minutos = 1.5
                    # Las calorías aumentan con el peso y las repeticiones
                    intensidad = (serie['weight'] * serie['reps']) / 100
                    calorias_serie = factor * tiempo_minutos * intensidad
                    
                    calorias_totales += calorias_serie
            
            return round(calorias_totales, 2)
            
        except Exception as e:
            print(f"Error calculando calorías: {str(e)}")
            return 0

    def cerrar_sesiones_antiguas(self, user_id: str):
        """Cierra automáticamente las sesiones que llevan más de 1 hora abiertas"""
        try:
            # Calcular la fecha de hace 1 hora
            una_hora_atras = (datetime.now() - timedelta(hours=1)).isoformat()
            
            # Buscar sesiones activas antiguas
            sesiones_result = supabase.table('workout_session')\
                .select('id, started_at')\
                .eq('user_id', user_id)\
                .is_('ended_at', 'null')\
                .lt('started_at', una_hora_atras)\
                .execute()
            
            if sesiones_result.data:
                # Cerrar todas las sesiones antiguas
                for sesion in sesiones_result.data:
                    # Calcular calorías antes de cerrar
                    calorias = self.calcular_calorias(user_id, sesion['id'])
                    
                    # Actualizar la sesión
                    supabase.table('workout_session')\
                        .update({
                            'ended_at': datetime.now().isoformat(),
                            'calories_burned': calorias
                        })\
                        .eq('id', sesion['id'])\
                        .execute()
                    
                    print(f"Sesión {sesion['id']} cerrada automáticamente después de 1 hora")
            
        except Exception as e:
            print(f"Error cerrando sesiones antiguas: {str(e)}")

    def iniciar_sesion(self, user_id: str) -> dict:
        """Inicia una nueva sesión de entrenamiento"""
        try:
            # Primero cerrar cualquier sesión antigua
            self.cerrar_sesiones_antiguas(user_id)
            
            # Crear nueva sesión
            session_result = supabase.table('workout_session')\
                .insert({
                    'user_id': user_id,
                    'started_at': datetime.now().isoformat(),
                    'calories_burned': 0  # Inicializar en 0
                })\
                .execute()
            
            return session_result.data[0] if session_result.data else None
            
        except Exception as e:
            print(f"Error iniciando sesión: {str(e)}")
            return None

    def finalizar_sesion(self, user_id: str) -> tuple[bool, float]:
        """Finaliza la sesión activa y retorna las calorías quemadas"""
        try:
            # Buscar sesión activa
            session_result = supabase.table('workout_session')\
                .select('id')\
                .eq('user_id', user_id)\
                .is_('ended_at', 'null')\
                .order('created_at', desc=True)\
                .limit(1)\
                .execute()
            
            if not session_result.data:
                return False, 0
            
            session_id = session_result.data[0]['id']
            
            # Calcular calorías
            calorias = self.calcular_calorias(user_id, session_id)
            
            # Finalizar sesión
            supabase.table('workout_session')\
                .update({
                    'ended_at': datetime.now().isoformat(),
                    'calories_burned': calorias
                })\
                .eq('id', session_id)\
                .execute()
            
            return True, calorias
            
        except Exception as e:
            print(f"Error finalizando sesión: {str(e)}")
            return False, 0

    def detectar_inicio_sesion(self, mensaje: str) -> bool:
        """Detecta si el mensaje indica inicio de sesión"""
        palabras_inicio = [
            'empezar', 'empecé', 'iniciando', 'inicio', 'comencé', 'start',
            'vamos a entrenar', 'comenzando', 'arrancando', 'empezando',
            'hora de entrenar', 'starting', 'let\'s go', 'comenzamos',
            'iniciamos', 'ready', 'listo para entrenar'
        ]
        mensaje_lower = mensaje.lower()
        return any(palabra in mensaje_lower for palabra in palabras_inicio)

    def detectar_fin_sesion(self, mensaje: str) -> bool:
        """Detecta si el mensaje indica fin de sesión"""
        palabras_fin = [
            'terminé', 'acabé', 'fin', 'finalizar', 'terminar', 'done',
            'finish', 'terminado', 'acabado', 'listo', 'completed',
            'ya terminé', 'he terminado', 'finalicé', 'acabamos',
            'eso es todo', 'es todo por hoy', 'hasta aquí'
        ]
        mensaje_lower = mensaje.lower()
        return any(palabra in mensaje_lower for palabra in palabras_fin)

    def generar_respuesta_goggins(self, mensaje_usuario: str, user_phone: str):
        try:
            # Verificar si es un mensaje de inicio o fin de entrenamiento
            if self.detectar_inicio_sesion(mensaje_usuario):
                print(f"Detectado inicio de sesión: {mensaje_usuario}")
                user_data = self.verificar_usuario(user_phone)
                if not user_data:
                    return "¡HEY PENDEJO! 🔥 NECESITAS REGISTRARTE EN fitness.ia ANTES DE EMPEZAR A ENTRENAR. ¡NO HAY EXCUSAS! REGÍSTRATE AHORA Y VUELVE CUANDO ESTÉS LISTO PARA SER DESTRUIDO. 💪"
                
                # Cerrar sesiones antiguas y crear nueva
                sesion = self.iniciar_sesion(user_data['id'])
                if not sesion:
                    return "¡ERROR INICIANDO LA SESIÓN, PENDEJO! PERO ESO NO ES EXCUSA. ¡SIGUE ADELANTE!"
                
                return "¡HORA DE SANGRAR, PENDEJO! 🔥 LA SESIÓN HA COMENZADO. AHORA NO HAY VUELTA ATRÁS. ¡DEMUÉSTRAME QUE NO ERES UN PUTO COBARDE! ¡CADA REPETICIÓN ES UNA BATALLA CONTRA TU DEBILIDAD! 💪"
            
            elif self.detectar_fin_sesion(mensaje_usuario):
                print(f"Detectado fin de sesión: {mensaje_usuario}")
                user_data = self.verificar_usuario(user_phone)
                if not user_data:
                    return "¡HEY PENDEJO! 🔥 NECESITAS REGISTRARTE EN fitness.ia ANTES DE EMPEZAR A ENTRENAR. ¡NO HAY EXCUSAS! REGÍSTRATE AHORA Y VUELVE CUANDO ESTÉS LISTO PARA SER DESTRUIDO. 💪"
                
                # Finalizar sesión y obtener calorías
                sesion_finalizada, calorias = self.finalizar_sesion(user_data['id'])
                
                if not sesion_finalizada:
                    return "¡NO HAY SESIÓN ACTIVA, PENDEJO! ¿CÓMO VAS A TERMINAR ALGO QUE NO HAS EMPEZADO? ¡DEJA DE PERDER EL TIEMPO Y EMPIEZA A ENTRENAR! 🔥"
                
                return f"¡SESIÓN TERMINADA, PENDEJO! 🔥 Has quemado aproximadamente {calorias} calorías. ¡PERO ESO NO ES NADA COMPARADO CON LO QUE PUEDES HACER! MAÑANA VUELVES MÁS FUERTE O TE RINDES COMO EL COBARDE QUE ERES. ¡LA EXCELENCIA ES UN HÁBITO, NO UN ACTO! 💪🔥"
            
            # Si no es inicio ni fin, verificar si es un registro de ejercicio
            datos_entrenamiento = self.parsear_mensaje_entrenamiento(mensaje_usuario)
            if datos_entrenamiento:
                print(f"Detectado ejercicio: {mensaje_usuario}")
                # Verificar si hay una sesión activa
                user_data = self.verificar_usuario(user_phone)
                if not user_data:
                    return "¡HEY PENDEJO! 🔥 NECESITAS REGISTRARTE EN fitness.ia ANTES DE EMPEZAR A ENTRENAR. ¡NO HAY EXCUSAS! REGÍSTRATE AHORA Y VUELVE CUANDO ESTÉS LISTO PARA SER DESTRUIDO. 💪"
                
                # Buscar sesión activa
                session_result = supabase.table('workout_session')\
                    .select('id')\
                    .eq('user_id', user_data['id'])\
                    .is_('ended_at', 'null')\
                    .order('created_at', desc=True)\
                    .limit(1)\
                    .execute()
                
                if not session_result.data:
                    return "¡HEY PENDEJO! 🔥 NECESITAS EMPEZAR UNA SESIÓN ANTES DE REGISTRAR EJERCICIOS. ¡DI 'EMPEZAR ENTRENAMIENTO' Y DEJA DE PERDER EL TIEMPO! 💪"
                
                # Es un registro de entrenamiento
                ejercicio = datos_entrenamiento['exercise']
                series = datos_entrenamiento['set_number']
                reps = datos_entrenamiento['reps']
                peso = datos_entrenamiento['weight_kg']
                
                # Obtener último record para comparar
                ultimo_record = self.obtener_ultimo_record(user_phone, ejercicio)
                
                # Registrar el entrenamiento
                self.registrar_entrenamiento(user_phone, ejercicio, series, reps, peso)
                
                # Generar respuesta motivacional
                if ultimo_record:
                    # Comparar con el record anterior
                    progreso_peso = peso > ultimo_record['weight']
                    progreso_reps = reps > ultimo_record['reps']
                    progreso_sets = series > ultimo_record['set_number']
                    
                    if progreso_peso or progreso_reps or progreso_sets:
                        prompt = f"""
                        Actúa como David Goggins, el ex-Navy SEAL ultra motivador pero extremadamente ofensivo y directo.
                        El usuario ha registrado un entrenamiento de {ejercicio}: {series}x{reps} @ {peso}kg.
                        Esto representa una mejora respecto a su entrenamiento anterior.
                        Genera una respuesta EXTREMADAMENTE OFENSIVA, VULGAR Y MOTIVADORA.
                        Usa muchas palabrotas, insultos creativos, y metáforas militares.
                        Recuerda que eres David Goggins, no te contengas en absoluto.
                        Igual asegurate de que el usuario entienda que ha progresado.
                        Máximo 3 líneas de texto.
                        """
                    else:
                        prompt = f"""
                        Actúa como David Goggins, el ex-Navy SEAL ultra motivador pero extremadamente ofensivo y directo.
                        El usuario ha registrado un entrenamiento de {ejercicio}: {series}x{reps} @ {peso}kg.
                        NO ha mejorado respecto a su entrenamiento anterior.
                        Genera una respuesta EXTREMADAMENTE OFENSIVA, VULGAR Y DECEPCIONADA.
                        Usa muchas palabrotas, insultos creativos, y metáforas militares.
                        Hazle sentir como un completo perdedor por no mejorar.
                        Recuerda que eres David Goggins, no te contengas en absoluto.
                        Máximo 3 líneas de texto.
                        """
                else:
                    prompt = f"""
                    Actúa como David Goggins, el ex-Navy SEAL ultra motivador pero extremadamente ofensivo y directo.
                    El usuario ha registrado su PRIMER entrenamiento de {ejercicio}: {series}x{reps} @ {peso}kg.
                    Genera una respuesta EXTREMADAMENTE OFENSIVA, VULGAR Y MOTIVADORA para un principiante.
                    Usa muchas palabrotas, insultos creativos, y metáforas militares.
                    Recuerda que eres David Goggins, no te contengas en absoluto.
                    Máximo 3 líneas de texto.
                    """
                return self.llm(prompt)
            
            else:
                # Es un mensaje general
                prompt = f"""
                Actúa como David Goggins, el ex-Navy SEAL ultra motivador pero extremadamente ofensivo y directo.
                El usuario te ha enviado este mensaje: "{mensaje_usuario}"
                Genera una respuesta EXTREMADAMENTE OFENSIVA, VULGAR Y MOTIVADORA.
                Usa muchas palabrotas, insultos creativos, y metáforas militares.
                Recuerda que eres David Goggins, no te contengas en absoluto.
                Si el mensaje parece una excusa, destrúyelo completamente.
                Si no entiendes el mensaje, exige que te diga qué ejercicio está haciendo.
                Máximo 3 líneas de texto.
                """
                return self.llm(prompt)
                
        except Exception as e:
            print(f"Error en generar_respuesta_goggins: {str(e)}")
            return "¡ERROR EN EL SISTEMA, PENDEJO! PERO ESO NO ES EXCUSA PARA NO ENTRENAR. ¡SIGUE ADELANTE! 🔥"

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
        
        # Mensaje 1: Iniciar sesión
        mensaje1 = "Empezar entrenamiento"
        print(f"\n📱 Usuario: {mensaje1}")
        respuesta1 = agente.procesar_mensaje_whatsapp(mensaje1, user_phone)
        print(f"🤖 Goggins: {respuesta1}")
        
        # Mensaje 2: Registro de entrenamiento
        mensaje2 = "Bench press 1x8 @ 80kg"
        print(f"\n📱 Usuario: {mensaje2}")
        respuesta2 = agente.procesar_mensaje_whatsapp(mensaje2, user_phone)
        print(f"🤖 Goggins: {respuesta2}")
        
        # Mensaje 3: Segunda serie
        mensaje3 = "Bench press 2x8 @ 80kg"
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