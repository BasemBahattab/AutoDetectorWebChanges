from typing import Final
from telegram import Update
from telegram.ext import (
    Application,
    CommandHandler,
    ContextTypes,
)
import time
import requests
from bs4 import BeautifulSoup
import threading
import asyncio

# Variables #
# If you want to connect it to telegram, you need to talk to BotFather in telegram in order to get the TOKEN.
TOKEN: Final = 'ENTER YOUR TOKEN'
BOT_USERNAME: Final = '@BOT_NAME'


# Add div class name to keep you in track if it got removed.
div_class = 'Enter Here the Div name'

# Add the URL into div such as: 
# url[0] = www.google.com
url = []

# Start command just to notify the user it is working.
async def start_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    print(f'Update {update.message.chat.first_name} starting')
    await update.message.reply_text('Started')

# to start the tracking using enable commaned
async def enable_command(update, context):
    
    # Force track for all URLs based on Div_class
    await forceTrack(url, div_class, update, context)

    time.sleep(15)

    await update.message.reply_text("Tracking has started ...")
    time.sleep(5)

    threads = []

    # Each URL has it's own thread
    for i in url:
        thread = threading.Thread(target=asyncio.run, daemon=True, args=(finder(i, div_class, update, context),))
        threads.append(thread)

    # Start threads
    for thread in threads:
        thread.start()

    # Join threads
    for thread in threads:
        thread.join()


# Finder function: it will be in a infinite loop in order to find if the Div class is existed or not.
# If the div is not exist it will make the thread sleep for 600 seconds.
# If the div exist it will make the thread sleep for 30 seconds.
async def finder(url, div_class, update: Update, context: ContextTypes.DEFAULT_TYPE):
    while True:
        print("Finding ... ", url)
        dummy = await find_context_in_div(url, div_class, update, context)
        print(url, dummy[2])
        if dummy[2] == True:
            time.sleep(600)
        else:
            print(url, "1 HERE")
            time.sleep(30)

# Forcer Command/functions to force publish the result to the user.
async def forcer(update: Update, context: ContextTypes.DEFAULT_TYPE):
    print("forcing")
    print(f'Update {update.message.chat.first_name} Forcing track')
    await update.message.reply_text("Forcing track")
    await forceTrack(url, div_class, update, context)

async def forceTrack(url, div_class, update: Update, context: ContextTypes.DEFAULT_TYPE):
    for i in url:
        tempTest = await find_context_in_div(i, div_class, update, context)
        time.sleep(3)
        await websiteChanged(tempTest[0], tempTest[1], update, context, 0, 1)  

    time.sleep(5)
    newURL: str = "Test case completed"
    print(f'Update {update.message.chat.first_name} {newURL}')
    return await update.message.reply_text(newURL)
        
# find_context_in_div function it will send HTTP request to given URL and return the if the div exist or not.
async def find_context_in_div(url, div_class, update: Update, contextt: ContextTypes.DEFAULT_TYPE):
    response = requests.get(url)
    status = False
    if response.status_code == 200:
        soup = BeautifulSoup(response.content, 'html.parser') 
        div = soup.find('div', class_=div_class)
        if div:
            context = div.get_text(strip=True)
            print(context)
        else:
            status = True
            print("Div not found.")
            await websiteChanged(url, response.status_code, update, contextt, status, 0)
    else:
        print("Failed to retrieve URL:", response.status_code)

    print(url, response.status_code)
    return [url, response.status_code, status]

# websiteChanged function responsiable to update the user the website changed.
async def websiteChanged(url, status_code, update: Update, context: ContextTypes.DEFAULT_TYPE, status, flag):
    if status == False:
        updatedDiv = "Product Not Available"
    else:
        updatedDiv = "Product Available Product Available Product Available Product Available Product Available Product Available"

    newURL: str = "Test Case ", url, status_code, updatedDiv
    if flag == 1:
        print(f'Update {update.message.chat.first_name} {newURL}')
        await update.message.reply_text(newURL)
        return
    if status_code == 200 and status == True:
        newURL: str = "One of the products is available", url
        print(f'Update {update.message.chat.first_name} {newURL}')
        await update.message.reply_text(newURL)
    elif status_code == 200 and status == False:
        newURL: str = "The products is not available", url
        print(f'Update {update.message.chat.first_name} {newURL}')


# Error message for troubleshooting purposes.
async def error(update: Update, context: ContextTypes.DEFAULT_TYPE):
    print(f'Update {update} caused error {context.error}')

# Main function with app builder.
if __name__ == '__main__':
    app = Application.builder().token(TOKEN).build()

    # You can add as much handler you want.
    # app.add_handler(CommandHandler('command written by user in telegram with slash', which function))
    # for examble: 
    # Telegram user typed: /start
    # app.add_handler(CommandHandler('start', startFunction))
    app.add_handler(CommandHandler('start', start_command))
    app.add_handler(CommandHandler('track', enable_command))
    app.add_handler(CommandHandler('forcetrack', forceTrack))

    # Error Handler
    app.add_error_handler(error)

    print('Polling ...')
    app.run_polling(poll_interval=3)
