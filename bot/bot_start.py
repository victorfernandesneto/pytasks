import os
import logging
from dotenv import load_dotenv
from telegram.ext import ApplicationBuilder, CommandHandler, MessageHandler, filters
from bot_commands import start, add_task, tasks, task, update_task, finish_task, commands, filler_command, unknown_message

load_dotenv()

logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)

if __name__ == '__main__':
    application = ApplicationBuilder().token(os.getenv('BOT_TOKEN')).build()

    start_handler = CommandHandler('start', start)
    add_task_handler = CommandHandler('add_task', add_task)
    task_list_handler = CommandHandler('tasks', tasks)
    task_retrieve_handler = CommandHandler('task', task)
    task_update_handler = CommandHandler('update_task', update_task)
    task_finish_handler = CommandHandler('finish_task', finish_task)
    commands_handler = CommandHandler('commands', commands)
    filler_command_handler = MessageHandler(
        filters.Regex(r'/.*'), filler_command)
    unknown_message_handler = MessageHandler(
        filters.ChatType.PRIVATE & ~filters.Command(), unknown_message)

    application.add_handler(start_handler)
    application.add_handler(add_task_handler)
    application.add_handler(task_list_handler)
    application.add_handler(task_retrieve_handler)
    application.add_handler(task_update_handler)
    application.add_handler(task_finish_handler)
    application.add_handler(commands_handler)
    application.add_handler(filler_command_handler)
    application.add_handler(unknown_message_handler)

    application.run_polling()
