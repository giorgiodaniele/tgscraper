# tgscraper

**tgscraper** allows you to authenticate to the Telegram servers as a user and operate on public chats and groups.

The tool supports exporting messages, users, and media (such as photos), as well as deleting messages sent by the authenticated user.

It is intended for monitoring and controlling one’s own activity in public chats, and for collecting structured datasets from public groups and channels for analysis, auditing, or archival purposes.


## Features

Currently, the tool supports both local data storage and optional Azure-based redundancy.

Data generated in `/data/messages`, `/data/users`, and `/data/photos` is saved locally and, when Azure integration is enabled, also uploaded to a privately owned Azure Blob Storage container.

## Configuration

The tool requires a `.env` file containing the following environment variables:

```bash
# Telegram credentials
TELEGRAM_API_ID=
TELEGRAM_API_HASH=

# Optional: Azure Blob Storage backup
AZURE_ENABLED=
AZURE_STORAGE_ACCOUNT=
AZURE_STORAGE_ACCOUNT_BLOB=
```


## Requirements

- Python 3.10 or newer  
- A Telegram account  
- Telegram API credentials (API ID and API hash)

You can obtain your Telegram API ID and API hash by creating an application at: https://my.telegram.org, **API development tools**


## Azure Configuration
Within `azure/` folder, terraform scripts are provided to spawn a storage account with a BLOB (Binary Large OBject) storage inside. In order to allocate storage, run:

```bash
terraform init
terraform apply -auto-approve
```

Before using Azure as a backup site, ensure that the required access permissions and credentials are properly configured so the application can authenticate and write to the Blob Storage.