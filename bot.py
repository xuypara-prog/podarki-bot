import os
import random
from flask import Flask
import telebot

# Токен вашего бота
TOKEN = os.environ.get("TOKEN", "8666501249:AAH1esd_1_Pp2N2N1CLwfMnu3Jh0EO89mzA")
bot = telebot.TeleBot(TOKEN)

active_users = {}

# Здесь можно настроить индивидуальные шансы для ников (без @)
CUSTOM_WEIGHTS = {
    # "username": 50,
}

# Ссылка на картинку из мема (или отправьте фото боту и возьмите его file_id,
# либо укажите прямую ссылку на картинку в интернете)
IMAGE_URL = (
    "https://pin.it/1dRWapSsm"  # замените на ссылку вашей картинки с копателем
)


@bot.message_handler(
    func=lambda message: message.chat.type in ["group", "supergroup"],
    content_types=["text", "photo", "sticker", "voice"],
)
def track_users(message):
  if message.from_user.is_bot:
    return

  chat_id = message.chat.id
  user = message.from_user

  if chat_id not in active_users:
    active_users[chat_id] = {}

  if user.username:
    mention = f"@{user.username}"
  else:
    mention = f"[{user.first_name}](tg://user?id={user.id})"

  active_users[chat_id][user.id] = {
      "mention": mention,
      "username": user.username or "",
  }

  # Если пишут команду /roll, запускаем розыгрыш
  if message.text and message.text.startswith("/roll"):
    pick_random_user(message)


def pick_random_user(message):
  chat_id = message.chat.id
  users_in_chat = active_users.get(chat_id, {})

  if not users_in_chat:
    bot.reply_to(
        message,
        "Я пока никого не запомнил в этом чате. Пусть участники напишут"
        " сообщение!",
    )
    return

  mentions = []
  weights = []

  for uid, data in users_in_chat.items():
    mentions.append(data["mention"])
    uname = data["username"]
    weight = CUSTOM_WEIGHTS.get(uname, 10)
    weights.append(weight)

  # Выбираем случайного победителя с учетом шансов
  chosen_user = random.choices(mentions, weights=weights, k=1)[0]

  # Текст сообщения точь-в-точь как на скриншоте
  caption_text = (
      f"💜 **Поздравляю!**\n"
      f"🎁 Ты выиграл Мишка 🧸 от @@bobr719\n"
      f"💎 Подарок отправлен.\n\n"
      f"‼️ пишите сообщения в чате, и получайте возможность так же залутать"
      f" подарки\n\n"
      f"🤍 так же вы можете выбить мишку рекламируя нас в другом чате"
  )

  # Отправляем фото с этим текстом и кнопкой/разметкой Markdown
  try:
    bot.send_photo(
        chat_id,
        photo=IMAGE_URL,
        caption=caption_text.format(user=chosen_user),
        parse_mode="Markdown",
    )
  except Exception as e:
    # Если картинка по ссылке не загрузилась, отправим просто текст
    bot.send_message(chat_id, caption_text, parse_mode="Markdown")


# Простой Flask-сервер для удержания бота в сети (для хостинга)
app = Flask("")


@app.route("/")
def home():
  return "Bot is alive!"


import threading


def run_bot():
  bot.infinity_polling()


if __name__ == "__main__":
  threading.Thread(target=run_bot).name = "TelegramBotThread"
  port = int(os.environ.get("PORT", 5000))
  app.run(host="0.0.0.0", port=port)
