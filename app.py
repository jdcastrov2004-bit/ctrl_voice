import os
import time
import glob
import json
import streamlit as st
from PIL import Image
from bokeh.models.widgets import Button
from bokeh.models import CustomJS
from streamlit_bokeh_events import streamlit_bokeh_events
import paho.mqtt.client as paho
from gtts import gTTS
from googletrans import Translator

# ---------- MQTT ----------
def on_publish(client, userdata, result):
    print("el dato ha sido publicado \n")

def on_message(client, userdata, message):
    global message_received
    time.sleep(2)
    message_received = str(message.payload.decode("utf-8"))
    st.write(message_received)

broker = "broker.mqttdashboard.com"
port = 1883
client1 = paho.Client("JUANDA-21github")
client1.on_message = on_message

# ---------- UI ----------
st.set_page_config(page_title="Control por voz", page_icon="🎙️", layout="centered")

st.title("🎙️ Interfaces Multimodales")
st.subheader("Control por voz")

image = Image.open("voice_ctrl.jpg")
st.image(image, width=280)

with st.sidebar:
    st.subheader("Instrucciones")
    st.write(
        "1) Presiona **Inicio** para activar el dictado.\n"
        "2) Di tu comando de voz con claridad.\n"
        "3) Se publicará en el canal MQTT configurado."
    )
    st.caption("Broker: broker.mqttdashboard.com • Tema: `voice_JUANDA`")

st.write(
    "Cuando estés listo, toca el botón y habla. "
    "Tu frase se mostrará aquí y se enviará al broker MQTT como un mensaje JSON."
)

# ---------- Botón de dictado (Bokeh) ----------
stt_button = Button(label="🎤  Inicio", width=200)

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
        if (value != "") {
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
    override_height=80,
    debounce_time=0
)

# ---------- Procesamiento de resultado ----------
if result:
    if "GET_TEXT" in result:
        frase = (result.get("GET_TEXT") or "").strip()
        st.markdown("#### Texto detectado")
        st.success(frase if frase else "No se capturó texto.")

        if frase:
            try:
                client1.on_publish = on_publish
                client1.connect(broker, port, keepalive=30)
                payload = json.dumps({"Act1": frase})
                _ = client1.publish("voice_JUANDA", payload)
                st.toast("Comando publicado en MQTT ✅", icon="✅")
            except Exception as e:
                st.error(f"No se pudo publicar en MQTT: {e}")

    try:
        os.makedirs("temp", exist_ok=True)
    except Exception:
        pass
