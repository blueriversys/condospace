import os

import boto3
import io
from botocore.exceptions import ClientError
from io import BytesIO
from PIL import Image
import logging



class AWS():
    def __init__(self, prefix, bucket_name, access_key, secret_access_key):
        self.prefix = prefix
        self.bucket_name = bucket_name
        self.access_key = access_key
        self.secret_access_key = secret_access_key
        self.s3 = boto3.client("s3", aws_access_key_id=access_key, aws_secret_access_key=secret_access_key,)


    """Get a list of files for a given customer Id"""
    def get_file_list(self, customer_id):
        objects_list = self.s3.list_objects_v2(Bucket=self.bucket_name, Prefix=f"{self.prefix}/{customer_id}").get("Contents")
        obj_list = []
        print(objects_list)
        for obj in objects_list:
            obj_name = obj["Key"]
            if obj_name.endswith("/"):
                continue
            obj_list.append(obj_name)
        return obj_list

    """Get a list of folders for a given customer_id + folder"""
    def get_folder_list(self, customer_id, folder):
        prefix = f"{self.prefix}/{customer_id}/{folder}"
        objects_list = self.s3.list_objects_v2(Bucket=self.bucket_name, Prefix=prefix).get("Contents")
        folder_dict = {}
        for obj in objects_list:
            obj_name = obj["Key"]
            folder_name = obj_name[:obj_name.rfind("/")] # search for the last occur of "/"
            folder_dict[folder_name] = ''
        return folder_dict.keys()


    """ Get a list of files for a given customer Id and folder. WARNING: list_objects_v2() returns frst 1000 objects only """
    def get_file_list_folder(self, customer_id, folder):
        objects_list = self.s3.list_objects_v2(Bucket=self.bucket_name, Prefix=f"{self.prefix}/{customer_id}/{folder}").get("Contents")
        if objects_list is None:
            return []
        obj_list = []
        for obj in objects_list:
            obj_name = obj["Key"]
            if obj_name == f"{self.prefix}/{customer_id}/":
                continue
            if not obj_name.startswith(f"{self.prefix}/{customer_id}/{folder}/"):
                continue
            obj_list.append(obj_name)
        return obj_list


    def is_file_found(self, file_path):
        full_path = f"{self.prefix}/{file_path}"
        response = self.s3.list_objects(Bucket=self.bucket_name, Prefix=full_path)
        if 'ETag' in str(response):
            return True
        else:
            return False


    def read_text_obj(self, file_path):
        full_path = f"{self.prefix}/{file_path}"
        response = self.s3.get_object(Bucket=self.bucket_name, Key=full_path)
        # Read the object’s content as text
        object_content = response["Body"].read().decode("utf-8")
        return object_content


    def read_binary_obj(self, file_path):
        response = self.s3.get_object(Bucket=self.bucket_name, Key=f"{self.prefix}/{file_path}")
        # Read the object’s content as text
        object_content = response["Body"].read()
        return BytesIO(object_content)


    def upload_text_obj(self, file_path, data):
         bin_data = BytesIO(bytes(data, 'utf-8'))
         full_path = f"{self.prefix}/{file_path}"
         self.s3.upload_fileobj(bin_data, self.bucket_name, full_path)


    def upload_binary_obj(self, file_path, data):
         bin_data = BytesIO(bytes(data))
         self.s3.upload_fileobj(bin_data, self.bucket_name, f"{self.prefix}/{file_path}")


    """Upload a file to an S3 bucket
      :param file_name: File to upload
      :param bucket: Bucket to upload to
      :param object_name: S3 object name. If not specified then file_name is used
      :return: True if file was uploaded, else False
    """
    def upload_file(self, file_path, object_name=None):
        # If S3 object_name was not specified, use file_name
        if object_name is None:
            object_name = os.path.basename(file_path)

        # Upload the file
        try:
            response = self.s3.upload_file(file_path, self.bucket_name, f"{self.prefix}/{object_name}")
        except ClientError as e:
            logging.error(e)
            return False
        return True


    def delete_object(self, file_path):
        try:
            response = self.s3.delete_object(Bucket=self.bucket_name, Key=f"{self.prefix}/{file_path}")
        except ClientError as e:
            logging.error(e)
            return False
        return True

    def delete_folder(self, folder_path):
        paginator = self.s3.get_paginator('list_objects_v2')
        # the trailing slash is important after folder_path to delete only that folder
        pages = paginator.paginate(Prefix=f"{self.prefix}/{folder_path}/", Bucket=self.bucket_name)

        delete_us = dict(Objects=[])
        for item in pages.search('Contents'):
            delete_us['Objects'].append(dict(Key=item['Key']))

            # flush once aws limit reached
            if len(delete_us['Objects']) >= 1000:
                self.s3.delete_objects(Bucket=self.bucket_name, Delete=delete_us)
                delete_us = dict(Objects=[])

        # flush rest
        if len(delete_us['Objects']):
            self.s3.delete_objects(Bucket=self.bucket_name, Delete=delete_us)

