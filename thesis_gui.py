import tkinter as tk
from tkinter import filedialog, messagebox
import os
import email
from email import policy
import re
from datetime import datetime, timedelta
import pickle
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build

SCOPES = ['https://www.googleapis.com/auth/calendar.events']

# --- Google Calendar Authentication ---
def get_calendar_service():
    creds = None
    if os.path.exists('token.pkl'):
        with open('token.pkl', 'rb') as token:
            creds = pickle.load(token)
    if not creds:
        flow = InstalledAppFlow.from_client_secrets_file('credentials.json', SCOPES)
        creds = flow.run_local_server(port=0)
        with open('token.pkl', 'wb') as token:
            pickle.dump(creds, token)
    return build('calendar', 'v3', credentials=creds)

# --- .eml Parser ---
def parse_eml(file_path):
    with open(file_path, 'r', encoding='utf-8') as f:
        msg = email.message_from_file(f, policy=policy.default)
        body = msg.get_body(preferencelist=('plain')).get_content()

    event_type = None
    if re.search(r"MSc Thesis Proposal", body, re.IGNORECASE):
        event_type = "MSc Thesis Proposal"
    elif re.search(r"MSc Thesis Defense", body, re.IGNORECASE):
        event_type = "MSc Thesis Defense"
    elif re.search(r"PhD\. Seminar", body, re.IGNORECASE):
        event_type = "PhD Seminar"
    elif re.search(r"PhD\. Comprehensive Exam", body, re.IGNORECASE):
        event_type = "PhD Comprehensive Exam"

    date_match = re.search(r"Date:\s*([A-Za-z]+,?\s+[A-Za-z]+,?\s+\d{1,2}(?:[a-z]{2})?,?\s+\d{4})", body)
    time_match = re.search(r"Time:\s*(\d{1,2}:\d{2}\s*(?:AM|PM|am|pm))", body)
    location_match = re.search(r"Location:\s*(.+)", body)

    if not all([event_type, date_match, time_match, location_match]):
        return None

    try:
        dt_string = f"{date_match.group(1).strip()} {time_match.group(1).strip()}"
        dt_string = re.sub(r'(\d+)(st|nd|rd|th)', r'\1', dt_string)
        dt_string = re.sub(r',', '', dt_string)
        start = datetime.strptime(dt_string, "%A %B %d %Y %I:%M %p")
        end = start + timedelta(hours=1)
    except Exception as e:
        print(f"Date parsing error: {e}")
        return None

    summary = event_type

    return {
        'summary': summary,
        'location': location_match.group(1).strip(),
        'start': start.isoformat(),
        'end': end.isoformat(),
        'start_dt': start
    }

# --- Check for Duplicate ---
def is_duplicate_event(service, summary, start_dt):
    time_min = (start_dt - timedelta(minutes=1)).isoformat() + 'Z'
    time_max = (start_dt + timedelta(minutes=1)).isoformat() + 'Z'

    events_result = service.events().list(
        calendarId='primary',
        timeMin=time_min,
        timeMax=time_max,
        q=summary,
        singleEvents=True,
        orderBy='startTime'
    ).execute()
    events = events_result.get('items', [])

    for event in events:
        if summary.lower() in event['summary'].lower():
            return True
    return False

# --- Create Google Calendar Event ---
def create_calendar_event(service, event):
    event_body = {
        'summary': event['summary'],
        'location': event['location'],
        'start': {'dateTime': event['start'], 'timeZone': 'America/Toronto'},
        'end': {'dateTime': event['end'], 'timeZone': 'America/Toronto'},
    }
    service.events().insert(calendarId='primary', body=event_body).execute()

# --- File Handler ---
def handle_files(file_paths):
    if not file_paths:
        messagebox.showinfo("No Files", "No .eml files selected. Closing application.")
        root.destroy()
        return

    service = get_calendar_service()

    for file_path in file_paths:
        if not file_path.lower().endswith(".eml"):
            continue
        event = parse_eml(file_path)
        if not event:
            messagebox.showwarning("Skipped", f"Could not extract data from: {os.path.basename(file_path)}")
            continue

        if is_duplicate_event(service, event['summary'], event['start_dt']):
            os.remove(file_path)
            messagebox.showinfo("Duplicate Skipped", f"Duplicate event found. File deleted: {os.path.basename(file_path)}")
            continue

        confirm = messagebox.askyesno("Confirm Event", f"Add the following event?\n\n"
                                        f"Type: {event['summary']}\n"
                                        f"Location: {event['location']}\n"
                                        f"Start: {event['start']}\n"
                                        f"End: {event['end']}")

        if confirm:
            create_calendar_event(service, event)
            os.remove(file_path)
            messagebox.showinfo("Success", f"Event added and file deleted: {event['summary']}")

    root.destroy()

# --- GUI Setup ---
root = tk.Tk()
root.title("Thesis Events to Calendar (.eml)")
root.geometry("500x300")

label = tk.Label(root, text="Click below to select .eml files", pady=20)
label.pack()

btn = tk.Button(root, text="Select .eml Files", command=lambda: handle_files(filedialog.askopenfilenames(filetypes=[("Email files", "*.eml")])))
btn.pack(pady=10)

close_btn = tk.Button(root, text="Close", command=root.destroy)
close_btn.pack(pady=5)

root.mainloop()
