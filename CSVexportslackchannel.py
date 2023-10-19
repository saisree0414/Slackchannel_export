import os
import csv
import requests
from slack import WebClient
from slack.errors import SlackApiError

# Initialize the Slack API client with your token
slack_token = "YOUR_SLACK_API_TOKEN"
client = WebClient(token=slack_token)

# Define the channel ID and output CSV file path
channel_id = "YOUR_CHANNEL_ID"
output_csv = "channel_history.csv"
output_images_folder = "images"  # Folder to save images

# Create the images folder if it doesn't exist
os.makedirs(output_images_folder, exist_ok=True)

# Function to download and save images
def download_and_save_image(url, filename):
    try:
        response = requests.get(url)
        if response.status_code == 200:
            with open(filename, 'wb') as file:
                file.write(response.content)
    except Exception as e:
        print(f"Error downloading image: {str(e)}")

# Function to export channel history to CSV
def export_channel_history_to_csv():
    try:
        with open(output_csv, 'w', newline='') as csv_file:
            csv_writer = csv.writer(csv_file)
            csv_writer.writerow(["User", "Timestamp", "Text", "Image"])

            # Retrieve the initial channel history
            result = client.conversations_history(channel=channel_id)

            for message in result["messages"]:
                user = message.get("user", "Unknown User")
                timestamp = message.get("ts")
                text = message.get("text", "")

                # Check for attachments (including images)
                attachments = message.get("attachments", [])
                for attachment in attachments:
                    if attachment.get("image_url"):
                        image_url = attachment["image_url"]
                        image_filename = os.path.join(output_images_folder, f"{timestamp}.jpg")
                        download_and_save_image(image_url, image_filename)
                        csv_writer.writerow([user, timestamp, text, image_filename])
                    else:
                        csv_writer.writerow([user, timestamp, text, ""])

                # Check for thread replies and write them
                if "thread_ts" in message:
                    thread_ts = message["thread_ts"]
                    thread_messages = client.conversations_replies(channel=channel_id, ts=thread_ts)
                    for thread_message in thread_messages["messages"]:
                        user = thread_message.get("user", "Unknown User")
                        timestamp = thread_message.get("ts")
                        text = thread_message.get("text", "")
                        csv_writer.writerow([user, timestamp, text, ""])

            # Continue retrieving older messages if available
            while result["has_more"]:
                result = client.conversations_history(channel=channel_id, cursor=result["response_metadata"]["next_cursor"])
                for message in result["messages"]:
                    user = message.get("user", "Unknown User")
                    timestamp = message.get("ts")
                    text = message.get("text", "")

                    attachments = message.get("attachments", [])
                    for attachment in attachments:
                        if attachment.get("image_url"):
                            image_url = attachment["image_url"]
                            image_filename = os.path.join(output_images_folder, f"{timestamp}.jpg")
                            download_and_save_image(image_url, image_filename)
                            csv_writer.writerow([user, timestamp, text, image_filename])
                        else:
                            csv_writer.writerow([user, timestamp, text, ""])

    except SlackApiError as e:
        print(f"Error exporting channel history: {e.response['error']}")

if __name__ == "__main__":
    export_channel_history_to_csv()
