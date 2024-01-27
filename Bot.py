import time
from datetime import datetime, timedelta
import requests
from google.oauth2 import service_account
from googleapiclient.discovery import build

# Gexbot API details
ticker = 'spx'  # Replace 'spx' with your desired ticker
api_key = 'sTkKwPnpP9TE'

# Google Sheets API details
sheets_credentials_file = 'C:\\Users\\TeamZone-IT\\Downloads\\Client project\\sheet.json'
spreadsheet_id = '15SnBrZ8uEhMmtewFODGob15dU7Hv9wQcL_iNqxJzkqI'
sheet_range = 'Sheet1'

def get_gexbot_data(endpoint):
    gexbot_url = f'https://api.gexbot.com/{ticker}/gex/{endpoint}?key={api_key}'
    response = requests.get(gexbot_url)
    
    if response.status_code == 200:
        data = response.json()
        return data
    else:
        print(f"Failed to fetch data from {gexbot_url}. Status code: {response.status_code}")
        return None

def update_google_sheets(data):
    credentials = service_account.Credentials.from_service_account_file(sheets_credentials_file, scopes=['https://www.googleapis.com/auth/spreadsheets'])
    
    service = build('sheets', 'v4', credentials=credentials)
    
    # Format data for Google Sheets
    values = [['', ''], [''], ['Strike', 'GEX by Volume', 'GEX by OI', 'Prior 1', 'Prior 5', 'Prior 10', 'Prior 15', 'Prior 30']]

    for strike in data['strikes']:
        values.append([strike[0], strike[1], strike[2], *strike[3]])

    # Add the updated date and time at the end
    updated_time = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    values.append(['Updated Time', updated_time, '', '', '', '', '', ''])

    body = {'values': values}
    
    # Append data to Google Sheets
    result = service.spreadsheets().values().append(
        spreadsheetId=spreadsheet_id, range=f'{sheet_range}!A:H',
        valueInputOption='RAW', body=body).execute()

    print(f'Appended {result["updates"]["updatedCells"]} cells.')

def main():
    try:
        while True:
            # Get real-time data from Gexbot API
            gexbot_data = get_gexbot_data('all')

            if gexbot_data:
                # Update Google Sheets
                update_google_sheets(gexbot_data)

                # Print message for testing (remove or modify as needed)
                print('Data added to Google Sheet.')

                # Sleep for 24 hours before updating again
                time.sleep(24 * 60 * 60)

    except Exception as e:
        print(f"An error occurred: {e}")

if __name__ == "__main__":
    main()
