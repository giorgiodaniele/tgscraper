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

def ensure_output_dir() -> Path:
    folder = Path(__file__).parent / ".." / "data"
    folder.mkdir(parents=True, exist_ok=True)
    return folder

async def action(client: telethon.TelegramClient, target, chat_name):


     folder = ensure_output_dir()
     
     # Selects all messages sent in a chat within a given time 
     # range (if specified) and saves the results to disk. The 
     # selected messages are stored in the ../data/ directory, 
     # using a timestamp to indicate when the data was saved

     records = []

     ts = parse_utc(TS)
     te = parse_utc(TE)

     async for m in client.iter_messages(
          target,
          offset_date=te if te else None,
     ):
          if ts and m.date < ts:
               break

          if ts and te:
               if ts <= m.date <= te:
                    records.append(m)

     # Use CSV as data format for data...
     data = pandas.DataFrame(
          [
               {
                    "id"        : r.id,
                    "username"  : r.username,
                    "first_name": r.first_name,
                    "last_name" : r.last_name,
                    "phone"     : r.phone,
                    "bot"       : r.bot,
               }
               for r in records
          ],
          columns=[
               "id",
               "username",
               "first_name",
               "last_name",
               "phone",
               "bot",
          ],
     )

     # ... and save on disk
     path = folder / f"{chat_name}_users_{ts}_{te}.csv"
     data.to_csv(path, index=False)

     return len(data)

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
     res = await action(client=client, target=target, chat_name=TELEGRAM_CHAT_NAME.replace(" ", "_"))
     print(f"[info]: {res} records been exported")


     # End connection
     await client.disconnect()


if __name__ == "__main__":
    asyncio.run(main())
