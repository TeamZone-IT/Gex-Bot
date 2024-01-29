import time
from datetime import datetime, timedelta
import requests
from google.oauth2 import service_account
from googleapiclient.discovery import build
import pytz
import discord
from discord.ext import tasks

# Discord bot token and channel ID
DISCORD_TOKEN = "MTIwMTQ0MDAxNTAwODM5OTM4MQ.G67_k0.MqAqz33rVw9-Hnfy-n0d6IIaOJYCG9aCjDIEIk"
CHANNEL_ID = 1088988445587816579

# Gexbot API details
ticker = 'spx'  # Replace 'spx' with your desired ticker
api_key = 'sTkKwPnpP9TE'

# Google Sheets API details
sheets_credentials_file = 'sheet.json'
spreadsheet_id = '1kVW7HkTxwLTmlmeHPBT84nYbVXuAIQRGPFhiO38vFJA'
sheet_range = 'Sheet1'

# Initialize Discord client
client = discord.Client()

async def get_gexbot_data(endpoint):
    gexbot_url = f'https://api.gexbot.com/{ticker}/gex/{endpoint}?key={api_key}'
    response = requests.get(gexbot_url)
    
    if response.status_code == 200:
        data = response.json()
        return data
    else:
        print(f"Failed to fetch data from {gexbot_url}. Status code: {response.status_code}")
        return None

async def update_google_sheets(data):
    credentials = service_account.Credentials.from_service_account_file(sheets_credentials_file, scopes=['https://www.googleapis.com/auth/spreadsheets'])
    
    service = build('sheets', 'v4', credentials=credentials)
    
    # Format data for Google Sheets
    values = [['', ''], [''], ['Strike', 'GEX by Volume', 'GEX by OI', 'Prior 1', 'Prior 5', 'Prior 10', 'Prior 15', 'Prior 30']]

    for strike in data['strikes']:
        values.append([strike[0], strike[1], strike[2], *strike[3]])

    # Convert current time to PST
    pst_timezone = pytz.timezone('America/Los_Angeles')
    current_time_pst = datetime.now(pst_timezone).strftime('%Y-%m-%d %H:%M:%S PST')
    
    # Add the updated date and time at the end
    values.append(['Updated Time', current_time_pst, '', '', '', '', '', ''])

    body = {'values': values}
    
    # Append data to Google Sheets
    result = service.spreadsheets().values().append(
        spreadsheetId=spreadsheet_id, range=f'{sheet_range}!A:H',
        valueInputOption='RAW', body=body).execute()

    print(f'Appended {result["updates"]["updatedCells"]} cells.')
    
    # Send message to Discord channel
    channel = client.get_channel(CHANNEL_ID)
    if channel:
        message = f"Data added to Google Sheet at {current_time_pst}."
        await channel.send(message)
    else:
        print("Failed to find channel.")

@client.event
async def on_ready():
    print(f'We have logged in as {client.user}')

@tasks.loop(minutes=1)
async def main():
    try:
        # Get real-time data from Gexbot API
        gexbot_data = await get_gexbot_data('all')

        if gexbot_data:
            # Update Google Sheets
            await update_google_sheets(gexbot_data)

            # Print message for testing (remove or modify as needed)
            print('Data added to Google Sheet.')
            
    except Exception as e:
        print(f"An error occurred: {e}")

# Start the Discord bot
main.start()
client.run(DISCORD_TOKEN)
