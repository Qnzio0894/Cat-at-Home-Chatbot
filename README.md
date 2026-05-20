# Cat at Home — Booking Chatbot

An AI-powered booking chatbot for Cat at Home, a cat-sitting service based in Montevideo, Uruguay. Built for a real client and currently in use.

## What it does

Clients access the chatbot through a web link and have a natural conversation to make a reservation. The assistant collects all the necessary information step by step and closes with a confirmation summary.

**Information collected during the conversation:**
- Client's full name
- Address where the cat will be cared for
- Cat's name and dates of service
- Special requirements (feeding, medication, behavior, etc.)

## Demo

```
Asistente: ¡Hola! Bienvenida a Cat at Home 🐱 Estoy aquí para ayudarte
           a hacer una reserva. ¿Cuál es tu nombre y apellido?

Cliente:   Sofía Martínez

Asistente: ¡Hola Sofía! ¿En qué fechas necesitás el cuidado?
...
Asistente: Perfecto, aquí está el resumen de tu reserva:
           - Nombre: Sofía Martínez
           - Dirección: ...
           - Gato: ...
           - Fechas: ...
```

## Tech stack

- **Python 3.10+**
- **Flask** — lightweight web framework
- **Anthropic API** — Claude AI model for conversation
- **python-dotenv** — secure API key management
- **HTML & CSS** — custom frontend with warm, editorial design

## Setup

**1. Clone the repository**
```bash
git clone https://github.com/Qnzio0894/cat-at-home.git
cd cat-at-home
```

**2. Install dependencies**
```bash
pip3 install flask anthropic python-dotenv
```

**3. Create a `.env` file**
```
ANTHROPIC_API_KEY=your_api_key_here
```

**4. Run the app**
```bash
python3 app.py
```

**5. Open in browser**
```
http://127.0.0.1:5000
```

## Project structure

```
cat-at-home/
├── app.py          # Flask backend + Anthropic API integration
├── index.html      # Chat interface
├── .gitignore      # Excludes .env from version control
└── README.md       # This file
```

## About

Built by [Diego González Caselli](https://github.com/Qnzio0894) for Isabel's cat-sitting business, Cat at Home.
This project demonstrates conversational AI design, prompt engineering, Python backend development, and custom frontend design.

**Planned features:**
- Live availability calendar
- Admin panel for Isabel to manage bookings
- Email confirmation on reservation
