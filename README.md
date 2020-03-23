# Parser for standupstore.ru

Parser, that periodically checks new events on [standupstore.ru](https://standupstore.ru/) and posts notifications to telegram channel.

### Quick start
1. Install git, docker and docker-compose
2. Clone repo
    ```sh
    git clone git@github.com:dvabidonamoloka/standupstoreparser.git
    ```
3. Add settings.py to `susp/` folder by the following template:
    ```python
    import telegram
    TOKEN = 'your_telegram_bot_token'
    REQPROXY = telegram.utils.request.Request(  # proxy settings
        proxy_url='proxy_url',
        urllib3_proxy_kwargs={'some': 'kwargs'}
    )
    CHAT_ID = '@your_telegram_channel_name'
    EXCEPTIONS_EMAIL_TO = 'email'  # email to which you will receive error logs
    EXCEPTIONS_EMAIL_FROM = 'email'  # email from which error logs will be sent
    SMPT_SERVER = 'smpt_server_adress'
    SMPT_PORT = 'smpt_server_port'
    SMPT_PASSWORD = 'password of email from which error logs will be sent'
    ```
    Note, that telegram bot has to be the admin of the channel
4. Run containers with docker-compose
    ```sh
    docker-compose up -d
    ```


### Run the app in docker
Running prod version
```sh
docker-compose up -d
```
Running dev version, which has port forwarding
```sh
docker-compose -f docker-compose.yml -f docker-compose.dev.yml up -d
```
Rebuild app image before running container:
```sh
docker-compose -f docker-compose.yml -f docker-compose.dev.yml up -d --build --force-recreate
```
Running only mongo container
```sh
docker-compose -f docker-compose.yml -f docker-compose.dev.yml up -d mongo
```
