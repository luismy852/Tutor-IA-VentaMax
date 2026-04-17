# VentaMax Tutor IA

Tutor inteligente basado en IA para entrenar equipos de ventas B2B. Evalúa respuestas sobre técnicas de venta, genera retroalimentación específica por pregunta y permite conversaciones de seguimiento con simulación de clientes reales.

## Stack

| Capa | Tecnología |
|---|---|
| Frontend | React 18, Server-Sent Events |
| Backend | Python 3.11+, FastAPI, aiosqlite |
| IA | OpenAI GPT-4o-mini |
| Base de datos | SQLite (archivo local) |

## Funcionalidades

- **Evaluación de 5 preguntas** sobre técnicas de venta con retroalimentación por cada respuesta
- **Retroalimentación general** al finalizar la evaluación
- **Chat de seguimiento** con contexto completo de la evaluación
- **Simulación de ventas**: el tutor actúa como cliente PyME con identidad secreta (El Quemado / El Tacaño / El Asfixiado)
- **Análisis post-simulación** con calificación del desempeño del vendedor
- **Streaming en tiempo real** con efecto typewriter en todas las respuestas
- **Persistencia de sesión** mediante localStorage

## Requisitos previos

- Python 3.11 o superior
- Node.js 18 o superior
- Una API key de OpenAI — [obtenerla aquí](https://platform.openai.com/api-keys)
## Clonar el repositorio
```bash
git clone https://github.com/luismy852/Tutor-IA-VentaMax.git
cd Tutor-IA-VentaMax
```

## Configuración del backend

```bash
cd back

# Crear entorno virtual
python -m venv venv

# Activar entorno virtual
# Windows:
venv\Scripts\activate
# macOS/Linux:
source venv/bin/activate

# Instalar dependencias
pip install -r requirements.txt

# Configurar variables de entorno
cp .env.example .env
# Editar .env y añadir tu OPENAI_API_KEY
```

## Configuración del frontend

```bash
cd front

# Instalar dependencias
npm install

# Configurar variables de entorno
cp .env.example .env.local
# El valor por defecto (http://localhost:8000) funciona sin cambios para desarrollo local
```

## Variables de entorno

### Backend (`back/.env`)

| Variable | Requerida | Descripción | Default |
|---|---|---|---|
| `OPENAI_API_KEY` | Sí | Clave de API de OpenAI | — |
| `DATABASE_URL` | No | Ruta del archivo SQLite | `conversations.db` |
| `OPENAI_MODEL` | No | Modelo de OpenAI | `gpt-4o-mini` |
| `CORS_ORIGINS` | No | Orígenes permitidos | `["http://localhost:3000"]` |

### Frontend (`front/tutor-ia-front/.env.local`)

| Variable | Descripción | Default |
|---|---|---|
| `REACT_APP_API_URL` | URL base del backend | `http://localhost:8000` |

## Ejecución

Abrir dos terminales:

**Terminal 1 — Backend:**
```bash
cd back
uvicorn main:app --reload
```
El servidor queda disponible en `http://localhost:8000`.
Documentación de la API: `http://localhost:8000/docs`

**Terminal 2 — Frontend:**
```bash
cd front
npm start
```
La aplicación queda disponible en `http://localhost:3000`.

## Flujo de uso

1. Al entrar, se crea una sesión automáticamente y comienza la evaluación
2. El tutor presenta 5 preguntas sobre técnicas de venta B2B
3. Después de cada respuesta, el tutor genera retroalimentación específica en tiempo real
4. Al terminar las 5 preguntas, se genera un análisis general
5. El usuario pasa al modo chat para preguntas de seguimiento
6. Cuando el usuario domina el tema, el tutor propone una simulación de ventas
7. Si el usuario lo solicita explícitamente (ej. *"quiero simular"*, *"hagamos un roleplay"*), comienza la simulación: el tutor actúa como cliente PyME con objeciones reales
8. Al cerrar la simulación, se genera un análisis del desempeño con calificación
9. El botón **Nuevo Chat** reinicia la sesión desde cero
