#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# =============================================================================
# Amigo Invisible V1 - Prototipo, no funciona
# 
# Created By  : Agustin Aponte
# Created Date: Mon Dic 04 2023
# =============================================================================
# Imports
# =============================================================================
import smtplib
import random

# =============================================================================
# Set mail auth
# =============================================================================
gmail_user = 'agustin.aponte@gmail.com'
gmail_app_password = 'nnex uqyl zgkp cjhm'

# =============================================================================
# Set list of Friends
# =============================================================================
friends_list=[["agustin","agustin.aponte@gmail.com", []],["agustin2","agustin.aponte@gmail.com",[]],["agustin3","agustin.aponte@gmail.com",[]]]

# =============================================================================
# Define notifyFriend function
# =============================================================================

def notifyFriend(gmail_user, dest_email, dest_name,gifts_to):
    sent_from = gmail_user
    sent_to = dest_email
    sent_subject = "Amigo Invisible 2023"
    sent_body = ("Buen día "+dest_name+"! \n\n"+
                 "Este email es para avisarte que tenes que regalarle a "+gifts_to+"\n"
                 "\n\n"
                 "Agustin\n")
    
    email_text = """\
    From: %s
    To: %s
    Subject: %s
    
    %s
    """ % (sent_from, ", ".join(sent_to), sent_subject, sent_body)

    try:
        server = smtplib.SMTP_SSL('smtp.gmail.com', 465)
        server.ehlo()
        server.login(gmail_user, gmail_app_password)
        server.sendmail(sent_from, sent_to, email_text)
        server.close()
    
        print('Email sent!')
    except Exception as exception:
        print("Error: %s!\n\n" % exception)
        
def shuffle_gifts(friends_list):
    # Receive a list with an element for each friend, composed of [name,email]
    #
    # Append gifts_to field from a scrambled copy of friends_list
    # 
    # While tests_passed==False:
    #   Scramble and perform tests
    # 
    # Return friends_list
    tests_passed = False
    
    def shuffle_names(friends_list):
        # Shuffle names
        names = [f[0]for f in friends_list]
        names = random.shuffle(names)
        print("shuffle_names done")
        return names
    
    def test_shuffle(friends,shuffled_list):
        print(type(friends[0][0]))
        print(shuffled_list)
        for index in range(len(friends_list)):
            if friends[index][0]==shuffled_list[index]:
                print("list rejected: can't gift yourself")
                return False
            if shuffled_list[index] in friends[2]:
                print("list rejected: can't gift partner")
                return False
        print("tests passed")
        return True
    
    # Shuffle forever until tests are passed
    while tests_passed == False:
        shuffled_names=shuffle_names(friends_list)
        tests_passed = test_shuffle(friends_list, shuffled_names)
    
    # Merge lists and return resulting list
    for index in range(len(friends_list)): friends_list[index].append(shuffled_names[index])
    return friends_list

print(list(r) for r in shuffle_gifts(friends_list))
    
    

