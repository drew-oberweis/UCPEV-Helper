import os.path

from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError

# If modifying these scopes, delete the file token.json.
SCOPES = ["https://www.googleapis.com/auth/spreadsheets.readonly"]

# The ID and range of a sample spreadsheet.
spreadsheet_id = "1elIIh9jrFYl2tBIUDy3sIHrNXBirY2wh7naDZacp0SY"

def __get_sheet():
    """Shows basic usage of the Sheets API.
    Prints values from a sample spreadsheet.
    """
    creds = None
    # The file token.json stores the user's access and refresh tokens, and is
    # created automatically when the authorization flow completes for the first
    # time.
    if os.path.exists("google_token.json"):
        creds = Credentials.from_authorized_user_file("google_token.json", SCOPES)
    # If there are no (valid) credentials available, attempt to refresh
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            raise Exception("Outdated Credentials")

    try:
        service = build("sheets", "v4", credentials=creds)

        # Call the Sheets API
        sheet = service.spreadsheets()

    except HttpError as err:
        raise err
    
    return sheet

def get_rides():
        
        sheet = __get_sheet()

        data_range = "RideQuery!A2:G"
    
        result = (
            sheet.values()
            .get(spreadsheetId=spreadsheet_id, range=data_range)
            .execute()
        )
        values = result.get("values", [])

        # pad the array to ALWAYS have 7 elements

        for row in values:
            while len(row) < 7:
                row.append("")

        return values

    


def get_route(name):
    if(name == None):
        return None
    
    sheet = __get_sheet()

    data_range = "Routes!A2:J"

    result = (
        sheet.values()
        .get(spreadsheetId=spreadsheet_id, range=data_range)
        .execute()
    )
    values = result.get("values", [])

    # name is the first column in the range

    route = None

    for row in values:
        if row[0] == name:
            route = row[0:]

    # pad the array to ALWAYS have 10 elements


    while len(route) < 10:
        route.append("")

    return route



if __name__ == "__main__":
    result = get_rides()[0]
    print(result)
    print(f"Length: {len(result)}")
    result_2 = get_route(result[4])
    print(result_2)
    print(f"Length: {len(result_2)}")