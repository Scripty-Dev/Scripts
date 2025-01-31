import json
import requests
import re
from datetime import datetime, timedelta

def extract_sender_info(from_header):
    """Extract name and email from From header."""
    name = re.match(r'^([^<]+)', from_header)
    email = re.findall(r'<(.+?)>', from_header)
    return {
        'name': name.group(1).strip() if name else '',
        'email': email[0] if email else from_header.strip()
    }

def classify_email(subject, from_header):
    # First check automated patterns
    sender = extract_sender_info(from_header)
    automated_patterns = [r'noreply@', r'no-reply@', r'donotreply@', r'notifications?@']
    if any(re.search(pattern, sender['email'].lower()) for pattern in automated_patterns):
        return False

    messages = [
        {"role": "system", "content": "You are an email assistant that determines if emails need replies."},
        {"role": "user", "content": f"""Determine if this email needs a reply based on sender and subject only. Reply with "NEEDS_REPLY" or "NO_REPLY".

Rules:
- NEEDS_REPLY: Personal emails, business communications needing action, direct questions
- NO_REPLY: Marketing, newsletters, broadcasts, automated notifications

From Name: {sender['name']}
From Email: {sender['email']}
Subject: {subject}"""}
    ]

    response = requests.post(
        "https://scripty.me/api/assistant/call",
        headers={"Authorization": f"Bearer {authtoken}"},
        json={
            "model": "mixtral-8x7b-32768",
            "messages": messages
        }
    ).json()

    return "NEEDS_REPLY" in response.get('content', '').upper()

def generate_draft(subject, body, from_header, to_addr):
    sender = extract_sender_info(from_header)
    
    # Format proper email headers
    reply_subject = subject if subject.startswith('Re:') else f'Re: {subject}'
    reply_to = sender['email']
    
    messages = [
        {"role": "system", "content": f"You are an email assistant helping {to_addr} write replies."},
        {"role": "user", "content": f"""Write a reply from {to_addr} to {sender['name']}.

Original Email:
Subject: {subject}
Body: {body}

Guidelines:
1. Address sender by name when appropriate
2. Match original tone
3. Address all points
4. Be concise but thorough
5. Don't include email headers in the response body"""}
    ]

    response = requests.post(
        "https://scripty.me/api/assistant/call",
        headers={"Authorization": f"Bearer {authtoken}"},
        json={
            "model": "mixtral-8x7b-32768",
            "messages": messages
        }
    ).json()

    return response.get('content', "Thank you for your email. I will respond shortly.")

def process_unread_emails(days=1):
    try:
        print(f"Checking emails from past {days} days")
        response = requests.get(
            "https://scripty.me/api/assistant/email/unread",
            headers={"Authorization": f"Bearer {authtoken}"},
            params={"days": days}
        )
        emails = response.json()
        print(f"Found {len(emails) if isinstance(emails, list) else 'invalid'} emails")
        if not isinstance(emails, list):
            return {"success": False, "error": "Invalid response from email API"}
        
        results = []
        for email_data in emails:
            if classify_email(email_data["subject"], email_data["from"]):
                draft = generate_draft(
                    email_data["subject"],
                    email_data["body"], 
                    email_data["from"],
                    email_data["to"]
                )
                
                if draft:
                    # Format proper email draft
                    formatted_draft = {
                        "original_message_id": email_data["message_id"],
                        "content": draft,
                        "subject": f"Re: {email_data['subject']}" if not email_data['subject'].startswith('Re:') else email_data['subject'],
                        "to": extract_sender_info(email_data["from"])["email"]
                    }
                    
                    requests.post(
                        "https://scripty.me/api/assistant/email/draft",
                        headers={"Authorization": f"Bearer {authtoken}"},
                        json=formatted_draft
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
        days = int(args.get("days", 1))
        return json.dumps(process_unread_emails(days))
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
            }
        }
    }
}

modules = ['requests']
