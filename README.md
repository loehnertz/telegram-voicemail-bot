# telegram-voicemail-bot
A telegram bot back-end that saves incoming voice and text messages into a hosting space


## Features

- Receive voicemails and text messages from telegram users
- Save the incoming messages into S3-compatible storage
- Perfect for podcasters who want to offer a voicemail option to their listeners


## Motivation

I produce a podcast myself in German ([shameless plug][podcast-as-a-service]),
and I wanted to incorporate voicemails of our listeners into the show.
Since I didn't found a good solution similar to `Google Voice` (which isn't available outside of the US),
I quickly coded one myself.


## Configuration

First, duplicate the `config.template.json` to a file with the name `config.json`.    
Next, populate the `config.json` file with your information.

### Remarks

- `accessKey`: Look up the documentation of your hosting provider regarding AWS S3 API compatibility.
  In `AWS S3`, it is called `aws_access_key_id`.
- `secret`: Look up the documentation of your hosting provider regarding AWS S3 API compatibility.
  In `AWS S3`, it is called `aws_secret_access_key`.
- `uploadPath`: Corresponds to the path in the bucket of the hosting provider
  as a relative path from the `bucketName` root.
- `endpointUrl`, `regionName`: Have to be looked up in the hosting providers documentation, this is necessary
  as per AWS S3 API. Consequently, if your provider does not offer these values, it probably is not AWS S3 API compliant.
- `adminUserId`: This field is optional but can be filled with any Telegram user ID. If set, the bot will
  additionally send every message to an admin user with that ID.
- `textHandlerActive` & `voicemailHandlerActive`: Can be respectively used to activate or deactivate the handling
  of both, incoming text and voice messages.


## Usage

You probably want to run this program as a server process as it needs to be available at all times.
After creating a new Telegram bot as described [here][botfather], you should've received a bot token
such as this example one: `110201543:AAHdqTcvCH1vGWJxfSeofSAs0K5PALDsaw`.

Next, fill this into the `config.json` file together with all of the other settings.

### Installation

You need a server to run this program. First make sure, that `python3` is installed on the system.

Clone this repository into a desired path:
```sh
cd /var/opt/ && git clone https://github.com/loehnertz/telegram-voicemail-bot.git
```

Next, the dependencies of this program need to be installed into the system:
```sh
cd /var/opt/telegram-voicemail-bot && pip install -r requirements.txt
```
You can of course alternatively use a `virtualenv` and change the paths in the following configuration file accordingly.

If you are using Linux, I can recommend `supervisord` for the execution.
On Ubuntu, install `supervisord` with:
```sh
sudo apt install supervisor
```

As the next step, you need to create a new configuration file for the program. Here is an example one:
```
[program:telegram-voicemail-bot]
command=/usr/bin/python3 /var/opt/telegram-voicemail-bot/backend/bot.py
directory=/var/opt/telegram-voicemail-bot/backend/
autostart=true
autorestart=true
startretries=3
stderr_logfile=/var/opt/telegram-voicemail-bot/err.log
stdout_logfile=/var/opt/telegram-voicemail-bot/out.log
user=root  # FILL IN A PROPER UNIX USER HERE PLEASE
```
Save this to `/etc/supervisor/conf.d/telegram-voicemail-bot.conf`. Note that you of course need to change
all of the paths in the file in case you cloned the repository to another path initially.

Enable and start `supervisord` with:
```sh
sudo service supervisor enable && sudo service supervisor restart
```

Next, reload the `supervisord` configuration files:
```sh
sudo supervisorctl reread && sudo supervisorctl update
```

Finally, start the program with:
```sh
sudo supervisorctl restart telegram-voicemail-bot
```

Additionally, both normal as well as error logs are available in the paths set in the `telegram-voicemail-bot.conf` file.


[botfather]: https://core.telegram.org/bots#6-botfather
[podcast-as-a-service]: https://podcast-as-a-service.fm
