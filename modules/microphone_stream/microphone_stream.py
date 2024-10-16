import pyaudio
import queue
from typing import Generator

class MicrophoneStream:
    def __init__(self, rate: int, chunk: int, device_index: int) -> None:
        self._rate = rate
        self._chunk = chunk
        self._device_index = device_index
        self._buff = queue.Queue()
        self.closed = True

    def __enter__(self) -> 'MicrophoneStream':
        try:
            self._audio_interface = pyaudio.PyAudio()
            self._audio_stream = self._audio_interface.open(
                format=pyaudio.paInt16,
                channels=1,
                rate=self._rate,
                input=True,
                input_device_index=self._device_index,
                frames_per_buffer=self._chunk,
                stream_callback=self._fill_buffer,
            )
            self.closed = False
            return self
        except Exception as e:
            print(f"Error initializing audio stream: {e}")
            self.closed = True
            raise

    def __exit__(self, type, value, traceback) -> None:
        try:
            if self._audio_stream is not None:
                self._audio_stream.stop_stream()
                self._audio_stream.close()
            self._audio_interface.terminate()
        except Exception as e:
            print(f"Error closing audio stream: {e}")
        finally:
            self.closed = True
            self._buff.put(None)

    def _fill_buffer(self, in_data, frame_count, time_info, status_flags):
        try:
            self._buff.put(in_data)
        except Exception as e:
            print(f"Error filling buffer: {e}")
        return None, pyaudio.paContinue

    def generator(self) -> Generator[bytes, None, None]:
        try:
            while not self.closed:
                chunk = self._buff.get()
                if chunk is None:
                    return
                data = [chunk]

                while not self._buff.empty():
                    chunk = self._buff.get_nowait()
                    if chunk is None:
                        return
                    data.append(chunk)

                yield b"".join(data)
        except Exception as e:
            print(f"Error in audio generator: {e}")
            return
