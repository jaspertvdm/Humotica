"""
BETTI Wake Word Detection

Detects wake words to activate voice assistant.

Supported:
- Simple keyword matching (built-in)
- Porcupine (Picovoice)
- OpenWakeWord
"""

import asyncio
import logging
from typing import Optional, List, Callable
from abc import ABC, abstractmethod

logger = logging.getLogger(__name__)


class WakeWordDetector(ABC):
    """Base wake word detector"""

    def __init__(self, wake_word: str = "hey betti"):
        self.wake_word = wake_word.lower()
        self._callback: Optional[Callable] = None

    def on_wake_word(self, callback: Callable):
        """Register callback for wake word detection"""
        self._callback = callback

    @abstractmethod
    async def wait_for_wake_word(self, timeout: Optional[float] = None) -> bool:
        """Wait for wake word. Returns True if detected."""
        pass

    @abstractmethod
    async def start_detection(self):
        """Start continuous wake word detection"""
        pass

    @abstractmethod
    async def stop_detection(self):
        """Stop detection"""
        pass


class SimpleWakeWordDetector(WakeWordDetector):
    """
    Simple wake word detector using keyword matching.

    Uses continuous speech recognition to detect wake word.

    Example:
        detector = SimpleWakeWordDetector("hey betti")
        if await detector.wait_for_wake_word(timeout=30):
            print("Wake word detected!")
    """

    def __init__(
        self,
        wake_word: str = "hey betti",
        stt_engine: str = "vosk"
    ):
        super().__init__(wake_word)
        self.stt_engine = stt_engine
        self._running = False
        self._stt = None

    def _get_stt(self):
        """Get STT engine for detection"""
        if self._stt is None:
            from .stt import get_stt_engine
            self._stt = get_stt_engine(self.stt_engine, language="en")
        return self._stt

    async def wait_for_wake_word(self, timeout: Optional[float] = None) -> bool:
        """Listen for wake word"""
        stt = self._get_stt()
        if not stt:
            logger.error("STT not available for wake word detection")
            return False

        start_time = asyncio.get_event_loop().time()
        chunk_duration = 2.0  # Listen in 2-second chunks

        while True:
            # Check timeout
            if timeout:
                elapsed = asyncio.get_event_loop().time() - start_time
                if elapsed >= timeout:
                    return False

            # Listen for a chunk
            text = await stt.listen(timeout=chunk_duration)

            if text:
                text_lower = text.lower()
                logger.debug(f"Heard: {text_lower}")

                # Check for wake word
                if self._contains_wake_word(text_lower):
                    logger.info(f"Wake word detected: {self.wake_word}")
                    if self._callback:
                        await self._callback()
                    return True

    def _contains_wake_word(self, text: str) -> bool:
        """Check if text contains wake word"""
        # Direct match
        if self.wake_word in text:
            return True

        # Fuzzy matching for common misrecognitions
        wake_variants = self._get_wake_variants()
        for variant in wake_variants:
            if variant in text:
                return True

        return False

    def _get_wake_variants(self) -> List[str]:
        """Get common variations of wake word"""
        variants = [self.wake_word]

        # Common BETTI variations
        if "betti" in self.wake_word:
            variants.extend([
                self.wake_word.replace("betti", "betty"),
                self.wake_word.replace("betti", "beddy"),
                self.wake_word.replace("betti", "body"),
                self.wake_word.replace("betti", "ready"),
            ])

        # Hey/hi variations
        if self.wake_word.startswith("hey "):
            variants.extend([
                self.wake_word.replace("hey ", "hi "),
                self.wake_word.replace("hey ", "hay "),
                self.wake_word.replace("hey ", "a "),
            ])

        return variants

    async def start_detection(self):
        """Start continuous detection"""
        self._running = True
        while self._running:
            detected = await self.wait_for_wake_word(timeout=None)
            if detected and self._callback:
                await self._callback()

    async def stop_detection(self):
        """Stop detection"""
        self._running = False


class PorcupineDetector(WakeWordDetector):
    """
    Porcupine wake word detector (Picovoice).

    Requires access key from https://picovoice.ai/

    Install: pip install pvporcupine

    Example:
        detector = PorcupineDetector(
            wake_word="betti",
            access_key="your-access-key"
        )
    """

    def __init__(
        self,
        wake_word: str = "betti",
        access_key: Optional[str] = None,
        keyword_path: Optional[str] = None
    ):
        super().__init__(wake_word)
        self.access_key = access_key
        self.keyword_path = keyword_path
        self._porcupine = None
        self._running = False

    def _get_porcupine(self):
        """Initialize Porcupine"""
        if self._porcupine is None:
            try:
                import pvporcupine

                if self.keyword_path:
                    # Custom keyword
                    self._porcupine = pvporcupine.create(
                        access_key=self.access_key,
                        keyword_paths=[self.keyword_path]
                    )
                else:
                    # Built-in keyword (limited options)
                    self._porcupine = pvporcupine.create(
                        access_key=self.access_key,
                        keywords=["computer"]  # Use available built-in
                    )

            except ImportError:
                logger.error("Porcupine not installed. Install: pip install pvporcupine")

        return self._porcupine

    async def wait_for_wake_word(self, timeout: Optional[float] = None) -> bool:
        """Wait for wake word using Porcupine"""
        porcupine = self._get_porcupine()
        if not porcupine:
            # Fallback to simple detector
            fallback = SimpleWakeWordDetector(self.wake_word)
            return await fallback.wait_for_wake_word(timeout)

        try:
            import pyaudio
            import struct

            pa = pyaudio.PyAudio()
            stream = pa.open(
                rate=porcupine.sample_rate,
                channels=1,
                format=pyaudio.paInt16,
                input=True,
                frames_per_buffer=porcupine.frame_length
            )

            start_time = asyncio.get_event_loop().time()

            while True:
                # Check timeout
                if timeout:
                    elapsed = asyncio.get_event_loop().time() - start_time
                    if elapsed >= timeout:
                        stream.close()
                        pa.terminate()
                        return False

                # Read audio
                pcm = stream.read(porcupine.frame_length)
                pcm = struct.unpack_from("h" * porcupine.frame_length, pcm)

                # Process
                keyword_index = porcupine.process(pcm)

                if keyword_index >= 0:
                    logger.info("Wake word detected (Porcupine)")
                    stream.close()
                    pa.terminate()
                    if self._callback:
                        await self._callback()
                    return True

                await asyncio.sleep(0.01)

        except Exception as e:
            logger.error(f"Porcupine error: {e}")
            return False

    async def start_detection(self):
        """Start continuous detection"""
        self._running = True
        while self._running:
            await self.wait_for_wake_word()

    async def stop_detection(self):
        """Stop detection"""
        self._running = False
        if self._porcupine:
            self._porcupine.delete()
            self._porcupine = None


# Default detector
def get_wake_word_detector(
    wake_word: str = "hey betti",
    engine: str = "simple",
    **kwargs
) -> WakeWordDetector:
    """
    Get wake word detector.

    Args:
        wake_word: Wake word phrase
        engine: Detector type (simple, porcupine)
        **kwargs: Engine-specific options

    Returns:
        WakeWordDetector instance
    """
    if engine == "porcupine" and kwargs.get("access_key"):
        return PorcupineDetector(wake_word, **kwargs)
    else:
        return SimpleWakeWordDetector(wake_word)
