# 🔥 Agente de Fitness David Goggins

Este proyecto implementa un agente de IA con la personalidad de David Goggins que registra entrenamientos de usuarios a través de WhatsApp y los almacena en Supabase. El agente es implacable, directo y brutalmente honesto, motivando a los usuarios a superar sus límites.

## 🚀 Características

- **Personalidad de David Goggins**: Lenguaje crudo, directo y motivacional
- **Registro de Entrenamientos**: Via WhatsApp con lenguaje natural
- **Sobrecarga Progresiva**: Análisis automático de progreso
- **Base de Datos Supabase**: Almacenamiento persistente de records
- **Memoria de Conversación**: Contexto de entrenamientos anteriores
- **Análisis de Progreso**: Comparación automática con records anteriores
- **Integración WhatsApp**: Via Twilio con webhook automático
- **API REST**: FastAPI con documentación automática

## 📋 Requisitos Previos

1. **Python 3.8+** instalado
2. **Cuenta de OpenAI** con saldo disponible
3. **Proyecto Supabase** configurado
4. **Cuenta de Twilio** con WhatsApp habilitado
5. **ngrok** instalado para tunneling

## 🔧 Instalación

1. **Clonar o descargar el proyecto**

   ```bash
   git clone <tu-repositorio>
   cd backend
   ```

2. **Instalar dependencias**

   ```bash
   pip install -r requirements.txt
   ```

3. **Configurar variables de entorno**
   
   Crea un archivo `.env` en la raíz del proyecto:

   ```env
   # OpenAI API Key
   OPENAI_API_KEY=sk-tu_api_key_de_openai_aqui

   # Supabase Configuration
   SUPABASE_URL=https://tu-proyecto.supabase.co
   SUPABASE_KEY=tu_supabase_anon_key_aqui
   
   # Twilio Configuration
   TWILIO_ACCOUNT_SID=tu_account_sid_de_twilio
   TWILIO_AUTH_TOKEN=tu_auth_token_de_twilio
   TWILIO_PHONE_NUMBER=whatsapp:+1234567890
   ```

## 🗄️ Configuración de Supabase

### 1. Crear la tabla de entrenamientos

```sql
CREATE TABLE workouts (
  id SERIAL PRIMARY KEY,
  user_phone TEXT NOT NULL,
  exercise TEXT NOT NULL,
  sets INT NOT NULL,
  reps INT NOT NULL,
  weight_kg FLOAT NOT NULL,
  is_progress BOOLEAN NOT NULL,
  created_at TIMESTAMPTZ DEFAULT NOW()
);
```

### 2. Configurar políticas de seguridad

```sql
-- Permitir inserción de entrenamientos
CREATE POLICY "Users can insert their own workouts" ON workouts
FOR INSERT WITH CHECK (true);

-- Permitir lectura de entrenamientos propios
CREATE POLICY "Users can view their own workouts" ON workouts
FOR SELECT USING (true);
```

## 📱 Configuración de Twilio WhatsApp

### Ejecutar el agente completo
```bash
python start_server.py
```

### Usar el agente en tu código
```python
from agente import GogginsFitnessAgent

# Crear el agente
agente = GogginsFitnessAgent()

# Procesar mensaje de WhatsApp
mensaje = "Bench press 3x8 @ 80kg"
user_phone = "+1234567890"
respuesta = agente.procesar_mensaje_whatsapp(mensaje, user_phone)
print(respuesta)
```

## 📱 Formato de Mensajes

### Registro de Entrenamiento

El agente reconoce automáticamente entrenamientos en formato:

- `"Bench press 3x8 @ 80kg"`
- `"Squat 4x10 @ 100kg"`
- `"Deadlift 3x5 @ 120kg"`

### Ejercicios Soportados

- **bench_press**: bench, press, pecho, pectoral
- **squat**: squat, sentadilla, pierna
- **deadlift**: deadlift, peso muerto, muerto
- **pull_up**: pull-up, dominada, dominadas
- **push_up**: push-up, flexión, flexiones
- **curl**: curl, bicep, bíceps
- **overhead_press**: overhead, press, hombro, militar

## 🛠️ Funcionalidades del Agente

### 1. Análisis de Progreso

- Compara automáticamente con el último record
- Detecta sobrecarga progresiva (peso, reps, series)
- Responde según el nivel de progreso

### 2. Personalidad de Goggins

- **Con progreso**: "¡BIEN! ¡Finalmente estás dejando de ser un puto perdedor!"
- **Sin progreso**: "¡¿ESTO ES UNA BROMA?! ¡Tu último entrenamiento se está riendo de ti!"
- **Saludos**: "¡¿QUÉ CARAJO QUIERES?! ¡No tengo tiempo para saludos de mierda!"

### 3. Memoria y Contexto

- Recuerda entrenamientos anteriores
- Mantiene historial de conversación
- Analiza tendencias de progreso

## 🔌 Integración con WhatsApp

### Webhook Endpoint
```python
from flask import Flask, request, jsonify
from agente import GogginsFitnessAgent

app = Flask(__name__)
agente = GogginsFitnessAgent()

@app.route('/webhook', methods=['POST'])
def webhook():
    data = request.json
    
    # Extraer mensaje y número de teléfono
    mensaje = data['message']['text']
    user_phone = data['message']['from']
    
    # Procesar con Goggins
    respuesta = agente.procesar_mensaje_whatsapp(mensaje, user_phone)
    
    return jsonify({
        'response': respuesta,
        'status': 'success'
    })

if __name__ == '__main__':
    app.run(debug=True, port=5000)
```

## 📊 Análisis de Datos

### Consultas Útiles en Supabase

```sql
-- Últimos entrenamientos de un usuario
SELECT * FROM workouts
WHERE user_phone = '+1234567890'
ORDER BY created_at DESC
LIMIT 10;

-- Progreso por ejercicio
SELECT exercise,
       MAX(weight_kg) as max_weight,
       MAX(reps) as max_reps,
       COUNT(*) as total_workouts
FROM workouts
WHERE user_phone = '+1234567890'
GROUP BY exercise;

-- Entrenamientos con progreso
SELECT * FROM workouts
WHERE user_phone = '+1234567890'
AND is_progress = true
ORDER BY created_at DESC;
```

## ⚙️ Configuración Avanzada

### Personalizar Respuestas

Modifica la función `generar_respuesta_goggins()` para ajustar:

- Nivel de intensidad del lenguaje
- Tipos de ejercicios reconocidos
- Criterios de progreso

### Agregar Nuevos Ejercicios

```python
patrones = {
    'bench_press': r'bench|press|pecho|pectoral',
    'squat': r'squat|sentadilla|pierna',
    # Agregar nuevo ejercicio
    'new_exercise': r'patron|regex|aqui'
}
```

### Configurar Logging
```python
# En server.py
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
```

## 🔍 Solución de Problemas

### Error: "SUPABASE_URL y SUPABASE_KEY deben estar configuradas"
- Verifica que el archivo `.env` existe
- Asegúrate de que todas las variables estén correctamente definidas

### Error: "Incorrect API key provided"

- Verifica que tu API key de OpenAI sea válida
- Asegúrate de tener saldo en tu cuenta

### Error: "Table 'workouts' does not exist"

- Ejecuta el script SQL para crear la tabla en Supabase
- Verifica las políticas de seguridad

### Error: "Webhook not receiving messages"
- Verifica que ngrok esté ejecutándose
- Confirma que la URL del webhook en Twilio sea correcta
- Revisa los logs del servidor para errores

### Error: "Twilio authentication failed"
- Verifica TWILIO_ACCOUNT_SID y TWILIO_AUTH_TOKEN
- Asegúrate de que las credenciales sean correctas

## 📝 Estructura del Proyecto

```
backend/
├── agente.py          # Agente principal de David Goggins
├── server.py          # Servidor FastAPI con webhook
├── start_server.py    # Script para iniciar el servidor
├── requirements.txt   # Dependencias del proyecto
├── README.md         # Este archivo
└── .env              # Variables de entorno (crear tú)
```

## 🎯 Próximos Pasos

1. **Dashboard web con NextJS**
2. **Análisis avanzado de progreso**
3. **Generación automática de rutinas**
4. **Notificaciones y recordatorios**
5. **Integración con más plataformas**

## 🤝 Contribuir

1. Fork el proyecto
2. Crea una rama para tu feature
3. Commit tus cambios
4. Push a la rama
5. Abre un Pull Request

## 📄 Licencia

Este proyecto está bajo la Licencia MIT.

## 🆘 Soporte

Si tienes problemas o preguntas:

1. Revisa la sección de solución de problemas
2. Verifica que todas las dependencias estén instaladas
3. Asegúrate de que tu API key sea válida
4. Confirma que la tabla de Supabase esté creada correctamente 