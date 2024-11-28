import os
import streamlit as st
from bokeh.models.widgets import Button
from bokeh.models import CustomJS
from streamlit_bokeh_events import streamlit_bokeh_events
from PIL import Image
import time
import glob
import paho.mqtt.client as paho
import json
from gtts import gTTS
from googletrans import Translator

# Configuración de tema futurista
st.set_page_config(
    page_title="Voice Control Interface",
    page_icon="🎙️",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# Estilos CSS personalizados
st.markdown("""
    <style>
    .main {
        background: linear-gradient(45deg, #1a1a2e, #16213e);
        color: #e94560;
    }
    .stButton>button {
        background-color: #0f3460;
        color: #e94560;
        border: 2px solid #e94560;
        border-radius: 25px;
        padding: 15px 30px;
        transition: all 0.3s ease;
    }
    .stButton>button:hover {
        background-color: #e94560;
        color: #0f3460;
        box-shadow: 0 0 15px #e94560;
    }
    h1, h2, h3 {
        color: #e94560 !important;
        text-shadow: 0 0 10px rgba(233, 69, 96, 0.5);
        font-family: 'Arial', sans-serif;
    }
    .decoration-bar {
        background: linear-gradient(90deg, #e94560, #0f3460);
        height: 3px;
        margin: 20px 0;
        animation: pulse 2s infinite;
    }
    @keyframes pulse {
        0% { opacity: 0.6; }
        50% { opacity: 1; }
        100% { opacity: 0.6; }
    }
    .status-indicator {
        width: 10px;
        height: 10px;
        background-color: #e94560;
        border-radius: 50%;
        display: inline-block;
        margin-right: 10px;
        animation: blink 1.5s infinite;
    }
    @keyframes blink {
        0% { opacity: 0.2; }
        50% { opacity: 1; }
        100% { opacity: 0.2; }
    }
    </style>
""", unsafe_allow_html=True)

def on_publish(client, userdata, result):
    st.success("Datos transmitidos exitosamente")
    pass

def on_message(client, userdata, message):
    global message_received
    time.sleep(2)
    message_received = str(message.payload.decode("utf-8"))
    st.write(f"📡 Mensaje recibido: {message_received}")

broker = "157.230.214.127"
port = 1883
client1 = paho.Client("GIT-HUBC")
client1.on_message = on_message

# Interfaz principal
st.markdown("<div class='decoration-bar'></div>", unsafe_allow_html=True)
st.title("🎙️ CONTROL POR VOZ INTELIGENTE")
st.markdown("<div class='decoration-bar'></div>", unsafe_allow_html=True)

# Contenedor para la imagen y el botón
col1, col2 = st.columns([1, 2])

with col1:
    image = Image.open('voice_ctrl.jpg')
    st.image(image, width=200)

with col2:
    st.markdown("<div class='status-indicator'></div> Sistema Activo", unsafe_allow_html=True)
    st.markdown("### Instrucci-ones")
    st.markdown("1. Presiona el botón para iniciar")
    st.markdown("2. Habla claramente al micrófono")
    st.markdown("3. Espera la confirmación del sistema")

# Botón de control por voz
stt_button = Button(label="▶️ INICIAR RECONOCIMIENTO", width=200)
stt_button.js_on_event("button_click", CustomJS(code="""
    var recognition = new webkitSpeechRecognition();
    recognition.continuous = true;
    recognition.interimResults = true;
 
    recognition.onresult = function (e) {
        var value = "";
        for (var i = e.resultIndex; i < e.results.length; ++i) {
            if (e.results[i].isFinal) {
                value += e.results[i][0].transcript;
            }
        }
        if ( value != "") {
            document.dispatchEvent(new CustomEvent("GET_TEXT", {detail: value}));
        }
    }
    recognition.start();
    """))

result = streamlit_bokeh_events(
    stt_button,
    events="GET_TEXT",
    key="listen",
    refresh_on_update=False,
    override_height=75,
    debounce_time=0)

if result:
    if "GET_TEXT" in result:
        st.markdown("""
            <div style='background-color: rgba(15, 52, 96, 0.5); 
                        padding: 20px; 
                        border-radius: 10px; 
                        border: 1px solid #e94560;
                        margin: 20px 0;'>
                <h3 style='color: #e94560; margin: 0;'>Texto Reconocido:</h3>
                <p style='color: #fff; margin: 10px 0 0 0;'>{}</p>
            </div>
        """.format(result.get("GET_TEXT")), unsafe_allow_html=True)
        
        client1.on_publish = on_publish
        client1.connect(broker, port)
        message = json.dumps({"Act1": result.get("GET_TEXT").strip()})
        ret = client1.publish("voice/cosplay", message)

try:
    os.mkdir("temp")
except:
    pass
