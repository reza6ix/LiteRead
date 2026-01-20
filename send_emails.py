import csv
import subprocess
import os
import sys

SENDER_ADDRESS = "reza@pulzivo.dev"

def send_email(name, email, subject, body):
    # Escape double quotes in body for AppleScript
    safe_body = body.replace('"', '\\"')
    safe_subject = subject.replace('"', '\\"')
    
    script = f'''
    tell application "Mail"
        set newMessage to make new outgoing message with properties {{subject:"{safe_subject}", content:"{safe_body}", visible:false}}
        tell newMessage
            make new to recipient at end of to recipients with properties {{address:"{email}"}}
            set sender to "{SENDER_ADDRESS}"
        end tell
        send newMessage
    end tell
    '''
    
    try:
        result = subprocess.run(['osascript', '-e', script], capture_output=True, text=True)
        if result.returncode == 0:
            print(f"✅ Sent email to {name} <{email}>")
        else:
            print(f"❌ Failed to send to {name} <{email}>: {result.stderr}")
    except Exception as e:
        print(f"❌ Error sending to {name} <{email}>: {e}")

LOG_FILE = 'sent_history.log'

def is_sent(email):
    if not os.path.exists(LOG_FILE):
        return False
    with open(LOG_FILE, 'r') as f:
        return email in f.read()

def mark_as_sent(email):
    with open(LOG_FILE, 'a') as f:
        f.write(f"{email}\n")

def main():
    csv_path = 'leads.csv'
    
    if not os.path.exists(csv_path):
        print(f"Error: {csv_path} not found.")
        return

    # Read CSV and send emails
    with open(csv_path, 'r') as csvfile:
        reader = csv.DictReader(csvfile)
        reader.fieldnames = [name.lower() for name in reader.fieldnames]
        
        rows = list(reader)
        total_emails = len(rows)
        
        for i, row in enumerate(rows):
            email = row['email']
            name = row.get('name', 'there')
            subject = row['subject']
            body = row['body']
            
            if not email or is_sent(email):
                print(f"Skipping {email} (already sent or empty)")
                continue
            
            print(f"[{i+1}/{total_emails}] Sending to {name} <{email}>...")
            send_email(name, email, subject, body)
            mark_as_sent(email)
            
            if i < total_emails - 1:
                import time
                wait_time = 300
                for remaining in range(wait_time, 0, -60):
                    print(f"Waiting... {remaining//60} minutes left.")
                    time.sleep(60 if remaining >= 60 else remaining)

if __name__ == "__main__":
    main()
