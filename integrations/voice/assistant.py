"""
BETTI Voice Assistant

Main voice assistant class that coordinates TTS, STT, and BETTI.
"""

import asyncio
import logging
from typing import Callable, Optional, Dict, Any
from dataclasses import dataclass


logger = logging.getLogger(__name__)


@dataclass
class VoiceConfig:
    """Voice assistant configuration"""
    betti_url: str = "http://localhost:8010"
    tts_engine: str = "piper"
    stt_engine: str = "whisper"
    wake_word: str = "hey betti"
    language: str = "en"
    voice_id: Optional[str] = None
    sample_rate: int = 16000
    device_id: str = "voice-assistant"


class VoiceAssistant:
    """
    Complete voice assistant with BETTI integration.

    Example:
        assistant = VoiceAssistant(
            betti_url="http://localhost:8010",
            tts_engine="piper",
            stt_engine="whisper"
        )

        @assistant.on_intent
        async def handle(intent, context, tibet_token):
            return f"Executing {intent}"

        assistant.run()
    """

    def __init__(
        self,
        betti_url: str = "http://localhost:8010",
        tts_engine: str = "piper",
        stt_engine: str = "whisper",
        wake_word: str = "hey betti",
        language: str = "en",
        device_id: str = "voice-assistant"
    ):
        """
        Initialize voice assistant.

        Args:
            betti_url: URL of BETTI API
            tts_engine: TTS engine (piper, coqui, azure, google)
            stt_engine: STT engine (whisper, vosk, azure, google)
            wake_word: Wake word phrase
            language: Language code
            device_id: Device identifier for TIBET
        """
        self.config = VoiceConfig(
            betti_url=betti_url,
            tts_engine=tts_engine,
            stt_engine=stt_engine,
            wake_word=wake_word.lower(),
            language=language,
            device_id=device_id
        )

        self._tts = None
        self._stt = None
        self._wake_detector = None
        self._intent_handler = None
        self._running = False

        self._setup_engines()

    def _setup_engines(self):
        """Initialize TTS and STT engines"""
        # TTS setup
        if self.config.tts_engine == "piper":
            from .tts import PiperTTS
            self._tts = PiperTTS(language=self.config.language)
        elif self.config.tts_engine == "coqui":
            from .tts import CoquiTTS
            self._tts = CoquiTTS(language=self.config.language)
        else:
            from .tts import TTSEngine
            self._tts = TTSEngine()

        # STT setup
        if self.config.stt_engine == "whisper":
            from .stt import WhisperSTT
            self._stt = WhisperSTT(language=self.config.language)
        elif self.config.stt_engine == "vosk":
            from .stt import VoskSTT
            self._stt = VoskSTT(language=self.config.language)
        else:
            from .stt import STTEngine
            self._stt = STTEngine()

        # Wake word
        from .wake_word import WakeWordDetector
        self._wake_detector = WakeWordDetector(self.config.wake_word)

    def on_intent(self, handler: Callable):
        """
        Decorator to register intent handler.

        The handler receives:
        - intent: str - The recognized intent
        - context: dict - Context from speech
        - tibet_token: str - TIBET authorization token

        Returns:
        - str: Response to speak
        """
        self._intent_handler = handler
        return handler

    async def speak(self, text: str):
        """Speak text using TTS"""
        if self._tts:
            await self._tts.speak(text)

    async def listen(self, timeout: float = 5.0) -> Optional[str]:
        """Listen for speech and return transcription"""
        if self._stt:
            return await self._stt.listen(timeout=timeout)
        return None

    async def _process_command(self, text: str) -> str:
        """Process voice command through BETTI"""
        import aiohttp

        # Extract intent from text
        intent = self._extract_intent(text)
        context = {
            "source": "voice",
            "raw_text": text,
            "language": self.config.language,
            "device_id": self.config.device_id
        }

        # Validate through BETTI
        async with aiohttp.ClientSession() as session:
            try:
                async with session.post(
                    f"{self.config.betti_url}/betti/validate",
                    json={
                        "device_id": self.config.device_id,
                        "intent": intent,
                        "context": context,
                        "protocol": "voice"
                    }
                ) as resp:
                    if resp.status == 200:
                        data = await resp.json()

                        if not data.get("snaft_approved", False):
                            return "Sorry, I can't do that."

                        tibet_token = data.get("tibet_token", "")

                        # Call intent handler
                        if self._intent_handler:
                            result = await self._intent_handler(
                                intent, context, tibet_token
                            )
                            return result or "Done."

                        return data.get("humotica", "Command received.")
                    else:
                        return "Sorry, there was an error."
            except Exception as e:
                logger.error(f"BETTI validation failed: {e}")
                return "Sorry, I couldn't connect to the server."

    def _extract_intent(self, text: str) -> str:
        """Extract intent from spoken text"""
        text_lower = text.lower()

        # Simple intent extraction patterns
        intent_patterns = {
            "turn on": "device_on",
            "turn off": "device_off",
            "switch on": "device_on",
            "switch off": "device_off",
            "what time": "get_time",
            "what's the time": "get_time",
            "set timer": "set_timer",
            "remind me": "set_reminder",
            "play": "media_play",
            "stop": "media_stop",
            "pause": "media_pause",
            "call": "make_call",
            "message": "send_message",
            "text": "send_message",
            "weather": "get_weather",
            "temperature": "get_temperature",
            "help": "get_help"
        }

        for pattern, intent in intent_patterns.items():
            if pattern in text_lower:
                return intent

        # Default: use the whole text as intent
        return text_lower.replace(" ", "_")[:50]

    async def _run_loop(self):
        """Main voice assistant loop"""
        await self.speak(f"Voice assistant ready. Say '{self.config.wake_word}' to activate.")

        while self._running:
            # Wait for wake word
            if self._wake_detector:
                detected = await self._wake_detector.wait_for_wake_word()
                if not detected:
                    continue

            # Play acknowledgment
            await self.speak("Yes?")

            # Listen for command
            text = await self.listen(timeout=5.0)

            if not text:
                await self.speak("I didn't hear anything.")
                continue

            logger.info(f"Heard: {text}")

            # Process command
            response = await self._process_command(text)

            # Speak response
            await self.speak(response)

    def run(self):
        """Start the voice assistant"""
        self._running = True
        try:
            asyncio.run(self._run_loop())
        except KeyboardInterrupt:
            self._running = False
            logger.info("Voice assistant stopped")

    def stop(self):
        """Stop the voice assistant"""
        self._running = False


# Example usage function
async def demo_voice_assistant():
    """Demo voice assistant without actual audio"""
    print("BETTI Voice Assistant Demo")
    print("=" * 40)

    assistant = VoiceAssistant(
        betti_url="http://localhost:8010",
        tts_engine="piper",
        stt_engine="whisper",
        wake_word="hey betti"
    )

    @assistant.on_intent
    async def handle_intent(intent, context, tibet_token):
        print(f"Intent: {intent}")
        print(f"TIBET Token: {tibet_token[:20]}...")
        return f"Executing {intent}"

    print("Voice assistant configured.")
    print("In production, call assistant.run() to start listening.")


if __name__ == "__main__":
    asyncio.run(demo_voice_assistant())
