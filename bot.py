import os
import threading
from flask import Flask
import telebot

TOKEN = os.environ.get("TOKEN", "8666501249:AAH1esd_1_Pp2N2N1CLwfMnu3Jh0EO89mzA")
bot = telebot.TeleBot(TOKEN)

active_games = {}
game_lock = threading.Lock()

# Картинка с тортиком для финала
IMAGE_URL = "https://i.pinimg.com/736x/52/3b/7a/523b7ab4a5bb49f27b6eed81b32c7b89.jpg"


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
    # Если пишет тот же игрок, не сбрасываем его таймер
    if chat_id in active_games and active_games[chat_id]["user_id"] == user.id:
      return

    # Если игрока перебили — отменяем старый таймер
    if chat_id in active_games:
      old_game = active_games[chat_id]
      if "timer" in old_game and old_game["timer"]:
        old_game["timer"].cancel()

    # Запускаем новый таймер на 2 минуты (120 секунд)
    timer = threading.Timer(120.0, finish_game, args=(chat_id, user.id))

    game_data = {
        "user_id": user.id,
        "name": mention,
        "chat_id": chat_id,
        "timer": timer,
    }
    active_games[chat_id] = game_data
    timer.start()

  text = (
      f"*{mention}*, ты первый на очереди что бы получить тортик🎂 Осталось"
      f" продерждатся 2 минуты без перебивов!🤯❤️\n\nудачи💕"
  )

  try:
    bot.reply_to(message, text, parse_mode="Markdown")
  except Exception:
    bot.send_message(chat_id, text, parse_mode="Markdown")


def finish_game(chat_id, user_id):
  with game_lock:
    if chat_id in active_games and active_games[chat_id]["user_id"] == user_id:
      game_data = active_games.pop(chat_id)
      winner = game_data["name"]

      caption_text = (
          f"💜 **Поздравляю, {winner}!**\n"
          f"🏆 Ты продержался 2 минуты без перебивов и победил в игре «Царь"
          f" горы»!\n\n‼️ Пиши сообщения в чате, чтобы запустить новую игру!"
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


app = Flask("")


@app.route("/")
def home():
  return "King of the Hill Bot is alive!"


def run_bot():
  bot.infinity_polling()


if __name__ == "__main__":
  t = threading.Thread(target=run_bot)
  t.name = "TelegramBotThread"
  t.start()
  port = int(os.environ.get("PORT", 5000))
  app.run(host="0.0.0.0", port=port)
    
