#this script extracts metadata(creator,title,last time modified etc.) from 
#xlsx files.Takes a single file as input.Saves results into 
#<filename>_metadata.csv 


import zipfile
import sys
from bs4 import BeautifulSoup
import shutil
import csv
import os

def xlsx_metadata_parser_func():
    if len(sys.argv)>=3 or len(sys.argv)==1:
        print(f"Usage: python3 {sys.argv[0]} <filename>")
        sys.exit(1)
    else:
        #check if file exists
        if os.path.exists(sys.argv[1]) and sys.argv[1].endswith('.xlsx'):
            
            directory = os.path.join(os.getcwd(),'temp')
            xlsx_file = sys.argv[1]
            zip_file = xlsx_file.replace('xlsx','zip')
            zip_file_path = os.path.join(os.getcwd(),directory,zip_file)
            csv_file = xlsx_file.replace('xlsx','csv')

            #first we need to convert the xls file into zip
            

            try:
                os.mkdir(directory)
            except Exception as e:
                print(f"[-]An error occured: {e}")
                sys.exit(1)

            shutil.copy2(xlsx_file,zip_file_path)

            #extract the zip file
            with zipfile.ZipFile(zip_file_path,'r') as f:
                f.extractall(directory)

            #metadata info stored in docProps/app.xml and
            # docProps/core.xml
            
            with open(os.path.join(directory,"docProps","app.xml")) as f:
                content = f.read()
                soup = BeautifulSoup(content,"xml")
                Application = soup.find("Application").string
                AppVersion = soup.find("AppVersion").string
                
                print(f"Application: {Application}")
                print(f"AppVersion: {AppVersion}")

            with open(os.path.join(directory,"docProps","core.xml")) as f:
                content = f.read()
                soup = BeautifulSoup(content,'xml')
                try:
                    Creator = soup.find("creator").string
                except:
                    Creator = ''
                try:
                    Title = soup.find("title").string
                except:
                    Title = ''
                try:
                    Subject = soup.find("subject").string
                except:
                    Subject = ''
                try:
                    Description = soup.find('description').string
                except:
                    Description = ''
                LastModified = soup.find('modified').string

            print(f"Creator: {Creator}")
            print(f"Title: {Title}")
            print(f"Subject: {Subject}")
            print(f"Description: {Description}")
            print(f"LastModified: {LastModified}")

            #save results in csv file
            with open(csv_file, mode='w') as f:
                csv_writer = csv.writer(f,delimiter=',')
                csv_writer.writerow(["Application","AppVersion","Creator","Title","Subject","Description","LastModified"])
                csv_writer.writerow([Application,AppVersion,Creator,Title,Subject,Description,LastModified])

            #remove temp directory after finished
            shutil.rmtree(directory)
        else:
            print("[-]File not found")
            sys.exit(1)


xlsx_metadata_parser_func()
