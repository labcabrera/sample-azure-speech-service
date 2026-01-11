ffmpeg -i sample-01.flac -acodec pcm_s16le -ar 16000 -ac 1 sample-01.wav

ffmpeg -y -i sample-01.wav -ac 1 -ar 16000 -sample_fmt s16 sample-01-16k.wav

ffmpeg -y -i sample-01-16k.wav -af "silenceremove=start_periods=1:start_silence=0.5:start_threshold=-50dB" sample-01-trim.wav