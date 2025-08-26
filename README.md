# Automated Response ChatBot

**Keith Faunce**

## The Purpose

This chatbot is purely for entertainment purposes; it is not a product. The bot is designed to assist new and current players of the mobile game *Knights and Dragons*. As a leader in the game's community, I noticed that many new players had similar questions. The bot answers these questions using keyword-triggered responses.  

For example:  
- Typing `!chests` displays chest system info.  
- Typing `!help` displays all available commands. 

## Creation

<p>The bot is created and maintained through a Python script. It is connected to LINE's development studio via a channel access token and key. The script utilizes the Python packages `dotenv` and `flask` for hosting, while transaction/response commands are configured with LINE’s `linebot` package. It can be used in both individual conversations and large groups.</p>

To display images and videos in real-time, I used **Imgur** to upload all media files.

* Link to .py file: [Chatbot](line_pybot.py)

<br>

## Deployment

_LINE is a communication app traditionally used in Japan, iconically known for its creative sticker packs. The Knights & Dragons community began using LINE long before I came around._  

LINE Developer Studio issues token credentials for deploying the bot, but it does not support hosting. To solve this, the script is hosted on **Render**, a cloud application platform that provides free web services. Render connects directly to my GitHub repository. When I push updates to GitHub, Render automatically pulls the new code, installs the required Python packages from *requirements.txt*, and redeploys the bot.  

### Render Live Feed

<b> April 28th logs </b>

![render_logs](img/readme1.PNG)

### In Action

![chat_msgs](img/readme2.jpg)

