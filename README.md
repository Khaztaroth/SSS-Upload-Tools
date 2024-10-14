### Python scripts used to process the videos for Secret Sleepover Society.
- `create-subtitles.py` takes a video, extracts the audio, chops it into segments, re-samples it, and transcribes it using WhisperX to create an SRT file.
- `parse-timestamps.py` uses a CSV file with marker data exported from Davinci Resolve and transforms the timecodes to easily paste them into the description of a YouTube video, into a comment, or set mid-roll ads.


- For the WhisperX files I use `https://github.com/Hasan-Naseer/whisperX` which includes more recent Faster-Whisper version compativility as well as support for `Distil` models 
    Set up a conda environment with `conda create --name whisperx python=3.10` (name can be anything) activate it, then install the whisper fork with `pip install git+https://github.com/Hasan-Naseer/whisperX.git` 
    You will also need `moviepy` `librosa` `soundfile` `pydub` & `demucs`