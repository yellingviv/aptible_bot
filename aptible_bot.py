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
        print('***Queue successfully retrieved.***')
        # what_to_do()
    else:
        print('Unknown error encountered.')
        print('Error: ',  request_queue.status_code)
        print('')

    return queue_info

    # dict['authorization_requests'] contains list of n requests
    # each request is a dict
    # 'id', 'created_at', 'updated_at', '_type', 'dataroom_id', 'email', 'message', 'status', 'requested_at'
    # 'links' { 'self': {' href': }}

def show_queue_info():
    # clean up the queue to be easier to put into blocks. this is vanity mostly.

    queue_size = len(queue_info)
    print('There are ', queue_size, ' requests in the queue.')
    queue_specifics = []

    for i in range(0, len(queue_info)):
        queue_item = {}
        queue_item['id'] = queue_info[i]['id']
        queue_item['time'] = queue_info[i]['requested_at']
        queue_item['from'] = queue_info[i]['email']
        queue_item['message'] = queue_info[i]['message']
        queue_item['status'] = queue_info[i]['status']
        queue_item['url'] = queue_info[i]['_links']['self']['href']
        queue_specifics.append(queue_item)

    return queue_specifics


def approve_requests():
    # approve a request? all? tbd

    approve_id = queue_info[index]['id']
    group_pull = requests.get(apt_url + 'access_groups', headers=apt_head)
    group_blob = group_pull.json()
    group_list = group_blob['access_groups']
    access_ids = []
    if accesses != '00':
        access_list = list(accesses)
        for access in access_list:
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


def get_perms():
    # pull access groups and format to use in options

    access_pull = requests.get(apt_url + 'access_groups', headers=apt_head)
    access_blob = access_pull.json()
    access_list = access_blob['access_groups']
    access_choices = []
    for i in range(0, len(access_list)):
        access_option = {
            "text": {
                "type": "plain_text",
                "text": access_list[i]['name']
            },
            "value": access_list[i]['id']
        }
        access_choices.append(access_option)
    return access_choices


def get_selections(payload, selections):
    # sort through the giant effing block of slack interactivity response for data

    block_id = []
    for field in payload:
        if field['type'] == 'input':
            block_id.append(field['block_id'])
    if len(block_id) != 1:
        print('somehow we have more than one input field, please panic')
        return('yikes')
    extras = []
    num_selected = len(selections[block_id[0]]['perms']['selected_options'])
    for i in range(0, num_selected):
        access_id = selections[block_id[0]]['perms']['selected_options'][i]['value']
        extras.append(access_id)
    print(extras)
    return extras


queue_info = pending_request_check()
# what_to_do()
