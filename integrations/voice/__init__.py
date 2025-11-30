"""
BETTI Voice Integration

Complete voice assistant framework with TTS, STT, and wake word detection.
Integrates with BETTI for validated intent execution.

Supported Engines:
- TTS: Piper, Coqui, Azure, Google
- STT: Whisper, Vosk, Azure, Google
- Wake Word: Porcupine, Snowboy, OpenWakeWord

Example:
    from humotica.integrations.voice import VoiceAssistant

    assistant = VoiceAssistant(
        betti_url="http://localhost:8010",
        tts_engine="piper",
        stt_engine="whisper",
        wake_word="hey betti"
    )

    @assistant.on_intent
    async def handle_intent(intent, context, tibet_token):
        print(f"Executing: {intent}")
        return "Done!"

    assistant.run()
"""

from .assistant import VoiceAssistant
from .tts import TTSEngine, PiperTTS, CoquiTTS
from .stt import STTEngine, WhisperSTT, VoskSTT
from .wake_word import WakeWordDetector

__all__ = [
    "VoiceAssistant",
    "TTSEngine",
    "PiperTTS",
    "CoquiTTS",
    "STTEngine",
    "WhisperSTT",
    "VoskSTT",
    "WakeWordDetector"
]
