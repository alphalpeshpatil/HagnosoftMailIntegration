from email import encoders, parser
from email.mime.audio import MIMEAudio
from email.mime.base import MIMEBase
from email.mime.image import MIMEImage
import enum
import io
import mimetypes
import psycopg2

import logging
from oauth2client.client import flow_from_clientsecrets
from oauth2client.client import FlowExchangeError
# from googleapiclient.discovery import build


import pathlib
from flask import jsonify
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from google_auth_oauthlib.flow import Flow
import base64
import pickle
from googleapiclient.errors import HttpError
import os
import json
import base64
from flask import Flask, jsonify, request
from email.message import EmailMessage

from Google import Create_Service
import base64
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
# from google.oauth2.credentials import AccessTokenCredentials
import google.auth
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError
from bs4 import BeautifulSoup

from login import API_NAME, API_VERSION, CLIENT_SECRET_FILE

from apiclient import discovery
from apiclient import errors
from httplib2 import Http
import base64
from bs4 import BeautifulSoup
import re
import time
# import dateutil.parser as parser
import datetime
from datetime import datetime

from google.oauth2.credentials import Credentials
from google.auth.transport.requests import Request
from google.oauth2 import id_token
import google.auth.credentials
from google.auth.transport.requests import AuthorizedSession

connection = psycopg2.connect(user="postgres",password="root",host="localhost",port="5433",database="postgres")
cursor = connection.cursor()

# app.config['SECRET_KEY']='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'
# app.config['SESSION_PERMANENT']=False
# app.config['SESSION_TYPE']="filesystem"
# If modifying these scopes, delete the file token.json.
SCOPES = ['https://www.googleapis.com/auth/gmail.readonly']
global_creds=[]
home_dir=os.path.expanduser('~')
pickle_path=os.path.join(home_dir,'gmail.pickle')
global_creds_set=""
global_creds.clear()
global_creds.append(global_creds_set)


def exchange_code(authorization_code):
  """Exchange an authorization code for OAuth 2.0 credentials.

  Args:
    authorization_code: Authorization code to exchange for OAuth 2.0
                        credentials.
  Returns:
    oauth2client.client.OAuth2Credentials instance.
  Raises:
    CodeExchangeException: an error occurred.
  """
  flow=InstalledAppFlow.from_client_secrets_file('credentials.json',SCOPES)
  try:
    credentials = flow.step2_exchange(authorization_code)
    return credentials
  except:
      print("sorry")

def get_user_info(credentials):
  """Send a request to the UserInfo API to retrieve the user's information.

  Args:
    credentials: oauth2client.client.OAuth2Credentials instance to authorize the
                 request.
  Returns:
    User information as a dict.
  """
  user_info_service = build(
      serviceName='oauth2', version='v2',
    #   http=credentials.authorize(httplib2.Http()))
  )
  user_info = None
  try:
    user_info = user_info_service.userinfo().get().execute()
  except:
      print("sorry")

def gmail_auth():
    try:
        client_secrets_file = os.path.join(pathlib.Path(__file__).parent, "credentials.json")
        home_dir=os.path.expanduser('~')
        flow =InstalledAppFlow.from_client_secrets_file(client_secrets_file=client_secrets_file,scopes=SCOPES,
        redirect_uri="http://127.0.0.1:5000/callback")
        authorization_url, state = flow.authorization_url()
        print(authorization_url)
        creds=flow.run_local_server(port=5001)
        pickle_path=os.path.join(home_dir,'gmail.pickle')

        
        # pickled_object=pickle.dump(creds,open('token_gmail_v1.pickle','wb'))
        # print(pickled_object)
        # print(pickle.load(open('test.pickle','rb')))
        
        with open('token_gmail_v1.pickle','wb') as token:
            pickle.dump(creds,token)
            print("pickling done!!")
        with open('token_gmail_v1.pickle','rb') as token:
            obj=pickle.load(token)
            print("unpickling done!!")
            print(obj)
        # global_creds_set=pickle.load(open('token_gmail_v1.pickle','rb'))
        # print(
        #     f"a_dict of unpickled objects:\n{global_creds_set}\n"
        #     )
        # global_creds.clear()
        # global_creds.append(global_creds_set)
        # print(global_creds)
        # print(global_creds_set)
        return authorization_url
    except Exception as ex:
        print(ex)
        return str(ex)

def send_message(email,mailid,cc,bcc,subject,body,file):
    cursor.execute("SELECT * FROM token WHERE useremail = %s", (email,))
    row=cursor.fetchone()
    reto=row[1]
    msg=send_message_with_Attachment(mailid,cc,bcc,subject,body,file)
    try:
#         client_secrets_file = os.path.join(pathlib.Path(__file__).parent, "credentials.json")
#         flow = Flow.from_client_secrets_file(
#         client_secrets_file=client_secrets_file,
#         scopes=["https://www.googleapis.com/auth/userinfo.profile", "https://www.googleapis.com/auth/userinfo.email", "openid"]
#         # redirect_uri="http://127.0.0.1:5000/callback"
# )
#         # try to 
#         authorization_url, state = flow.authorization_url()
#         print(authorization_url)
#         service =Create_Service(CLIENT_SECRET_FILE, API_NAME, API_VERSION, SCOPES)
        # message = service.users().messages().send(userId='me', body={'raw': raw_string}).execute()
        creds = AccessTokenCredentials(reto, 'my-user-agent/1.0')
        service = build('gmail', 'v1', credentials=creds)
        draft = service.users().messages().send(userId="me",body=msg).execute()
        print(draft)
        print("Message sent successfuly!!!!")
    except HttpError as error:
        print(F'An error occurred: {error}')
        draft = None
    return draft
# def convertToBinaryData(filename):
#     # Convert digital data to binary format
#     with open(filename, 'rb') as file:
#         binaryData = file.read()
#     return binaryData
def send_message_with_Attachment(mailid,cc,bcc,subject,body,file):

        message = MIMEMultipart()
        message['to'] = mailid
        message['cc']=cc
        message['bcc']=bcc
        message['subject'] = subject

        msg = MIMEText(body)
        message.attach(msg)
        # buffer = io.BytesIO()     # create file in memory
        # file.save(buffer, 'jpeg') # save in file in memory - it has to be `jpeg`, not `jpg`
        # buffer.seek(0)            # move to the beginning of file

        # file = buffer 
        # file='butterfly.jpg'
        # print((file)
        # print(type(file))
        # file = convertToBinaryData(file)
        file = str(file.filename)
        (content_type, encoding) = mimetypes.guess_type(file)

        if content_type is None or encoding is not None:
            content_type = 'application/octet-stream'

        (main_type, sub_type) = content_type.split('/', 1)
        # print(file)
        if main_type == 'text':
            with open(file, 'rb') as f:
                msg = MIMEText(f.read().decode('utf-8'), _subtype=sub_type)
        elif main_type == 'image':
                f=open(file,'rb')
                msg=MIMEImage(f.read(),_subtype=sub_type)
                f.close()
        elif main_type == 'audio':
            with open(file, 'rb') as f:
                msg = MIMEAudio(f.read(), _subtype=sub_type)
            
        else:
            with open(file, 'rb') as f:
                msg = MIMEBase(main_type, sub_type)
                msg.set_payload(f.read())

        filename = os.path.basename(file)
        msg.add_header('Content-Disposition', 'attachment',
                    filename=filename)
        message.attach(msg)

        raw_message = \
            base64.urlsafe_b64encode(message.as_string().encode('utf-8'))
        return {'raw': raw_message.decode('utf-8')}
    



SCOPES = ['https://www.googleapis.com/auth/gmail.readonly','https://www.googleapis.com/auth/gmail.modify']

# to store all lables in list
def labels():
    client_secrets_file = os.path.join(pathlib.Path(__file__).parent, "credentials.json")
    flow = Flow.from_client_secrets_file(
    client_secrets_file=client_secrets_file,
    scopes=["https://www.googleapis.com/auth/userinfo.profile", "https://www.googleapis.com/auth/userinfo.email", "openid"])
        # redirect_uri="http://127.0.0.1:5000/callback"


    authorization_url, state = flow.authorization_url()
    service =Create_Service(CLIENT_SECRET_FILE, API_NAME, API_VERSION, SCOPES)

    msg_lables=service.users().labels().list(userId='me').execute()  #to get list of all labels
    msg_lable_list=msg_lables['labels']
    all_list=[]
    for mll in msg_lable_list:
        l_name=mll['name']
        all_list.append(l_name)
        # sql = """ INSERT INTO demo (lable_id,lable_name) VALUES (%s,%s)"""
        # sql_where=(l_id,l_name)
        # cursor.execute(sql,sql_where)
        # connection.commit()
    print ("Total labels in inbox: ", str(len(all_list)))
    return all_list


# to get mails to get all the mails of that particular lable
def connections(connection,cursor,lable_id_one,lable_id_two):
    client_secrets_file = os.path.join(pathlib.Path(__file__).parent, "credentials.json")
    flow = Flow.from_client_secrets_file(
    client_secrets_file=client_secrets_file,
    scopes=["https://www.googleapis.com/auth/userinfo.profile", "https://www.googleapis.com/auth/userinfo.email", "openid"])
        # redirect_uri="http://127.0.0.1:5000/callback"

    authorization_url, state = flow.authorization_url()
    service =Create_Service(CLIENT_SECRET_FILE, API_NAME, API_VERSION, SCOPES)
    ans1=[]
    ans1=labels()

    
    ans2=[]
    # 
    # We get a dictonary. Now reading values for the key 'messages'
   
    # to store them in database
    length1=len(ans1)
    j=1
    for j in range(length1):
        i=1
        lable=str(ans1[j])
        # print(lable)
        if(lable!="CHAT" and lable!="TRASH"):
            unread_msgs = service.users().messages().list(userId='me',labelIds=lable,q=None,maxResults=5000).execute()
            # print(unread_msgs)
            mssg_list = unread_msgs["messages"]
            print ("Total ",lable," messages are :", str(len(mssg_list)))
            for mssg in mssg_list:
                m_id = mssg['id'] # get id of individual message
                sql = """ INSERT INTO email1 (sno,message_id,lable) VALUES (%s,%s,%s)"""
                sql_where=(i,m_id,lable)
                i=i+1
                cursor.execute(sql,sql_where)
                connection.commit()
    return "connection done"
# to get 1-10 mails of particular lable and messageId stored in database
def getEmails(lable_id,cursor,n,m,subject,date,sender,body):
    client_secrets_file = os.path.join(pathlib.Path(__file__).parent, "credentials.json")
    flow = Flow.from_client_secrets_file(
    client_secrets_file=client_secrets_file,
    scopes=["https://www.googleapis.com/auth/userinfo.profile", "https://www.googleapis.com/auth/userinfo.email", "openid"])
        # redirect_uri="http://127.0.0.1:5000/callback"

    authorization_url, state = flow.authorization_url()
    service =Create_Service(CLIENT_SECRET_FILE, API_NAME, API_VERSION, SCOPES)

    final_list = [ ]
    dict={}
    def function(para):
        if para=="Subject" or para=="Date" or para=="Sender" or para=="Body":
            return True
        else:
            return False

    for i in range(n,m):
        temp_dict = { }
        sql = "SELECT * FROM email1 WHERE sno=%s and lable=%s"
        sql_where=(i,lable_id)
        cursor.execute(sql,sql_where)
        row=cursor.fetchone()
        msg_id=row[1]
        lable_id=row[2]
        message = service.users().messages().get(userId='me',id=msg_id).execute() # fetch the message using API
        payld = message['payload'] # get payload of the message 
        headr = payld['headers'] # get header of the payload

        if function(subject):
            for one in headr: # getting the Subject
                # print('subject diya he!!!!')
                if one['name'] == 'Subject':
                    msg_subject = one['value']
                    temp_dict['Subject'] = msg_subject
                else:
                    pass
        else:
            pass
        if function(date):
            for two in headr: # getting the date
                if two['name'] == 'Date':
                    msg_date = two['value']
                    # date_parse = (msg_date)
                    # m_date = (date_parse.date())
                    temp_dict['Date'] = str(msg_date)
                else:
                    pass
        else:
            pass

        if function(sender):
            for three in headr: # getting the Sender   
                if three['name'] == 'From':
                    msg_from = three['value']
                    temp_dict['Sender'] = msg_from
                else:
                    pass
        else:
            pass
        temp_dict['Snippet'] = message['snippet'] # fetching message snippet
        if function(body):
            try:
                # Fetching message body
                mssg_parts = payld['parts'] # fetching the message parts
                part_one  = mssg_parts[0] # fetching first element of the part 
                part_body = part_one['body'] # fetching body of the message
                part_data = part_body['data'] # fetching data from the body
                clean_one = part_data.replace("-","+") # decoding from Base64 to UTF-8
                clean_one = clean_one.replace("_","/") # decoding from Base64 to UTF-8
                clean_two = base64.b64decode (bytes(clean_one, 'UTF-8')) # decoding from Base64 to UTF-8
                soup = BeautifulSoup(clean_two , "lxml" )
                mssg_body = soup.body()
                # mssg_body is a readible form of message body
                # depending on the end user's requirements, it can be further cleaned 
                # using regex, beautiful soup, or any other method
                temp_dict['Message_body'] = mssg_body
            except :
                pass
        else:
            pass

        print (temp_dict)
        dict[i]=temp_dict
        final_list.append(temp_dict) # This will create a dictonary item in the final list
        
        # This will mark the messagea as read
        service.users().messages().modify(userId='me', id=msg_id,body={ 'removeLabelIds': ['UNREAD']}).execute() 
    print ("Total messaged retrived: ", str(len(final_list)))
    return dict

def getProfile():
    client_secrets_file = os.path.join(pathlib.Path(__file__).parent, "credentials.json")
    flow = Flow.from_client_secrets_file(
    client_secrets_file=client_secrets_file,
    scopes=["https://www.googleapis.com/auth/userinfo.profile", "https://www.googleapis.com/auth/userinfo.email", "openid"])
        # redirect_uri="http://127.0.0.1:5000/callback"


    authorization_url, state = flow.authorization_url()
    service =Create_Service(CLIENT_SECRET_FILE, API_NAME, API_VERSION, SCOPES)
    dict=service.users().getProfile(userId='me').execute()
    # to get particular value from dictionary object like dict['emailAddress']
    result={
        "ThreadTotal":dict['threadsTotal'], 
        "emailAddress":dict['emailAddress'],
        "historyId":dict['historyId'],
        "messageTotal":dict['messagesTotal'],
    }
    return result
    
def getThread():
    client_secrets_file = os.path.join(pathlib.Path(__file__).parent, "credentials.json")
    flow = Flow.from_client_secrets_file(
    client_secrets_file=client_secrets_file,
    scopes=["https://www.googleapis.com/auth/userinfo.profile", "https://www.googleapis.com/auth/userinfo.email", "openid"])
        # redirect_uri="http://127.0.0.1:5000/callback"


    authorization_url, state = flow.authorization_url()
    service =Create_Service(CLIENT_SECRET_FILE, API_NAME, API_VERSION, SCOPES)
    
    threads = service.users().threads().list(userId='me').execute().get('threads', [])
    for thread in threads:
        tdata = service.users().threads().get(userId='me', id=thread['id']).execute()
        nmsgs = len(tdata['messages'])

        # skip if <3 msgs in thread
        if nmsgs >= 1:
            # message = (service.users().messages().trash(userId='me', id=thread['id']).execute())
            # print('Message Id: %s sent to Trash.' % message['id']) to sent a particular mesage to trash..
            # message = (service.users().messages().untrash(userId='me', id=thread['id']).execute()) to untrash.
            msg = tdata['messages'][0]['payload']
            subject = ''
            for header in msg['headers']:
                if header['name'] == 'Subject':
                    subject = header['value']
                    break
            if subject:  # skip if no Subject line
                print(F'- {subject}, {nmsgs}')
        else:
            print("no such mails")
    return threads

def createLable(Lablename):
    client_secrets_file = os.path.join(pathlib.Path(__file__).parent, "credentials.json")
    flow = Flow.from_client_secrets_file(
    client_secrets_file=client_secrets_file,
    scopes=["https://www.googleapis.com/auth/userinfo.profile", "https://www.googleapis.com/auth/userinfo.email", "openid"])
        # redirect_uri="http://127.0.0.1:5000/callback"
    authorization_url, state = flow.authorization_url()
    label_body = {
    "name": Lablename,
    }
    service =Create_Service(CLIENT_SECRET_FILE, API_NAME, API_VERSION, SCOPES)
    service.users().labels().create(userId='me',body=label_body).execute()
    result="lable created"
    return result

def listLableId():
    client_secrets_file = os.path.join(pathlib.Path(__file__).parent, "credentials.json")
    flow = Flow.from_client_secrets_file(
    client_secrets_file=client_secrets_file,
    scopes=["https://www.googleapis.com/auth/userinfo.profile", "https://www.googleapis.com/auth/userinfo.email", "openid"])
        # redirect_uri="http://127.0.0.1:5000/callback"
    authorization_url, state = flow.authorization_url()
    
    service =Create_Service(CLIENT_SECRET_FILE, API_NAME, API_VERSION, SCOPES)
    msg_lables=service.users().labels().list(userId='me').execute()  #to get list of all labels
    msg_lable_list=msg_lables['labels']
    dict={}
    for mll in msg_lable_list:
        l_id=mll['id']
        l_name=mll['name']
        dict[l_id]=l_name
    print ("Total labels in inbox: ", str(len(dict)))
    return dict
    
def deleteLable(Lablename):
    client_secrets_file = os.path.join(pathlib.Path(__file__).parent, "credentials.json")
    flow = Flow.from_client_secrets_file(
    client_secrets_file=client_secrets_file,
    scopes=["https://www.googleapis.com/auth/userinfo.profile", "https://www.googleapis.com/auth/userinfo.email", "openid"])
        # redirect_uri="http://127.0.0.1:5000/callback"
    authorization_url, state = flow.authorization_url()
    
    service =Create_Service(CLIENT_SECRET_FILE, API_NAME, API_VERSION, SCOPES)
    service.users().labels().delete(userId='me',id=Lablename).execute()
    result="lable deleted"
    return result

def getMessageIdsOfThatLable(lableName):
    client_secrets_file = os.path.join(pathlib.Path(__file__).parent, "credentials.json")
    flow = Flow.from_client_secrets_file(
    client_secrets_file=client_secrets_file,
    scopes=["https://www.googleapis.com/auth/userinfo.profile", "https://www.googleapis.com/auth/userinfo.email", "openid"])
        # redirect_uri="http://127.0.0.1:5000/callback"
    authorization_url, state = flow.authorization_url()
    
    service =Create_Service(CLIENT_SECRET_FILE, API_NAME, API_VERSION, SCOPES)
    
    unread_msgs=service.users().messages().list(userId='me',labelIds=lableName,q=None,maxResults=5000).execute()
    dict={}
    mssg_list = unread_msgs["messages"]
    print ("Total ",lableName," messages are :", str(len(mssg_list)))
    for mssg in mssg_list:
        m_id = mssg['id'] # get id of individual message
        msgs=service.users().messages().get(userId='me',id=m_id).execute()
        temp={}
        message=msgs['payload']
        temp["message"]=message
        dict[m_id]=temp
    return dict

def modifyLable(preLable,newLable,m_id):
    client_secrets_file = os.path.join(pathlib.Path(__file__).parent, "credentials.json")
    flow = Flow.from_client_secrets_file(
    client_secrets_file=client_secrets_file,
    scopes=["https://www.googleapis.com/auth/userinfo.profile", "https://www.googleapis.com/auth/userinfo.email", "openid"])
        # redirect_uri="http://127.0.0.1:5000/callback"
    authorization_url, state = flow.authorization_url()
    
    service =Create_Service(CLIENT_SECRET_FILE, API_NAME, API_VERSION, SCOPES)
    label_body = {
                "removeLabelIds":[preLable],
                "addLabelIds": [newLable]
                }
    try:
        service.users().messages().modify(userId='me', id=m_id, body=label_body ).execute()
        result="Lable changed successfuly!!"
    except:
        result="errro came!!"
    return result

def create_draft_message(mailid,cc,bcc,subject,body,file):
    message = MIMEMultipart()
    message['To'] = mailid
    message['Cc'] = cc
    message['Bcc']=bcc
    message['Subject'] = subject
    msg = MIMEText(body)
    message.attach(msg)
    
    file = str(file.filename)
    (content_type, encoding) = mimetypes.guess_type(file)

    if content_type is None or encoding is not None:
        content_type = 'application/octet-stream'

    (main_type, sub_type) = content_type.split('/', 1)
    # print(file)
    if main_type == 'text':
        with open(file, 'rb') as f:
            msg = MIMEText(f.read().decode('utf-8'), _subtype=sub_type)
    elif main_type == 'image':
            f=open(file,'rb')
            msg=MIMEImage(f.read(),_subtype=sub_type)
            f.close()
    elif main_type == 'audio':
        with open(file, 'rb') as f:
            msg = MIMEAudio(f.read(), _subtype=sub_type)
        
    else:
        with open(file, 'rb') as f:
            msg = MIMEBase(main_type, sub_type)
            msg.set_payload(f.read())

    filename = os.path.basename(file)
    msg.add_header('Content-Disposition', 'attachment',
                filename=filename)
    message.attach(msg)


    # encoded message
    encoded_message = base64.urlsafe_b64encode(message.as_bytes()).decode()

    create_message = {
        'message': {
            'raw': encoded_message
        }
    }
    try:
        client_secrets_file = os.path.join(pathlib.Path(__file__).parent, "credentials.json")
        flow = Flow.from_client_secrets_file(
        client_secrets_file=client_secrets_file,
        scopes=["https://www.googleapis.com/auth/userinfo.profile", "https://www.googleapis.com/auth/userinfo.email", "openid"]
        # redirect_uri="http://127.0.0.1:5000/callback"
)
        authorization_url, state = flow.authorization_url()
        service =Create_Service(CLIENT_SECRET_FILE, API_NAME, API_VERSION, SCOPES)

        # message = service.users().messages().send(userId='me', body={'raw': raw_string}).execute()
        draft = service.users().drafts().create(userId="me",body=create_message).execute()
        # draft = service.users().drafts().create(userId="me",
        #                                         body=create_message).execute()

        print(draft)
        print("Draft Message created successfuly!!!!")
    except HttpError as error:
        print("message nahi created hua!!!!!!!!!!!!!!!!!")
        print(F'An error occurred: {error}')
        draft = None
    return draft

def getDraftsList():
    client_secrets_file = os.path.join(pathlib.Path(__file__).parent, "credentials.json")
    flow = Flow.from_client_secrets_file(
    client_secrets_file=client_secrets_file,
    scopes=["https://www.googleapis.com/auth/userinfo.profile", "https://www.googleapis.com/auth/userinfo.email", "openid"])
        # redirect_uri="http://127.0.0.1:5000/callback"
    authorization_url, state = flow.authorization_url()
    
    service =Create_Service(CLIENT_SECRET_FILE, API_NAME, API_VERSION, SCOPES)
    unread_msgs=service.users().drafts().list(userId='me').execute()
    mssg_list = unread_msgs["drafts"]
    print ("Total draft messages are :", str(len(mssg_list)))
    dict={}
    i=1
    for mssg in mssg_list:
        m_id = mssg['id'] # get id of individual message
        dict[i]=m_id
        i=i+1
    return dict

def getDrafts():
    client_secrets_file = os.path.join(pathlib.Path(__file__).parent, "credentials.json")
    flow = Flow.from_client_secrets_file(
    client_secrets_file=client_secrets_file,
    scopes=["https://www.googleapis.com/auth/userinfo.profile", "https://www.googleapis.com/auth/userinfo.email", "openid"])
        # redirect_uri="http://127.0.0.1:5000/callback"
    authorization_url, state = flow.authorization_url()
    
    service =Create_Service(CLIENT_SECRET_FILE, API_NAME, API_VERSION, SCOPES)
    unread_msgs=service.users().drafts().list(userId='me').execute()
    mssg_list = unread_msgs["drafts"]
    print ("Total draft messages are :", str(len(mssg_list)))
    dict={}
    for mssg in mssg_list:
        m_id = mssg['id'] # get id of individual message
        msgs=service.users().drafts().get(userId='me',id=m_id).execute()
        temp={}
        message=msgs['message']
        temp["message"]=message
        dict[m_id]=temp
    return dict

def deleteDrafts(draftId):
    client_secrets_file = os.path.join(pathlib.Path(__file__).parent, "credentials.json")
    flow = Flow.from_client_secrets_file(
    client_secrets_file=client_secrets_file,
    scopes=["https://www.googleapis.com/auth/userinfo.profile", "https://www.googleapis.com/auth/userinfo.email", "openid"])
        # redirect_uri="http://127.0.0.1:5000/callback"
    authorization_url, state = flow.authorization_url()
    
    service =Create_Service(CLIENT_SECRET_FILE, API_NAME, API_VERSION, SCOPES)
    msgs=service.users().drafts().delete(userId='me',id=draftId).execute()
    result={
        "draftid":draftId,
        "message":"deleted successufuly!!"
    }
    return result

def sendDrafts(DraftId):
    client_secrets_file = os.path.join(pathlib.Path(__file__).parent, "credentials.json")
    flow = Flow.from_client_secrets_file(
    client_secrets_file=client_secrets_file,
    scopes=["https://www.googleapis.com/auth/userinfo.profile", "https://www.googleapis.com/auth/userinfo.email", "openid"])
        # redirect_uri="http://127.0.0.1:5000/callback"
    authorization_url, state = flow.authorization_url()
    
    service =Create_Service(CLIENT_SECRET_FILE, API_NAME, API_VERSION, SCOPES)
    # draft = service.users().drafts().send(userId="me",body={ 'id': DraftId }).execute()
    draft=service.users().drafts().send(userId='me', body={ 'id': DraftId }).execute()
    result="sent"
    return draft['id']

def updateLanguage():
    client_secrets_file = os.path.join(pathlib.Path(__file__).parent, "credentials.json")
    flow = Flow.from_client_secrets_file(
    client_secrets_file=client_secrets_file,
    scopes=["https://www.googleapis.com/auth/userinfo.profile", "https://www.googleapis.com/auth/userinfo.email", "openid"])
        # redirect_uri="http://127.0.0.1:5000/callback"
    authorization_url, state = flow.authorization_url()
    
    service =Create_Service(CLIENT_SECRET_FILE, API_NAME, API_VERSION, SCOPES)
    language=service.users().settings().updateLanguage(userId='me',body=None).execute()
    
def getLanguage():
    client_secrets_file = os.path.join(pathlib.Path(__file__).parent, "credentials.json")
    flow = Flow.from_client_secrets_file(
    client_secrets_file=client_secrets_file,
    scopes=["https://www.googleapis.com/auth/userinfo.profile", "https://www.googleapis.com/auth/userinfo.email", "openid"])
        # redirect_uri="http://127.0.0.1:5000/callback"
    authorization_url, state = flow.authorization_url()
    
    service =Create_Service(CLIENT_SECRET_FILE, API_NAME, API_VERSION, SCOPES)
    language=service.users().settings().getLanguage(userId='me').execute()
    return language['displayLanguage']

def updatePop(access,diss):
    # client_secrets_file = os.path.join(pathlib.Path(__file__).parent, "credentials.json")
    # flow = Flow.from_client_secrets_file(
    # client_secrets_file=client_secrets_file,
    # scopes=["https://www.googleapis.com/auth/userinfo.profile", "https://www.googleapis.com/auth/userinfo.email", "openid"])
    #     # redirect_uri="http://127.0.0.1:5000/callback"
    # authorization_url, state = flow.authorization_url()
    
    # service =Create_Service(CLIENT_SECRET_FILE, API_NAME, API_VERSION, SCOPES)
    # pop=service.users().settings().updatePop(userId='me',body={ 'accessWindow': access,'disposition': diss}).execute()
    # return "hello"
    client_secrets_file = os.path.join(pathlib.Path(__file__).parent, "credentials.json")
    flow = Flow.from_client_secrets_file(
    client_secrets_file=client_secrets_file,
    scopes=["https://www.googleapis.com/auth/userinfo.profile", "https://www.googleapis.com/auth/userinfo.email", "openid"])
        # redirect_uri="http://127.0.0.1:5000/callback"
    authorization_url, state = flow.authorization_url()
    
    service =Create_Service(CLIENT_SECRET_FILE, API_NAME, API_VERSION, SCOPES)
    pop=service.users().settings().updatePop(userId='me',body=None).execute()
    return pop['disposition']



def getPop():
    client_secrets_file = os.path.join(pathlib.Path(__file__).parent, "credentials.json")
    flow = Flow.from_client_secrets_file(
    client_secrets_file=client_secrets_file,
    scopes=["https://www.googleapis.com/auth/userinfo.profile", "https://www.googleapis.com/auth/userinfo.email", "openid"])
        # redirect_uri="http://127.0.0.1:5000/callback"
    authorization_url, state = flow.authorization_url()
    
    service =Create_Service(CLIENT_SECRET_FILE, API_NAME, API_VERSION, SCOPES)
    pop=service.users().settings().getPop(userId='me').execute()
    return pop['disposition']

def updateImap():
    client_secrets_file = os.path.join(pathlib.Path(__file__).parent, "credentials.json")
    flow = Flow.from_client_secrets_file(
    client_secrets_file=client_secrets_file,
    scopes=["https://www.googleapis.com/auth/userinfo.profile", "https://www.googleapis.com/auth/userinfo.email", "openid"])
        # redirect_uri="http://127.0.0.1:5000/callback"
    authorization_url, state = flow.authorization_url()
    dict={}
    service =Create_Service(CLIENT_SECRET_FILE, API_NAME, API_VERSION, SCOPES)
    imap=service.users().settings().updateImap(userId='me',body=None).execute()
    # dict['enabled']=imap['enabled']
    # dict['expungeBehavior']=imap['expungeBehavior']
    # dict['enabled']=imap['enabled']
    # dict['maxFolderSize']=imap['maxFolderSize']
    print("hello")
    return dict
 
def getImap():
    client_secrets_file = os.path.join(pathlib.Path(__file__).parent, "credentials.json")
    flow = Flow.from_client_secrets_file(
    client_secrets_file=client_secrets_file,
    scopes=["https://www.googleapis.com/auth/userinfo.profile", "https://www.googleapis.com/auth/userinfo.email", "openid"])
        # redirect_uri="http://127.0.0.1:5000/callback"
    authorization_url, state = flow.authorization_url()
    dict={}
    service =Create_Service(CLIENT_SECRET_FILE, API_NAME, API_VERSION, SCOPES)
    imap=service.users().settings().getImap(userId='me').execute()
    dict['enabled']=imap['enabled']
    dict['expungeBehavior']=imap['expungeBehavior']
    dict['enabled']=imap['enabled']
    dict['maxFolderSize']=imap['maxFolderSize']
    return dict

def createSendAs():
    client_secrets_file = os.path.join(pathlib.Path(__file__).parent, "credentials.json")
    flow = Flow.from_client_secrets_file(
    client_secrets_file=client_secrets_file,
    scopes=["https://www.googleapis.com/auth/userinfo.profile", "https://www.googleapis.com/auth/userinfo.email","https://www.googleapis.com/auth/gmail.settings.sharing","openid"])
        # redirect_uri="http://127.0.0.1:5000/callback"
    authorization_url, state = flow.authorization_url()
    service =Create_Service(CLIENT_SECRET_FILE, API_NAME, API_VERSION, SCOPES)
    
    create_body={
  "displayName": "hagnosoftSoftwareDeveloper",
  "isDefault": "true",
  "isPrimary": "true",
  "replyToAddress": "alpeshpatilalpesh91",
  "sendAsEmail": "alpesh.patil@creysto.com",
  "signature": "https://www.any-api.com/googleapis_com/gmail/docs/users/gmail_users_settings_sendAs_create",
  "smtpMsa": {
    "host": "mail.smtpeter.com",
    "password": "alpesh18.,AE",
    "port": 0,
    "securityMode": "none",
    "username": "alpesh patil alpesh"
  },
  "treatAsAlias": "true",
  "verificationStatus": "accepted"
}
    
    create_send=service.users().settings().sendAs().create(userId='me',body=create_body).execute()
    return "Created"
    
  