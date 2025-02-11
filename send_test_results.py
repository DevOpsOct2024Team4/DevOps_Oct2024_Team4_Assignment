import requests
import sys

def send_discord_notification(message):
    webhook_url = 'https://discord.com/api/webhooks/1338626501951619092/JZI8ay8463JtuMcwTgU_-Y4sFLD1FEC0eRwdbrvZ9GTZ-KuWZRdhsApyATWv43V78Tk4'
    data = {"content": message}
    requests.post(webhook_url, json=data)

if __name__ == "__main__":
    # Receive the message as a command-line argument
    message = sys.argv[1] if len(sys.argv) > 1 else "Robot Framework test completed."
    send_discord_notification(message)
