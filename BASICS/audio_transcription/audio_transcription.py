import sounddevice as sd
import numpy as np
from scipy.io.wavfile import write
from faster_whisper import WhisperModel

fs = 44100
duration = 5
device_index = 15

print("🎤 बोलो...")

audio = sd.rec(
    int(duration * fs),
    samplerate=fs,
    channels=2,   # 🔥 FIX
    dtype='float32',
    device=device_index
)
sd.wait()

print("🔍 Audio level:", np.max(audio))

# 👉 stereo → mono convert (important for whisper)
audio = np.mean(audio, axis=1)

audio_int16 = (audio * 32767).astype(np.int16)
write("temp.wav", fs, audio_int16)

print("💾 saved")

model = WhisperModel("small", device="cuda")

segments, _ = model.transcribe("temp.wav")

print("\n🧠 OUTPUT:")
for segment in segments:
    print(segment.text)