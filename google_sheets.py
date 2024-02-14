import os.path
import json
import requests
from loguru import logger
from urllib import response

from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError

# If modifying these scopes, delete the file token.json.
SCOPES = ["https://www.googleapis.com/auth/spreadsheets"]

# Logging parameters
# logger.add("logs/logs.log", rotation="1 day", compression="zip")

class GoogleAPI:
    # returns creds
    def google_authenticate(self):
        creds = None
        # The file token.json stores the user's access and refresh tokens, and is
        # created automatically when the authorization flow completes for the first
        # time.
        if os.path.exists("jsons/token.json"):
            creds = Credentials.from_authorized_user_file("jsons/token.json", SCOPES)
        # If there are no (valid) credentials available, let the user log in.
        if not creds or not creds.valid:
            if creds and creds.expired and creds.refresh_token:
                creds.refresh(Request())
            else:
                flow = InstalledAppFlow.from_client_secrets_file(
                    "jsons/credentials.json", SCOPES
                )
                creds = flow.run_local_server(port=0)
            # Save the credentials for the next run
            with open("jsons/token.json", "w") as token:
                token.write(creds.to_json())

        return creds

    # addings new rows to google sheets
    def append_values(self, spreadsheet_id, range_name, value_input_option, values):
        creds = self.google_authenticate()
        # pylint: disable=maybe-no-member
        try:
            service = build("sheets", "v4", credentials=creds)

            body = {"values": values}
            result = (
                service.spreadsheets()
                .values()
                .append(
                    spreadsheetId=spreadsheet_id,
                    range=range_name,
                    valueInputOption=value_input_option,
                    body=body,
                )
                .execute()
            )
            logger.success(
                f"{(result.get('updates').get('updatedCells'))} cells appended."
            )
            return result

        except HttpError as error:
            logger.error("Failed to append values to the sheet!!!")
            return error

    def get_column_values(self, spreadsheet_id, range_name):
        creds = self.google_authenticate()

        try:
            service = build("sheets", "v4", credentials=creds)

            result = (
                service.spreadsheets()
                .values()
                .get(spreadsheetId=spreadsheet_id, range=range_name)
                .execute()
            )
            return result

        except HttpError as error:
            logger.error("Failed to get columns values")
            return error

    def check_id(self, user_id, spreadsheet_id):
        result = self.get_column_values(
            spreadsheet_id=spreadsheet_id,
            range_name='A2:A'
        )

        ids = [int(uid[0]) for uid in result['values']]  # type: ignore
        return int(user_id) in ids

    def is_token_expired(self):
        with open('jsons/token.json', 'r') as file:
            json_file = json.load(file)
            try:
                token = json_file['access_token']
            except:
                try:
                    token = json_file['token']
                except:
                    logger.error("Failed to read token.json. Check it out!")
                    return

            URL = "https://www.googleapis.com/oauth2/v1/tokeninfo"
            params = {
                "access_token": token
            }

            response = requests.post(URL, data=params)
            try:
                expiricy = int(response.json()['expires_in'])
            except:
                expiricy = 0
            
            if expiricy < 60:
                return True
            return False
    def check_token_expicicy_and_refresh(self):
        is_expired = self.is_token_expired()
        if not is_expired:
            logger.info(f"Token's current state: {not is_expired}")
            return

        for i in range(5):
            if self.is_token_expired():
                logger.warning(f"Token has expired. Attempt: {i} to refresh it")
                self.refresh_token()
            else:
                logger.success('Token has been succesfully refreshed')
                break

        return self.is_token_expired()

    def refresh_token(self):
        url = "https://oauth2.googleapis.com/token"
        refreshToken = "1//0cItyMyvHrfKkCgYIARAAGAwSNwF-L9Irrq-t06v9yIIaIKkLUVwqqU7xRBV0_YcZa4I4wcHKdSB6IF171z6_WPYOF8JLKJ9vjUg"
        client_id = '753678716474-uamgr48j2hknslfhj9qon62sr0cuvlfj.apps.googleusercontent.com'
        cliend_secret = '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'

        data = {
            "access_type": "offline",
            "refresh_token": refreshToken,
            "client_id": client_id,
            "client_secret": cliend_secret,
            "grant_type": "refresh_token"
        }

        response = requests.post(url, data=data)

        data = response.json()

        if response.status_code == 200:
            data['client_id'] = client_id
            data['client_secret'] = cliend_secret
            data['refresh_token'] = refreshToken
        else:
            logger.error(
                f"Failed to refresh token. Status code: {response.status_code}")

        with open('jsons/token.json', 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=4)


# runs the script
if __name__ == "__main__":
    GoogleAPI().google_authenticate()
