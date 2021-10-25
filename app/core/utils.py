import os
import re
import boto3
from botocore.config import Config
from botocore.exceptions import ClientError

from app import settings


regex = re.compile(r'(\d+)$')


def increment_reference(reference: str):
    previous_count = regex.findall(reference)[0]
    next_count = str(int(previous_count) + 1).zfill(len(previous_count))
    return re.sub(regex, next_count, reference)


def create_presigned_url(object_name, expiration=3600):
    """Generate a presigned URL to share an S3 object

    :param bucket_name: string
    :param object_name: string
    :param expiration: Time in seconds for the presigned URL to remain valid
    :return: Presigned URL as string. If error, returns None.
    """

    # Generate a presigned URL for the S3 object
    config = Config(
        region_name='eu-west-3',
        signature_version='s3v4',
        retries={
            'max_attempts': 10,
        },
        s3={'addressing_style': 'path'})
    key_id = settings.AWS_ACCESS_KEY_ID
    secret_key = settings.AWS_SECRET_ACCESS_KEY
    s3_client = boto3.client('s3',
                             aws_access_key_id=key_id,
                             aws_secret_access_key=secret_key,
                             config=config)

    params = {'Bucket': settings.AWS_BUCKET_NAME,
              'Key': object_name}
    print(params)
    try:
        response = s3_client.generate_presigned_url('get_object',
                                                    Params=params,
                                                    ExpiresIn=expiration)
    except ClientError:
        return None

    # The response contains the presigned URL
    return response


def upload_file(file_name, object_name=None):
    """Upload a file to an S3 bucket

    :param file_name: File to upload
    :param bucket: Bucket to upload to
    :param object_name: S3 object name. If not specified then file_name is used
    :return: True if file was uploaded, else False
    """

    # If S3 object_name was not specified, use file_name
    if object_name is None:
        object_name = os.path.basename(file_name)

    # Upload the file
    key_id = settings.AWS_ACCESS_KEY_ID
    secret_key = settings.AWS_SECRET_ACCESS_KEY
    s3_client = boto3.client('s3',
                             aws_access_key_id=key_id,
                             aws_secret_access_key=secret_key)
    try:
        s3_client.upload_file(file_name, settings.AWS_BUCKET_NAME, object_name)
    except ClientError:
        return False
    return True
