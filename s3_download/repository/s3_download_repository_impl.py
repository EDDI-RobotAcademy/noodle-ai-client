import os

import boto3
from dotenv import load_dotenv

from s3_download.repository.s3_download_repository import S3DownloadRepository


load_dotenv()

class S3DownloadRepositoryImpl(S3DownloadRepository):
    __instance = None
    AWS_ACCESS_KEY_ID = os.getenv('AWS_ACCESS_KEY_ID')
    AWS_SECRET_ACCESS_KEY = os.getenv('AWS_SECRET_ACCESS_KEY')
    AWS_REGION_NAME = os.getenv('AWS_REGION')
    AWS_BUCKET_NAME = os.getenv('BUCKET_NAME')

    def __new__(cls):
        if cls.__instance is None:
            cls.__instance = super().__new__(cls)

        return cls.__instance

    @classmethod
    def getInstance(cls):
        if cls.__instance is None:
            cls.__instance = cls()

        return cls.__instance

    async def downloadFile(self, fileName, filePath):
        s3 = boto3.client(
            's3',
            aws_access_key_id=self.AWS_ACCESS_KEY_ID,
            aws_secret_access_key=self.AWS_SECRET_ACCESS_KEY,
            region_name=self.AWS_REGION_NAME
        )

        s3.download_file(self.AWS_BUCKET_NAME, fileName, filePath)

        print(f"File downloaded to {filePath}.")
