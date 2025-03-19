from flask import Flask, request, abort
from linebot import LineBotApi, WebhookHandler
from linebot.exceptions import InvalidSignatureError
from linebot.models import MessageEvent, TextMessage, TextSendMessage, ImageSendMessage, VideoSendMessage
import os

# Environment variables for deployment
CHANNEL_ACCESS_TOKEN = os.environ.get('XTux+dcUCXcUqKCED5VM0fl4W6AuEEAYdv76NeFVCLAzCjfgPcAcf/YpX3XXpvHBJ/lZdpXZAVi++pw3WHosrDAeEBJccUuO7hS9Jsoc7WKj0argZrCs1AwmJSPp9nFaDOGyLBnILnw1GFNF8G+3iAdB04t89/1O/w1cDnyilFU=')
CHANNEL_SECRET = os.environ.get('eb662dcadc93e62b412bdf2c1113a86b')

# Initialize app and LINE API
app = Flask(__name__)
line_bot_api = LineBotApi(CHANNEL_ACCESS_TOKEN)
handler = WebhookHandler(CHANNEL_SECRET)

# Command responses
COMMANDS = {
    "help": {"type": "text", "value": "Here are the available commands: !help, !ping, !about, !cat"},
    "ping": {"type": "text", "value": "Pong!"},
    "about": {"type": "text", "value": "I'm a simple LINE bot created to respond to commands."},
    "cat": {
        "type": "combo",
        "text": "Here’s a cute cat for you!",
        "image": "https://example.com/cat.jpg"
    },
    "pets": {
        "type": "media",
        "text": (
            " *There are 3 important pet abilities* \n"
            " Special Regen: Used in raids and heroic. Causing knights to constantly use special attack."
            " 🔹 Only pets from season 76P (s76P) and newer's abilities are viable for special regen. 🔹\n"
            "Durable Rock Shield: Used for arena, war and heroic. Stage 1 ability, reduces the amount of "
            "damage your knights take for 3 turns.\n"
            "🔹🔹 You want the primal variant of the pet for pets that use rock shield or regen, there "
            "is no primal for shatter shield pets. A primal pet has a P next to their season number. 🔹🔹\n"
            "Shatter Shield: Used in raids. Stage 2 ability, creates a shield that absords a lot of damage.\n"
            "The images show all the shatter shield pets, and what a special regen pet looks like. The "
            "video showcases the special regeneration pet ability.\n"
            "🔹 To check pet abilites '!pet abilities' 🔹"
        ),
        "video_url": "https://i.imgur.com/6lycWFs.mp4",
        "preview_image_url": "https://i.imgur.com/cYYcMFB.png",
        "images": [
            "https://i.imgur.com/aXFROEF.jpeg",
            "https://i.imgur.com/5TeRUlZ.jpeg"
        ]
        },
    "pet abilities": {
        "type": "video",
        "text": "You can find out your pets abilities through the video.",
        "video_url": "https://i.imgur.com/YksBtpO.mp4",
        "preview_image_url": "https://i.imgur.com/cYYcMFB.png"
    },
    "war elixirs": {
        "type": "image",
        "text": (
            "The amount of points you get per attack during wars can be increased using elixirs.\n"
            "🔹 With elixirs 40% And up POWER ATTACK (using four energy) to get the most points. 🔹"
        ),
        "value": "https://i.imgur.com/yjWBqMC.jpeg"
    }

}

@app.route("/callback", methods=['POST'])
def callback():
    signature = request.headers['X-Line-Signature']
    body = request.get_data(as_text=True)
    
    try:
        handler.handle(body, signature)
    except InvalidSignatureError:
        abort(400)
    
    return 'OK'

@handler.add(MessageEvent, message=TextMessage)
def handle_message(event):
    text = event.message.text.lower().strip()
    
    # Check if message starts with '!'
    if not text.startswith('!'):
        return
    
    # Commands with spaces instead of _
    command = text[1:].strip()  # Extract the command
    response = COMMANDS.get(command)
    
    if response:
        messages = []
        if response["type"] == "text":
            messages.append(TextSendMessage(text=response["value"]))
        elif response["type"] == "image":
            messages.append(TextSendMessage(text=response["text"]))
            messages.append(ImageSendMessage(original_content_url=response["value"], preview_image_url=response["value"]))
        elif response["type"] == "combo":
            messages.append(TextSendMessage(text=response["text"]))
            messages.append(ImageSendMessage(original_content_url=response["image"], preview_image_url=response["image"]))
        elif response["type"] == "video":
            messages.append(TextSendMessage(text=response["text"]))
            messages.append(VideoSendMessage(original_content_url=response["video_url"], preview_image_url=response["preview_image_url"]))
        elif response["type"] == "media":
            messages.append(TextSendMessage(text=response["text"]))  # Add text
            messages.append(VideoSendMessage(original_content_url=response["video_url"], preview_image_url=response["preview_image_url"]))  # Add video
            for img_url in response["images"]:  # Add multiple images
                messages.append(ImageSendMessage(original_content_url=img_url, preview_image_url=img_url))
        elif response["type"] == "images":
            messages.append(TextSendMessage(text=response["text"]))  # Add text
            for img_url in response["images"]:  # Add multiple images
                messages.append(ImageSendMessage(original_content_url=img_url, preview_image_url=img_url))
        
        line_bot_api.reply_message(event.reply_token, messages)
    else:
        line_bot_api.reply_message(
            event.reply_token,
            TextSendMessage(text=f"No response found for '!{command}'.")
        )

if __name__ == "__main__":
    port = int(os.getenv("PORT", 5000))
    app.run(host="0.0.0.0", port=port)
