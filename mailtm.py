#!/usr/bin/python3

import requests
import time
import json
import NewMailService

MAILTM_HEADERS = {   
    "Accept": "application/json",
    "Content-Type": "application/json",
    "Authorization":"Bearer eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzUxMiJ9.eyJpYXQiOjE3MDIzODQ0NjEsInJvbGVzIjpbIlJPTEVfVVNFUiJdLCJhZGRyZXNzIjoibXVueWlyaTFAd2lyZWNvbm5lY3RlZC5jb20iLCJpZCI6IjY1Nzg0ZjkxOWJhMjU2NWZmNjBmYmYwMyIsIm1lcmN1cmUiOnsic3Vic2NyaWJlIjpbIi9hY2NvdW50cy82NTc4NGY5MTliYTI1NjVmZjYwZmJmMDMiXX19.kHgYramr6D7IrYl5KYtzMsGikcWeeJwozRJBrDji1fccOrztbf1tnzpPuZRiF6ptTqSjRihglvMwU0UvlHhNyw"
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

# request to get the id and token

# my_data = requests.post(BASE_URL + '/token',json={
#   "address": 'munyiri1@wireconnected.com',
#   "password": "1000waystodie",
# })

# print(my_data.json())

# received token and id

# {'token': 'eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzUxMiJ9.eyJpYXQiOjE3MDIzODQ0NjEsInJvbGVzIjpbIlJPTEVfVVNFUiJdLCJhZGRyZXNzIjoibXVueWlyaTFAd2lyZWNvbm5lY3RlZC5jb20iLCJpZCI6IjY1Nzg0ZjkxOWJhMjU2NWZmNjBmYmYwMyIsIm1lcmN1cmUiOnsic3Vic2NyaWJlIjpbIi9hY2NvdW50cy82NTc4NGY5MTliYTI1NjVmZjYwZmJmMDMiXX19.kHgYramr6D7IrYl5KYtzMsGikcWeeJwozRJBrDji1fccOrztbf1tnzpPuZRiF6ptTqSjRihglvMwU0UvlHhNyw', '@id': '/accounts/65784f919ba2565ff60fbf03', 'id': '65784f919ba2565ff60fbf03'}

# get the messages received. From WIRED.com

messages_request = BASE_URL + '/messages'

messages = requests.get(messages_request,headers = MAILTM_HEADERS)

# print(messages.json())

new_messages = messages.json()

# listen to messages

webhook_url = 'https://mercure.mail.tm/.well-known/mercure'

# all messages coming as read (remain as unread even after fetch), fetch message, save message id in a list
read_messages_ids = []

patch_url =  BASE_URL + '/messages/'

# get messages periodically, get the messa
# save all current messages as read. Mark all as read


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
    

# parseMail(new_messages)
print(parseMail(new_messages))

# read the messages
start = 0
while (start < len(new_messages)):
    msgid = new_messages[start]['msgid']
    if new_messages[start]['seen'] == 'False':
        requests.patch(patch_url + msgid,headers = MAILTM_HEADERS)
        read_messages_ids.append(msgid)
    read_messages_ids.append(msgid)
    start = start + 1

