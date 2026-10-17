from fastapi import FastAPI, HTTPException, BackgroundTasks # <-- Added BackgroundTasks here
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import os
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
import time
import uvicorn

from rag_engine import get_ai_response, analyze_job_match

app = FastAPI(title="Atharva's Portfolio API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

class ContactMessage(BaseModel):
    name: str
    email: str
    message: str

class ChatRequest(BaseModel):
    question: str
    
class JobMatchRequest(BaseModel):
    job_description: str

def send_contact_emails(receiver_email: str, receiver_name: str, user_message: str):
    sender_email = os.getenv("EMAIL_SENDER")
    sender_password = os.getenv("EMAIL_PASSWORD")
    
    if not sender_email or not sender_password:
        print("Skipping email: Setup missing in .env file.")
        return False

    try:
        server = smtplib.SMTP('smtp.gmail.com', 587, timeout=10) 
        server.starttls()  
        server.login(sender_email, sender_password)

        # 1. Admin Notification Email (Aapke liye alert)
        admin_msg = MIMEMultipart('alternative')
        admin_msg['From'] = f"Portfolio Contact <{sender_email}>"
        admin_msg['To'] = sender_email
        admin_msg['Subject'] = f"New Portfolio Message from {receiver_name}!"
        
        admin_body = f"""Hello Atharva,

You have received a new message through your portfolio contact form:

Name: {receiver_name}
Email: {receiver_email}
Message: 
{user_message}

Best regards,
Portfolio System
"""
        admin_msg.attach(MIMEText(admin_body, 'plain'))
        server.sendmail(sender_email, sender_email, admin_msg.as_string())

        # 2. Thank You Email (User ke liye confirmation)
        user_msg = MIMEMultipart('alternative')
        user_msg['From'] = f"Atharva Phadake <{sender_email}>"
        user_msg['To'] = receiver_email
        user_msg['Subject'] = f"Received your message, {receiver_name}!"
        
        user_body = f"""Hello {receiver_name},

Thank you for visiting my portfolio platform and reaching out.

This is a quick confirmation to let you know that I have safely received your message. I am looking forward to reviewing it and connecting with you shortly.

Best regards,
Atharva Phadake
"""
        user_msg.attach(MIMEText(user_body, 'plain'))
        server.sendmail(sender_email, receiver_email, user_msg.as_string())

        server.quit()
        print(f"-> Notifications and confirmation emails successfully sent!")
        return True
    except Exception as e:
        print(f"Email failure log: {e}")
        return False

# --- UPDATED CONTACT ENDPOINT WITH BACKGROUND TASKS ---
@app.post("/api/contact")
async def contact_form(contact: ContactMessage):
    # Direct function call karke check kar rahe hain ki kya error aa raha hai
    try:
        success = send_contact_emails(contact.email, contact.name, contact.message)
        if success:
            return {"status": "success", "message": "Email sent successfully!"}
        else:
            return {"status": "error", "message": "Function returned False. Check credentials."}
    except Exception as e:
        # Exact error ko seedha frontend par dikha denge!
        return {"status": "error", "message": f"SMTP Error: {str(e)}"}


@app.post("/api/chat")
async def chat_with_resume(request: ChatRequest):
    ai_answer = get_ai_response(request.question)
    return {"answer": ai_answer}


@app.post("/api/match-job")
async def match_job_description(request: JobMatchRequest):
    try:
        # 1. Aapka banaya hua function call hota hai aur JD pass hoti hai
        analysis_result = analyze_job_match(request.job_description)
        
        # 2. Result ko JSON format mein frontend par wapas bhej dete hain
        return {"status": "success", "match_analysis": analysis_result}
        
    except Exception as e:
        print(f"Match API Error: {e}")
        return {"status": "error", "match_analysis": "Could not analyze the job description at the moment."}
    
