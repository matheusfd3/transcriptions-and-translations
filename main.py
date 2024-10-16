import threading
import time
import numpy
import queue
import whisper

from modules.microphone_stream.microphone_stream import MicrophoneStream

RATE = 16000
CHUNK = int(RATE * 0.1) # 100ms

MAX_CHUNK_BUFFER = (3000 / 100) # 3 segundos de chunks
MAX_MAIN_TRANSCRIPT_LENGTH = 500

audio_buffer = queue.Queue(maxsize=MAX_CHUNK_BUFFER)

main_transcript = ""
last_chunk_transcript = ""

def refactoring_main_transcription(main_transcript, last_chunk_transcript, current_chunk_transcript):
    biggest_match = ""
    
    for i in range(len(last_chunk_transcript)):
        for j in range(i + 1, len(last_chunk_transcript) + 1):
            subsequence = last_chunk_transcript[i:j]

            if subsequence in current_chunk_transcript and len(subsequence) > len(biggest_match):
                biggest_match = subsequence
    
    if biggest_match:
        current_chunk_transcription_result = biggest_match + current_chunk_transcript.rsplit(biggest_match, 1)[1]

        return main_transcript.rsplit(biggest_match, 1)[0] + current_chunk_transcription_result
    else:
        return main_transcript + current_chunk_transcript

def fix_transcription_length(transcription: str) -> str:
    if len(transcription) > MAX_MAIN_TRANSCRIPT_LENGTH:
        return transcription[-MAX_MAIN_TRANSCRIPT_LENGTH:]
    return transcription

def process_transcription(model) -> None:
    global main_transcript
    global last_chunk_transcript
    while True:
        if audio_buffer.full():
            audio_buffer_join = b''.join(list(audio_buffer.queue))

            audio_array = numpy.frombuffer(audio_buffer_join, numpy.int16)

            mean_abs_value = numpy.abs(audio_array).mean()

            if mean_abs_value > 0:
                audio_array = audio_array.astype(numpy.float32) / 32768.0

                result = model.transcribe(audio_array, condition_on_previous_text = False)

                current_chunk_transcript = result['text']

                main_transcript = fix_transcription_length(refactoring_main_transcription(main_transcript, last_chunk_transcript, current_chunk_transcript))

                last_chunk_transcript = current_chunk_transcript
            else:
                print("Nenhuma fala detectada...")

        time.sleep(0.3)

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
    model = whisper.load_model("tiny.en")

    audio_thread = threading.Thread(target=process_audio)
    audio_thread.start()

    transcription_thread = threading.Thread(target=process_transcription, args=(model, ))
    transcription_thread.start()

if __name__ == "__main__":
    main()