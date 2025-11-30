"""
BETTI TTS (Text-to-Speech) Engines

Supported engines:
- Piper: Fast, local, high quality
- Coqui: Neural TTS, many voices
- Azure: Cloud TTS
- Google: Cloud TTS
"""

import asyncio
import subprocess
import tempfile
import os
from abc import ABC, abstractmethod
from typing import Optional
import logging

logger = logging.getLogger(__name__)


class TTSEngine(ABC):
    """Base class for TTS engines"""

    def __init__(self, language: str = "en", voice_id: Optional[str] = None):
        self.language = language
        self.voice_id = voice_id

    @abstractmethod
    async def speak(self, text: str) -> bool:
        """Speak text. Returns True if successful."""
        pass

    @abstractmethod
    async def synthesize(self, text: str) -> Optional[bytes]:
        """Synthesize text to audio bytes."""
        pass


class PiperTTS(TTSEngine):
    """
    Piper TTS - Fast local neural TTS.

    Install: pip install piper-tts
    Models: https://github.com/rhasspy/piper

    Example:
        tts = PiperTTS(language="en", voice_id="en_US-lessac-medium")
        await tts.speak("Hello, I am BETTI.")
    """

    # Default voices per language
    DEFAULT_VOICES = {
        "en": "en_US-lessac-medium",
        "nl": "nl_NL-mls-medium",
        "de": "de_DE-thorsten-medium",
        "fr": "fr_FR-siwis-medium",
        "es": "es_ES-sharvard-medium"
    }

    def __init__(
        self,
        language: str = "en",
        voice_id: Optional[str] = None,
        model_path: Optional[str] = None
    ):
        super().__init__(language, voice_id)
        self.voice_id = voice_id or self.DEFAULT_VOICES.get(language, "en_US-lessac-medium")
        self.model_path = model_path

    async def speak(self, text: str) -> bool:
        """Speak text using Piper"""
        audio = await self.synthesize(text)
        if audio:
            return await self._play_audio(audio)
        return False

    async def synthesize(self, text: str) -> Optional[bytes]:
        """Synthesize text to audio using Piper"""
        try:
            # Try using piper command
            process = await asyncio.create_subprocess_exec(
                "piper",
                "--model", self.voice_id,
                "--output-raw",
                stdin=asyncio.subprocess.PIPE,
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE
            )

            stdout, stderr = await process.communicate(input=text.encode())

            if process.returncode == 0:
                return stdout
            else:
                logger.error(f"Piper error: {stderr.decode()}")
                return None

        except FileNotFoundError:
            logger.warning("Piper not installed. Install with: pip install piper-tts")
            # Fallback to espeak
            return await self._espeak_fallback(text)

    async def _espeak_fallback(self, text: str) -> Optional[bytes]:
        """Fallback to espeak if piper not available"""
        try:
            with tempfile.NamedTemporaryFile(suffix=".wav", delete=False) as f:
                temp_path = f.name

            process = await asyncio.create_subprocess_exec(
                "espeak-ng", "-w", temp_path, text,
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE
            )
            await process.communicate()

            if os.path.exists(temp_path):
                with open(temp_path, "rb") as f:
                    audio = f.read()
                os.unlink(temp_path)
                return audio

        except FileNotFoundError:
            logger.error("Neither piper nor espeak-ng available")

        return None

    async def _play_audio(self, audio: bytes) -> bool:
        """Play audio bytes"""
        try:
            # Try aplay (Linux)
            process = await asyncio.create_subprocess_exec(
                "aplay", "-r", "22050", "-f", "S16_LE", "-t", "raw", "-",
                stdin=asyncio.subprocess.PIPE,
                stdout=asyncio.subprocess.DEVNULL,
                stderr=asyncio.subprocess.DEVNULL
            )
            await process.communicate(input=audio)
            return process.returncode == 0

        except FileNotFoundError:
            # Try paplay (PulseAudio)
            try:
                with tempfile.NamedTemporaryFile(suffix=".wav", delete=False) as f:
                    f.write(audio)
                    temp_path = f.name

                process = await asyncio.create_subprocess_exec(
                    "paplay", temp_path,
                    stdout=asyncio.subprocess.DEVNULL,
                    stderr=asyncio.subprocess.DEVNULL
                )
                await process.communicate()
                os.unlink(temp_path)
                return process.returncode == 0

            except FileNotFoundError:
                logger.error("No audio playback available (aplay, paplay)")
                return False


class CoquiTTS(TTSEngine):
    """
    Coqui TTS - Neural TTS with many voices.

    Install: pip install TTS

    Example:
        tts = CoquiTTS(language="en")
        await tts.speak("Hello from Coqui!")
    """

    def __init__(
        self,
        language: str = "en",
        voice_id: Optional[str] = None,
        model_name: str = "tts_models/en/ljspeech/tacotron2-DDC"
    ):
        super().__init__(language, voice_id)
        self.model_name = model_name
        self._tts = None

    def _get_tts(self):
        """Lazy load TTS model"""
        if self._tts is None:
            try:
                from TTS.api import TTS
                self._tts = TTS(model_name=self.model_name)
            except ImportError:
                logger.error("Coqui TTS not installed. Install with: pip install TTS")
        return self._tts

    async def speak(self, text: str) -> bool:
        """Speak text using Coqui TTS"""
        tts = self._get_tts()
        if not tts:
            return False

        with tempfile.NamedTemporaryFile(suffix=".wav", delete=False) as f:
            temp_path = f.name

        try:
            # Run synthesis in thread pool (blocking call)
            await asyncio.get_event_loop().run_in_executor(
                None,
                lambda: tts.tts_to_file(text=text, file_path=temp_path)
            )

            # Play the file
            process = await asyncio.create_subprocess_exec(
                "aplay", temp_path,
                stdout=asyncio.subprocess.DEVNULL,
                stderr=asyncio.subprocess.DEVNULL
            )
            await process.communicate()

            return process.returncode == 0

        finally:
            if os.path.exists(temp_path):
                os.unlink(temp_path)

    async def synthesize(self, text: str) -> Optional[bytes]:
        """Synthesize to audio bytes"""
        tts = self._get_tts()
        if not tts:
            return None

        with tempfile.NamedTemporaryFile(suffix=".wav", delete=False) as f:
            temp_path = f.name

        try:
            await asyncio.get_event_loop().run_in_executor(
                None,
                lambda: tts.tts_to_file(text=text, file_path=temp_path)
            )

            with open(temp_path, "rb") as f:
                return f.read()

        finally:
            if os.path.exists(temp_path):
                os.unlink(temp_path)


class SystemTTS(TTSEngine):
    """
    System TTS - Uses OS built-in TTS.

    Works on:
    - Linux: espeak-ng
    - macOS: say
    - Windows: SAPI
    """

    async def speak(self, text: str) -> bool:
        """Speak using system TTS"""
        import platform

        system = platform.system()

        try:
            if system == "Darwin":  # macOS
                process = await asyncio.create_subprocess_exec(
                    "say", text,
                    stdout=asyncio.subprocess.DEVNULL,
                    stderr=asyncio.subprocess.DEVNULL
                )
            elif system == "Linux":
                process = await asyncio.create_subprocess_exec(
                    "espeak-ng", text,
                    stdout=asyncio.subprocess.DEVNULL,
                    stderr=asyncio.subprocess.DEVNULL
                )
            else:  # Windows
                # Use PowerShell
                ps_cmd = f'Add-Type -AssemblyName System.Speech; (New-Object System.Speech.Synthesis.SpeechSynthesizer).Speak("{text}")'
                process = await asyncio.create_subprocess_exec(
                    "powershell", "-Command", ps_cmd,
                    stdout=asyncio.subprocess.DEVNULL,
                    stderr=asyncio.subprocess.DEVNULL
                )

            await process.communicate()
            return process.returncode == 0

        except FileNotFoundError:
            logger.error(f"System TTS not available on {system}")
            return False

    async def synthesize(self, text: str) -> Optional[bytes]:
        """System TTS doesn't support synthesis to bytes easily"""
        return None


# Factory function
def get_tts_engine(
    engine: str = "piper",
    language: str = "en",
    **kwargs
) -> TTSEngine:
    """
    Get TTS engine by name.

    Args:
        engine: Engine name (piper, coqui, system)
        language: Language code
        **kwargs: Engine-specific options

    Returns:
        TTSEngine instance
    """
    engines = {
        "piper": PiperTTS,
        "coqui": CoquiTTS,
        "system": SystemTTS
    }

    engine_class = engines.get(engine, PiperTTS)
    return engine_class(language=language, **kwargs)
