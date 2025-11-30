"""
BETTI STT (Speech-to-Text) Engines

Supported engines:
- Whisper: OpenAI Whisper (local or API)
- Vosk: Fast local recognition
- Azure: Cloud STT
- Google: Cloud STT
"""

import asyncio
import tempfile
import os
from abc import ABC, abstractmethod
from typing import Optional
import logging

logger = logging.getLogger(__name__)


class STTEngine(ABC):
    """Base class for STT engines"""

    def __init__(self, language: str = "en", sample_rate: int = 16000):
        self.language = language
        self.sample_rate = sample_rate

    @abstractmethod
    async def listen(self, timeout: float = 5.0) -> Optional[str]:
        """Listen for speech and return transcription."""
        pass

    @abstractmethod
    async def transcribe(self, audio: bytes) -> Optional[str]:
        """Transcribe audio bytes to text."""
        pass


class WhisperSTT(STTEngine):
    """
    OpenAI Whisper STT - High accuracy, multilingual.

    Install: pip install openai-whisper
    Or faster: pip install faster-whisper

    Example:
        stt = WhisperSTT(language="en", model_size="base")
        text = await stt.listen(timeout=5.0)
        print(f"Heard: {text}")
    """

    def __init__(
        self,
        language: str = "en",
        model_size: str = "base",
        use_faster: bool = True
    ):
        super().__init__(language)
        self.model_size = model_size
        self.use_faster = use_faster
        self._model = None

    def _get_model(self):
        """Lazy load Whisper model"""
        if self._model is None:
            try:
                if self.use_faster:
                    from faster_whisper import WhisperModel
                    self._model = WhisperModel(self.model_size, device="cpu")
                else:
                    import whisper
                    self._model = whisper.load_model(self.model_size)
            except ImportError:
                logger.error("Whisper not installed. Install with: pip install faster-whisper")
        return self._model

    async def listen(self, timeout: float = 5.0) -> Optional[str]:
        """Listen for speech from microphone"""
        # Record audio
        audio_path = await self._record_audio(timeout)
        if not audio_path:
            return None

        try:
            return await self.transcribe_file(audio_path)
        finally:
            if os.path.exists(audio_path):
                os.unlink(audio_path)

    async def _record_audio(self, duration: float) -> Optional[str]:
        """Record audio from microphone"""
        with tempfile.NamedTemporaryFile(suffix=".wav", delete=False) as f:
            temp_path = f.name

        try:
            # Use arecord on Linux
            process = await asyncio.create_subprocess_exec(
                "arecord",
                "-f", "S16_LE",
                "-r", str(self.sample_rate),
                "-d", str(int(duration)),
                "-t", "wav",
                temp_path,
                stdout=asyncio.subprocess.DEVNULL,
                stderr=asyncio.subprocess.DEVNULL
            )

            await asyncio.wait_for(process.communicate(), timeout=duration + 2)

            if os.path.exists(temp_path) and os.path.getsize(temp_path) > 0:
                return temp_path

        except FileNotFoundError:
            logger.error("arecord not available. Install alsa-utils.")
        except asyncio.TimeoutError:
            logger.error("Recording timeout")

        return None

    async def transcribe_file(self, audio_path: str) -> Optional[str]:
        """Transcribe audio file"""
        model = self._get_model()
        if not model:
            return None

        try:
            if self.use_faster:
                # faster-whisper
                segments, _ = await asyncio.get_event_loop().run_in_executor(
                    None,
                    lambda: model.transcribe(
                        audio_path,
                        language=self.language if self.language != "auto" else None
                    )
                )
                text = " ".join([s.text for s in segments])
            else:
                # Original whisper
                result = await asyncio.get_event_loop().run_in_executor(
                    None,
                    lambda: model.transcribe(
                        audio_path,
                        language=self.language if self.language != "auto" else None
                    )
                )
                text = result["text"]

            return text.strip()

        except Exception as e:
            logger.error(f"Transcription error: {e}")
            return None

    async def transcribe(self, audio: bytes) -> Optional[str]:
        """Transcribe audio bytes"""
        with tempfile.NamedTemporaryFile(suffix=".wav", delete=False) as f:
            f.write(audio)
            temp_path = f.name

        try:
            return await self.transcribe_file(temp_path)
        finally:
            if os.path.exists(temp_path):
                os.unlink(temp_path)


class VoskSTT(STTEngine):
    """
    Vosk STT - Fast local recognition.

    Install: pip install vosk

    Example:
        stt = VoskSTT(language="en")
        text = await stt.listen()
    """

    # Model paths by language
    MODEL_URLS = {
        "en": "vosk-model-small-en-us-0.15",
        "nl": "vosk-model-small-nl-0.22",
        "de": "vosk-model-small-de-0.15",
        "fr": "vosk-model-small-fr-0.22",
        "es": "vosk-model-small-es-0.42"
    }

    def __init__(
        self,
        language: str = "en",
        model_path: Optional[str] = None
    ):
        super().__init__(language)
        self.model_path = model_path
        self._model = None
        self._recognizer = None

    def _get_recognizer(self):
        """Lazy load Vosk model"""
        if self._recognizer is None:
            try:
                from vosk import Model, KaldiRecognizer
                import json

                # Load model
                if self.model_path:
                    model = Model(self.model_path)
                else:
                    model_name = self.MODEL_URLS.get(self.language, self.MODEL_URLS["en"])
                    model = Model(model_name=model_name)

                self._model = model
                self._recognizer = KaldiRecognizer(model, self.sample_rate)

            except ImportError:
                logger.error("Vosk not installed. Install with: pip install vosk")

        return self._recognizer

    async def listen(self, timeout: float = 5.0) -> Optional[str]:
        """Listen for speech"""
        recognizer = self._get_recognizer()
        if not recognizer:
            return None

        # Record audio
        with tempfile.NamedTemporaryFile(suffix=".wav", delete=False) as f:
            temp_path = f.name

        try:
            process = await asyncio.create_subprocess_exec(
                "arecord",
                "-f", "S16_LE",
                "-r", str(self.sample_rate),
                "-d", str(int(timeout)),
                "-t", "wav",
                temp_path,
                stdout=asyncio.subprocess.DEVNULL,
                stderr=asyncio.subprocess.DEVNULL
            )
            await process.communicate()

            return await self.transcribe_file(temp_path)

        finally:
            if os.path.exists(temp_path):
                os.unlink(temp_path)

    async def transcribe_file(self, audio_path: str) -> Optional[str]:
        """Transcribe audio file using Vosk"""
        import json
        import wave

        recognizer = self._get_recognizer()
        if not recognizer:
            return None

        try:
            wf = wave.open(audio_path, "rb")
            recognizer.AcceptWaveform(wf.readframes(wf.getnframes()))
            result = json.loads(recognizer.FinalResult())
            wf.close()

            return result.get("text", "").strip()

        except Exception as e:
            logger.error(f"Vosk transcription error: {e}")
            return None

    async def transcribe(self, audio: bytes) -> Optional[str]:
        """Transcribe audio bytes"""
        with tempfile.NamedTemporaryFile(suffix=".wav", delete=False) as f:
            f.write(audio)
            temp_path = f.name

        try:
            return await self.transcribe_file(temp_path)
        finally:
            if os.path.exists(temp_path):
                os.unlink(temp_path)


# Factory function
def get_stt_engine(
    engine: str = "whisper",
    language: str = "en",
    **kwargs
) -> STTEngine:
    """
    Get STT engine by name.

    Args:
        engine: Engine name (whisper, vosk)
        language: Language code
        **kwargs: Engine-specific options

    Returns:
        STTEngine instance
    """
    engines = {
        "whisper": WhisperSTT,
        "vosk": VoskSTT
    }

    engine_class = engines.get(engine, WhisperSTT)
    return engine_class(language=language, **kwargs)
