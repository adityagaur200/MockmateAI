from faster_whisper import WhisperModel

model = WhisperModel(
    "base",
    device="cpu",          
    compute_type="int8"    
)


def transcribe_audio(file_path):
    segments, _ = model.transcribe(file_path, 
                                   beam_size=5,
                                   vad_filter=True)

    transcript = " ".join([segment.text for segment in segments])

    return transcript