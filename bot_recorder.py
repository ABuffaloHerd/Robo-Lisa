#TODO filter message:check if emoji exists. is it an emoji found within the guild? if not discard. 
#TODO filter message pt2. :figure out what the reply is, find author of reply. 
#TODO record message in training.csv 

import re

def record_msg(msg, guild_emojis):
    if not emoji_check(msg, guild_emojis):
        return

    filtered_message = filter_message(msg)

    with open('training.csv', 'a') as file:
        file.write(filtered_message + '\n')
    return

# return true if emoji exists in message and if emoji is found within guild
def emoji_check(msg, guild_emojis):
    discord_emoji_pattern = re.compile(r":[a-zA-Z0-9_]+:")

    matches = discord_emoji_pattern.findall(msg.content)
    match = matches[0]

    if match != '':
        for guild_emoji in guild_emojis:
            if guild_emoji.name == match:
                return True

    return False

# return a line of csv's containing author, message, and lisa's reply. 
def filter_message(msg):
    filtered_message = ""

    return filtered_message
