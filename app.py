from flask import Flask, request, jsonify, send_from_directory
from anthropic import Anthropic
from dotenv import load_dotenv
import os

load_dotenv()

app = Flask(__name__)
client = Anthropic(api_key=os.getenv("ANTHROPIC_API_KEY"))

SYSTEM_PROMPT = """Sos el asistente virtual de Cat at Home, un servicio de cuidado de gatos a domicilio en Montevideo, Uruguay.
Tu tarea es recopilar la información necesaria para hacer una reserva de manera amigable y conversacional.

La información que necesitás recopilar es:
1. Nombre y apellido del cliente
2. Dirección donde se cuidará al gato
3. Nombre del gato
4. Fechas en las que se necesita el cuidado

Una vez que tengas esos datos, preguntá orgánicamente por requerimientos especiales del gato, por ejemplo:
- Alimentación (qué come, cuántas veces por día)
- Medicamentos o necesidades médicas
- Comportamiento (si es sociable, asustadizo, etc.)
- Cualquier otra cosa importante que el cuidador deba saber

Cuando tengas toda la información, mostrá un resumen de confirmación claro y prolijo con todos los datos de la reserva.

Respondé siempre en español, con un tono amigable y profesional. Hacé una pregunta a la vez para no abrumar al cliente."""

conversation_history = []

@app.route("/")
def index():
    return send_from_directory(".", "index.html")

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
            system=SYSTEM_PROMPT,
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
        system=SYSTEM_PROMPT,
        messages=conversation_history
    )
    
    assistant_message = response.content[0].text
    conversation_history.append({"role": "assistant", "content": assistant_message})
    
    return jsonify({"response": assistant_message})

if __name__ == "__main__":
    app.run(debug=True)