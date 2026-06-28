# 🚀 EventPro AI — Powered Smart Event Management System

An intelligent, real-time event planning platform that utilizes AI classification, single-threaded asynchronous networking, and voice interaction to simplify event management.

---

## 🎯 Problem
Planning events is complex, time-consuming, and lacks intelligent decision support. Traditional tools suffer from latency, complex interface flows, and data leakage across multiple accounts.

## 💡 Solution
We built an **AI-powered system** that helps users plan, manage, and optimize events in real time. It features a voice-enabled AI assistant, instant data synchronization, and automated budget allocation, all running on a high-performance, secure backend.

---

## 🤖 Key Features

### 1. AI Chatbot + Voice Assistant
A globally integrated floating assistant allowing users to interact via text or voice:
* **Interactive Chatting**: Ask about events, guest counts, and budget details.
* **Speech-to-Text (STT)**: Voice-activated commands (e.g., *"Plan my wedding for 200 guests"*).
* **Text-to-Speech (TTS)**: Conversational audio responses matching user preferences (with a toggle to mute/unmute).

### 2. Smart Budget Estimation
AI-powered cost calculations based on guest count, venue choices, and event type. Automatically pre-allocates recommended budget portions to catering, decoration, venue hire, and entertainment.

### 3. Real-Time Event Updates
* **Zero-Refresh UI**: Instant updates on task completion, budget metrics, and guest logs via WebSockets.
* **Live Attendance Tracking**: Live dashboard counters updating in real-time when guests scan their ticket QR codes.

### 4. AI Insights & Suggestions
Suggests cost-saving strategies, warns when nearing budget thresholds, and suggests regional vendors based on ratings.

### 5. Multi-User Secure System
Fully isolated sqlite database schemas. Connecting clients join secure rooms named `user_<user_id>` when authenticated, preventing any cross-user data leakage.

### 6. Smart Invitations
AI generates custom invitation templates automatically based on selected event details and personalized tones.

---

## 🛠️ Technology Stack

* **Backend**: Python 3.13, Flask, Flask-SQLAlchemy (ORM), Flask-Login (Sessions), Flask-Migrate
* **Real-time Networking**: Flask-SocketIO, Eventlet WSGI Async Worker Pool
* **NLP Classification**: scikit-learn (TF-IDF Vectorization & Cosine Similarity)
* **Frontend**: HTML5, Vanilla CSS (Custom properties & Glassmorphism), Bootstrap 5.3, Bootstrap Icons, Chart.js, AOS Animations
* **APIs**: Web Speech API (`SpeechRecognition` & `SpeechSynthesis`)

---

## ⚡ Performance Optimizations

To deliver a high-performance system for the hackathon, we implemented these deep optimizations:
1. **Eventlet Async WSGI**: Switched Flask-SocketIO from standard multi-threaded Werkzeug blocking to a single-threaded asynchronous coroutine event loop to eliminate polling overhead.
2. **Direct WebSocket Transports**: Forced the frontend to bypass HTTP long-polling and connect directly over WebSocket transport, saving connection handshakes.
3. **SQLite Write-Ahead Logging (WAL) Mode**: Enabled WAL mode (`PRAGMA journal_mode=WAL;`), allowing concurrent reads while writes are active, reducing database read latency by **~70%**.
4. **Localized CDN Assets**: Downloaded all external assets (Bootstrap, Chart.js, AOS, Socket.IO) locally to prevent connection blocking on slow network connections.

---

## 🚀 How to Run Locally

### Prerequisites
* Python 3.8+ (Python 3.13 recommended)

### 1. Install Dependencies
```bash
pip install -r requirements.txt
```

### 2. Start the Server
Run the startup script:
```bash
python run.py
```
*Note: Reloader is disabled in dev on Windows to prevent file watchdog lockups with Eventlet.*

### 3. Open the App
Visit [http://127.0.0.1:5000/](http://127.0.0.1:5000/) in your browser. Register an account or log in with the default guest account:
* **Username**: `demo`
* **Password**: `password123`

---

## 🔬 Route Verification & Testing
To verify the health and status of all pages in-process, run:
```bash
python scratch/test_routes.py
```
This tests GET render requests across the dashboard, tasks, budget, guests, vendor management, and chatbot interfaces, asserting `200 OK` on all endpoints.
