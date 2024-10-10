import asyncio

from pyrogram import Client, filters, types
from dotenv import load_dotenv
from pyrogram.handlers import MessageHandler

from config import Config
from utils import logger, setup_logger


load_dotenv()

app = Client('my_account')

setup_logger()

media_ids = set()

source_channels_ids = [channel['source_channel'] for channel in Config.CHANNELS]
print(source_channels_ids)


async def text_contain_banword(text: str, ban_words_list: list) -> bool:
    return any(word.lower() in text.lower() for word in ban_words_list)


async def change_channel_signature(text: str, channel_signatures: tuple, target_channel_signature: str) -> str:
    new_text = text
    for signature in channel_signatures:
        if signature in text:
            new_text = text.replace(signature, target_channel_signature)
    return new_text


async def new_media_post_in_channel(client: Client, message: types.Message):
    # Search proper channel
    await message.forward('me')
    matching_channel = next((channel for channel in Config.CHANNELS if channel['source_channel'] == message.chat.id), None)

    if not matching_channel:
        logger.info('A proper channel was not found')
        return

    # We do not copy post from channel if it is video circle
    if message.video_note:
        logger.info('Post is video circle')
        return

    if message.caption:
        if await text_contain_banword(message.caption, Config.BAN_WORDS):
            logger.info('Post contains ban word')
            return
        message.caption = await change_channel_signature(message.caption, Config.CHANNELS_SIGNATURES,
                                                         matching_channel['channel_signature'])

    if message.text:
        if await text_contain_banword(message.text, Config.BAN_WORDS):
            logger.info('Post contains ban word')
            return
        message.text = await change_channel_signature(message.text, Config.CHANNELS_SIGNATURES,
                                                      matching_channel['channel_signature'])

    if message.media_group_id:
        print('media')
        if message.media_group_id not in media_ids:
            media_ids.add(message.media_group_id)
            await app.copy_media_group(matching_channel['target_channel'], matching_channel['source_channel'],
                                       message.id, message.caption)
            await asyncio.sleep(3)
            media_ids.clear()

    else:
        await message.copy(matching_channel['target_channel'])

app.add_handler(MessageHandler(new_media_post_in_channel, filters.chat(source_channels_ids)))

if __name__ == '__main__':
    logger.info('Starting client...')
    app.run()
