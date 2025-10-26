import logging
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Application, CommandHandler, ContextTypes, CallbackQueryHandler
import threading
import time
from profit import profit, calculate_stakes
from find import save_bet
from dct import read_and_parse_file
from constants import *

# Настройки
KEY_VALUE = 3
USER_IDS = ID_SET
# USER_IDS = ID_SET_TEST
BOT_TOKEN = TOKEN

def get_current_value() -> list:
    try:
        return profit(update=True)
    except Exception as e:
        print(f"Ошибка получения значения: {e}")
        return 0
    
async def calc_bet(update: Update, context: ContextTypes.DEFAULT_TYPE):
    try:
        values = calculate_stakes(float(context.args[0]), float(context.args[1]), summa=float(context.args[2]))
        await update.message.reply_text(f"Коэффициенты: {values[0]} - {values[1]}")
    except Exception as e:
        await update.message.reply_text(f"Введите корректные значения")

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

async def broadcast_to_all(message: str, bot, reply_markup=None):
    """Синхронная функция для рассылки с поддержкой inline кнопок"""
    for user_id in list(USER_IDS):
        try:
            await bot.send_message(
                chat_id=user_id, 
                text=message,
                reply_markup=reply_markup
            )
        except Exception as e:
            print(f"Ошибка отправки {user_id}: {e}")

def is_bigger(values: list) -> list:
    return [i for i in values if i >= KEY_VALUE]

def get_fork_info(index: int, values: list) -> str:
    """Твоя функция для получения информации о вилке по индексу"""
    save_bet(profit_value=values[index], input_file='index.txt', output_file='current.txt')
    result = read_and_parse_file('current.txt')
    return result

async def button_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    
    # Получаем индекс из callback_data (формат: "fork_0", "fork_1" и т.д.)
    fork_index = int(query.data.split("_")[1])
    
    # Получаем информацию о выбранной вилке
    fork_info = get_fork_info(fork_index, get_current_value())  # Твоя функция для получения информации
    
    # Сохраняем оригинальную клавиатуру из сообщения
    original_reply_markup = query.message.reply_markup
    
    # Редактируем сообщение, но сохраняем клавиатуру
    await query.edit_message_text(
        text=f"Информация о вилке {fork_index + 1}:\n{fork_info}",
        reply_markup=original_reply_markup  # Сохраняем кнопки
    )
    
def value_checker():
    """Функция для проверки значения в отдельном потоке"""
    prev_values = []
    while True:
        values_list = is_bigger(get_current_value())
        current_value = values_list[0]
        
        if len(values_list) > 0 and values_list != prev_values:
            prev_values = values_list
            import asyncio
            application = Application.builder().token(BOT_TOKEN).build()
            
            # Создаем inline кнопки
            keyboard = []
            for i in range(len(values_list)):
                # Нумерация с 1, соответствует 1 + индекс элемента
                keyboard.append([InlineKeyboardButton(str(values_list[i]), callback_data=f"fork_{i}")])
            
            reply_markup = InlineKeyboardMarkup(keyboard)
            
            message = f"Найдено {len(values_list)} вилок с доходом больше {KEY_VALUE}%. Максимальная - {current_value}%"
            
            # Передаем reply_markup в функцию рассылки
            asyncio.run(broadcast_to_all(message, application.bot, reply_markup))
            
            time.sleep(60)
        
        time.sleep(60)

def main():
    # Запускаем проверку в отдельном потоке
    checker_thread = threading.Thread(target=value_checker, daemon=True)
    checker_thread.start()
    
    # Создаем и запускаем бота
    application = Application.builder().token(BOT_TOKEN).build()
    application.add_handler(CommandHandler("start", start))
    application.add_handler(CommandHandler("set", set_key))
    application.add_handler(CommandHandler("calc", calc_bet))
    application.add_handler(CallbackQueryHandler(button_handler))
    
    print("Бот запущен...")
    application.run_polling()

if __name__ == "__main__":
    main()
