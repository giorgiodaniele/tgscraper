import asyncio
import os
import sys
import telethon
import datetime
import dotenv
import pandas
from   pathlib import Path

dotenv.load_dotenv()

TELEGRAM_API_ID    = os.environ["TELEGRAM_API_ID"]
TELEGRAM_API_HASH  = os.environ["TELEGRAM_API_HASH"]
TELEGRAM_CHAT_NAME = os.environ["TELEGRAM_CHAT_NAME"]
TS                 = os.environ["TS"]
TE                 = os.environ["TE"]


def parse_utc(value):
     if not value:
          return None
     return datetime.datetime.strptime(value, "%Y-%m-%d").replace(tzinfo=datetime.timezone.utc)

async def action(client: telethon.TelegramClient, target, chat_name):

     # Selects all messages sent in a chat within a given time 
     # range (if specified) and delete them

     ts = parse_utc(TS)
     te = parse_utc(TE)

     async for msg in client.iter_messages(
          target, 
          from_user="me", 
          offset_date=te if te else None
     ):
          if ts and msg.date < ts:
               break

          found += 1
          batch.append(msg.id)

          if len(batch) == 100:
               try:
                    await client.delete_messages(target, batch)
                    deleted += len(batch)
               except Exception:
                    pass
               batch = []
               await asyncio.sleep(0.7)

     if batch:
          try:
               await client.delete_messages(target, batch)
               deleted += len(batch)
          except Exception:
               pass

async def main():
     
     # Generate a new client
     session = "telegram_client_session"
     client  =  telethon.TelegramClient(session, api_id=TELEGRAM_API_ID, api_hash=TELEGRAM_API_HASH)

     # Start a new connection
     await client.start()

     # Search for the chat
     chats  = await client.get_dialogs()
     target = None
     for chat in chats:
          if chat.name == TELEGRAM_CHAT_NAME:
               target = chat

     if target == None:
          sys.exit(-100)

     # Logic goes here...
     await action(client=client, target=target, chat_name=TELEGRAM_CHAT_NAME.replace(" ", "_"))

     # End connection
     await client.disconnect()


if __name__ == "__main__":
    asyncio.run(main())
