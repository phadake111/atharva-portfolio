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

def send_thank_you_email(receiver_email: str, receiver_name: str):
    sender_email = os.getenv("EMAIL_SENDER")
    sender_password = os.getenv("EMAIL_PASSWORD")
    
    if not sender_email or not sender_password:
        print("Skipping email: Setup missing in .env file.")
        return False

    msg = MIMEMultipart('alternative') # Changed from blank to 'alternative' to look natural to spam filters
    msg['From'] = f"Atharva Phadake Portfolio <{sender_email}>" # Clean Sender Name format
    msg['To'] = receiver_email
    msg['Subject'] = f"Received your message, {receiver_name}!"
    
    # Anti-Spam Headers: Makes the email look authentic
    msg['Message-ID'] = f"<{time.time()}@{sender_email.split('@')[1]}>"
    msg['X-Mailer'] = "Python-smtplib"

    # Professional email layout content block
    body = f"""Hello {receiver_name},

Thank you for visiting my portfolio platform and reaching out.

This is a quick confirmation to let you know that I have safely received your contact submission. I am looking forward to reviewing your message and connecting with you shortly.

If you want to review more of my engineering projects or technical skills in the meantime, feel free to chat with my interactive portfolio AI assistant on the website!

Best regards,
Atharva Phadake
"""
    msg.attach(MIMEText(body, 'plain'))

    try:
        server = smtplib.SMTP('smtp.gmail.com', 587, timeout=10) 
        server.starttls()  
        server.login(sender_email, sender_password)
        server.sendmail(sender_email, receiver_email, msg.as_string())
        server.quit()
        print(f"-> Confirmation email successfully sent to {receiver_email}")
        return True
    except Exception as e:
        print(f"Email failure log: {e}")
        return False


# --- UPDATED CONTACT ENDPOINT WITH BACKGROUND TASKS ---
@app.post("/api/contact")
async def contact_form(contact: ContactMessage, background_tasks: BackgroundTasks):
    # 1. Format text file entry
    log_entry = (
        f"========================================\n"
        f"Name: {contact.name}\n"
        f"Email: {contact.email}\n"
        f"Message: {contact.message}\n"
        f"Timestamp: {time.strftime('%Y-%m-%d %H:%M:%S')}\n"
        f"========================================\n\n"
    )
    
    try:
        # 2. Write to text file instantly
        with open("contacts_log.txt", "a", encoding="utf-8") as file:
            file.write(log_entry)
        print(f"-> Successfully saved message entry for {contact.name}")
    except Exception as e:
        print(f"Local file system error: {e}")
        raise HTTPException(status_code=500, detail="Could not save message details locally.")

    # 3. Queue the email to process quietly in the background
    # This prevents the network error from blocking your web page or crashing the endpoint response!
    background_tasks.add_task(send_thank_you_email, contact.email, contact.name)
    
    # 4. Return success immediately to the frontend user interface
    return {"status": "success", "message": "Thanks! Your message has been received."}


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
    