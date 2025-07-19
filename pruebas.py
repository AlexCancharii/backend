import os
from dotenv import load_dotenv

load_dotenv()  # Carga el .env
print(os.environ["OPENAI_API_KEY"])  # Debería imprimir tu clave
