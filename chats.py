chat_ids = [355908770, -749620842]

def send_message_to_all_chats(bot, message):
    for chat_id in chat_ids:
        bot.send_message(chat_id, message)