import json
import os
import boto3


s3_client = boto3.client("s3")
translate_client = boto3.client("translate")
RESULT_BUCKET = os.environ["RESULT_BUCKET"]

def handler(event, context):
    print(f"Received event: {json.dumps(event)}")

    try:
        video_id = "mock-video-id"
        transcript_text = (
            "Hello and welcome to this demonstration. "
            "The proof of concept discovered that YouTube blocks requests from cloud providers. "
            "Therefore, we are now testing the rest of our pipeline, "
            "from translation to S3 storage, with this sample text."
        )
        translation_response = translate_client.translate_text(
            Text=transcript_text,
            SourceLanguageCode="en",
            TargetLanguageCode="es",
        )
        translated_text = translation_response["TranslatedText"]

        file_name = f"{video_id}-spanish.txt"
        s3_client.put_object(
            Bucket=RESULT_BUCKET, Key=file_name, Body=translated_text
        )

        return {
            "statusCode": 200,
            "body": json.dumps(
                {
                    "message": "Mock translation successful!",
                    "output_file": f"s3://{RESULT_BUCKET}/{file_name}",
                }
            ),
        }
    except Exception as e:
        print(f"An unexpected error occurred: {e}")
        return {
            "statusCode": 500,
            "body": json.dumps({"message": f"An internal error occurred: {str(e)}"}),
        }