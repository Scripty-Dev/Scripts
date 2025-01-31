import json
import requests
import email
from email.mime.text import MIMEText
import re
from datetime import datetime, timedelta

def classify_email(subject, body, from_header, auth_token):
    # Check for automated senders
    automated_patterns = [r'noreply@', r'no-reply@', r'donotreply@', r'notifications?@']
    email_addr = re.findall(r'<(.+?)>', from_header)[0] if '<' in from_header else from_header
    if any(re.search(pattern, email_addr.lower()) for pattern in automated_patterns):
        return False

    messages = [
        {"role": "system", "content": "You are an email assistant that determines if emails need replies."},
        {"role": "user", "content": f"""Analyze this email and determine if it needs a reply. Respond with ONLY "NEEDS_REPLY" or "NO_REPLY".

Rules:
1. NEEDS_REPLY for:
   - Personal emails requiring response
   - Business communications needing action
   - Direct questions or requests
2. NO_REPLY for:
   - Marketing newsletters
   - Automated notifications
   - FYI/broadcast messages

From: {from_header}
Subject: {subject}
Body: {body}"""}
    ]

    response = requests.post(
        "https://scripty.me/api/assistant/call",
        headers={"Authorization": f"Bearer {auth_token}"},
        json={
            "model": "mixtral-8x7b-32768",
            "messages": messages
        }
    ).json()

    return "NEEDS_REPLY" in response.get('content', '').upper()

def generate_draft(subject, body, from_header, to_addr, auth_token):
    messages = [
        {"role": "system", "content": f"You are an email assistant helping {to_addr} write replies."},
        {"role": "user", "content": f"""Write a reply to this email from {to_addr} to {from_header}.

Original Email:
From: {from_header}
To: {to_addr}
Subject: {subject}
Body: {body}

Guidelines:
1. Write from {to_addr}'s perspective
2. Use sender's name when appropriate
3. Match original tone
4. Address all questions
5. Be concise but thorough"""}
    ]

    response = requests.post(
        "https://scripty.me/api/assistant/call",
        headers={"Authorization": f"Bearer {auth_token}"},
        json={
            "model": "mixtral-8x7b-32768",
            "messages": messages
        }
    ).json()

    return response.get('content', "Thank you for your email. I will respond shortly.")

def process_unread_emails(days_ago=1, auth_token=None):
    try:
        response = requests.get(
            "https://scripty.me/api/assistant/email/unread",
            headers={"Authorization": f"Bearer {auth_token}"},
            params={"days": days_ago}
        )
        emails = response.json()
        
        results = []
        for email_data in emails:
            if classify_email(email_data["subject"], email_data["body"], email_data["from"], auth_token):
                draft = generate_draft(
                    email_data["subject"],
                    email_data["body"], 
                    email_data["from"],
                    email_data["to"],
                    auth_token
                )
                
                if draft:
                    requests.post(
                        "https://scripty.me/api/assistant/email/draft",
                        headers={"Authorization": f"Bearer {auth_token}"},
                        json={
                            "original_message_id": email_data["message_id"],
                            "content": draft
                        }
                    )
                    results.append({
                        "subject": email_data["subject"],
                        "draft_created": True
                    })

        return {"success": True, "results": results}
    except Exception as e:
        return {"success": False, "error": str(e)}

async def func(args):
    try:
        if "auth_token" not in args:
            return json.dumps({"success": False, "error": "auth_token required"})
            
        days = int(args.get("days", 1))
        return json.dumps(process_unread_emails(days, args["auth_token"]))
    except Exception as e:
        return json.dumps({"success": False, "error": str(e)})

object = {
    "name": "email_draft_manager",
    "description": "Process unread emails and generate AI-powered draft replies",
    "parameters": {
        "type": "object",
        "properties": {
            "days": {
                "type": "number",
                "description": "Number of days back to process emails",
                "default": 1
            },
            "auth_token": {
                "type": "string",
                "description": "Authentication token"
            }
        },
        "required": ["auth_token"]
    }
}

modules = ['requests']
