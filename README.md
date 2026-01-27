🤖 My Companion — LIBRA AI

LIBRA is a futuristic, web-based AI companion designed to chat, joke, assist, and interact with users in real time.
It supports both online AI mode (Google Gemini API) and a smart offline fallback mode, making it reliable even without internet or API access.

Built with Flask, modern UI design, and cloud deployment using Render.

🌟 Features
💬 Real-Time AI Chat (Gemini-powered)
⚡ Offline AI Mode (Smart fallback replies)
😂 Jokes & Dark Humor API
🎨 Futuristic Animated UI
🌐 Cloud Deployed (Render)
📱 Mobile Friendly
🔐 Secure API Key Handling via Environment Variables

🧠 Tech Stack
------------------------------------------------
Technology	               |  Purpose
Python (Flask)	           |  Backend Server
HTML / CSS / JavaScript	   |  Frontend UI
Google Gemini API          | 	AI Responses
Render	                   |  Cloud Hosting
Gunicorn	                 |  Production Server
JokeAPI      	             |  Humor System

## 🚀 Live Demo
👉 **Try LIBRA Online**  
https://my-companion-libra-ai.onrender.com

--------------------------------------------------------------------------------
## License
This project is licensed under the Apache License 2.0 © 2026 Gaurav Giradkar
--------------------------------------------------------------------------------

## ⚙️ Installation (Local Setup)

### 1️⃣ Clone Repository

git clone https://github.com/Gaurav-giradkar/My-Companion-Libra-AI.git
cd My-Companion-Libra-AI
2️⃣ Install Dependencies
pip install -r requirements.txt
3️⃣ Set Environment Variable
Create a .env file:

GEMINI_API_KEY=your_api_key_here
4️⃣ Run App
python main.py
Open in browser:

http://127.0.0.1:5000
☁️ Deployment (Render)
Connect GitHub repository

Build Command:
pip install -r requirements.txt
Start Command:
gunicorn main:app
Environment Variable:

GEMINI_API_KEY=your_api_key_here
🧪 API Endpoints
Endpoint	Method	Description
/api/chat	POST	AI Chat
/api/joke	GET	Normal Joke
/api/dark-joke	GET	Dark Humor
/api/ping	GET	Health Check
🛡️ Security
API keys are stored using environment variables

.env file is excluded from GitHub using .gitignore

🧑‍💻 Developer
Gaurav Giradkar
Second-Year Student | AI & Web Developer

📜 License
This project is licensed under the MIT License

🌠 Future Enhancements
🎙️ Voice Input & Output
📲 PWA Mobile App Mode
🧠 Memory System
👤 User Accounts
🌐 Multi-AI Support
⭐ Support

If you like this project:
Star this repo ⭐
Fork it 🍴
Share it 🚀
