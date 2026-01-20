# LiteRead - Automated Email Outreach Tool

LiteRead is a simple tool designed to help you send personalized emails to business leads automatically, one by one. It uses your Mac's built-in "Mail" app to send messages safely and looks completely human.

## What It Does
1.  **Reads Your List:** It looks at a list of people you want to email (stored in a `leads.csv` file).
2.  **Personalizes Each Email:** It takes the specific subject and message you wrote for each person.
3.  **Sends Automatically:** It opens your Apple Mail app and sends the email for you.
4.  **Waits Between Emails:** To keep your account safe and avoid being marked as spam, it waits **5 minutes** between every email it sends.
5.  **Remembers History:** It keeps a list of who has already been emailed so you don't accidentally message the same person twice.

## How to Use It

### 1. Requirements
- A Mac computer.
- The "Mail" app set up with your email account (e.g., `reza@pulzivo.dev`).
- Python installed (most Macs have this).

### 2. Setup
1.  Download this folder.
2.  Open your "Terminal" app.
3.  Go to the folder where you downloaded this tool:
    ```bash
    cd path/to/LiteRead/email_tool
    ```

### 3. Adding Leads
Open the `leads.csv` file. You will see columns for `name`, `email`, `subject`, and `body`.
- **name:** The person's name (e.g., Karmen LaMer).
- **email:** Their email address.
- **subject:** The subject line of the email.
- **body:** The full message you want to send. (Make sure it is in quotes if it has multiple lines).

### 4. Running the Tool
In your Terminal, run:
```bash
python3 send_emails.py
```

### 5. What Happens Next?
- The tool will start sending emails.
- It will tell you on the screen who it is sending to.
- It will show a countdown (e.g., "Waiting... 4 minutes left") between emails.
- **Do not close the Terminal window** until it is finished.

## Safety Features
- **Spam Protection:** The 5-minute delay ensures you don't send too many emails too quickly.
- **Duplicate Protection:** If you run the tool again, it checks `sent_history.log` and skips anyone you have already contacted.
