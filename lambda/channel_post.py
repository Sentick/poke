import os
import re
import message_functions as msg
import raid_function as raid

ADMIN_CHAT_ID      = os.environ['ADMIN_CHAT_ID']
AUTHORISED_CHATS   = [-1001182465706, -1001431112583]
UNSUPPORTED_EVENTS = ['reply_to_message', 'photo']
SUPPORTED_EVENTS   = ['chat']
SUPPORTED_COMMANDS = ['raid']

def channel_post_handler(channel_post):
    
    # Do not respond to unsupported events
    if (any(x in channel_post for x in UNSUPPORTED_EVENTS)) or not (any(x in channel_post for x in SUPPORTED_EVENTS)):
        return
    
    message_id = channel_post['message_id']
    chat = channel_post['chat']
    channel_id = chat['id']
    
    # Is the channel authorised?
    if not channel_id in AUTHORISED_CHATS:
        msg.send_message('Bot found in unauthorised channel:\n{0}'.format(channel_post), ADMIN_CHAT_ID)
        msg.send_message('Bot not authorised for this channel.', channel_id)
        return
    
    # Do not respond to chats with no text content
    if not 'text' in channel_post:
        return
    
    text = channel_post['text']
    
    # Finally, only respond to bot commands
    if not text.startswith('/'):
        return
    
    # Get the bot command and check the command is supported
    bot_command = text[1:].split(' ')[0].strip()
    bot_command_params = text[1:].replace(bot_command, '').strip()
    
    if not any(x==bot_command for x in SUPPORTED_COMMANDS):
        return
    
    if bot_command == 'raid':
        return bot_command_raid(bot_command_params, channel_id)
    
    msg.send_message('Unhandled bot command received in channel_post_handler:\n{0}'.format(channel_post), ADMIN_CHAT_ID)
    return

# Given a valid raid id number and a chat id:
# This method will return a formatted message displaying the raid details.
# It will also add the sent message id to the tracking table so updates can be sent.
def bot_command_raid(bot_command_params, chat_id):
    
    if not re.match('^\d+$', bot_command_params):
        return msg.send_message('That is not a valid raid id.', chat_id, None)
    
    raid_id = int(bot_command_params)
    raid_detail = raid.get_raid_by_id(raid_id)
    if not raid_detail:
        return msg.send_message('That is not a valid raid id.', chat_id, None)
    
    tracked_data = msg.decode_http_response_as_dict(msg.send_message(raid.format_raid_message(raid_detail), chat_id, 'MarkdownV2', True))
    raid.insert_message_tracking(bot_command_params, tracked_data['result']['chat']['id'], tracked_data['result']['message_id'])
    return