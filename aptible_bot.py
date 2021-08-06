# this is a friendly lil bot for room request approvals in aptible
# it sends requests into slack and allows authorized users to approve from within slack
# this is something of a beta test of the new API so let's be kind :)

import requests
import time
import json
import os
import logging
from dotenv import load_dotenv
from rooms_model import connect_to_db, db, Asks
from datetime import datetime

format = "%(asctime)s: %(message)s"
logging.basicConfig(format=format, level=logging.INFO, datefmt="%H:%M:%S")
logger = logging.getLogger(__name__)

load_dotenv()
apt_key = os.getenv('APTIBLE_KEY')
apt_url = os.getenv('APTIBLE_ROUTE')
apt_head = {'X-API-KEY': apt_key, 'Accept': 'application/json', 'Content-Type': 'application/json'}


def pending_request_check():
    # pull the current queue and compare against known requests
    # remove repeat requests and return new requests

    request_queue = requests.get(apt_url + 'authorization_request_queue', headers=apt_head)
    if request_queue.status_code == 200:
        queue_blob = request_queue.json()
        queue_info = queue_blob['authorization_requests']
        logger.info(f"Queue successfully retrieved. It is length: {len(queue_info)}")
    else:
        logger.info('Error: ',  request_queue.status_code)
    to_pop = []
    for i in range(0, len(queue_info)):
        check_db = db.session.query(Asks).filter_by(request_id=queue_info[i]['id']).first()
        if check_db:
            to_pop.append(i)
    logger.info(f"{len(to_pop)} out of {len(queue_info)} already in DB, skipped in queue")
    for i in range(len(to_pop) - 1, -1, -1):
        queue_info.pop(i)

    return queue_info


def get_queue_info(queue_info):
    # clean up the queue to be easier to put into blocks. this is vanity mostly.

    queue_size = len(queue_info)
    queue_specifics = []
    for i in range(0, len(queue_info)):
        queue_item = {}
        queue_item['id'] = queue_info[i]['id']
        queue_item['time'] = queue_info[i]['requested_at']
        queue_item['from'] = queue_info[i]['email']
        queue_item['message'] = queue_info[i]['message']
        queue_item['url'] = queue_info[i]['_links']['self']['href']
        queue_specifics.append(queue_item)
        new_request = Asks(request_id=queue_item['id'],
                            email=queue_item['from'],
                            requested_at=queue_item['time'],
                            message=queue_item['message'],
                            status='waiting',
                            url=queue_item['url'])
        db.session.add(new_request)
        db.session.commit()
        logger.info(f"added {queue_info[i]['id']} request to database")

    return queue_specifics


def approve_requests(request_id, email, addtl_perms):
    # approve a request with specified permissions where applicable

    payload = { 'request_id': request_id,
                'reviewer_email': email,
                'access_group_ids': addtl_perms,
                'nda_bypass': False }
    do_approval = requests.post(apt_url + 'authorizations', headers=apt_head, json=payload)
    if str(do_approval.status_code)[0] == '2':
        update_request_info(request_id, email, 'approved')
        return('yay')
    else:
        error_msg = 'Error encountered while attempting to approve this request. Error code received is ' + str(do_approval.status_code) + '. Please contact @vivienne for help.'
        return error_msg


def reject_requests(request_id, email, note):
    # reject a request, mwahaha

    payload = { 'status': 'ignored',
                'reviewer_email': email }
    do_rejection = requests.patch(apt_url + 'authorization_requests/' + request_id, headers=apt_head, json=payload)
    if str(do_rejection.status_code)[0] == '2':
        update_request_info(request_id, email, 'rejected', note)
        return('yay')
    else:
        error_msg = 'Error encountered while attempting to reject this request. Error code received is ' + str(do_rejection.status_code) + '. Please contact @vivienne for help.'
        return error_msg


def get_perms():
    # pull access group permissions list and format to use in options list on Slack

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
    # specifically the data about what permissions are selected, and the request id

    block_id = []
    for field in payload:
        if field['type'] == 'input':
            block_id.append(field['block_id'])
    if len(block_id) != 1:
        return('yikes')
    extras = []
    num_selected = len(selections[block_id[0]]['perms']['selected_options'])
    for i in range(0, num_selected):
        access_id = selections[block_id[0]]['perms']['selected_options'][i]['value']
        extras.append(access_id)
    return extras


def update_request_info(request_id, email, action, note="N/A"):
    # update request info in the db once approved or not

    timestamp = datetime.now()
    reviewed = timestamp.strftime("%B %d, %Y, %I:%M %p")
    processed_request = db.session.query(Asks).filter_by(request_id=request_id).first()
    processed_request.reviewer = email
    processed_request.reviewed_at = reviewed
    processed_request.status = action
    processed_request.reject_note = note
    db.session.commit()
