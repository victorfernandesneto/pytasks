import os
import logging
from dotenv import load_dotenv
from telegram import Update
from telegram.ext import ApplicationBuilder, ContextTypes, CommandHandler, MessageHandler, filters
import requests
from datetime import datetime

load_dotenv()

logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)


async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await context.bot.send_message(
        chat_id=update.effective_chat.id,
        text="Welcome to Pytask! I'll help you organize!"
    )


async def add_task(update: Update, context: ContextTypes.DEFAULT_TYPE):
    # Extract task and date from command
    if len(context.args) < 2:
        await update.message.reply_text("Please provide both task description and date with time. Example: /addtask Buy groceries 2023-01-01 15:30")
        return

    date_with_time = ' '.join(context.args[-2:])

    try:
        task = ' '.join(context.args[:-2])
        deadline = datetime.strptime(date_with_time, "%Y-%m-%d %H:%M")
    except ValueError:
        await update.message.reply_text("Invalid format. Please use: /add_task Buy groceries 2023-01-01 15:30")
        return

    # Send task data to DRF API
    api_url = os.getenv('DRF_API_URL')
    if not api_url:
        await update.message.reply_text("DRF_API_URL is not configured.")
        return

    payload = {
        'task_name': task,
        'deadline': deadline.isoformat(),
        'user': update.effective_user.id,
    }

    try:
        response = requests.post(api_url, json=payload)
        response.raise_for_status()
        await update.message.reply_text("Task added successfully!")
    except requests.RequestException as e:
        await update.message.reply_text(f"Failed to add task. Error: {str(e)}")


async def tasks(update: Update, context: ContextTypes.DEFAULT_TYPE):
    # Send a request to DRF API to retrieve tasks
    api_url = os.getenv('DRF_API_URL')
    if not api_url:
        await update.message.reply_text("DRF_API_URL is not configured.")
        return

    # Define parameters for filtering tasks per user
    params = {
        'user': update.effective_user.id,
    }

    try:
        response = requests.get(api_url, params=params)
        response.raise_for_status()
        tasks_data = response.json()

        if tasks_data:
            # Format and send the tasks to the user
            task_list = "\n".join([f"ID: {task['id']} - {task['task_name']} - Deadline: {task['deadline'][0:10]} {
                                  task['deadline'][11:-4]}" for task in tasks_data])
            await update.message.reply_text(f"Unfinished tasks:\n{task_list}")
        else:
            await update.message.reply_text("No tasks found.")
    except requests.RequestException as e:
        await update.message.reply_text(f"Failed to retrieve tasks. Error: {str(e)}")


async def task(update, context):
    params = {
        'user': update.effective_user.id,
    }
    task_id = context.args[0]
    api_url = f"{os.getenv('DRF_API_URL')}{task_id}/"
    if not api_url:
        await update.message.reply_text("DRF_API_URL is not configured.")
        return
    try:
        response = requests.get(api_url, params=params)
        task_data = response.json()
    except requests.RequestException as e:
        await update.message.reply_text(f"Failed to retrieve tasks. Error: {str(e)}")
    try:
        task = f"ID: {task_data['id']} - {task_data['task_name']} - Deadline: {task_data['deadline'][0:10]} {
            task_data['deadline'][11:-4]} {'\U00002705' if task_data['finished'] else '\U0000274C'}"
        await update.message.reply_text(str(task))
    except KeyError:
        await update.message.reply_text('No task found.')


async def update_task(update, context):
    params = {
        'user': update.effective_user.id,
    }
    task_id = context.args[0]
    new_name = ' '.join(context.args[1:-2])
    new_date = ' '.join(context.args[-2:])
    data = {
        'user': update.effective_user.id, "task_name": new_name, "deadline": new_date
    }
    api_url = f"{os.getenv('DRF_API_URL')}{task_id}/"
    if not api_url:
        await update.message.reply_text("DRF_API_URL is not configured.")
        return
    response = requests.put(api_url, json=data, params=params)
    try:
        if response.json()['detail']:
            await update.message.reply_text('Permission denied.')
    except KeyError:
        await update.message.reply_text('Task updated successfully.')


async def finish_task(update, context):
    params = {
        'user': update.effective_user.id,
    }
    task_id = context.args[0]
    api_url = f"{os.getenv('DRF_API_URL')}{task_id}/"
    if not api_url:
        await update.message.reply_text("DRF_API_URL is not configured.")
        return
    response = requests.delete(api_url, params=params)
    data = response.json()
    try:
        if data['detail']:
            await update.message.reply_text('Permission denied.')
    except KeyError:
        if data['finished']:
            await update.message.reply_text('Task completed successfully.')
        else:
            await update.message.reply_text('Task uncompleted successfully.')


async def commands(update: Update, context: ContextTypes.DEFAULT_TYPE):
    # Explanation of all available commands
    explanation = (
        "/start - Start the bot and receive a welcome message.\n"
        "/add_task <task_description> <deadline> - Add a new task with a deadline (e.g., /add_task Buy groceries 2023-01-01 15:30).\n"
        "/tasks - Retrieve the list of unfinished tasks.\n"
        "/task <task_id> - Retrieve details about a specific task.\n"
        "/update_task <task_id> <new_description> <new_deadline> - Update a task's description and deadline.\n"
        "/finish_task <task_id> - Finish a task and mark it as completed."
    )
    await update.message.reply_text(explanation)


async def filler_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("I don't recognize your command. See /commands for the list of available commands.")


async def unknown_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    # Check if message is in a private chat and not a command
    if update.message.chat.type == 'private' and not update.message.text.startswith('/'):
        await update.message.reply_text("I don't recognize your command. See /commands for the list of available commands.")


if __name__ == '__main__':
    application = ApplicationBuilder().token(os.getenv('BOT_TOKEN')).build()

    start_handler = CommandHandler('start', start)
    add_task_handler = CommandHandler('add_task', add_task)
    task_list_handler = CommandHandler('tasks', tasks)
    task_retrieve_handler = CommandHandler('task', task)
    task_update_handler = CommandHandler('update_task', update_task)
    task_finish_handler = CommandHandler('finish_task', finish_task)
    commands_handler = CommandHandler('commands', commands)
    filler_command_handler = MessageHandler(filters.Regex(r'/.*'), filler_command)
    unknown_message_handler = MessageHandler(filters.ChatType.PRIVATE & ~filters.Command(), unknown_message)




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
