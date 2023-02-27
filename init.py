import requests
from gmailapis import gmail_auth,send_message,getEmails
import os.path
# python -m virtualenv myvirtualenv
import os
import webbrowser
import psycopg2
import gmailapis
# import apiclientz
from apiclient import discovery
import flask_mail
import pathlib
from flask import Flask,jsonify,render_template, session, abort, redirect, request
from google.oauth2 import id_token
from google_auth_oauthlib.flow import Flow
from Google import Create_Service
import base64
import json
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from flask_mail import Mail
from flask_cors import CORS,cross_origin
from flask import Flask, jsonify, request, session

from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from google_auth_oauthlib.flow import Flow

app = Flask(__name__)
CORS(app,supports_credentials=True)
app.secret_key='alpeshpatil'
app.config['Mail_server']='smtp.gmail.com'
app.config['MAIL_PORT']=465
app.config['MAIL_USERNAME']='alpeshpatilalpesh@gmail.com'
app.config['MAIL_PASSWORD']='12345678'
app.config['MAIL_USE_TSL']=False
app.config['MAIL_USE_SSL']=True
mail=Mail(app)
app.config['SECRET_KEY']='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'
app.config['SESSION_PERMANENT']=False
app.config['SESSION_TYPE']="filesystem"

connection = psycopg2.connect(user="postgres",password="root",host="localhost",port="5433",database="postgres")
cursor = connection.cursor()


# api_endpoint_entry="/api/staging"
SCOPES = ['https://mail.google.com/',
          'https://www.googleapis.com/auth/gmail.send',
          'https://www.googleapis.com/auth/gmail.modify',
          "https://www.googleapis.com/auth/gmail.addons.current.action.compose",
          "https://www.googleapis.com/auth/gmail.addons.current.message.action",
          "https://www.googleapis.com/auth/gmail.addons.current.message.metadata",
          "https://www.googleapis.com/auth/gmail.addons.current.message.readonly",
          "https://www.googleapis.com/auth/gmail.compose",
          "https://www.googleapis.com/auth/gmail.insert",
          "https://www.googleapis.com/auth/gmail.labels",
          "https://www.googleapis.com/auth/gmail.metadata",
          "https://www.googleapis.com/auth/gmail.readonly",
          "https://www.googleapis.com/auth/gmail.send",
          "https://www.googleapis.com/auth/gmail.settings.basic",
          "https://www.googleapis.com/auth/gmail.settings.sharing"
          ]
flow = InstalledAppFlow.from_client_secrets_file('credentials.json', SCOPES,redirect_uri='http://localhost:5000/oauth2callback')

@app.route('/gmailoauth',methods=['GET'])
def code():
    # auth_url, _ = flow.authorization_url(prompt='consent')
    auth_uri,state=flow.authorization_url()
    print(auth_uri)
    webbrowser.open_new(auth_uri)
    return "Done!"
    
@app.route('/oauth2callback',methods=['GET'])
def gmail_auth():
    try:
        flow.fetch_token(authorization_response=request.url)
        print("excess token")
        excessToken=flow.credentials.token
        print("refresh token")
        refreshToken=flow.credentials.refresh_token
        print("expiry time")
        expirationTime=flow.credentials.expiry
        
        # using gmial api feature using access token
        
        credentials = flow.credentials
        service = build('gmail', 'v1', credentials=credentials)
        dict=service.users().getProfile(userId='me').execute()
        # to get particular value from dictionary object like dict['emailAddress']
        emailAddress=dict['emailAddress']
        
        # result=cursor.execute("SELECT exists (select * FROM token WHERE useremail ='"+emailAddress+"')")
        # other way to check whether data exist or not..
        
        cursor.execute("SELECT * FROM token WHERE useremail = %s", (emailAddress,))
        # sql = """SELECT * FROM token WHERE useremail=%s"""
        # sql_where=(emailAddress)
        # cursor.execute(sql,sql_where)
        row=cursor.fetchone()
        if row is not None and row[0] is not None:
            # Accessing the first element of the row
            ans = row[0]
            sql_update_query = """Update token set accesstoken = %s, refreshtoken=%s,time=%s where useremail = %s"""
            cursor.execute(sql_update_query,(excessToken,refreshToken,expirationTime,ans))
            connection.commit()
            count = cursor.rowcount
            print(count, "Record Updated successfully ")
            
        else:
            sql = """ INSERT INTO token (useremail,accesstoken,refreshtoken,time) VALUES (%s,%s,%s,%s)"""
            sql_where=(emailAddress,excessToken,refreshToken,expirationTime)
            cursor.execute(sql,sql_where)
            connection.commit()
        
        # connection = psycopg2.connect(user="postgres",password="root",host="localhost",port="5433",database="postgres")
        # cursor = connection.cursor()
        # sql = """ INSERT INTO token (userEmail,accesstoken,refreshtoken,time) VALUES (%s,%s,%s,%s)"""
        # sql_where=(emailAddress,excessToken,refreshToken,expirationTime)
        # cursor.execute(sql,sql_where)
        # connection.commit()
        
        return 'Authentication done successfuly!!'
    except Exception as ex:
        return str(ex)
# @app.route('/gmailoauth',methods=['POST'])
# def gmailoauth():
#     result=gmailapis.gmail_auth()
#     return jsonify(result)

@app.route('/getAccessToken',methods=['GET',"POST"])
def getAccessToken():
    _req=request.form
    email=_req['email']
    print("email is ",email)
    cursor.execute("SELECT * FROM token WHERE useremail = %s", (email,))
    row=cursor.fetchone()
    reto=row[2]
    print(email)
    print("refresh token is",reto)
    params = {
    "grant_type": "refresh_token",
    "client_id":"1018064724252-pg3ki9d8kss0o9m2ahn0js9fin9apssh.apps.googleusercontent.com" ,
    "client_secret": "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",
    "refresh_token": reto
    }

    authorization_url = "https://oauth2.googleapis.com/token"

    response = requests.post(authorization_url, data=params)

    if response.status_code == requests.codes.ok:
    # Extract the access token from the response
        token_data = response.json()
        access_token = token_data['access_token']
        return (f'Access token: {access_token}')
    else:
        # Print the error message returned by the OAuth 2.0 token endpoint
        error_data = response.json()
        return (f'Error getting access token: {error_data["error_description"]}')
    


    # REFRESH_TOKEN=cursor.execute("SELECT refreshtoken FROM token WHERE useremail = %s", (emailAddress,))

# @app.route('/getAccessToken',methods=['POST'])
# def getAccessToken():
#     flow.fetch_token(authorization_response=request.url)
#     refreshToken=flow.credentials.refresh_token
#     credentials = flow.credentials
#     service = build('gmail', 'v1', credentials=credentials)
#     dict=service.users().getProfile(userId='me').execute()
#     # to get particular value from dictionary object like dict['emailAddress']
#     emailAddress=dict['emailAddress']
#     CLIENT_ID = '1018064724252-pg3ki9d8kss0o9m2ahn0js9fin9apssh.apps.googleusercontent.com'
#     CLIENT_SECRET = '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'
    
#     # sql = "SELECT * FROM token WHERE useremail=%s"
#     print("yaha tak chala!!!")
#     REFRESH_TOKEN=cursor.execute("SELECT refreshtoken FROM token WHERE useremail = %s", (emailAddress,))

#     # creds = Credentials.from_authorized_user_info(info=None, client_id=CLIENT_ID, client_secret=CLIENT_SECRET)
#     # print("djfkjdkfjkdj!!!!!!!!!!!!!!!!!1")
#     # creds.refresh(Request())

#     # print(creds.to_json()) # This will print out the access token and other relevant details.

#     # params = {
#     # "grant_type": "refresh_token",
#     # "client_id": CLIENT_ID,
#     # "client_secret": CLIENT_SECRET,
#     # "refresh_token": REFRESH_TOKEN
#     # }

#     # authorization_url = "https://oauth2.googleapis.com/token"

#     # r = requests.post(authorization_url, data=params)

#     # if r.ok:
#     #     return r.json()['access_token']
#     # else:
#     #     return None
#     return ("jay hindh!!")

@app.route('/send_message',methods=['GET',"POST"])
def send_message():
    _json=request.form
    mailid=_json['mailid']
    cc=_json['cc']
    bcc=_json['bcc']
    subject=_json['sub']
    body=_json['body']
    file=request.files['fileName']
    email=_json['email']
    result=gmailapis.send_message(email,mailid,cc,bcc,subject,body,file)
    return result

# @app.route('/get_labels',methods=['Get',"POST"])
# def get_labels():
#     connection = psycopg2.connect(user="postgres",password="root",host="localhost",port="5433",database="postgres")
#     cursor = connection.cursor()
#     result=gmailapis.labels(connection,cursor)
#     return result

@app.route('/get_connected',methods=['Get',"POST"])
def get_connected():
    connection = psycopg2.connect(user="postgres",password="root",host="localhost",port="5433",database="postgres")
    cursor = connection.cursor()
    _json=request.form
    lable_id_one=_json['first_lable']
    lable_id_two=_json['second_lable']
    result=gmailapis.connections(connection,cursor,lable_id_one,lable_id_two)
    return result

    
@app.route('/get_message',methods=["POST"])
def get_message():
    connection = psycopg2.connect(user="postgres",password="root",host="localhost",port="5433",database="postgres")
    cursor = connection.cursor()
    _json=request.json
    n=_json['start']
    m=_json['end']
    lable_id=_json['lable_id']
    subject=_json['subject']
    date=_json['date']
    sender=_json['sender']
    body=_json['body']
    
    result=gmailapis.getEmails(lable_id,cursor,n,m,subject,date,sender,body)
    return result

@app.route('/get_profile',methods=["POST"])
def get_profile():
    # result={}
    result=gmailapis.getProfile()
    return (result)

@app.route('/get_thread',methods=["POST"])
def get_thread():
    # result={}
    result=gmailapis.getThread()
    return (result)

@app.route('/create_lable',methods=["POST"])
def create_lable():
    _json=request.form
    lableName=_json['name']
    result=gmailapis.createLable(lableName)
    return (result)

@app.route('/list_lables',methods=["POST"])
def list_lables():
    result=gmailapis.listLableId()
    return (result)

@app.route('/delete_lable',methods=["POST"])
def delete_lable():
    _json=request.form
    lableName=_json['name']
    result=gmailapis.deleteLable(lableName)
    return (result)

@app.route('/get_message_ids_of_lable',methods=["POST"])
def get_message_ids_of_lable():
    _json=request.form
    preLable=_json['lableName']
    result=gmailapis.getMessageIdsOfThatLable(preLable)
    return (result)

@app.route('/modify_lable',methods=["POST"])
def modify_lable():
    _json=request.form
    preLable=_json['preLable']
    newLable=_json['newLable']
    mId=_json['m_id']
    result=gmailapis.modifyLable(preLable,newLable,mId)
    return (result)

@app.route('/create_draft_message',methods=['GET',"POST"])
def create_draft_message():
    _json=request.form
    mailid=_json['mailid']
    cc=_json['cc']
    bcc=_json['bcc']
    subject=_json['sub']
    body=_json['body']
    file=request.files['fileName']
    result=gmailapis.create_draft_message(mailid,cc,bcc,subject,body,file)
    return result

@app.route('/get_drafts_list',methods=["POST"])
def get_drafts_list():
    # result={}
    result=gmailapis.getDraftsList()
    return (result)

@app.route('/get_drafts',methods=["POST"])
def get_drafts():
    # result={}
    result=gmailapis.getDrafts()
    return (result)

@app.route('/delete_drafts',methods=["POST"])
def delete_drafts():
    _json=request.form
    draftId=_json['draft_id']
    result=gmailapis.deleteDrafts(draftId)
    return (result)

@app.route('/send_drafts',methods=["POST"])
def send_drafts():
    _json=request.form
    draftId=_json['draft_id']
    result=gmailapis.sendDrafts(draftId)
    return (result)

@app.route('/update_language',methods=["POST"])
def update_language():
    result=gmailapis.updateLanguage()
    return (result)

@app.route('/get_language',methods=["POST"])
def get_language():
    result=gmailapis.getLanguage()
    return (result)

@app.route('/update_pop',methods=["POST"])
def update_pop():
    _json=request.form
    access=_json['accesswindow']
    disposition=_json['disposition']
    result=gmailapis.updatePop(access,disposition)
    return (result)

@app.route('/get_pop',methods=["POST"])
def get_pop():
    result=gmailapis.getPop()
    return (result)

@app.route('/update_imap',methods=["POST"])
def update_imap():
    result=gmailapis.updateImap()
    return (result)

@app.route('/get_imap',methods=["POST"])
def get_imap():
    result=gmailapis.getImap()
    return (result)

@app.route('/create_sendAs',methods=["POST"])
def create_sendAs():
    # _json=request.json
    # displayName=_json['displayName']
    # isDefault=_json['isDefault']
    # isPrimary=_json['isPrimary']
    # replyToAddress=_json['replyToAddress']
    # sendAsEmail=_json['sendAsEmail']
    # signature=_json['signature']
    # host=_json['host']
    # password=_json['password']
    # port=_json['port']
    # securityMode=_json['securityMode']
    # username=_json['username']
    # treatAsAlias=_json['treatAsAlias']
    # verificationStatus=_json['verificationStatus']
    # result=gmailapis.createSendAs(sendAsEmail,displayName,replyToAddress,signature,isPrimary,isDefault,treatAsAlias,host,port,username,password,securityMode,verificationStatus)
    result=gmailapis.createSendAs()
    return (result)



if __name__ == '__main__':
    app.run(debug=True)

# read/unread/,filter-subject,body,attachment cahiye..