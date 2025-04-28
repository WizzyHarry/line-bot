import os
import time
import threading
from flask import Flask, request, abort
from dotenv import load_dotenv
from linebot import LineBotApi, WebhookHandler
from linebot.exceptions import InvalidSignatureError
from linebot.models import MessageEvent, TextMessage, TextSendMessage, ImageSendMessage, VideoSendMessage


load_dotenv()

# Environment variables for deployment
CHANNEL_ACCESS_TOKEN = os.getenv('CHANNEL_ACCESS_TOKEN')
CHANNEL_SECRET = os.getenv('CHANNEL_SECRET')


# Debugging
#if not CHANNEL_ACCESS_TOKEN or not CHANNEL_SECRET:
#    print("Error: CHANNEL_ACCESS_TOKEN or CHANNEL_SECRET is not set properly.")
#    exit(1)


# Initialize app and LINE API
app = Flask(__name__)
line_bot_api = LineBotApi(CHANNEL_ACCESS_TOKEN)
handler = WebhookHandler(CHANNEL_SECRET)

# admin account ID's
ADMIN_USERS = ["cummywummies"]


# Command responses
COMMANDS = {
    "help": {
        "type": "text", 
        "value": (
            "Here are the available commands:\n"
            "\n!help"
            "\n!pets"
            "\n!pet abilities"
            "\n!heroic"
            "\n!war elixirs"
            "\n!blitz arena"
            "\n!anniversary"
            "\n!gems"
            "\n!mats"
            "\n!pushes"
            "\n!chests"
            "\n!set bonus"
            "\n!family"
            "\n!settings"
            "\n!account switching"
            "\n!ua"
            "\nfor datamine data do !num (!105)"
            "\n!calendar"
            "\n!epic boss"    
        )
    },
    "cat": {
        "type": "combo",
        "text": "Here’s a cute cat for you!",
        "image": "https://example.com/cat.jpg"
    },
    "pets": {
        "type": "media",
        "text": (
            " There are 3 important pet abilities \n"
            "\nSpecial Regen: Used in raids and heroic. Causes knights to constantly use special attack."
            " 🔹 Only pets from season 76P (s76P) and newer's abilities are viable for special regen.\n"
            "\nDurable Rock Shield: Used for arena, war and heroic. Stage 1 ability, reduces the amount of "
            "damage your knights take for 3 turns.\n"
            "\n🔹 You want the primal variant of the pet for pets that use rock shield or regen, there "
            "is no primal for shatter shield pets. A primal pet has a P next to their season number.\n"
            "\nShatter Shield: Used in raids. Stage 2 ability, creates a shield that absords a lot of damage.\n"
            "\nThe images show all the shatter shield pets, and what a special regen pet looks like. The "
            "video showcases the special regeneration pet ability.\n"
            "\n🔹 To check pet abilites '!pet abilities' "
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
            "\n🔹 With elixirs 40% And up POWER ATTACK (using four energy) to get the most points."
        ),
        "value": "https://i.imgur.com/yjWBqMC.jpeg"
    },
    "heroic": {
        "type": "video",
        "text": (
            "Herioc mode is a bi-weekly event that provides easy access to competitive armors. "
            "There are usually 2 events per month, with the armor elements combinations being: "
            "E/F - E/W - F/A - S/W - S/A. Occasionally there will be 3 events in a month, "
            "providing rare elements combinations: A/E - F/W - S/F...\n"
            "\nUsing friends makes Herioc easy, even if you're just starting out. Pester your "
            "guild & family for friends with UA armors.\n"
            "\n🔹 Herioc glitch allows you to heal your friends mid-battle, video demonstration below."
        ),
        "video_url": "https://i.imgur.com/A1KWCti.mp4",
        "preview_image_url": "https://i.imgur.com/cYYcMFB.png"
    },
    "blitz arena": {
        "type": "video",
        "text": (
            "Blitz arena is a short, bi-weekly event that takes place before every war weekend. "
            "Starting Tuesday at 3pm EST.\n"
            "\n🔹 200 gems on arena energy will get you 120 war energy in milestones. "
            "Along with pet ground peppers, silver coins, keys, and 3 t1 epic pets.\n"
            "\n🔹 Arena win streak glitch can be found below."
        ),
        "video_url": "https://i.imgur.com/gwUyNs9.mp4",
        "preview_image_url": "https://i.imgur.com/cYYcMFB.png"
    },
    "anniversary": {
        "type": "image",
        "text": (
            "Anniversary rewards are given out to players every year based on their download month. "
            "Rewards include: Anniversary Tokens & Gems."
        ),
        "value": "https://i.imgur.com/mwzUD5C.jpeg"
    },
    "gems": {
        "type": "text",
        "value": (
            "🔹 How to get Gems 🔹\n"
            "\n - Gem videos (30x day)"
            "\n - Event rewards"
            "\n - Event milestones"
            "\n - Level up"
            "\n - Quests"
            "\n - Daily login"
            "\n - Chests"
        )
    },
    "mats": {
        "type": "image",
        "text": (
            "🔹 Exclusive Armor Mats 🔹\n"
            "\n An exclusive is an armor having two of the same element, ex: fire/fire. "
            " These can be crafted by obtaining 10 monthly materials, more information "
            "on exclusives in '!ua' \n"
            "\nMaterials are avaliable in: Raid Milestones, War Milestones, Raid Guild Placement, "
            "War Guild Placement, Blitz Raid Milestones, Blitz War Milestones & Heroic. \n"
            "\n🔹 Monthly exclusive materials can ONLY be obtained during said month. The chart "
            "depicts old materials as well, EVEN if you acquire a month old material, it will have been "
            "automatically converted into a regular material, rather than an exclusive. Note: If you already "
            "acquired the exclusive mats, it is still craftable outside of said month."
        ),
        "value": "https://i.imgur.com/3H7VDKf.jpeg"
    },
    "pushes": {
        "type": "text",
        "value": (
            "A push is an organized event orchestrated with players from within a family/alliance. "
            "Pushes aim to achieve a certain placement, placements are based upon the minimums each "
            "player is expected to hit.\n"
            "\nPushes are helpful for getting armors with set bonus, exclusive materials, and MOGGING. "
            "Please message you're guild master or ask around for avaliable pushes.\n"
            "\nOur family, Lost, offers pushes every weekend. War minimums are straightfoward, and are "
            "easy to hit if you have the right amount of gems. Raids vary based on your lineup, if you're "
            "unsure about your ability to do a raid push, ask your GM."
        )
    },
    "chests": {
        "type": "text",
        "value": (
            "AVOID purchasing chests with gems, set bonus is an extremely viable asset to an armor. "
            "Chests make it difficult to acquire an armor + bling at a low cost.\n"
            "\nNaturally obtained keys are useful for the occasional gems & lucky armor grabs."
        )
    },
    "set bonus": {
        "type": "image",
        "text": (
            "Set bonus is a crucial part of creating strong knights. Each armor piece has a ring and "
            "amulet pair, increasing damage, defense and health. \n"
            "\n🔹 Obtaining Sets 🔹\n"
            "\n - Heroic Armor: 50 Heroic scrolls can be used to purchase the bling from item shop. "
            "These scrolls are obtained through the final four Heroic stages. Heroic bling can be crafted "
            "five seasons after it has been released.\n"
            "\n - War Armor: War armor is achieved through a top20 guild placement. The set is given "
            "through individual milestones at 195k points.\n"
            "\n - Raid Armor: Raid armor is achieved through a top10 guild placement. The set is given "
            "through individual milestones at 30mil (idrk).\n"
            "\n - Exclusive Armor: Exclusive armor is crafted with 10 monthly materials. The set is given "
            "in the first blitz war of the month at 475k points.\n"
            "\n - UA Armor: UA armor is given after getting the 5 seasonal exclusives. The set is craftable "
            "after getting at least 2/5 of the exclusive set bonuses."
        ),
        "value": "https://i.imgur.com/rjLNI2f.jpeg"
    },
    "bling": {
        "type": "image",
        "text": (
            "Set bonus is a crucial part of creating strong knights. Each armor piece has a ring and "
            "amulet pair, increasing damage, defense and health. \n"
            "\n🔹 Obtaining Sets 🔹\n"
            "\n - Heroic Armor: 50 Heroic scrolls can be used to purchase the bling from item shop. "
            "These scrolls are obtained through the final four Heroic stages. Heroic bling can be crafted "
            "five seasons after it has been released.\n"
            "\n - War Armor: War armor is achieved through a top20 guild placement. The set is given "
            "through individual milestones at 195k points.\n"
            "\n - Raid Armor: Raid armor is achieved through a top10 guild placement. The set is given "
            "through individual milestones at 30mil (idrk).\n"
            "\n - Exclusive Armor: Exclusive armor is crafted with 10 monthly materials. The set is given "
            "in the first blitz war of the month at 475k points.\n"
            "\n - UA Armor: UA armor is given after getting the 5 seasonal exclusives. The set is craftable "
            "after getting at least 2/5 of the exclusive set bonuses."
        ),
        "value": "https://i.imgur.com/rjLNI2f.jpeg"
    },
    "family": {
        "type": "text",
        "value": (
            "What is a family? If you're reading this you're probably in one. A family is a group of guilds "
            "that operate together to setup pushes and help new players.\n"
            "\nSimilar to a family is an alliance, a group of families that work together to fill pushes, "
            "and setup strip wars."
        )
    },
    "settings": {
        "type": "image",
        "text": (
            "KnD is an automated game system, to help your knights move faster I recommended following these "
            "settings. Note: Based on your iOS device, player capes may slightly slow down game performance."
        ),
        "value": "https://i.imgur.com/JQDnn0R.jpeg"
    },
    "account switching": {
        "type": "video",
        "text": (
            "Players with multiple accounts and only one device are able to switch back and forth between them. "
            "To switch, both accounts need to be linked to game center. The process involves signing out of gamecenter -> "
            "launching KnD to load your device bound save -> signing into other gamecenter -> loading new save on KnD."
        ),
        "video_url": "https://i.imgur.com/e5bMn8S.mp4",
        "preview_image_url": "https://i.imgur.com/cYYcMFB.png"
    },
    "ua": {
        "type": "image",
        "text": (
            "🔹 UA Armor 🔹\n"
            "\n The UA aka. Universal Armor is the double white pentagon element. To get the UA armor you need to "
            "complete an elemental cycle. A cycle is a series of elemental months, with each element having its own month. "
            "Cycle's always begin with Fire month, following -> Spirit -> Earth -> Air -> Water.\n"
            "\nTo complete an elemental month you need to obtain that months exclusive. For example, in fire month "
            "you'd need to get the fire/fire armor. To obtain an exclusive armor, you'll need to collect 10 monthly materials. "
            "These materials come from event milestones, guild placements, heroic and other methods. More information can "
            "be found in '!mats'. If you're confused about exclusive materials, please ask your guildmates.\n"
            "\nTo get the ring and amulet for the UA, it's awarded naturally by obtaining at least 2/5 of the exclusive "
            "bling sets. The exclusive bling sets are obtained by hitting 475k in the first blitz war of the month.\n"
            "\nAt first glance the steps for UA are extreme, however it's important to note the armor is acquired over "
            "a span of 5 months. The UA is achievable completely f2p, if you have questions on how to use your gems "
            "sparingly please message your GM."
        ),
        "value": "https://i.imgur.com/BR3S2dC.jpeg"
    },
    "good boy": {
        "type": "text",
        "value": (
            "Wow you're such a good boy! I'm very proud of you!"
        )
    },
    "suck": {
        "type": "text",
        "value": (
            "Wow buddy, you really love sucking on it huh?"
        )
    },
    "interview": {
        "type": "text",
        "value": (
            "Welcome to Lost Family!\n"
            "\nWe're excited to have you join us! Lost Family is a collection of guilds that actively work together, "
            "as a whole we're apart of the Covenant alliance. If you could please answer these questions, no stress, "
            "this obviously isn't a real interview, we'd just like to learn a little about you!\n"
            "\n1. What is your account level?\n"
            "\n2. What guild were you in before?\n"
            "\n3. Why did you leave your previous guild (were you removed)?\n"
            "\n4. Where are you from?\n"
            "\n5. How long have you been playing the game?\n"
            "\n6. Did you know you can watch 30 video ads a day to earn free gems?\n"
            "\n7. Do you know how strip wars work? If yes, please briefly explain.\n"
            "\n8. Can you share screenshots of your knights and kingdom?\n"
        )
    },
    "good": {
        "type": "text",
        "value": (
            "I'm a good boy, yes I am."
        )
    },
    "105": {
        "type": "image",
        "text": "Datamine for season 105. Credits for Kobe for creation.",
        "value": "https://i.imgur.com/ArNuc8o.jpeg"
    },
    "calendar": {
        "type": "image",
        "text": "uhhhhhhhhhhhhh",
        "value": "https://i.imgur.com/iSBZ0bx.jpeg"
    },
    "stink": {
        "type": "text",
        "value": "wow you smell AWFUL. Take a shower bud"
    },
    "pause": {
        "type": "video",
        "text": "",
        "video_url": "https://i.imgur.com/gbH3N9m.mp4",
        "preview_image_url": "https://i.ytimg.com/vi/ox34KNKx8ew/mqdefault.jpg"
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

    
    # normal command msg formats
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
            TextSendMessage(text=(f"No response found for '!{command}'.Use !help for a full list of commands"))
        )



if __name__ == "__main__":
    port = int(os.getenv("PORT", 5000))
    app.run(host="0.0.0.0", port=port)




# linepy functions progress. Would be used in different bot
"""
# linepy functions, linepy is not supported by LINE
from linepy import LINE, OEPoll


LINE_USER_EMAIL = os.getenv("LINE_USER_EMAIL")
LINE_USER_PASSWORD = os.getenv("LINE_USER_PASSWORD")


# my login credentials
line_client = LINE(LINE_USER_EMAIL, LINE_USER_PASSWORD)
poll = OEPoll(line_client)


def unofficial_event_listener():

    while True:
        try:

            ops = poll.singleTrace(count=50)
            for op in ops:
                # Assume op.type == 124 corresponds to a group invitation event.
                if op.type == 124:
                    group_id = op.param1   # Group ID 
                    inviter = op.param2    # The user who sent the invitation
                    invitee = op.param3    # The user being invited
                    # Check if the inviter is admin
                    if inviter not in ADMIN_USERS:

                        # Attempt to cancel the invitation.
                        try:
                            # cancels the invitation for the given invitee in the group.
                            line_client.cancelGroupInvitation(group_id, [invitee])

                        except Exception as e:
                            print(f"Failed to cancel invitation for {invitee}: {e}")
                        # remove the non-admin inviter from the group.
                        try:
                            line_client.kickoutFromGroup(group_id, [inviter])

                        except Exception as e:
                            print(f"Failed to remove unauthorized inviter {inviter}: {e}")
            # Pause briefly before polling for the next batch of events.
                elif op.type == 19:
                    group_id = op.param1 # Group ID
                    operator = op.param2 # user who kicked
                    kicked = op.param3 # user who was kicked

                    if operator not in ADMIN_USERS and operator != kicked:
                        try:
                            line_client.kickoutFromGroup(group_id, [operator])
                        except Exception as e:
                            print(f"Failed to remove non-admin")

            time.sleep(2)
        except Exception as e:
            print("Error in event listener:", e)
            time.sleep(5)


def start_unofficial_listener():
    listener_thread = threading.Thread(target=unofficial_event_listener)
    listener_thread.daemon = True
    listener_thread.start()
"""
