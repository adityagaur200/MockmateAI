from faster_whisper import WhisperModel

model = WhisperModel("base")


def transcribe_audio(file_path):
    segments, _ = model.transcribe(file_path)

    transcript = " ".join([segment.text for segment in segments])

    return transcript