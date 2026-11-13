import os
import threading
from flask import Flask
import telebot

TOKEN = os.environ.get("TOKEN", "8666501249:AAH1esd_1_Pp2N2N1CLwfMnu3Jh0EO89mzA")
bot = telebot.TeleBot(TOKEN, threaded=True)

active_games = {}
game_lock = threading.Lock()

IMAGE_URL = "https://i.pinimg.com/736x/52/3b/7a/523b7ab4a5bb49f27b6eed81b32c7b89.jpg"


# 1. Приветствие по /start в ЛС
@bot.message_handler(commands=["start"], chat_types=["private"])
def send_welcome(message):
  user = message.from_user
  if user.username:
    mention = f"@{user.username}"
  else:
    mention = f"[{user.first_name}](tg://user?id={user.id})"

  welcome_text = (
      f"Привет, {mention}! Я очень рад видеть тебя в этом боте 💜\n\n"
      f"🎁 Ты можешь получить бесплатного мишку тут: https://t.me/bobrnft1"
  )

  bot.send_message(message.chat.id, welcome_text, parse_mode="Markdown")


# 2. Игра «Царь горы» в группах
@bot.message_handler(
    func=lambda message: message.chat.type in ["group", "supergroup"],
    content_types=["text", "photo", "sticker", "voice"],
)
def handle_chat_activity(message):
  if message.from_user.is_bot:
    return

  chat_id = message.chat.id
  user = message.from_user

  if user.username:
    mention = f"@{user.username}"
  else:
    mention = f"[{user.first_name}](tg://user?id={user.id})"

  with game_lock:
    if chat_id in active_games and active_games[chat_id]["user_id"] == user.id:
      return

    if chat_id in active_games:
      old_game = active_games[chat_id]
      if "timer" in old_game and old_game["timer"]:
        old_game["timer"].cancel()

    timer = threading.Timer(120.0, finish_game, args=(chat_id, user.id))
    active_games[chat_id] = {
        "user_id": user.id,
        "name": mention,
        "timer": timer,
    }
    timer.start()

  text = (
      f"*{mention}*, ты первый на очереди что бы получить подарок🎂 Осталось"
      f" продерждатся 2 минуты без перебивов!🤯❤️\n\nудачи💕"
  )
  bot.send_message(chat_id, text, parse_mode="Markdown")


def finish_game(chat_id, user_id):
  with game_lock:
    if chat_id in active_games and active_games[chat_id]["user_id"] == user_id:
      active_games.pop(chat_id)
      winner = game_id_name = active_games.get(chat_id, {}).get("name", "Игрок")

      caption_text = (
          f"💜 **Поздравляю!**\n🏆 Ты продержался 2 минуты без перебивов и"
          f" победил в игре «Самый Большой Карман в этом Чате»!\n\n‼️ Пиши сообщения в чате, чтобы"
          f" запустить новую игру!"
      )
      try:
        bot.send_photo(
            chat_id,
            photo=IMAGE_URL,
            caption=caption_text,
            parse_mode="Markdown",
        )
      except Exception:
        bot.send_message(chat_id, caption_text, parse_mode="Markdown")


# Веб-сервер Flask для хостинга на Render
app = Flask("")


@app.route("/")
def home():
  return "Bot is alive!"


def run_bot():
  # Запуск поллинга с автовосстановлением при обрывах связи
  while True:
    try:
      bot.infinity_polling(none_stop=True, interval=0, timeout=20)
    except Exception as e:
      print(f"Polling error: {e}")


if __name__ == "__main__":
  t = threading.Thread(target=run_bot)
  t.daemon = True
  t.start()

  port = int(os.environ.get("PORT", 5000))
  app.run(host="0.0.0.0", port=port)
  
