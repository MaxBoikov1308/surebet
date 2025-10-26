import logging
from telegram import Update
from telegram.ext import Application, CommandHandler, ContextTypes
import threading
import time
from files.get_profit import profit
from files.find import save_bet
from files.get_dict import read_and_parse_file

# Настройки
KEY_VALUE = 2
USER_IDS = {}
# USER_IDS = {}
BOT_TOKEN = ""

def get_current_value() -> float:
    try:
        return profit(update=True)
    except Exception as e:
        print(f"Ошибка получения значения: {e}")
        return 0

async def set_key(update: Update, context: ContextTypes.DEFAULT_TYPE):
    global KEY_VALUE
    try:
        KEY_VALUE = float(context.args[0])
        await update.message.reply_text(f"Ключ изменен на {KEY_VALUE}")
    except Exception as e:
        await update.message.reply_text(f"Введите корректное значение, текущее значение: {KEY_VALUE}")

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    USER_IDS.add(user_id)
    print(f"{user_id} подписался на уведомления")
    await update.message.reply_text(f"Вы подписались на уведомления! ID: {user_id}")

async def broadcast_to_all(message: str, bot):
    """Синхронная функция для рассылки"""
    for user_id in list(USER_IDS):
        try:
            await bot.send_message(chat_id=user_id, text=message)
        except Exception as e:
            print(f"Ошибка отправки {user_id}: {e}")

def value_checker():
    """Функция для проверки значения в отдельном потоке"""
    while True:
        current_value = get_current_value()
        print(f"Проверка значения: {current_value, KEY_VALUE}")
        
        if current_value >= KEY_VALUE:
            # Для отправки сообщений нужно создать экземпляр бота
            import asyncio
            application = Application.builder().token(BOT_TOKEN).build()
            
            save_bet(current_value, 'index.txt', 'index.txt')
            result = read_and_parse_file('index.txt')
            
            import json
            message = json.dumps(result, ensure_ascii=False, indent=2)
            asyncio.run(broadcast_to_all(message, application.bot))
            
            # Пауза после уведомления
            time.sleep(60)
        
        time.sleep(60)  # Проверка каждую минуту

def main():
    # Запускаем проверку в отдельном потоке
    checker_thread = threading.Thread(target=value_checker, daemon=True)
    checker_thread.start()
    
    # Создаем и запускаем бота
    application = Application.builder().token(BOT_TOKEN).build()
    application.add_handler(CommandHandler("start", start))
    application.add_handler(CommandHandler("set_key", set_key))
    
    print("Бот запущен...")
    application.run_polling()

if __name__ == "__main__":
    main()

