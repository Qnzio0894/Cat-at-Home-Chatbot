from flask import Flask, request, jsonify, send_from_directory
from anthropic import Anthropic
from dotenv import load_dotenv
from tinydb import TinyDB, Query
from datetime import date, datetime, timedelta
import os
import json

load_dotenv()

app = Flask(__name__)
client = Anthropic(api_key=os.getenv("ANTHROPIC_API_KEY"))
db = TinyDB('db.json')
reservas = db.table('reservas')
bloqueados = db.table('bloqueados')

def get_system_prompt():
    hoy = date.today().strftime("%d/%m/%Y")
    return f"""Sos el asistente virtual de Cat at Home, un servicio de cuidado de gatos a domicilio en Montevideo, Uruguay.
La fecha de hoy es {hoy}. Usá esta fecha como referencia para las reservas.
Tu tarea es recopilar la información necesaria para hacer una reserva de manera amigable y conversacional.

La información que necesitás recopilar es:
1. Nombre y apellido del cliente
2. Teléfono de contacto del cliente
3. Dirección donde se cuidará el gato
4. Nombre del gato
5. Fechas en las que se necesita el cuidado

Una vez que tengas esos datos, preguntá orgánicamente por requerimientos especiales del gato, por ejemplo:
- Alimentación (qué come, cuántas veces por día)
- Medicamentos o necesidades médicas
- Comportamiento (si es sociable, asustadizo, etc.)
- Cualquier otra cosa importante

Cuando tengas toda la información, mostrá un resumen de confirmación claro y cerrá con este mensaje exacto:
"¡Listo! Tu reserva está registrada. Isabel se va a contactar con vos al número que nos dejaste para coordinar la entrega de llaves."

Al final del mensaje incluí EXACTAMENTE este bloque JSON (sin markdown, sin backticks):

RESERVA_JSON:{{"nombre":"...","telefono":"...","direccion":"...","gato":"...","fechas":["YYYY-MM-DD"],"notas":"..."}}

Respondé siempre en español, con un tono amigable y profesional. Hacé una pregunta a la vez."""

conversation_history = []

def get_max_gatos(fecha_str):
    try:
        fecha = datetime.strptime(fecha_str, "%Y-%m-%d").date()
        mes = fecha.month
        dia = fecha.day
        if (mes == 12 and dia >= 15) or (mes == 1) or (mes == 2 and dia <= 15):
            return 4
        return 2
    except:
        return 2

def get_disponibilidad(año, mes):
    resultado = {}
    primer_dia = date(año, mes, 1)
    if mes == 12:
        ultimo_dia = date(año + 1, 1, 1)
    else:
        ultimo_dia = date(año, mes + 1, 1)

    delta = (ultimo_dia - primer_dia).days
    Reserva = Query()
    Bloqueado = Query()

    for i in range(delta):
        fecha = primer_dia + timedelta(days=i)
        fecha_str = fecha.strftime("%Y-%m-%d")

        if bloqueados.search(Bloqueado.fecha == fecha_str):
            resultado[fecha_str] = "bloqueado"
            continue

        count = len(reservas.search(Reserva.fechas.any([fecha_str])))
        max_g = get_max_gatos(fecha_str)

        if count >= max_g:
            resultado[fecha_str] = "lleno"
        elif count == max_g - 1:
            resultado[fecha_str] = "parcial"
        else:
            resultado[fecha_str] = "disponible"

    return resultado

def guardar_reserva(data):
    reservas.insert(data)

@app.route("/")
def index():
    return send_from_directory(".", "index.html")

@app.route("/admin")
def admin():
    return send_from_directory(".", "admin.html")

@app.route("/disponibilidad")
def disponibilidad():
    año = int(request.args.get("año", date.today().year))
    mes = int(request.args.get("mes", date.today().month))
    return jsonify(get_disponibilidad(año, mes))

@app.route("/bloquear", methods=["POST"])
def bloquear():
    data = request.json
    fecha = data.get("fecha")
    Bloqueado = Query()
    if not bloqueados.search(Bloqueado.fecha == fecha):
        bloqueados.insert({"fecha": fecha})
    return jsonify({"ok": True})

@app.route("/desbloquear", methods=["POST"])
def desbloquear():
    data = request.json
    fecha = data.get("fecha")
    Bloqueado = Query()
    bloqueados.remove(Bloqueado.fecha == fecha)
    return jsonify({"ok": True})

@app.route("/reservas")
def ver_reservas():
    todas = reservas.all()
    return jsonify(todas)

@app.route("/chat", methods=["POST"])
def chat():
    global conversation_history
    data = request.json
    user_message = data.get("message", "")

    if user_message == "__init__":
        conversation_history = []
        response = client.messages.create(
            model="claude-opus-4-5",
            max_tokens=1024,
            system=get_system_prompt(),
            messages=[{"role": "user", "content": "Hola"}]
        )
        assistant_message = response.content[0].text
        conversation_history.append({"role": "user", "content": "Hola"})
        conversation_history.append({"role": "assistant", "content": assistant_message})
        return jsonify({"response": assistant_message})

    conversation_history.append({"role": "user", "content": user_message})
    response = client.messages.create(
        model="claude-opus-4-5",
        max_tokens=1024,
        system=get_system_prompt(),
        messages=conversation_history
    )
    assistant_message = response.content[0].text
    conversation_history.append({"role": "assistant", "content": assistant_message})

    reserva_guardada = False
    if "RESERVA_JSON:" in assistant_message:
        try:
            json_str = assistant_message.split("RESERVA_JSON:")[1].strip().split("\n")[0]
            reserva_data = json.loads(json_str)
            guardar_reserva(reserva_data)
            reserva_guardada = True
            assistant_message = assistant_message.split("RESERVA_JSON:")[0].strip()
        except:
            pass

    return jsonify({"response": assistant_message, "reserva_guardada": reserva_guardada})

if __name__ == "__main__":
    app.run(debug=True, host='127.0.0.1', port=8080)