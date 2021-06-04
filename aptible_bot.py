# this is a friendly lil bot for room request approvals in aptible
# it sends requests into slack and allows authorized users to approve from within slack
# this is something of a beta test of the new API so let's be kind :)

# from flask import Flask, render_template, redirect, request, flash, session, jsonify
import requests
import time
import json
from dotenv import load_dotenv

load_dotenv()
apt_key = os.getenv('APTIBLE_KEY')
apt_url = os.getenv('APTIBLE_ROUTE')

# check for active requests in queue

def pending_request_check():

    request_queue = requests.get(url + 'authorization_request_queue')
    if request_queue.status_code == '200':
        queue_json = json.loads(request_queue.text)
        print("queue contents: ")
        print(queue_json)
        print("End of contents, returning to main menu.")
        print("")
        what_to_do()
    else:
        print("Unknown error encountered. Returning to main menu.")
        print("")
        what_to_do()

def pull_request_ids():
    # retrieve ids of active requests in queue
    print("pending")


def request_details():
    # get information on active requests
    print("pending")

def approve_requests():
    # approve a request? all? tbd
    print("pending")

def get_user_info():
    # for purposes of cli testing, get user info
    # in slack version, should pull from user info
    print("pending")

def handle_action_choice(choice):
    # for purposes of cli testing, handle cli input

    action = choice.lower()
    if action == 'q':
        pending_request_check()
    elif action == 'a':
        approve_requests()
    elif action == 'd':
        request_details()
    elif action == 'x':
        quit()
    else:
        print("Unclear input. Please try again.")
        print("")
        what_to_do()


def what_to_do():
    # for purposes of cli testing, serve option menu

    print("What would you like to do? Input a single letter.")
    print("     Q: check queue")
    print("     A: approve pending requests")
    print("     D: get details about pending requests")
    print("     X: exit")
    print("")
    action_choice = input(">>> ")
