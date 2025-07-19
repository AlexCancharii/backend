# 🤖 Agente con LangChain y GPT-4

Este proyecto implementa un agente inteligente usando LangChain y GPT-4 que puede realizar múltiples tareas como cálculos matemáticos, responder preguntas y proporcionar información del sistema.

## 🚀 Características

- **Modelo**: GPT-4 de OpenAI
- **Memoria**: Conversación persistente
- **Herramientas**: Calculadora e información del sistema
- **Configuración**: Variables de entorno seguras

## 📋 Requisitos Previos

1. **Python 3.8+** instalado
2. **Cuenta de OpenAI** con saldo disponible
3. **API Key de OpenAI**

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
   OPENAI_API_KEY=tu_api_key_de_openai_aqui
   ```

## 🎯 Uso

### Ejecutar el agente completo
```bash
python agente.py
```

### Usar el agente en tu código
```python
from agente import configurar_agente, ejecutar_agente

# Configurar el agente
agente = configurar_agente()

# Hacer una pregunta
respuesta = ejecutar_agente(agente, "¿Cuánto es 25 * 4?")
print(respuesta)
```

## 🛠️ Herramientas Disponibles

### 1. Calculadora
- **Descripción**: Realiza cálculos matemáticos
- **Ejemplo**: "¿Cuánto es 15 * 23?"

### 2. Información del Sistema
- **Descripción**: Proporciona información sobre el sistema operativo y Python
- **Ejemplo**: "¿Qué información tienes sobre el sistema?"

## ⚙️ Configuración Avanzada

### Parámetros del modelo
Puedes modificar estos parámetros en la función `configurar_agente()`:

```python
llm = OpenAI(
    model_name="gpt-4",     # Modelo a usar
    temperature=0.7,        # Creatividad (0.0-1.0)
    max_tokens=1000         # Máximo tokens en respuesta
)
```

### Agregar nuevas herramientas
Para agregar más herramientas, modifica la lista `herramientas`:

```python
herramientas = [
    # ... herramientas existentes ...
    Tool(
        name="Nueva Herramienta",
        func=tu_funcion,
        description="Descripción de la herramienta"
    )
]
```

## 🔍 Solución de Problemas

### Error: "OPENAI_API_KEY no está configurada"
- Verifica que el archivo `.env` existe
- Asegúrate de que la variable `OPENAI_API_KEY` esté correctamente definida

### Error: "No module named 'langchain'"
- Ejecuta: `pip install -r requirements.txt`

### Error: "Insufficient funds"
- Verifica que tu cuenta de OpenAI tenga saldo disponible

## 📝 Estructura del Proyecto

```
backend/
├── agente.py          # Archivo principal del agente
├── requirements.txt   # Dependencias del proyecto
├── README.md         # Este archivo
└── .env              # Variables de entorno (crear tú)
```

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