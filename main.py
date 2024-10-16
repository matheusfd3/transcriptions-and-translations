import threading
import time
import numpy
import queue
import whisper
from deep_translator import GoogleTranslator
import tkinter
import pyaudio

from modules.microphone_stream.microphone_stream import MicrophoneStream
from modules.graphical_user_interface.graphical_user_interface import GraphicalUserInterface

RATE = 16000
CHUNK = int(RATE * 0.1) # 100ms

MAX_CHUNK_BUFFER = (3000 / 100) # 3 segundos de chunks
MAX_MAIN_TRANSCRIPT_LENGTH = 500

audio_buffer = queue.Queue(maxsize=MAX_CHUNK_BUFFER)

main_transcript = ""
last_chunk_transcript = ""

def process_translation(gui, translator) -> None:
    global main_transcript
    last_main_transcript_used = ""
    while True:
        if main_transcript != last_main_transcript_used and gui.is_running_transcription_and_translation:
            translated = translator.translate(main_transcript)
            gui.set_text_area_translation(translated)
            last_main_transcript_used = main_transcript
        time.sleep(0.1)

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

def process_transcription(gui, model) -> None:
    global main_transcript
    global last_chunk_transcript
    while True:
        if audio_buffer.full() and gui.is_running_transcription_and_translation:
            audio_buffer_join = b''.join(list(audio_buffer.queue))

            audio_array = numpy.frombuffer(audio_buffer_join, numpy.int16)

            mean_abs_value = numpy.abs(audio_array).mean()

            if mean_abs_value > 0:
                audio_array = audio_array.astype(numpy.float32) / 32768.0

                result = model.transcribe(audio_array, condition_on_previous_text = False)

                current_chunk_transcript = result['text']

                main_transcript = fix_transcription_length(refactoring_main_transcription(main_transcript, last_chunk_transcript, current_chunk_transcript))

                gui.set_text_area_transcription(main_transcript)

                last_chunk_transcript = current_chunk_transcript
            else:
                print("Nenhuma fala detectada...")

        time.sleep(0.3)

def microphone_stream_generator(gui, device_index) -> None:
    with MicrophoneStream(RATE, CHUNK, device_index) as stream:
        for audio_data in stream.generator():
            if audio_buffer.full():
                audio_buffer.get()

            audio_buffer.put(audio_data)
            
            audio_array = numpy.frombuffer(audio_data, numpy.int16)

            mean_abs_value = numpy.abs(audio_array).mean() * 3

            normalized_mean_abs_value = (mean_abs_value / 32767) * 100

            gui.update_progress_bar(normalized_mean_abs_value)

            if gui.device_was_updated:
                gui.device_was_updated = False
                break

def process_audio(gui) -> None:
    while True:
        device_index = gui.get_device_index()
        microphone_stream_generator(gui, device_index)
        time.sleep(0.1)

def test_device_sample_rate(device_index, rate):
    audio_interface = pyaudio.PyAudio()
    try:
        stream = audio_interface.open(
            rate=rate,
            channels=1,
            format=pyaudio.paInt16,
            input=True,
            input_device_index=device_index
        )
        stream.close()
        return True
    except:
        return False

def list_devices() -> list:
    audio_interface = pyaudio.PyAudio()
    supported_devices = []
    for i in range(audio_interface.get_device_count()):
        device_info = audio_interface.get_device_info_by_index(i)
        device_name = device_info['name']
        device_index = device_info['index']
        device_max_input_channels = device_info['maxInputChannels']
        if device_max_input_channels > 0:
            if test_device_sample_rate(device_index, RATE):
                supported_devices.append(f"{device_name} (INDEX:{device_index})")
    
    audio_interface.terminate()
    return supported_devices

def main() -> None:
    model = whisper.load_model("tiny.en")
    translator = GoogleTranslator(source='en', target='pt')

    root = tkinter.Tk()
    device_options = list_devices()
    gui = GraphicalUserInterface(root, device_options)

    audio_thread = threading.Thread(target=process_audio,  args=(gui, ))
    audio_thread.start()

    transcription_thread = threading.Thread(target=process_transcription, args=(gui, model))
    transcription_thread.start()

    translation_thread = threading.Thread(target=process_translation, args=(gui, translator))
    translation_thread.start()

    root.mainloop()

if __name__ == "__main__":
    main()
    