#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# =============================================================================
# Amigo Invisible V1
# 
# Created By  : Agustin Aponte
# Created Date: Mon Dic 04 2023

# ===========================================================================
# Imports
# ===========================================================================
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
import random

# ===========================================================================
# Debugging settings
# ===========================================================================

#If debug==True, results are printed without sending emails
debug = True

# ===========================================================================
# Class definition
# ===========================================================================

# Friend class. Each instance needs a name, email, and can include a do_not_match_list
class Friend:
    def __init__(self, name, email, do_not_match_list=None):
        self.name = name
        self.email = email
        self.do_not_match_list = do_not_match_list if do_not_match_list else []

# ===========================================================================
# Helper functions
# ===========================================================================

# Parse friends from friends.txt
def parse_friends():
    friends=[]
    with open("./friends.txt", "r") as file:
        for line in file:
            data = line.strip().split(";")
            if len(data) >= 2:  # Ensure there are at least 2 elements in the data list
                name = data[0]
                email = data[1]
                # Split the third item (if exists) into a list based on comma-separated values
                do_not_match_list = data[2].split(",") if len(data) > 2 else []
                friend = Friend(name, email, do_not_match_list)
                friends.append(friend)
            else:
                print(f"Empty line: {line.strip()}. Skipping.")
    file.close()
    return friends

# Parse credentials from credentials.txt
def parse_credentials():
    with open("./credentials.txt","r") as file:
        for line in file:
            if line != "":
                data = line.split("=")
                if str(data[0]).strip()=="gmail_user": gmail_user=str(data[1]).strip()
                if str(data[0]).strip()=="gmail_app_password": gmail_app_password=str(data[1]).strip()
    return gmail_user,gmail_app_password
    file.close()

# Send an email to each gifter
def notify_friend(gifter_email, gifter_name, gifts_to):
    sent_from = gmail_user
    sent_subject = "Amigo Invisible 2023"
    email_text = f"""\
    Buen día {gifter_name}!

    Este email es para avisarte que tienes que regalarle a {gifts_to}

    Felicidades!
    
    """
    if debug==True:
        print("From "+sent_from)
        print(("To "+gifter_email))
        print(MIMEText(email_text, 'plain'))
    if debug==False:
        # Create a multipart message and set headers
        message = MIMEMultipart()
        message['From'] = sent_from
        message['To'] = gifter_email
        message['Subject'] = sent_subject
    
        # Add body to email
        message.attach(MIMEText(email_text, 'plain'))
    
        try:
            server = smtplib.SMTP_SSL('smtp.gmail.com', 465)
            server.ehlo()
            server.login(gmail_user, gmail_app_password)
            server.send_message(message)
            server.close()
    
            print('Email sent!')
        except Exception as exception:
            print("Error: %s!\n\n" % exception)

# Assign gifts by calling assign_recipients
def assign_gifts(friends_list):
    assigned_gifts = {}
    random.shuffle(friends_list)
    assignments = {}
    if assign_recipients(friends_list, assignments):
        assigned_gifts = {friend.name: assignments[friend.name].name for friend in friends_list}
    return assigned_gifts

# Assign recipients that are not in the doNotMatch list
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

# Send email to each gifter
def send_emails(assigned_gifts):
    
# Return email of a friend by name
    for giver, receiver in assigned_gifts.items():
        giver_email = find_email_by_name(giver, friends_list)
        receiver_email = find_email_by_name(receiver, friends_list)
        if giver_email and receiver_email:
            print(f"{giver} {giver_email} le regala a  {receiver_email}")
            notify_friend(giver_email,giver, receiver)
        else:
            print("Email address not found for giver or receiver")
    print("emails sent...")
def find_email_by_name(name, friends_list):
    for friend in friends_list:
        if friend.name == name:
            return friend.email
    return None  # Return None if the name is not found in the friends_list

# ================================================
# MAIN
# ================================================
friends_list=[]

# Call function to parse credentials
gmail_user,gmail_app_password=parse_credentials()

# Call function to parse friends
friends_list = parse_friends()
if debug==True:
    print(len(friends_list))
    for friend in friends_list: print(friend)

# Call function to assign gifts
assigned_gifts = assign_gifts(friends_list)

if assigned_gifts:
    send_emails(assigned_gifts)
else:
    print("Unable to assign gifts. Please adjust constraints and try again.")
