"""
Voltage Control Layer - Dynamic CPU/GPU Performance Management
=================================================================

Philosophy from Jasper:
"Opslag is een vacuum waar niks is en input nergens gelijk aan staat maar ineens ruimte inneemt"
"RAM moet een constante doorloop zijn, alsof je waterstroom volgt die steady is ipv watervallen"

This controller manages voltage/frequency profiles to optimize:
- Storage: Treat as vacuum - instant availability, no resistance
- RAM: Steady flow like water, not bursts (waterfalls)
- CPU: Dynamic scaling based on task urgency
"""

import asyncio
import logging
from enum import Enum
from dataclasses import dataclass
from typing import Optional, Dict
import subprocess
import os

logger = logging.getLogger(__name__)


class VoltageProfile(Enum):
    """Voltage/Frequency profiles for different workload types"""
    ECO = "eco"  # Background tasks, idle
    BALANCED = "balanced"  # Normal operation
    PERFORMANCE = "performance"  # High-priority tasks
    TURBO = "turbo"  # Emergency/critical
    THERMAL_THROTTLE = "thermal_throttle"  # Overheat protection


@dataclass
class ProfileConfig:
    """Configuration for a voltage profile"""
    name: str
    cpu_min_freq_mhz: int
    cpu_max_freq_mhz: int
    cpu_governor: str  # conservative, ondemand, performance, powersave
    power_cap_watts: Optional[int] = None
    description: str = ""


class VoltageController:
    """
    Main voltage control system

    Orchestration Strategy (per Jasper's insight):
    - Storage (disk) = vacuum: Pre-allocated, instant access, no waiting
    - RAM = steady water flow: Constant throughput, no burst patterns
    - CPU = adaptive: Scale based on Archimedes urgency
    """

    PROFILES = {
        VoltageProfile.ECO: ProfileConfig(
            name="ECO",
            cpu_min_freq_mhz=800,
            cpu_max_freq_mhz=1200,
            cpu_governor="conservative",
            power_cap_watts=30,
            description="Background tasks, 15-30W power"
        ),
        VoltageProfile.BALANCED: ProfileConfig(
            name="BALANCED",
            cpu_min_freq_mhz=1200,
            cpu_max_freq_mhz=1800,
            cpu_governor="ondemand",
            power_cap_watts=65,
            description="Normal operation, 45-65W power"
        ),
        VoltageProfile.PERFORMANCE: ProfileConfig(
            name="PERFORMANCE",
            cpu_min_freq_mhz=2000,
            cpu_max_freq_mhz=2400,
            cpu_governor="performance",
            power_cap_watts=95,
            description="High-priority, 65-95W power"
        ),
        VoltageProfile.TURBO: ProfileConfig(
            name="TURBO",
            cpu_min_freq_mhz=2400,
            cpu_max_freq_mhz=3000,
            cpu_governor="performance",
            power_cap_watts=None,  # No cap
            description="Emergency/critical, max power"
        ),
        VoltageProfile.THERMAL_THROTTLE: ProfileConfig(
            name="THERMAL_THROTTLE",
            cpu_min_freq_mhz=800,
            cpu_max_freq_mhz=1000,
            cpu_governor="powersave",
            power_cap_watts=20,
            description="Overheat protection, <70°C target"
        )
    }

    def __init__(self):
        self.current_profile = VoltageProfile.BALANCED
        self.thermal_threshold_celsius = 75.0
        self.thermal_critical_celsius = 85.0
        self._monitoring_task: Optional[asyncio.Task] = None
        self._profile_lock = asyncio.Lock()

    async def start(self):
        """Start voltage controller and thermal monitoring"""
        logger.info("🔋 Starting Voltage Controller")
        await self.set_profile(VoltageProfile.BALANCED)
        self._monitoring_task = asyncio.create_task(self._thermal_monitor())

    async def stop(self):
        """Stop monitoring and return to balanced"""
        if self._monitoring_task:
            self._monitoring_task.cancel()
            try:
                await self._monitoring_task
            except asyncio.CancelledError:
                pass
        await self.set_profile(VoltageProfile.BALANCED)
        logger.info("🔋 Voltage Controller stopped")

    async def set_profile(self, profile: VoltageProfile, force: bool = False):
        """
        Change voltage/frequency profile

        Args:
            profile: Target profile
            force: Skip safety checks (use with caution)
        """
        async with self._profile_lock:
            if not force:
                # Safety: Check temperature before boosting
                temp = await self._get_cpu_temperature()
                if temp and temp > self.thermal_threshold_celsius and profile in [VoltageProfile.PERFORMANCE, VoltageProfile.TURBO]:
                    logger.warning(f"⚠️ Temp {temp}°C too high for {profile.value}, staying at {self.current_profile.value}")
                    return False

            config = self.PROFILES[profile]
            logger.info(f"🔋 Switching to {config.name} profile: {config.description}")

            try:
                # Apply CPU frequency scaling
                await self._set_cpu_freq(config.cpu_min_freq_mhz, config.cpu_max_freq_mhz)
                await self._set_cpu_governor(config.cpu_governor)

                # Apply power cap if specified (Intel RAPL)
                if config.power_cap_watts:
                    await self._set_power_cap(config.power_cap_watts)

                self.current_profile = profile
                return True

            except Exception as e:
                logger.error(f"❌ Failed to set profile {profile.value}: {e}")
                return False

    async def profile_for_urgency(self, urgency: int) -> VoltageProfile:
        """
        Map BETTI Archimedes urgency (1-10) to voltage profile

        Urgency scale:
        10 = emergency call (TURBO)
        7-9 = high priority (PERFORMANCE)
        4-6 = normal (BALANCED)
        1-3 = low priority (ECO)
        """
        if urgency >= 9:
            return VoltageProfile.TURBO
        elif urgency >= 7:
            return VoltageProfile.PERFORMANCE
        elif urgency >= 4:
            return VoltageProfile.BALANCED
        else:
            return VoltageProfile.ECO

    async def _thermal_monitor(self):
        """Background task to monitor temperature and throttle if needed"""
        while True:
            try:
                temp = await self._get_cpu_temperature()
                if temp:
                    if temp >= self.thermal_critical_celsius:
                        logger.error(f"🔥 CRITICAL TEMP {temp}°C! Emergency throttle!")
                        await self.set_profile(VoltageProfile.THERMAL_THROTTLE, force=True)
                    elif temp >= self.thermal_threshold_celsius and self.current_profile in [VoltageProfile.TURBO, VoltageProfile.PERFORMANCE]:
                        logger.warning(f"🔥 Temp {temp}°C high, downgrade profile")
                        await self.set_profile(VoltageProfile.BALANCED, force=True)

                await asyncio.sleep(5)  # Check every 5s

            except asyncio.CancelledError:
                break
            except Exception as e:
                logger.error(f"Thermal monitor error: {e}")
                await asyncio.sleep(10)

    async def _get_cpu_temperature(self) -> Optional[float]:
        """Get current CPU temperature"""
        try:
            result = subprocess.run(
                ["sensors", "-u"],
                capture_output=True,
                text=True,
                timeout=2
            )

            # Parse sensors output for CPU temp
            for line in result.stdout.split('\n'):
                if 'temp1_input' in line or 'Tctl_input' in line or 'Core 0_input' in line:
                    parts = line.split(':')
                    if len(parts) == 2:
                        return float(parts[1].strip())

        except Exception as e:
            logger.debug(f"Could not read temperature: {e}")

        return None

    async def _set_cpu_freq(self, min_mhz: int, max_mhz: int):
        """Set CPU frequency range"""
        try:
            # Use cpufreq-set or direct sysfs
            num_cpus = os.cpu_count() or 1

            for cpu in range(num_cpus):
                min_path = f"/sys/devices/system/cpu/cpu{cpu}/cpufreq/scaling_min_freq"
                max_path = f"/sys/devices/system/cpu/cpu{cpu}/cpufreq/scaling_max_freq"

                if os.path.exists(min_path):
                    with open(min_path, 'w') as f:
                        f.write(str(min_mhz * 1000))  # Convert MHz to KHz

                if os.path.exists(max_path):
                    with open(max_path, 'w') as f:
                        f.write(str(max_mhz * 1000))

            logger.debug(f"✓ CPU freq set to {min_mhz}-{max_mhz} MHz")

        except PermissionError:
            logger.warning("⚠️ Need root for CPU freq control (run as root or use sudo)")
        except Exception as e:
            logger.error(f"Failed to set CPU freq: {e}")

    async def _set_cpu_governor(self, governor: str):
        """Set CPU governor (conservative, ondemand, performance, powersave)"""
        try:
            num_cpus = os.cpu_count() or 1

            for cpu in range(num_cpus):
                gov_path = f"/sys/devices/system/cpu/cpu{cpu}/cpufreq/scaling_governor"

                if os.path.exists(gov_path):
                    with open(gov_path, 'w') as f:
                        f.write(governor)

            logger.debug(f"✓ CPU governor set to {governor}")

        except Exception as e:
            logger.error(f"Failed to set governor: {e}")

    async def _set_power_cap(self, watts: int):
        """Set Intel RAPL power cap (if available)"""
        try:
            # Intel RAPL interface
            rapl_path = "/sys/class/powercap/intel-rapl/intel-rapl:0/constraint_0_power_limit_uw"

            if os.path.exists(rapl_path):
                with open(rapl_path, 'w') as f:
                    f.write(str(watts * 1000000))  # Convert W to uW

                logger.debug(f"✓ Power cap set to {watts}W")
            else:
                logger.debug("Intel RAPL not available (AMD CPU or no support)")

        except Exception as e:
            logger.debug(f"Could not set power cap: {e}")


# Global singleton
_voltage_controller: Optional[VoltageController] = None


def get_voltage_controller() -> VoltageController:
    """Get or create global voltage controller"""
    global _voltage_controller
    if _voltage_controller is None:
        _voltage_controller = VoltageController()
    return _voltage_controller
