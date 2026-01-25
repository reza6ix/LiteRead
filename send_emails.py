import csv
import subprocess
import os
import sys
import time

SENDER_ADDRESS = "reza@pulzivo.dev"
TEMPLATE_FILE = 'template.txt'
CSV_FILE = 'special.csv'
LOG_FILE = 'sent_history.log'

def get_customer_type(business_type):
    bt = business_type.lower()
    if any(x in bt for x in ['dental', 'clinic', 'medspa', 'physio', 'chiro', 'health', 'medical', 'doctor', 'wellness']):
        return "patient"
    elif any(x in bt for x in ['gym', 'fitness', 'club', 'training', 'martial']):
        return "member"
    elif any(x in bt for x in ['salon', 'barber', 'hair', 'beauty', 'spa']):
        return "client"
    else:
        return "customer"

def load_template():
    if not os.path.exists(TEMPLATE_FILE):
        print(f"Error: {TEMPLATE_FILE} not found.")
        sys.exit(1)
    
    with open(TEMPLATE_FILE, 'r') as f:
        content = f.read()
    
    # Split subject and body
    lines = content.split('\n')
    subject_line = ""
    body_start_index = 0
    
    for i, line in enumerate(lines):
        if line.lower().startswith("subject:"):
            subject_line = line[len("subject:"):].strip()
            body_start_index = i + 1
            break
            
    body = "\n".join(lines[body_start_index:]).strip()
    return subject_line, body

def send_email(name, email, subject, body):
    # Remove markdown bold/italics
    clean_body = body.replace('**', '').replace('_', '')
    
    # Escape double quotes and backslashes for AppleScript
    safe_body = clean_body.replace('\\', '\\\\').replace('"', '\\"')
    safe_subject = subject.replace('\\', '\\\\').replace('"', '\\"')
    safe_name = name.replace('\\', '\\\\').replace('"', '\\"')
    safe_email = email.replace('\\', '\\\\').replace('"', '\\"')
    
    script_content = f'''
    tell application "Mail"
        set newMessage to make new outgoing message with properties {{subject:"{safe_subject}", content:"{safe_body}", visible:false}}
        tell newMessage
            make new to recipient at end of to recipients with properties {{name:"{safe_name}", address:"{safe_email}"}}
            set sender to "{SENDER_ADDRESS}"
        end tell
        send newMessage
    end tell
    '''
    
    script_path = 'temp_mail.applescript'
    with open(script_path, 'w') as f:
        f.write(script_content)
    
    try:
        result = subprocess.run(['osascript', script_path], capture_output=True, text=True)
        if os.path.exists(script_path):
            os.remove(script_path)
        
        if result.returncode == 0:
            print(f"✅ Sent email to {name} <{email}>")
            return True
        else:
            print(f"❌ Failed to send to {name} <{email}>: {result.stderr}")
            return False
    except Exception as e:
        if os.path.exists(script_path):
            os.remove(script_path)
        print(f"❌ Error sending to {name} <{email}>: {e}")
        return False

def is_sent(email):
    if not os.path.exists(LOG_FILE):
        return False
    with open(LOG_FILE, 'r') as f:
        return email in f.read()

def mark_as_sent(email):
    with open(LOG_FILE, 'a') as f:
        f.write(f"{email}\n")

def main():
    if not os.path.exists(CSV_FILE):
        print(f"Error: {CSV_FILE} not found.")
        return

    subject_template, body_template = load_template()

    # Read CSV and send emails
    with open(CSV_FILE, 'r') as csvfile:
        reader = csv.DictReader(csvfile)
        
        # Normalize headers to match expected keys if necessary, strictly using headers from special.csv
        # Columns: Region,Business Name,Business Type,Website,Google Maps URL,City,Decision Maker Name,Decision Maker Role,Direct Phone (public),Direct Email (public),...
        
        rows = list(reader)
        total_emails = len(rows)
        
        sent_count = 0
        
        for i, row in enumerate(rows):
            email = row.get('Direct Email (public)')
            if not email:
                email = row.get('Main Business Email') # Fallback
            
            if not email:
                print(f"Skipping row {i+1}: No email found.")
                continue

            # Check if already sent
            if is_sent(email):
                print(f"Skipping {email} (already sent)")
                continue

            full_name = row.get('Decision Maker Name', 'there')
            first_name = full_name.split()[0] if full_name else "there"
            business_name = row.get('Business Name', 'your business')
            business_type = row.get('Business Type', '')
            
            customer_type = get_customer_type(business_type)
            
            # Personalize
            try:
                subject = subject_template.format(
                    business_name=business_name,
                    first_name=first_name,
                    decision_maker_name=full_name,
                    customer_type=customer_type
                )
                
                body = body_template.format(
                    business_name=business_name,
                    first_name=first_name,
                    decision_maker_name=full_name,
                    customer_type=customer_type
                )
            except KeyError as e:
                print(f"❌ Template Error: Missing key {e} for {email}")
                continue

            print(f"[{i+1}/{total_emails}] Sending to {first_name} at {business_name} <{email}>")
            
            if send_email(full_name, email, subject, body):
                mark_as_sent(email)
                sent_count += 1
                
                # Wait logic to avoid spamming
                if i < total_emails - 1:
                    wait_seconds = 120  # 2 minutes
                    print(f"Waiting {wait_seconds} seconds before next email...")
                    time.sleep(wait_seconds)
if __name__ == "__main__":
    main()