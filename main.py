import telebot
import os
import logging
from gtts import gTTS
from dotenv import load_dotenv

load_dotenv()

logger = telebot.logger
telebot.logger.setLevel(logging.INFO)


API_TOKEN = os.getenv("API_TOKEN")
bot = telebot.TeleBot(API_TOKEN)


@bot.message_handler(commands=['start'])
def send_welcome(message):
    bot.send_message(
        message.chat.id, "Send me a text and i will read it for you in english")
    

@bot.message_handler(func=lambda message: True)
def text_to_speech(message):
    text = message.text or ""
    if not text.strip():
        bot.send_message(message.chat.id, "Please send some text to convert to speech.")
        return

    voices_dir = os.path.join("voices")
    os.makedirs(voices_dir, exist_ok=True)
    file_name = os.path.join(voices_dir, f"output_{message.message_id}.mp3")
    output = gTTS(text=text, lang="en", tld='com.au')
    try:
        output.save(file_name)
        with open(file_name, "rb") as f:
            bot.send_voice(chat_id=message.chat.id, reply_to_message_id=message.message_id, voice=f)
    except Exception as e:
        logger.exception("Failed to generate or send voice: %s", e)
        try:
            bot.send_message(message.chat.id, "Sorry, couldn't generate audio right now.")
        except Exception:
            pass
    finally:
        try:
            if os.path.exists(file_name):
                os.remove(file_name)
        except Exception:
            logger.exception("Failed to remove temporary audio file")
    

bot.infinity_polling()
