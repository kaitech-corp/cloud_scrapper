import datetime
import json
from google.cloud import storage
from google.cloud.exceptions import GoogleCloudError


class Storage:
    def store(self, json_obj):
        try:
            # Initialize the Google Cloud Storage client
            storage_client = storage.Client()

            folder_name = "cloudData"
            bucket_name = "api-project-371618.appspot.com"
            bucket = storage_client.get_bucket(bucket_name)

            # Serialize the JSON object to a string
            json_str = json.dumps(json_obj)

            # Upload the JSON string to the specified location in the bucket
            id_str = str(datetime.datetime.now())
            print(id_str)
            blob = bucket.blob(f"{folder_name}/{id_str}.json")
            blob.upload_from_string(json_str)

            print(
                f"File {id_str} uploaded to {bucket_name}/{folder_name}")
        except GoogleCloudError as e:
            # Handle Google Cloud Storage-related errors
            print(f"Google Cloud Storage Error: {e}")
        except Exception as e:
            # Handle other exceptions
            print(f"Error: {e}")

