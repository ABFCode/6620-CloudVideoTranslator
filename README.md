# 6620-CloudVideoTranslator


# POC

- Story 1: As a User, I need to submit a YouTube video URL to a web interface so that I can initiate the translation process.
- Story 2: As the System, I need to fetch the existing English transcript from a YouTube video so that I have the source text for translation, avoiding the need for expensive/complicated audio processing.
- Story 3: As the System, I need to translate the fetched transcript into a target language using an AI or ML service. 
- Story 4: As a User, I need to be able to view or download the final translated text file so that I can use the output.


# MVP

- Story 5: As a User, I need to upload my own video file (e.g., .mp4) so that I can get translations for content that isn't on YouTube.
- Story 6: As the System, I need to automatically transcribe the audio from an uploaded video file so that I can create a source transcript from scratch.
- Story 7: As the System, I need to orchestrate the multi-step process of transcribing, translating, and formatting so that the workflow is reliable.
- Story 8: As a User, I need to receive the final translated subtitles in a standard format so that I can easily use them with standard video players.

# POC DIAGRAM

<img width="1828" height="698" alt="7-1(5)" src="https://github.com/user-attachments/assets/a346dd62-6264-4112-bf64-35b2427842d3" />


# MVP DIAGRAM

<img width="1710" height="684" alt="7-1(6)" src="https://github.com/user-attachments/assets/fa8b1a4d-e9ba-4729-a8ae-0705275bcbe8" />


## Explanations && Tradeoffs
### Youtube URL
Pros:
- No need to process video/audio (AWS Transcribe)
- Fast and cheap
- Simple
Cons:
- Only works for YouTube videos with transcripts
- No support for other video sources

### Direct Upload:
Pros:
- Works for any video

Cons:
- More expensive (Transcribe)
- More complex
- Slower
---
### AWS Translate
Pros:
- Easy AWS Integration

Cons: 
- Locked in to AWS Translate

### Google Translate
Pros:
- Broad Language Support
- Cheap/Free

Cons:
- Integration is more complex
- Not AWS-native

### Open-source/AI API
Pros:
- Price can be very low
- Customizeable
- Quality can be very high

Cons:
- Price can be very high
- More difficult to implement
- Quality can vary depending on implementation

--- 

### S3 Static Website
Pros:
- Cheap
- Scalable
- No server management

Cons:
- Limited to static content
- Needs API for dynamic actions

### Server
Pros:
- More dynamic
- More capable

Cons:
- More expensive
- More DevOps work/complexity
---

Diagrams generated using https://excalidraw.com/ text to diagram feature. 



---

## AI USAGE:

What am I missing in my tf file? Here is my goal.

Make me a .gitignore for this project.

How do I parse the JSON body from an AWS Lambda event from API Gateway?

My Lambda is failing with an 'Internal Server Error'. Here are the CloudWatch logs. 

