#!/usr/bin/env python3

# Need to install python3 -m pip install --user requests
# Need to update the CONFIG part especially the Roku credentials

import json
import os
import re
import socket
import socketserver
import sys
from http.server import SimpleHTTPRequestHandler
from telnetlib import Telnet
from zipfile import ZIP_DEFLATED, ZipFile

import requests
from requests.auth import HTTPDigestAuth

# -----CONFIG-----#
SAMPLE_APP_DIRECTORY = 'sample'
SAMPLE_APP_NAME = 'app'
ROKU_USER = 'rokudev'
ROKU_PASS = 'webmedia'

def zip_sample_app():
    print('Packing sample app...')
    file_paths = get_all_file_paths(SAMPLE_APP_DIRECTORY, filtered_dirs=['/out', '/source/testFramework', '/source/tests', '/components/tests'],
                                    filtered_files=['test_screen.xml', 'globoSceneTest.xml'])
    if os.path.exists(SAMPLE_APP_NAME + '.zip'):
        os.remove(SAMPLE_APP_NAME + '.zip')
    with ZipFile(SAMPLE_APP_NAME + '.zip', 'w', compression=ZIP_DEFLATED) as zip:
        for path in file_paths:
            zip.write(path[0], path[1])
    print('Done')


def get_all_file_paths(directory, filtered_dirs=[], filtered_files=[]):
    length = len(directory)
    file_paths = []
    for root, directories, files in os.walk(directory):
        folder = root[length:]
        if isFilteredDir(filtered_dirs, folder): continue

        for filename in files:
            if filename in filtered_files: continue
            if re.match('.*xml|.*brs|.*json|.*png|manifest|.*ttf|.*graphql|.*jpg|.*jpeg', filename):
                filepath = (os.path.join(root, filename), os.path.join(folder, filename))
                file_paths.append(filepath)
           
    return file_paths

def isFilteredDir(filtered_dirs, folder):
    for filtered_dir in filtered_dirs:
        if folder.startswith(filtered_dir):
            return True
    return False

def upload_sample_app():
    # Reset by sending Home button press
    print('Sending Home key...')
    print(requests.post('http://' + ROKU_IP + ':8060/keypress/HOME'))
    # Remove existing sideloaded app
    files = {
        'mysubmit': (None, 'Delete'),
        'archive': (None, ''),
        'passwd': (None, ''),
    }
    print('Removing sideloaded app...')
    print(
        requests.post('http://' + ROKU_IP + '/plugin_install', files=files, auth=HTTPDigestAuth(ROKU_USER, ROKU_PASS)))
    
    os.system(" curl  --location --request POST \'" + "http://" + ROKU_IP + "/plugin_install"  + "\' \
        --user " + ROKU_USER + ":" + ROKU_PASS + " --anyauth\
        --header \'mysubmit: Install\' \
        --form \"archive=@app.zip\"\
        --form \'mysubmit=Install\'")

if __name__ == '__main__':
    args = sys.argv

    if len(args) > 0:
        for i in range(len(args)):
            if args[i] == '--ip':
                roku_ip = args[i+1]

        if ip:
            ROKU_IP = ip
            zip_sample_app()
            upload_sample_app()
            os.remove(SAMPLE_APP_NAME + '.zip')
    else:
        print('Passe o IP do device Roku...')
