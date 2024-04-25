from tkinter.filedialog import askopenfilename
from pathlib import Path
import os

base_file = askopenfilename()
audio_basename = Path(base_file).stem

from moviepy.editor import *

# Conver video file to mp3
video_file = VideoFileClip(base_file)
if not os.path.isdir('./audio_parser'):
    os.mkdir('./audio_parser')
video_file.audio.write_audiofile(f'./audio_parser/{audio_basename}.mp3')

# Vocals septaration adapted from https://colab.research.google.com/github/emmanuelinfante/SubtitlesEveryone/blob/main/SubtitlesEveryone.ipynb

import librosa
import soundfile as sf

# Re-sample audio file to 16k
def convert_frequency(input, output):
    signal, sample_rate = librosa.load(input)
    to_mono = librosa.to_mono(signal)
    new_sample_rate = 16000

    signal_out = librosa.resample(signal, orig_sr=sample_rate, target_sr=new_sample_rate)

    sf.write(output, signal_out, new_sample_rate)

input = (f'./audio_parser/{audio_basename}.mp3')
output = (f'./audio_parser/{audio_basename}_16_000.mp3')

print(">> Converting audio file to lower sample rate")
convert_frequency(input, output)

from pydub import AudioSegment
import demucs.separate
import shutil

max_duration = 30 * 60

audio_path = output
audio = AudioSegment.from_file(audio_path)
duration = librosa.get_duration(path=audio_path)

# Create necessary directory for file storage
if not os.path.isdir('./audio_parser/segments'):
    os.mkdir('./audio_parser/segments')

# If file is longer than the set max lenght it is divided into segments and processed
if duration > max_duration: 
    num_segments = int(duration // max_duration) + 1

    # Processing every segment and storing it
    for i in range(num_segments):
        start_time = i * max_duration
        end_time = (i + 1) * max_duration if (i + 1) * max_duration < duration else duration
        segment = audio[start_time * 1000:end_time * 1000]
        segment_path = f'./audio_parser/segments/{audio_basename}_segment{i}{os.path.splitext(audio_path)[1]}'
        segment.export(segment_path, format='wav')

        demucs.separate.main(["-d", "cuda", "--mp3", "--mp3-bitrate", "96", "--two-stems=vocals", "-n", "hdemucs_mmi", segment_path, "--out", "./audio_parser/segments", "--mp3-preset", "7"])
    
    folder_path = './audio_parser/segments/hdemucs_mmi'

    #Combining all the segments into a single mp3 file
    folders = [f for f in os.listdir(folder_path) if os.path.isdir(os.path.join(folder_path, f))]
    # Lists segmented folders assuming the last character is their index number
    folders.sort(key=lambda x: int(x.rsplit('segment', 1)[-1]))
    # Creating empty audio object to store segments within it
    combined = AudioSegment.empty()

    for folder in folders:
        vocals_file = os.path.join(folder_path, folder, 'vocals.mp3')
        if os.path.isfile(vocals_file):
            audio_segment = AudioSegment.from_mp3(vocals_file)
            combined += audio_segment
    
    combined.export(f'./audio_parser/{audio_basename}_vocals.mp3', format='mp3')
    shutil.rmtree('./audio_parser/segments/hdemucs_mmi')

# If the file is shorter than the set max lenght then process directly 
else:
    demucs.separate.main(["-d", "cuda", "--mp3", "--mp3-bitrate", "96", "--two-stems=vocals", "-n", "hdemucs_mmi", audio_path, "--out", "./audio_parser/segments", "--mp3-preset", "7"])
    
    output_path = f'./clean_vocals/audio_16_000/{audio_basename}_vocals.mp3'
    if os.path.isfile(output_path):
        shutil.move(output_path, f'./audio_parser/{audio_basename}_vocals.mp3')

import gc
import torch

# Garbage collection
gc.collect(); torch.cuda.empty_cache()

MODEL_OPTIONS = {
    "whisper_arch": "large-v3",
    "device": "cuda",
    "compute_type": "float16",
    "language": "en"
}

TRANS_OPTS =     {
"temperatures": [
        0.0,
        0.2,
        0.4,
        0.6000000000000001,
        0.8,
        1.0
    ],
    "best_of": 5,
    "beam_size": 5,
    "patience": 2,
    "initial_prompt": None,
    "condition_on_previous_text": True,
    "compression_ratio_threshold": 2.4,
    "log_prob_threshold": -1.0,
    "no_speech_threshold": 0.6,
    "word_timestamps": False,
    "prepend_punctuations": "\"'“¿([{-",
    "append_punctuations": "\"'.。,,!?:：”)]}、",
}

BATCH_SIZE = 12
CHUNK_SIZE = 8

source = f'./audio_parser/{audio_basename}_vocals.mp3'

import whisperx

# Loading transcription model
model = whisperx.load_model(**MODEL_OPTIONS, asr_options=TRANS_OPTS)

audio = whisperx.load_audio(source)
print(f'>> Transcribing {audio_basename}...')
result = model.transcribe(source, batch_size=BATCH_SIZE, chunk_size=CHUNK_SIZE)

# Extra garbage collection
gc.collect(); torch.cuda.empty_cache(); del model

# # Loading alignment model and processing segments
model_a, metadata = whisperx.load_align_model(language_code=result['language'], device=MODEL_OPTIONS["device"])
print(">> Aligning segments")
result_aligned = whisperx.align(result["segments"], model_a, metadata, source, MODEL_OPTIONS["device"], return_char_alignments=False)

# Setting transcription language for sentence formation
result_aligned['language'] = MODEL_OPTIONS["language"]

# Writing to disk
from whisperx.utils import WriteSRT
print(">> Writing SRT file")
srt_filename = (audio_basename + ".srt")
with open(srt_filename, "w", encoding="utf-8") as srt:
    writesrt=WriteSRT(".")  #output file directory
    writesrt.write_result(result=result_aligned, file=srt,options={"max_line_width":None,"max_line_count":2,"highlight_words":False,"chunk_size":10})

# Removing segmented and re-sampled files 
shutil.rmtree('./audio_parser')