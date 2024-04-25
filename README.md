### Python scripts used to process the videos for Secret Sleepover Society.
- `create-subtitles.py` takes a video, extracts the audio, chops it into segments, re-samples it, and transcribes it using WhisperX to create an SRT file.
- `parse-timestamps.py` uses a CSV file with marker data exported from Davinci Resolve and transforms the timecodes to easily paste them into the description of a YouTube video, into a comment, or set mid-roll ads.
