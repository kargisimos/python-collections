#this script sets up a temporary HTTP server
#for quick data exfiltration.
#Taken from: https://medium.com/maverislabs/bash-tricks-for-file-exfiltration-over-http-s-using-flask-112aed524ad

import os
import datetime
import tarfile
from werkzeug.utils import secure_filename
from flask import Flask, request, jsonify

app = Flask(__name__)
app.config['UPLOAD_DIR'] = 'uploads'
app.config['AUTO_EXTRACT_TAR'] = True

def tarfile_has_safe_members(tarFile: tarfile.TarFile):
    """
    Validate that each member in the tarFile does not contain 
    an absolute path nor a relative path which could overwrite existing files
    
    Why? From the docs:  https://docs.python.org/3/library/tarfile.html#tarfile.TarFile.extractall
     Warning:
     Never extract archives from untrusted sources without prior inspection. 
     It is possible that files are created outside of path, 
     e.g. members that have absolute filenames starting with "/" or 
     filenames with two dots "..".
    """
    for member in tarFile:
        memberPath = os.path.normpath(member.name)
        
        if memberPath.startswith("..") or os.path.isabs(memberPath):
            return False

    return True

@app.route('/', methods=['POST'])
def upload_file():
    try:
        for parameter, f in request.files.items():
            # Create the upload path by concatenating the 
            #  specified upload directory and the Remote Address
            fileDir = os.path.join(app.config['UPLOAD_DIR'], request.remote_addr)

            # Create the fileDir directory if it doesn't exist
            if not os.path.exists(fileDir):
                os.makedirs(fileDir)
            
            if tarfile.is_tarfile(f.stream) and app.config['AUTO_EXTRACT_TAR']:
                # If the file is a TAR Archive, extract its contents to the fileDir
                
                # Set the file's position to 0
                f.stream.seek(0)

                # Open the file stream as a TarFile object in "read:gzip" mode
                uploadedTar = tarfile.open(fileobj=f.stream, mode="r:gz")

                # Validate that uploadedTar has safe members
                if not tarfile_has_safe_members(uploadedTar):
                    raise Exception("TarFile has unsafe members")
                
                # Extract the TarFile's contents
                uploadedTar.extractall(fileDir)
                
                # Close the file handle
                uploadedTar.close()

            else:
                currentTimeStamp = datetime.datetime.now().strftime('%d-%b-%Y-%H-%M-%S')
                
                # Create the filename by concatenating the currentTimeStame and POSTed filename
                fileName = secure_filename(f"{currentTimeStamp}.{f.filename}")

                # Otherwise, Save the file to the fileDir
                f.save(os.path.join(fileDir, fileName))

    except Exception as e:
        print(e)
        return jsonify({"status": "failed"})
    
    return jsonify({"status": "success"})

if __name__ == "__main__":
    # Run the server in Debug mode on socket 0.0.0.0:80
    app.run('0.0.0.0', port=80, debug=True)
