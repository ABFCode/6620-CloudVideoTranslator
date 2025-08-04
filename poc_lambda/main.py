# poc_lambda/main.py

import json
import os
import boto3
from youtube_transcript_api import YouTubeTranscriptApi
from youtube_transcript_api._errors import NoTranscriptFound, TranscriptsDisabled

# Initialize AWS clients outside the handler for performance
s3_client = boto3.client("s3")
translate_client = boto3.client("translate")

# Name of the S3 bucket to store results, passed via environment variable
RESULT_BUCKET = os.environ["RESULT_BUCKET"]


def get_video_id(url):
    """Parses a YouTube URL to get the video ID."""
    if "v=" in url:
        return url.split("v=")[1].split("&")[0]
    if "shorts/" in url:
        return url.split("shorts/")[1].split("?")[0]
    return None


def handler(event, context):
    print(f"Received event: {json.dumps(event)}")

    body = json.loads(event.get("body", "{}"))
    youtube_url = body.get("url")

    if not youtube_url:
        return {
            "statusCode": 400,
            "body": json.dumps({"message": "URL is required"}),
        }

    try:
        video_id = get_video_id(youtube_url)
        if not video_id:
            return {
                "statusCode": 400,
                "body": json.dumps({"message": "Could not parse YouTube video ID from URL."}),
            }

        # 1. CORRECTED: Instantiate the class and fetch the transcript
        # We specify English ('en') as the desired language.
        ytt_api = YouTubeTranscriptApi()
        fetched_transcript = ytt_api.fetch(video_id, languages=['en'])

        # 2. CORRECTED: Use snippet.text to access the text from each object
        transcript_text = " ".join([snippet['text'] for snippet in fetched_transcript])

        # 3. Translate the text using Amazon Translate
        translation_response = translate_client.translate_text(
            Text=transcript_text,
            SourceLanguageCode="en",
            TargetLanguageCode="es",
        )
        translated_text = translation_response["TranslatedText"]

        # 4. Save the translated text to S3
        # For the PoC, a .txt file is fine. We can use the SRTFormatter in the MVP.
        file_name = f"{video_id}-spanish.txt"
        s3_client.put_object(
            Bucket=RESULT_BUCKET, Key=file_name, Body=translated_text
        )

        return {
            "statusCode": 200,
            "body": json.dumps(
                {
                    "message": "Translation successful!",
                    "output_file": f"s3://{RESULT_BUCKET}/{file_name}",
                }
            ),
        }
    
    except (NoTranscriptFound, TranscriptsDisabled) as e:
        print(f"Transcript not available for video {video_id}: {e}")
        return {
            "statusCode": 404,
            "body": json.dumps({"message": f"Could not retrieve transcript for the video. It may not have an English transcript available or transcripts may be disabled."}),
        }
    except Exception as e:
        # This will catch other errors, like potential IP blocks.
        print(f"An unexpected error occurred: {e}")
        return {
            "statusCode": 500,
            "body": json.dumps({"message": f"An internal error occurred: {str(e)}"}),
        }