# Speech Server Python

Python example codes to connect to Cognigy speech server. The script spawns an arecord subprocess to access microphone and read the audio chunks.
After sending chunks and end the stream, it wait for reply from brain.
SocketIO wait will stop after an event come, so currently we listen only for reply from brain.

# Speech Server Events
* stt_chunk_start - Signal speech server that a new stream started
* stt_chunk - Send audio chunk to speech server stream
* stt_chunk_end - Signal speech server that the audio stream has ended

# Options
* servicename: STT service name, either google or watson.
* sample_rate: optional, speech audio sample rate. Default to 16000
* language: optional, speech audio spoken language. Default to "en-US"

example:
```python
'{"servicename": "google", "sample_rate": 22000}'
```
