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


def approve_requests(request_id, email, addtl_perms):
    # approve a request

    payload = { 'request_id': request_id,
                'reviewer_email': email,
                'access_group_ids': addtl_perms,
                'nda_bypass': False }
    print('Payload: ', payload)
    do_approval = requests.post(apt_url + 'authorizations', headers=apt_head, json=payload)
    if str(do_approval.status_code)[0] == '2':
        print('Request successfully approved.')
        return('yay')
    else:
        error_msg = 'Error encountered while attempting to approve this request. Error code received is ' + str(do_approval.status_code) + '. Please contact @vivienne for help.'
        return error_msg


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
    return extras


def status_update(id, email):
    payload = {'status': 'ignored', 'reviewer_email': 'vpustell@pagerduty.com'}
    new_status = requests.patch(apt_url + 'authorization_requests/' + id, headers=apt_head, json=payload)
    print(new_status.status_code)


queue_info = pending_request_check()
# what_to_do()
