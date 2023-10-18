pip install slackclient
import os
from slack import WebClient
from slack.errors import SlackApiError

# Initialize the Slack API client with your token
slack_token = "YOUR_SLACK_API_TOKEN"
client = WebClient(token=slack_token)

# Define the channel ID and the output file path
channel_id = "YOUR_CHANNEL_ID"
output_file = "channel_history.txt"

# Function to retrieve and export channel history
def export_channel_history():
    try:
        # Open the output file in write mode
        with open(output_file, "w") as file:
            # Retrieve the initial channel history
            result = client.conversations_history(channel=channel_id)

            # Write messages to the output file
            for message in result["messages"]:
                file.write(f"{message['user']} - {message['text']}\n")

                # Check for thread replies and write them
                if "thread_ts" in message:
                    thread_ts = message["thread_ts"]
                    thread_messages = client.conversations_replies(channel=channel_id, ts=thread_ts)
                    for thread_message in thread_messages["messages"]:
                        file.write(f"  - {thread_message['user']} - {thread_message['text']}\n")

            # Continue retrieving older messages if available
            while result["has_more"]:
                result = client.conversations_history(channel=channel_id, cursor=result["response_metadata"]["next_cursor"])
                for message in result["messages"]:
                    file.write(f"{message['user']} - {message['text']}\n")

    except SlackApiError as e:
        print(f"Error exporting channel history: {e.response['error']}")

if __name__ == "__main__":
    export_channel_history()
