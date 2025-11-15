from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import sqlite3
import json
from datetime import datetime

app = FastAPI(
    title="🤖 AI Support Agent API",
    description="Intelligent customer support chatbot",
    version="1.0.0"
)

# CORS setup for frontend connection
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "http://127.0.0.1:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Database setup
def init_database():
    conn = sqlite3.connect('support.db')
    cursor = conn.cursor()
    
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS conversations (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id TEXT NOT NULL,
            user_message TEXT NOT NULL,
            ai_response TEXT NOT NULL,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS knowledge_base (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            question TEXT NOT NULL,
            answer TEXT NOT NULL,
            category TEXT NOT NULL
        )
    ''')
    
    # Insert sample knowledge data
    sample_data = [
        ("password reset", "You can reset your password by clicking 'Forgot Password' on login page.", "account"),
        ("payment issue", "For payment issues, please check your payment method or contact billing support.", "billing"),
        ("login problem", "Try clearing your browser cache and cookies or use incognito mode.", "technical"),
        ("order tracking", "You can track your order using tracking number from your email.", "orders")
    ]
    
    cursor.executemany(
        'INSERT OR IGNORE INTO knowledge_base (question, answer, category) VALUES (?, ?, ?)',
        sample_data
    )
    
    conn.commit()
    conn.close()
    print("✅ Database initialized successfully!")

# Initialize database
init_database()

class ChatRequest(BaseModel):
    message: str
    user_id: str = "user_001"

# AI Response Generator
def generate_ai_response(message: str) -> str:
    message_lower = message.lower()
    
    if "password" in message_lower:
        return "I can help with password reset. Click 'Forgot Password' on login page or contact support."
    elif "payment" in message_lower or "billing" in message_lower:
        return "For billing issues, please check payment method or contact: billing@company.com"
    elif "login" in message_lower:
        return "Try clearing browser cache, using incognito mode, or resetting password."
    elif "order" in message_lower or "tracking" in message_lower:
        return "You can track your order in 'Order History' section with your tracking number."
    else:
        return "Thank you for your message. How can I assist you today? Please provide more details."

@app.get("/")
async def root():
    return {
        "message": "🤖 AI Support Agent API is running!",
        "status": "active",
        "timestamp": datetime.now().isoformat()
    }

@app.post("/chat")
async def chat_with_ai(chat_data: ChatRequest):
    try:
        ai_response = generate_ai_response(chat_data.message)
        
        # Save to database
        conn = sqlite3.connect('support.db')
        cursor = conn.cursor()
        cursor.execute(
            'INSERT INTO conversations (user_id, user_message, ai_response) VALUES (?, ?, ?)',
            (chat_data.user_id, chat_data.message, ai_response)
        )
        conn.commit()
        conn.close()
        
        return {
            "success": True,
            "response": ai_response,
            "timestamp": datetime.now().isoformat()
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/conversations/{user_id}")
async def get_conversations(user_id: str):
    try:
        conn = sqlite3.connect('support.db')
        cursor = conn.cursor()
        cursor.execute(
            'SELECT user_message, ai_response, created_at FROM conversations WHERE user_id = ? ORDER BY created_at DESC LIMIT 10',
            (user_id,)
        )
        
        conversations = []
        for row in cursor.fetchall():
            conversations.append({
                "user_message": row[0],
                "ai_response": row[1],
                "timestamp": row[2]
            })
        
        conn.close()
        return {"success": True, "conversations": conversations}
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/health")
async def health_check():
    return {
        "status": "healthy",
        "service": "AI Support Agent API",
        "timestamp": datetime.now().isoformat()
    }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000, reload=True)
