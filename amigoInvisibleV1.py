#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# =============================================================================
# Amigo Invisible V1
# 
# Created By  : Agustin Aponte
# Created Date: Mon Dic 04 2023
# =============================================================================

# Imports
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
import random
import re
import argparse
import logging
from datetime import datetime

# ===========================================================================
# Logging Configuration
# ===========================================================================
LOG_FILE = "amigo_invisible.log"
logging.basicConfig(
    filename=LOG_FILE,
    level=logging.INFO,
    format="%(asctime)s - %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S",
)

def log(message):
    print(message)  # Print to console
    logging.info(message)

# ===========================================================================
# Debugging settings
# ===========================================================================
debug = True  # Defaults to True but can be overridden via args or settings file

# ===========================================================================
# Parse Arguments
# ===========================================================================
parser = argparse.ArgumentParser(description='Settings')
parser.add_argument('--debug', type=str,
                    help='If debug is set to 1, emails are not sent. Set to 0 for production use')
parser.add_argument('--gmail_user', type=str, 
                    help='Set this to your gmail account')
parser.add_argument('--gmail_app_password', type=str, 
                    help='Create application password https://support.google.com/mail/answer/185833?hl=en')
args = parser.parse_args()

# ===========================================================================
# Class definition
# ===========================================================================
class Friend:
    def __init__(self, name, email, do_not_match_list=None):
        self.name = name
        self.email = email
        self.do_not_match_list = do_not_match_list if do_not_match_list else []

# ===========================================================================
# Helper functions
# ===========================================================================
def parse_friends():
    friends = []
    with open("./friends.txt", "r") as file:
        for line in file:
            line = line.strip()
            if not line or line.startswith("#"):
                # Ignore empty lines and comments
                continue
            data = line.split(";")
            if len(data) >= 2:
                name = data[0]
                email = data[1]
                do_not_match_list = data[2].split(",") if len(data) > 2 else []
                friends.append(Friend(name, email, do_not_match_list))
    return friends


def validate_emails(friends_list):
    regex = r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,7}\b'
    for friend in friends_list:
        if not re.fullmatch(regex, friend.email):
            log(f"Invalid email: {friend.name} - {friend.email}")
            return False
    return True

def parse_credentials():
    # Prioridad a los argumentos pasados por línea de comandos
    if args.debug and args.gmail_user and args.gmail_app_password:
        debug = bool(int(args.debug))
        gmail_user = args.gmail_user
        gmail_app_password = args.gmail_app_password
    else:
        debug = None
        gmail_user = None
        gmail_app_password = None
        
        # Leer del archivo settings.txt si no están en los argumentos
        with open("./settings.txt", "r") as file:
            for line in file:
                # Ignorar líneas vacías o comentarios
                line = line.strip()
                if not line or line.startswith("#"):
                    continue

                # Separar clave y valor correctamente
                key, value = map(str.strip, line.split("=", 1))
                value = value.strip("'\"")  # Quitar comillas simples o dobles si están presentes

                if key == "debug":
                    debug = bool(int(value))
                elif key == "gmail_user":
                    gmail_user = value
                elif key == "gmail_app_password":
                    gmail_app_password = value

    # Validar que las credenciales se hayan obtenido correctamente
    if debug is None or gmail_user is None or gmail_app_password is None:
        raise ValueError("Missing required credentials in settings.txt or command-line arguments.")

    log(f"Parsed credentials: debug={debug}, gmail_user={gmail_user}")
    return debug, gmail_user, gmail_app_password


def notify_friend(gifter_email, gifter_name, gifts_to):
    sent_from = gmail_user
    subject = "Amigo Invisible 2024"
    email_text = f"Buen día {gifter_name}!\n\nEste email es para avisarte que tenes que regalarle a {gifts_to}.\n\nFelicidades!"
    
    if debug:
        log(f"Simulated Email:\nFrom: {sent_from}\nTo: {gifter_email}\nBody:\n{email_text}")
    else:
        message = MIMEMultipart()
        message['From'] = sent_from
        message['To'] = gifter_email
        message['Subject'] = subject
        message.attach(MIMEText(email_text, 'plain'))
        try:
            server = smtplib.SMTP_SSL('smtp.gmail.com', 465)
            server.login(gmail_user, gmail_app_password)
            server.send_message(message)
            server.close()
            log(f"Email sent to {gifter_email}")
        except Exception as e:
            log(f"Error sending email to {gifter_email}: {e}")

def assign_gifts(friends_list):
    random.shuffle(friends_list)
    assignments = {}
    if assign_recipients(friends_list, assignments):
        return {friend.name: assignments[friend.name].name for friend in friends_list}
    return {}

def assign_recipients(friends_list, assignments):
    if len(assignments) == len(friends_list):
        return True
    current_friend = friends_list[len(assignments)]
    possible_recipients = [f for f in friends_list if f != current_friend and f.name not in current_friend.do_not_match_list]
    random.shuffle(possible_recipients)
    for recipient in possible_recipients:
        if recipient not in assignments.values():
            assignments[current_friend.name] = recipient
            if assign_recipients(friends_list, assignments):
                return True
            del assignments[current_friend.name]
    return False

def send_emails(assigned_gifts):
    for giver, receiver in assigned_gifts.items():
        giver_email = find_email_by_name(giver, friends_list)
        if giver_email:
            notify_friend(giver_email, giver, receiver)
        else:
            log(f"Email not found for {giver}")

def find_email_by_name(name, friends_list):
    for friend in friends_list:
        if friend.name == name:
            return friend.email
    return None

# ===========================================================================
# Main Execution
# ===========================================================================
if __name__ == "__main__":
    friends_list = parse_friends()
    debug, gmail_user, gmail_app_password = parse_credentials()

    if debug:
        log("Running in TEST mode.")
    else:
        log("Running in PRODUCTION mode.")

    if validate_emails(friends_list):
        assigned_gifts = assign_gifts(friends_list)
        if assigned_gifts:
            log("Assigned gift pairs:")
            for giver, receiver in assigned_gifts.items():
                log(f"{giver} -> {receiver}")
            send_emails(assigned_gifts)
            log("Process completed successfully.")
        else:
            log("Unable to assign gifts. Check constraints.")
    else:
        log("Email validation failed.")
