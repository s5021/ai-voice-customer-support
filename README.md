# 🎙️ AI-Powered Voice Customer Support Bot

A production-ready voice AI customer support system built with 
Python, Flask, Deepgram, Groq, and RAG architecture.

## 🚀 Features

- 🎤 Real-time voice recognition (Deepgram Nova-2)
- 🧠 RAG-powered responses (ChromaDB + HuggingFace)
- ⚡ LLM intelligence (Groq + Llama 3.3 70B)
- 🗄️ Multi-database (PostgreSQL + MongoDB)
- 📊 Analytics dashboard
- 💬 Text and voice chat support

## 🛠️ Tech Stack

- **Backend:** Python, Flask, SQLAlchemy
- **AI/ML:** Groq (Llama 3.3), Deepgram, LangChain, ChromaDB
- **Databases:** PostgreSQL, MongoDB Atlas
- **Frontend:** HTML, CSS, JavaScript

## ⚙️ Setup

1. Clone the repository
```bash
git clone https://github.com/s5021/ai-voice-customer-support
cd ai-voice-customer-support
```

2. Create virtual environment
```bash
python -m venv venv
venv\Scripts\activate
```

3. Install dependencies
```bash
pip install -r requirements.txt
```

4. Create .env file
```bash
cp .env.template .env
# Add your API keys to .env
```

5. Run the application
```bash
python run.py
```

6. Open browser at http://localhost:5000

## 📁 Project Structure
```
voice-bot/
├── app/
│   ├── services/
│   │   ├── deepgram_service.py
│   │   ├── groq_service.py
│   │   ├── rag_service.py
│   │   └── analytics_service.py
│   ├── models.py
│   ├── routes.py
│   └── config.py
├── static/
│   ├── css/style.css
│   └── js/main.js
├── templates/
│   └── index.html
├── knowledge_base/
│   └── docs/
├── requirements.txt
└── run.py
```

## 🔑 Environment Variables
```
DEEPGRAM_API_KEY=your_deepgram_key
GROQ_API_KEY=your_groq_key
DATABASE_URL=postgresql://user:password@localhost/voicebot_db
MONGODB_URI=your_mongodb_uri
SECRET_KEY=your_secret_key
```

## 👩‍💻 Author

**Soni** - AI/ML Engineer
- LinkedIn: https://www.linkedin.com/in/soni-72780a2a6/
- GitHub: https://github.com/s5021