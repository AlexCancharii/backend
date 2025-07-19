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

3. **Instalar ngrok** (si no lo tienes)
   ```bash
   # Windows (con chocolatey)
   choco install ngrok
   
   # macOS (con homebrew)
   brew install ngrok
   
   # Linux
   wget https://bin.equinox.io/c/bNyj1mQVY4c/ngrok-v3-stable-linux-amd64.tgz
   tar xvzf ngrok-v3-stable-linux-amd64.tgz
   sudo mv ngrok /usr/local/bin
   ```

4. **Configurar variables de entorno**
   
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

### 1. Configurar WhatsApp Sandbox
1. Ve a [Twilio Console](https://console.twilio.com/)
2. Navega a **Messaging > Settings > WhatsApp Sandbox**
3. Copia el número de WhatsApp de Twilio
4. Agrega tu número personal al sandbox

### 2. Configurar Webhook
1. En la misma página de WhatsApp Sandbox
2. En **"When a message comes in"**, agrega tu URL de ngrok + `/webhook`
3. Ejemplo: `https://abc123.ngrok.io/webhook`
4. Guarda la configuración

## 🚀 Ejecutar el Servidor

### Opción 1: Script Automático (Recomendado)
```bash
python start_server.py
```

### Opción 2: Manual
```bash
# Terminal 1: Iniciar servidor
uvicorn server:app --reload --port 8000

# Terminal 2: Iniciar ngrok
ngrok http 8000
```

## 📡 Configuración del Webhook

### 1. Obtener URL de ngrok
Después de ejecutar `ngrok http 8000`, copia la URL HTTPS:
```
Forwarding    https://abc123.ngrok.io -> http://localhost:8000
```

### 2. Configurar en Twilio
1. Ve a [Twilio Console > WhatsApp Sandbox](https://console.twilio.com/us1/develop/messaging/manage/sandbox)
2. En **"When a message comes in"**, agrega: `https://abc123.ngrok.io/webhook`
3. Guarda los cambios

### 3. Probar la conexión
1. Envía un mensaje al número de WhatsApp de Twilio
2. Verifica que recibas respuesta del agente de Goggins
3. Revisa los logs del servidor para confirmar

## 🎯 Uso

### Enviar Mensajes de WhatsApp
Simplemente envía mensajes al número de Twilio:

- **Saludo**: "Hola, empecé mi entrenamiento"
- **Registro**: "Bench press 3x8 @ 80kg"
- **Más ejercicios**: "Squat 4x10 @ 100kg"
- **Finalizar**: "Terminé mi entrenamiento"

### Respuestas del Agente
- **Con progreso**: "¡BIEN! ¡Finalmente estás dejando de ser un puto perdedor!"
- **Sin progreso**: "¡¿ESTO ES UNA BROMA?! ¡Tu último entrenamiento se está riendo de ti!"
- **Saludos**: "¡¿QUÉ CARAJO QUIERES?! ¡No tengo tiempo para saludos de mierda!"

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

## 🔌 Endpoints de la API

### Webhook Principal
- **POST** `/webhook` - Recibe mensajes de WhatsApp

### Utilidades
- **GET** `/` - Página de información del webhook
- **GET** `/health` - Estado del servidor
- **POST** `/test-message` - Probar mensajes (desarrollo)

### Documentación Automática
- **GET** `/docs` - Swagger UI
- **GET** `/redoc` - ReDoc

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

### Error: "Variables de entorno faltantes"
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
5. Verifica la configuración del webhook en Twilio 