from pathlib            import Path
from azure.identity     import DefaultAzureCredential
from azure.storage.blob import BlobServiceClient


def container(
    azure_storage_account   : str,
    azure_storage_container : str,
):
     credential = DefaultAzureCredential()
     service    = BlobServiceClient(
         account_url=azure_storage_account,
         credential=credential,
     )

     # Return a ContainerClient used to interact with a specific
     # Azure Blob Storage container. All blobs are created and
     # managed within a container.

     return service.get_container_client(azure_storage_container)


def upload_blob(storage, path: Path) -> None:

     if storage is None:
          return

     with path.open("rb") as f:
          storage.upload_blob(
               name=path.name,
               data=f,
               overwrite=True,
          )
