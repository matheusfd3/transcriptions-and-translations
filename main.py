import threading
import time
import numpy
import queue

from modules.microphone_stream.microphone_stream import MicrophoneStream

RATE = 16000
CHUNK = int(RATE * 0.1) # 100ms

MAX_CHUNK_BUFFER = (3000 / 100) # 3 segundos de chunks

audio_buffer = queue.Queue(maxsize=MAX_CHUNK_BUFFER)

def microphone_stream_generator(device_index) -> None:
    with MicrophoneStream(RATE, CHUNK, device_index) as stream:
        for audio_data in stream.generator():
            if audio_buffer.full():
                audio_buffer.get()

            audio_buffer.put(audio_data)

def process_audio() -> None:
    while True:
        microphone_stream_generator(15)
        time.sleep(0.1)

def main() -> None:
    audio_thread = threading.Thread(target=process_audio)
    audio_thread.start()

if __name__ == "__main__":
    main()