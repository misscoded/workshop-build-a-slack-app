import logging, os, re
from slack_bolt.adapter.socket_mode import SocketModeHandler
from slack_bolt import App
from dotenv import load_dotenv

load_dotenv()

# export SLACK_APP_TOKEN=xapp-***
# export SLACK_BOT_TOKEN=xoxb-***
app = App(token=os.environ["SLACK_BOT_TOKEN"])

# logging.basicConfig(level=logging.DEBUG)

'''
Messages can be listened for, using specific words and phrases.
Note: your Slack app *must* be subscribed to the following events
and scopes, as well as be present in the channels where they occur.
Please see the 'Event Subscriptions' and 'OAuth & Permissions'
sections of your app's configuration to add the following:

Event subscription required:   messages.channels
OAuth scope required:          chat:write

Further Information & Resources
https://slack.dev/bolt-python/concepts#message-listening
https://api.slack.com/messaging/retrieving#permissions
'''
# @app.message(re.compile("(hi|hello|hey)"))
@app.message('hello')
def handle_hello(message, say):
    user = message["user"]
    say(f"Hello, <@{user}>! :smile:")


'''
Shortcuts can be global (accessible from anywhere in Slack), 
or specific to messages (shown only in message context menus).

Shortcuts can trigger both modals and other app interactions.
 
Further Information & Resources
https://slack.dev/bolt-python/concepts#shortcuts
'''
@app.shortcut("create_poll")
def handle_create_poll(ack, shortcut, client):
    ack()
    
    client.views_open(
        trigger_id=shortcut["trigger_id"],
        view={
            "type": "modal",
            "callback_id": "poll_shortcut_modal",
            "title": {"type": "plain_text", "text": "My App"},
            "close": {"type": "plain_text", "text": "Close"},
            "submit": {"type": "plain_text", "text": "Submit"},
            "blocks": [
                { 
                    "type": "input",
                    "block_id": "target_conversation",
                    "element": {
                        "type": "conversations_select",
                        "placeholder": {
                            "type": "plain_text",
                            "text": "Select a conversation",
                            "emoji": True
                        },
                        "filter": {
                            "include": [
                                "public",
                                "mpim"
                            ],
                            "exclude_bot_users": True
                        },
                        "action_id": "input",
                    },
                    "label": {
                        "type": "plain_text",
                        "text": "Select the conversation to publish your poll to:",
                        "emoji": True
                    }
                },

                # Poll Question
                {
                    "type": "input",
                    "block_id": "poll_question",
                    "element": {
                        "type": "plain_text_input",
                        "action_id": "input"
                    },
                    "label": {
                        "type": "plain_text",
                        "text": "Poll Question",
                        "emoji": True
                    }
                },

                # Poll Options
                {
                    "type": "input",
                    "block_id": "option_1",
                    "element": {
                        "type": "plain_text_input",
                        "action_id": "input"
                    },
                    "label": {
                        "type": "plain_text",
                        "text": "Option 1",
                        "emoji": True
                    }
                },
                {
                    "type": "input",
                    "block_id": "option_2",
                    "element": {
                        "type": "plain_text_input",
                        "action_id": "input"
                    },
                    "label": {
                        "type": "plain_text",
                        "text": "Option 2",
                        "emoji": True
                    }
                },
                {
                    "type": "input",
                    "block_id": "option_3",
                    "element": {
                        "type": "plain_text_input",
                        "action_id": "input"
                    },
                    "label": {
                        "type": "plain_text",
                        "text": "Option 3",
                        "emoji": True
                    }
                }
            ],
        }
    )


'''
The view_sumbmission event occurs when a modal is submitted by 
the user.

The ID used in app.view() to identify the view corresponds to
the callback_id used where the view was defined and sent via
client.views.open(). 
 
Further Information & Resources
https://slack.dev/bolt-js/concepts#view_submissions
'''
@app.view("poll_shortcut_modal")
def handle_submission(ack, body, client, view):
    ack()
    user = body["user"]

    # Grab Modal Input Values
    target_conversation = view["state"]["values"]["target_conversation"]
    poll_question = view["state"]["values"]["poll_question"]
    option_1 = view["state"]["values"]["option_1"]
    option_2 = view["state"]["values"]["option_2"]
    option_3 = view["state"]["values"]["option_3"]


    # Add Voting Emoji Options
    # Your app *must* be in the channel you're posting to
    # Required scope(s): chat:write
    res = client.chat_postMessage(
        channel=target_conversation["input"]["selected_conversation"], 
        blocks=[
            {
                "type": "section",
                "text": {
                "type": "mrkdwn",
                "text": f"<@{user['id']}> wants to know: *{poll_question['input']['value']}*"
                }
            },
            {
                "type": "section",
                "text": {
                "type": "plain_text",
                "text": f":one: {option_1['input']['value']}",
                "emoji": True
                }
            },
            {
                "type": "section",
                "text": {
                "type": "plain_text",
                "text": f":two: {option_2['input']['value']}",
                "emoji": True
                }
            },
            {
                "type": "section",
                "text": {
                "type": "plain_text",
                "text": f":three: {option_3['input']['value']}",
                "emoji": True
                }
            }
        ]
    )

    channel = res["channel"]
    ts = res["ts"]

    # Add Voting Emoji Options
    # Required scope(s): reactions:write
    client.reactions_add(
        channel=channel,
        timestamp=ts,
        name="one",
    )

    client.reactions_add(
        channel=channel,
        timestamp=ts,
        name="two",
    )

    client.reactions_add(
        channel=channel,
        timestamp=ts,
        name="three",
    )

if __name__ == "__main__":
    # Create an app-level token with connections:write scope
    handler = SocketModeHandler(app, os.environ["SLACK_APP_TOKEN"])
    handler.start()