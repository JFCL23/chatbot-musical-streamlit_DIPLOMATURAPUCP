import os
import urllib.parse
import streamlit as st
from groq import Groq
from dotenv import load_dotenv

st.set_page_config(
    page_title="Asistente Musical",
    page_icon="🎵",
    layout="wide"
)

# ---------------------------
# Cargar API key
# ---------------------------
load_dotenv()
API_KEY = os.getenv("GROQ_API_KEY") or st.secrets.get("GROQ_API_KEY")

if not API_KEY:
    st.error("Falta GROQ_API_KEY en .env o en st.secrets.")
    st.stop()

client = Groq(api_key=API_KEY)

# ---------------------------
# Estado de sesión
# ---------------------------
if "chat_history" not in st.session_state:
    st.session_state.chat_history = []

# ---------------------------
# Prompt del sistema
# ---------------------------
SYSTEM_PROMPT = """
Eres un asistente musical especializado en canciones, artistas, géneros, épocas y recomendaciones.

Tu función es ayudar al usuario a descubrir música, entender canciones y recibir sugerencias útiles.

Tus reglas son:

1. Si el usuario pide una canción específica, responde con una ficha clara que incluya:
   - nombre de la canción
   - artista
   - género aproximado
   - año o época aproximada
   - una breve descripción
   - recomendaciones del mismo género
   - recomendaciones de canciones del mismo año o época

2. Si el usuario pide recomendaciones, sugiere canciones similares indicando:
   - nombre de la canción
   - artista
   - género
   - año o década aproximada
   - por qué podrían gustarle

3. Si el usuario pide recomendaciones por estado de ánimo, ocasión o actividad, responde con una mini playlist.
   En esos casos devuelve entre 5 y 10 canciones recomendadas.

4. Si el usuario pide música por género, década, año o idioma, responde con varias opciones relevantes.

5. Si el usuario da el nombre de un artista, devuelve:
   - una breve descripción del artista
   - algunas de sus canciones más populares
   - el género principal
   - artistas o canciones similares

6. Si el usuario pide el significado, tema o explicación de una canción, resume de qué trata la canción de forma clara.

7. No devuelvas letras completas de canciones, pero sí puedes devolver un fragmento breve y literal del coro o estribillo si el usuario lo solicita.

8. Si el usuario pide el coro, estribillo o hook de una canción:
   - considera "coro", "estribillo" y "hook" como equivalentes
   - responde primero con un fragmento breve y literal del estribillo
   - no comiences con explicación; primero muestra el fragmento
   - No agregues explicación del estribillo, solo la información puntual.
   - no inventes citas textuales
   - no devuelvas la letra completa ni fragmentos demasiado largos
   - si no tienes seguridad sobre el texto exacto, dilo claramente y ofrece un resumen breve del estribillo en vez de citarlo

9. No inventes enlaces exactos oficiales de YouTube si no estás seguro.
   En vez de eso, devuelve una búsqueda de YouTube usando este formato:
   https://www.youtube.com/results?search_query=ARTISTA+CANCIÓN

10. Si el usuario no da suficiente información, pídele que indique alguno de estos datos:
   - canción
   - artista
   - género
   - año o década
   - estado de ánimo
   - actividad u ocasión

11. Responde siempre en español, con formato claro, amigable y ordenado.

12. Cuando sea posible, usa este formato de salida:

🎵 Canción o recomendación: ...
👤 Artista: ...
🎼 Género: ...
📅 Año o época: ...
📝 Descripción: ...
✨ Recomendaciones similares: ...
🔗 YouTube: ...

13. Si el usuario pide una playlist, usa este formato:

🎧 Playlist recomendada: [nombre de la playlist]

1. Canción - Artista
2. Canción - Artista
3. Canción - Artista
4. Canción - Artista
5. Canción - Artista

Cierra con una breve explicación de por qué esa selección encaja con lo que pidió el usuario.

14. Solo respondes preguntas relacionadas con música.

Si el usuario hace una pregunta que no está relacionada con música, responde de forma amable indicando que solo puedes ayudar con temas musicales y sugiere ejemplos de consultas válidas.
No respondas a preguntas matematicas, o de cualquier otro topico que no sea exclusivamente de musica. 
Ejemplo:
"Lo siento, solo puedo ayudarte con temas relacionados con música 🎵. Puedes preguntarme por canciones, artistas, géneros, playlists, recomendaciones o el significado de una canción."
"""

# ---------------------------
# Función link YouTube
# ---------------------------
def youtube_search_link(query: str) -> str:
    encoded = urllib.parse.quote_plus(query)
    return f"https://www.youtube.com/results?search_query={encoded}"

# ---------------------------
# Sidebar
# ---------------------------
st.sidebar.title("🎛️ Panel musical")

genero = st.sidebar.selectbox(
    "Género",
    ["Ninguno", "Pop", "Rock", "Reggaetón", "Jazz", "Balada", "Electrónica", "K-pop", "Salsa", "Rap"]
)

decada = st.sidebar.selectbox(
    "Década",
    ["Ninguna", "70s", "80s", "90s", "2000s", "2010s", "2020s"]
)

mood = st.sidebar.selectbox(
    "Estado de ánimo",
    ["Ninguno", "Feliz", "Triste", "Relajado", "Energético", "Romántico", "Nostálgico"]
)

actividad = st.sidebar.selectbox(
    "Actividad",
    ["Ninguna", "Estudiar", "Entrenar", "Fiesta", "Dormir", "Viajar", "Trabajar"]
)

if st.sidebar.button("🎧 Generar playlist"):
    partes = []
    if genero != "Ninguno":
        partes.append(f"del género {genero}")
    if decada != "Ninguna":
        partes.append(f"de la década {decada}")
    if mood != "Ninguno":
        partes.append(f"con mood {mood}")
    if actividad != "Ninguna":
        partes.append(f"para {actividad.lower()}")

    if partes:
        consulta_sidebar = "Recomiéndame una playlist " + ", ".join(partes)
    else:
        consulta_sidebar = "Recomiéndame una playlist musical variada"

    st.session_state.chat_history.append({
        "role": "user",
        "content": consulta_sidebar
    })

# ---------------------------
# Interfaz principal
# ---------------------------
st.title("🎵 Asistente Musical IA")
st.write("Pídeme canciones, artistas, playlists, recomendaciones o el significado de una canción.")
st.info("Ejemplos: 'Quiero rock de los 90', 'Canciones de Adele', '¿De qué trata Viva La Vida?', 'Dame el coro de Imagine'.")

col1, col2 = st.columns([1, 1])

with col1:
    if st.button("🗑️ Limpiar chat"):
        st.session_state.chat_history = []
        st.rerun()


# Mostrar historial
for msg in st.session_state.chat_history:
    with st.chat_message(msg["role"]):
        st.markdown(msg["content"])

# Input del usuario
user_input = st.chat_input("Escribe tu consulta musical aquí...")

if user_input:
    st.session_state.chat_history.append({
        "role": "user",
        "content": user_input
    })

# Responder solo si el último mensaje es del usuario
if st.session_state.chat_history and st.session_state.chat_history[-1]["role"] == "user":
    ultimo_mensaje = st.session_state.chat_history[-1]["content"]

    with st.chat_message("user"):
        st.markdown(ultimo_mensaje)

    messages = [{"role": "system", "content": SYSTEM_PROMPT}]
    messages.extend(st.session_state.chat_history)

    try:
        response = client.chat.completions.create(
            model="llama-3.1-8b-instant",
            messages=messages,
            temperature=0.7
        )
        respuesta_texto = response.choices[0].message.content.strip()

        link_youtube = youtube_search_link(ultimo_mensaje)

        respuesta_final = f"""{respuesta_texto}

🔎 **Búsqueda en YouTube:**  
{link_youtube}
"""

    except Exception as e:
        respuesta_final = f"Ocurrió un error al llamar a la API: {e}"

    with st.chat_message("assistant"):
        st.markdown(respuesta_final)

    st.session_state.chat_history.append({
        "role": "assistant",
        "content": respuesta_final
    })
