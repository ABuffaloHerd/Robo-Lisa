#TODO filter message:check if emoji exists. is it an emoji found within the guild? if not discard. 
#TODO filter message pt2. :figure out what the reply is, find author of reply. 
#TODO record message in training.csv 

import re
import emoji

def is_emoji_name(text):
    return text in emoji.UNICODE_EMOJI_ENGLISH

def record_msg(msg, guild_emojis):
    print("record_msg()")

    if not emoji_check(msg, guild_emojis):
        return

    filtered_message = filter_message(msg)

    with open('training.csv', 'a') as file:
        file.write(filtered_message + '\n')
    return

# return true if emoji exists in message and if emoji is found within guild
# need to also check for if it's a normal emoji. 
def emoji_check(msg, guild_emojis):
    discord_emoji_pattern = re.compile(r":[a-zA-Z0-9_]+:")

    matches = discord_emoji_pattern.findall(msg.content)
    if matches:
        match = matches[0][1:-1]  # Remove the colons

        if match:
            # Check against guild emojis
            for guild_emoji in guild_emojis:
                if guild_emoji.name == match:
                    return True
            
            # Check against standard emojis
            if is_emoji_name(match):
                return True

    return False

# return a line of csv's containing author, message, and lisa's reply. 
# author,original_message,reply_emojis
def filter_message(msg):
    filtered_message = ""

    author = msg.get_referenced_message.author
    original_message = msg.get_referenced_message.message

    discord_emoji_pattern = re.compile(r":[a-zA-Z0-9_]+:")
    matches = discord_emoji_pattern.findall(msg.content)
    reply_emoji = matches[0]

    filtered_message = ",".join([author, original_message, reply_emoji])

    return filtered_message
