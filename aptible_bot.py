# this is a friendly lil bot for room request approvals in aptible
# it sends requests into slack and allows authorized users to approve from within slack
# this is something of a beta test of the new API so let's be kind :)

# from flask import Flask, render_template, redirect, request, flash, session, jsonify
import requests
import time
import json
import os
from dotenv import load_dotenv

load_dotenv()
apt_key = os.getenv('APTIBLE_KEY')
apt_url = os.getenv('APTIBLE_ROUTE')
apt_head = {'X-API-KEY': apt_key, 'Accept': 'application/json', 'Content-Type': 'application/json'}


def pending_request_check():
    # check for active requests in queue

    request_queue = requests.get(apt_url + 'authorization_request_queue', headers=apt_head)
    if request_queue.status_code == 200:
        queue_blob = request_queue.json()
        queue_info = queue_blob['authorization_requests']
        print("***Queue successfully retrieved.***")
        # what_to_do()
    else:
        print("Unknown error encountered.")
        print("Error: ",  request_queue.status_code)
        print("")

    return queue_info

    # dict['authorization_requests'] contains list of n requests
    # each request is a dict
    # 'id', 'created_at', 'updated_at', '_type', 'dataroom_id', 'email', 'message', 'status', 'requested_at'
    # 'links' { 'self': {' href': }}

def show_queue_info():
    # display the information of what is in the queue

    queue_size = len(queue_info)
    print("There are ", queue_size, " requests in the queue.")

    for i in range(0, len(queue_info)):
        print("Request ", i + 1, ":")
        print("Request ID: ", queue_info[i]['id'])
        print("Request Date: ", queue_info[i]['requested_at'])
        print("Requester Email: ", queue_info[i]['email'])
        print("Request Message: ", queue_info[i]['message'])
        print("")


def approve_requests():
    # approve a request? all? tbd
    print("pending")

    to_approve = input("What number request would you like to approve? >>> ")
    if to_approve.isnumeric() == False:
        print("Please enter a number.")
        approve_requests()
    index = int(to_approve) - 1
    if index > len(queue_info):
        print("please try another request, this one is not found.")
        approve_requests()
    approve_id = queue_info[index]['id']
    group_pull = requests.get(apt_url + 'access_groups', headers=apt_head)
    group_blob = group_pull.json()
    group_list = group_blob['access_groups']
    print("Access Groups:")
    for i in range(0, len(group_list)):
        print(" > ", i+1, group_list[i]['name'])
    print(" > 00 Default access. Cannot be paired with any other access option.")
    accesses = input("Please enter the numbers you would like, no spaces or commas >>> ")
    if accesses.isnumeric() == False:
        print("Please enter only numeric group IDs.")
        approve_requests()
    access_list = list(accesses)
    access_ids = []
    print(access_list)
    for access in access_list:
        if access == '00':
            access_ids = []
        else:
            index = int(access) - 1
            id = group_list[index]['id']
            access_ids.append(id)
    email = get_user_info()
    payload = { 'request_id': approve_id,
                'reviewer_email': email,
                'access_group_ids': access_ids,
                'nda_bypass': False }
    print('Payload: ', payload)
    do_approval = requests.post(apt_url + 'authorizations', headers=apt_head, json=payload)
    if str(do_approval.status_code)[0] == '2':
        print('Request successfully approved.')
    else:
        print('Error encountered. Error code ', do_approval.status_code, '. Please contact @vivienne.')


def get_user_info():
    # for purposes of cli testing, get user info
    # in slack version, should pull from user info

    email = input("Please provide your email address >>> ")
    return email


def handle_action_choice(choice):
    # for purposes of cli testing, handle cli input

    action = choice.lower()
    if action == 'q':
        show_queue_info()
    elif action == 'a':
        approve_requests()
    elif action == 'd':
        request_details()
    elif action == 'x':
        os.exit()
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
    handle_action_choice(action_choice)


queue_info = pending_request_check()
# what_to_do()
