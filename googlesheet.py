from __future__ import print_function
import httplib2
import os

from apiclient import discovery
from oauth2client import client
from oauth2client import tools
from oauth2client.file import Storage

from googleapiclient import discovery
from googleapiclient.errors import HttpError

try:
    import argparse
    flags = argparse.ArgumentParser(parents=[tools.argparser]).parse_args()
except ImportError:
    flags = None

# If modifying these scopes, delete your previously saved credentials
# at ~/.credentials/sheets.googleapis.com-python-quickstart.json
SCOPES = 'https://www.googleapis.com/auth/spreadsheets'
CLIENT_SECRET_FILE = 'client_secret.json'
APPLICATION_NAME = 'Google Sheets API Python Quickstart'


def get_credentials():
    """Gets valid user credentials from storage.

    If nothing has been stored, or if the stored credentials are invalid,
    the OAuth2 flow is completed to obtain the new credentials.

    Returns: Credentials, the obtained credential.
    """
    home_dir = os.path.expanduser('~')
    credential_dir = os.path.join(home_dir, '.credentials')
    if not os.path.exists(credential_dir):
        os.makedirs(credential_dir)
    credential_path = os.path.join(credential_dir,
                                   'sheets.googleapis.com-python-quickstart.json')

    store = Storage(credential_path)
    credentials = store.get()
    if not credentials or credentials.invalid:
        flow = client.flow_from_clientsecrets(CLIENT_SECRET_FILE, SCOPES)
        flow.user_agent = APPLICATION_NAME
        if flags:
            credentials = tools.run_flow(flow, store, flags)
        else: # Needed only for compatibility with Python 2.6
            credentials = tools.run(flow, store)
        print('Storing credentials to ' + credential_path)
    return credentials

def write_to_googleSpreadsheet(username, newScore):
    """
    Creates a Sheets API service object and gets the names and scores 
    https://docs.google.com/spreadsheets/d/1wLJTkLUzMzNsjXkqZoeDxfZSj92xvi6QLlGrNRIWMgQ
    """
    credentials = get_credentials()
    http = credentials.authorize(httplib2.Http())
    discoveryUrl = ('https://sheets.googleapis.com/$discovery/rest?'
                    'version=v4')
 
    service = discovery.build('sheets', 'v4', http=http, 
                               discoveryServiceUrl=discoveryUrl)
    
    #get google spreadsheet id
    file = open('config')
    url_string = file.read()
    file.close()
    
    #spreadsheet_id = url_string.split(":")[1].replace(" ", "")  
    start_index = url_string.index(":") + 1
    spreadsheet_id = url_string[start_index:].replace(" ", "")
    range_name = 'ScoreTable'
    scoreDic = {}
    
    try:
        result = service.spreadsheets().values().get(
            spreadsheetId=spreadsheet_id, range=range_name).execute()
        
        values = result.get('values', [])
        
        if not values:
            #empty sheet, write new record
            scoreDic[username] = str(newScore) 
            
        else:
            for record_list in values:
                if len(record_list) != 0:
                    scoreDic[record_list[0]] = record_list[1]
                    
            if username in scoreDic:
                oldScore = float(scoreDic.get(username)) 
                scoreDic.update({username: str(oldScore + newScore)})
            else:
                scoreDic.update({username: str(newScore)})  
    
    except HttpError:
        spreadsheet_body = {
            "sheets": [
                {
                    "properties": {
                    "title": "ScoreTable"
                    }
                }
            ],
            "properties": {
                "title": "QF205G1T6"
            }
        }
        request = service.spreadsheets().create(body=spreadsheet_body)
        response = request.execute()
        
        spreadsheet_id = response.get('spreadsheetId')
        scoreDic[username] = str(newScore) 
        
        #update new URL to config file
        #with statement can help close file automatically 
        with open("config", "w") as file: 
            file.write("spreadsheet_id: " + spreadsheet_id) 
    
    finally:
        #create values_to_write list
        values_to_write = list()
        
        for k, v in scoreDic.items():
            values_to_write.append([k, v])
        
        body = {
            'values': values_to_write
        }
        
        #write to ScoreTable sheet
        result = service.spreadsheets().values().update(
            spreadsheetId=spreadsheet_id, range=range_name,
            valueInputOption="USER_ENTERED", body=body).execute()
