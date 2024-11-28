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

st.set_page_config(
    page_title="Voice Control Interface",
    page_icon="🎙️",
    layout="wide",
    initial_sidebar_state="collapsed"
)

st.markdown("""
    <style>
    .main {
        background-image: url("Interfaz_2024.png");
        background-size: cover;
        background-repeat: no-repeat;
        background-attachment: fixed;
        color: #e94560;
    }
    .stButton>button {
        background-color: #0f3460;
        color: #e94560;
        border: 2px solid #e94560;
        border-radius: 25px;
        padding: 15px 30px;
        margin: 10px;
        transition: all 0.3s ease;
    }
    .stButton>button:hover {
        background-color: #e94560;
        color: #0f3460;
        box-shadow: 0 0 15px #e94560;
    }
    h1 {
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
    </style>
""", unsafe_allow_html=True)

def on_publish(client, userdata, result):
    #st.success("Datos transmitidos exitosamente")
    pass

def on_message(client, userdata, message):
    global message_received
    time.sleep(2)
    message_received = str(message.payload.decode("utf-8"))
    st.write(f"📡 {message_received}")

broker = "157.230.214.127"
port = 1883
client1 = paho.Client("GIT-HUBC")
client1.on_message = on_message

st.markdown("<div class='decoration-bar'></div>", unsafe_allow_html=True)
st.title("INTERFAZ DE INTERACCIÓN")
st.markdown("<div class='decoration-bar'></div>", unsafe_allow_html=True)

col1, col2 = st.columns([1, 2])

with col1:
    image = Image.open('simbol.jpeg')
    st.image(image, width=200)

with col2:
    btn_col1, btn_col2 = st.columns(2)
    
    with btn_col1:
        if st.button("Nacer"):
            client1.on_publish = on_publish
            client1.connect(broker, port)
            message = json.dumps({"Act1": "nacer"})
            ret = client1.publish("voice/cosplay", message)
            
        if st.button("Morir"):
            client1.on_publish = on_publish
            client1.connect(broker, port)
            message = json.dumps({"Act1": "muerte"})
            ret = client1.publish("voice/cosplay", message)
            
    with btn_col2:
        if st.button("Apagar"):
            client1.on_publish = on_publish
            client1.connect(broker, port)
            message = json.dumps({"Act1": "apagar"})
            ret = client1.publish("voice/cosplay", message)
            
        if st.button("Decaer"):
            client1.on_publish = on_publish
            client1.connect(broker, port)
            message = json.dumps({"Act1": "ocaso"})
            ret = client1.publish("voice/cosplay", message)

stt_button = Button(label="▶️ INICIAR", width=200)
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
        st.markdown(f"""
            <div style='background-color: rgba(15, 52, 96, 0.5); 
                        padding: 20px; 
                        border-radius: 10px; 
                        border: 1px solid #e94560;
                        margin: 20px 0;'>
                <p style='color: #fff; margin: 0;'>{result.get("GET_TEXT")}</p>
            </div>
        """, unsafe_allow_html=True)
        
        client1.on_publish = on_publish
        client1.connect(broker, port)
        message = json.dumps({"Act1": result.get("GET_TEXT").strip()})
        ret = client1.publish("voice/cosplay", message)

try:
    os.mkdir("temp")
except:
    pass
