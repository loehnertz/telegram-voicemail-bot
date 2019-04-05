import json
import logging
import os
from datetime import datetime
from pathlib import Path

from telegram.ext import Updater, MessageHandler, Filters

from backend.uploader import Uploader

logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO)
logger = logging.getLogger(__name__)


class Bot:
    # General
    CONFIG_PATH = '../config.json'

    # Configuration keys
    ACCESS_KEY_KEY = 'accessKey'
    ADMIN_USER_KEY = 'adminUserId'
    BOT_TOKEN_KEY = 'botToken'
    BUCKET_NAME_KEY = 'bucketName'
    ENDPOINT_URL_KEY = 'endpointUrl'
    MESSAGE_SUCCESS_KEY = 'messageSuccess'
    REGION_NAME_KEY = 'regionName'
    SECRET_KEY = 'secret'
    UPLOAD_PATH_KEY = 'uploadPath'

    def __init__(self):
        self.config = self._load_config()
        self.uploader = self._init_uploader()
        self.bot_token = self._retrieve_bot_token()
        self.message_success = self._retrieve_message_success()
        self.admin_user_id = self.config.get(self.ADMIN_USER_KEY)

    def start(self):
        logger.info('Bot back-end is running...')

        updater = Updater(self.bot_token)
        dispatcher = updater.dispatcher

        dispatcher.add_handler(MessageHandler(Filters.voice, self.voicemail_handler))

        updater.start_polling()
        updater.idle()

    def voicemail_handler(self, bot, context):
        file = bot.getFile(context.message.voice.file_id)

        full_name = context.effective_user.full_name
        username = context.effective_user.name
        file_path = f'/tmp/{full_name} ({username}) {datetime.now()}.ogg'

        if self.admin_user_id:
            bot.send_voice(
                chat_id=self.admin_user_id,
                voice=file.file_id,
                caption=f'A new voicemail arrived by: {full_name} ({username})',
            )

        file.download(
            custom_path=file_path,
        )
        self.uploader.upload_file_privately(
            file_location=file_path,
            upload_path=self.upload_path,
            bucket=self.bucket_name,
        )
        self.delete_file(file_path)

        bot.send_message(chat_id=context.message.chat_id, text=self.message_success)

        logger.info(f"Received and saved incoming voicemail at file path '{file_path}'")

    def _load_config(self):
        with open(os.path.abspath(Path(self.CONFIG_PATH).resolve()), 'r') as file:
            config = json.loads(file.read())

            if not config:
                raise ImportError(f"A configuration file could not be found at the default path '{self.CONFIG_PATH}'")

            return config

    def _init_uploader(self):
        access_key = self.config.get(self.ACCESS_KEY_KEY)
        bucket_name = self.config.get(self.BUCKET_NAME_KEY)
        endpoint_url = self.config.get(self.ENDPOINT_URL_KEY)
        region_name = self.config.get(self.REGION_NAME_KEY)
        secret = self.config.get(self.SECRET_KEY)
        upload_path = self.config.get(self.UPLOAD_PATH_KEY)

        if not all([access_key, bucket_name, endpoint_url, region_name, secret, upload_path]):
            raise ImportError('Not every configuration option could be found; check the `config.json` file')

        self.bucket_name = bucket_name
        self.upload_path = upload_path

        return Uploader(region_name=region_name, endpoint_url=endpoint_url, access_key=access_key, secret=secret)

    def _retrieve_bot_token(self):
        bot_token = self.config.get(self.BOT_TOKEN_KEY)

        if not bot_token:
            raise ImportError('No bot token was supplied')
        else:
            return bot_token

    def _retrieve_message_success(self):
        message_success = self.config.get(self.MESSAGE_SUCCESS_KEY)

        if not message_success:
            raise ImportError('No success message was supplied')
        else:
            return message_success

    @staticmethod
    def delete_file(file_name):
        os.remove(file_name)


if __name__ == '__main__':
    try:
        Bot().start()
    except Exception as execption:
        logger.error(f"An exception was raised during the execution: {repr(execption)}")
        exit()
