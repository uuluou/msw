import telebot
import requests
import re
import time

TOKEN = '7048532102:AAHT_pxhpxhUd-TpruTnfRSV7WLHh7qwed4'
bot = telebot.TeleBot(TOKEN)

def check_card(card_details):
    n, mm, yy, cvc = card_details.split('|')
    yy = yy[-2:]

    if len(n) < 11:
        return "This 3DS gate requires a card with at least 11 digits."

    bin_response = requests.get(f'https://lookup.binlist.net/{n[:6]}')
    if bin_response.status_code == 200:
        bin_data = bin_response.json()
        card_type = bin_data.get('type', 'N/A')
        card_scheme = bin_data.get('scheme', 'N/A')
        bank_name = bin_data.get('bank', {}).get('name', 'N/A')
        country_name = bin_data.get('country', {}).get('name', 'N/A')
        country_emoji = bin_data.get('country', {}).get('emoji', '')
    else:
        card_type = card_scheme = bank_name = country_name = country_emoji = 'N/A'

    try:
        start_time = time.time()
        response = requests.get(f'https://rimuruchkbot.alwaysdata.net/vbv.php?bin={n}|{mm}|{yy}|{cvc}', timeout=10)
        end_time = time.time()
        time_taken = end_time - start_time

        if response.status_code == 200:
            json_response = response.json()
            result = json_response.get('result', '').strip()

            card_details_formatted = f"[ϟ] 𝘾𝘾 ↯ {card_details}\n"
            result_formatted = f"[ϟ] 𝙍𝙀𝙎𝙐𝙇𝙏 ↯ {result}\n"
            info_formatted = f"[ϟ] 𝙄𝙉𝙁𝙊 ↯ {card_scheme}-{card_type}\n"
            issuer_formatted = f"[ϟ] 𝙄𝙎𝙎𝙐𝙀𝙍 ↯ {bank_name}\n"
            country_formatted = f"[ϟ] 𝘾𝙊𝙐𝙉𝙏𝙍𝙔 ↯ {country_name} {country_emoji}\n"
            time_formatted = f"𝗧𝗼𝗼𝗸 : {time_taken:.2f} 𝘀𝗲𝗰𝗼𝗻𝗱𝘀\n━━━━━━━━━━━━━"
            developer_info = "\n Dev : @yyxwv"

            return f"{card_details_formatted}{result_formatted}{info_formatted}{issuer_formatted}{country_formatted}{time_formatted}{developer_info}"
        else:
            return f"Error: Status code {response.status_code}"
    except requests.exceptions.RequestException as e:
        return f"Error: {e}"

@bot.message_handler(regexp="^(/mvbv|\.mvbv) (.+)")
def handle_multiple_card_check(message):
    command, card_details = message.text.split(maxsplit=1)
    cards = card_details.strip().split('\n')
    if len(cards) > 8:
        bot.send_message(message.chat.id, "Please provide a maximum of 8 cards.")
        return

    results = "𝗠𝗮𝘀𝘀 𝟯𝗗𝗦 𝗟𝗼𝗼𝗸𝘂𝗽 🔍\n\n"
    for card in cards:
        result = check_card(card)
        results += f"{result}\n_ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ \n"

    bot.send_message(message.chat.id, results)

@bot.message_handler(regexp="^(/vbv|\.vbv) (.+)")
def handle_single_card_check(message):
    match = re.match(r'^(/vbv|\.vbv) (\d{16})[|/](\d{2})[|/](\d{4})[|/](\d{3})$', message.text)
    if match:
        card_details = f"{match.group(2)}|{match.group(3)}|{match.group(4)}|{match.group(5)}"
        result = check_card(card_details)
        bot.send_message(message.chat.id, result)
    else:
        bot.send_message(message.chat.id, "Please provide card details in the correct format")

@bot.message_handler(commands=['start'])
def send_welcome(message):
    markup = InlineKeyboardMarkup()
    join_button = InlineKeyboardButton("JOIN", url="https://t.me/yyxvw")
    markup.add(join_button)
    welcome_text = "𝗪𝗘𝗟𝗖𝗢𝗠𝗘, 𝗬𝗢𝗨 𝗖𝗔𝗡 𝗨𝗦𝗘 𝗖𝗢𝗠𝗠𝗔𝗡𝗗𝗦\n/vbv or .vbv "
    bot.send_message(message.chat.id, welcome_text, reply_markup=markup)

@bot.message_handler(func=lambda message: True)
def handle_reply(message):
    if message.reply_to_message:
        text = message.reply_to_message.text
        match = re.search(r'(\d{16})[|/](\d{2})[|/](\d{2})[|/](\d{3})', text)
        if match:
            year = '20' + match.group(3)
            card_details = f"{match.group(1)}|{match.group(2)}|{year}|{match.group(4)}"
            result = check_card(card_details)
            bot.reply_to(message.reply_to_message, result)


def is_valid_bin(bin_number):
    return bin_number.isdigit() and 6 <= len(bin_number) <= 16

def fetch_bin_data(bin_number):
    response = requests.get(f"https://lookup.binlist.net/{bin_number[:6]}", headers={'Accept-Version': "3"})
    if response.ok:
        return response.json()
    return None

def create_response_message(bin_number, bin_data, username):
    if not bin_data:
        return "Failed to retrieve BIN information."

    results = f"[ϟ] 𝘽𝙄𝙉 ↯ {bin_number[:6]}\n"
    results += f"[ϟ] 𝘽𝙍𝘼𝙉𝘿 ↯ {bin_data.get('scheme', 'Unknown')}\n"
    results += f"[ϟ] 𝙏𝙔𝙋𝙀 ↯ {bin_data.get('type', 'Unknown')}\n"
    results += f"[ϟ] 𝙇𝙀𝙑𝙀𝙇 ↯ {bin_data.get('brand', 'Unknown')}\n"
    results += f"[ϟ] 𝘽𝘼𝙉𝙆 ↯ {bin_data.get('bank', {}).get('name', 'Unknown')}\n"
    results += f"[ϟ] 𝘾𝙊𝙐𝙉𝙏𝙍𝙔 ↯ {bin_data.get('country', {}).get('name', 'Unknown')} {bin_data.get('country', {}).get('emoji', '')}\n"
    results += f"[ϟ] 𝘽𝘼𝙉𝙆 𝙒𝙀𝘽𝙎𝙄𝙏𝙀 ↯ {bin_data.get('bank', {}).get('url', 'Unknown')}\n"
    results += f"[ϟ] 𝘽𝘼𝙉𝙆 𝙋𝙃𝙊𝙉𝙀 ↯ {bin_data.get('bank', {}).get('phone', 'Unknown')}\n"
    results += f"[ϟ] 𝘾𝙃𝙀𝘾𝙆 𝘽𝙔 ↯ @{username if username else 'Unknown'}\n"
    results += "Bot by : @yyxwv ☁️"
    return results

@bot.message_handler(commands=['bin'])
def handle_bin_query(message):
    args = message.text.split()
    if len(args) != 2 or not is_valid_bin(args[1]):
        bot.send_message(message.chat.id, "Usage: /bin <6 to 16 digits of the card number>")
        return

    bin_number = args[1]
    bin_data = fetch_bin_data(bin_number)
    response_message = create_response_message(bin_number, bin_data, message.from_user.username)
    bot.send_message(message.chat.id, response_message)

bot.polling()
