import asyncio
import os
import sys
import telethon
import datetime
import dotenv
import pandas
import azure_integration
from   pathlib import Path

dotenv.load_dotenv()

# Core
TELEGRAM_API_ID    = os.environ["TELEGRAM_API_ID"]
TELEGRAM_API_HASH  = os.environ["TELEGRAM_API_HASH"]
TELEGRAM_CHAT_NAME = os.environ["TELEGRAM_CHAT_NAME"]
TS                 = os.environ["TS"]
TE                 = os.environ["TE"]

# Azure
AZURE_ENABLED              = os.environ["AZURE_ENABLED"]
AZURE_STORAGE_ACCOUNT      = os.environ["AZURE_STORAGE_ACCOUNT"]
AZURE_STORAGE_ACCOUNT_BLOB = os.environ["AZURE_STORAGE_ACCOUNT_BLOB"]

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
                    "id"    : r.id,
                    "date"  : r.date,
                    "text"  : r.message,
                    "sender": r.from_id.user_id,
               }
               for r in records if r.message
          ],
          columns=["id", "date", "text", "sender"],
     )

     # ... and save on disk
     path = folder / f"{chat_name}_messages.csv"
     data.to_csv(path, index=False)


     if AZURE_ENABLED and AZURE_ENABLED == "true":
          container = azure_integration.container(AZURE_STORAGE_ACCOUNT, AZURE_STORAGE_ACCOUNT_BLOB)
          azure_integration.upload_blob(container, path)

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
