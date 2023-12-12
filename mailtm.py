#!/usr/bin/python3

import requests
import time
import json
from server import NewMailService
from decouple import config
from threading import Timer
import threading

TOKEN = config('TOKEN')

MAILTM_HEADERS = {   
    "Accept": "application/json",
    "Content-Type": "application/json",
    "Authorization":"Bearer " + TOKEN
}

class MailTmError(Exception):
    pass

def _make_mailtm_request(request_fn, timeout = 600):
    tstart = time.monotonic()
    error = None
    status_code = None
    while time.monotonic() - tstart < timeout:
        try:
            r = request_fn()
            status_code = r.status_code
            if status_code == 200 or status_code == 201:
                return r.json()
            if status_code != 429:
                break
        except (requests.exceptions.Timeout, requests.exceptions.ConnectionError) as e:
            error = e
        time.sleep(1.0)
    
    if error is not None:
        raise MailTmError(error) from error
    if status_code is not None:
        raise MailTmError(f"Status code: {status_code}")
    if time.monotonic() - tstart >= timeout:
        raise MailTmError("timeout")
    raise MailTmError("unknown error")

def get_mailtm_domains():
    def _domain_req():
        return requests.get("https://api.mail.tm/domains", headers = MAILTM_HEADERS)
    
    r = _make_mailtm_request(_domain_req)

    return [ x['domain'] for x in r ]

def create_mailtm_account(address, password):
    account = json.dumps({"address": address, "password": password})   
    def _acc_req():
        return requests.post("https://api.mail.tm/accounts", data=account, headers=MAILTM_HEADERS)

    r = _make_mailtm_request(_acc_req)
    assert len(r['id']) > 0

# create account
# create_mailtm_account('munyiri1@wireconnected.com','1000waystodie')

#

BASE_URL = 'https://api.mail.tm'

mypage = BASE_URL + '/me'

messages_request = BASE_URL + '/messages'

def getMessages(request,headers):
    messages = requests.get(request,headers = headers)
    print(messages.json())
    return messages.json()

def parseMail(obj):
    unread = []
    email_sources = []
    headers = []
    for mail in obj:
        if mail['seen'] != 'False':
            unread.append(mail)
    for mail in unread:
        email_sources.append(mail['from']['address'])
        headers.append(mail['subject'])
    data = [email_sources,headers]
    return data


def displayMail(obj):
    # instantiate the class object from server.py
    new_mail = NewMailService()
    mails_length = len(obj[0])
    start = 0
    while start < mails_length:
        new_mail.on_new_mail(obj[0][start],obj[1][start])
        start = start + 1

# read the messages
def readMessages(obj):
    start = 0
    while (start < len(obj)):
        msgid = obj[start]['id']
        if obj[start]['seen'] == 'False':
            print(patch_url + msgid)
            requests.patch(patch_url + msgid,headers = MAILTM_HEADERS)
            start = start + 1

def runAll():
    new_messages = getMessages(messages_request,MAILTM_HEADERS)
    parsed_messages = parseMail(new_messages)
    displayMail(parsed_messages)
    readMessages(new_messages)

t = Timer(10, runAll)

t.start()
