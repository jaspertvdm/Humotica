# DID System Implementatie voor Humotica SDK v2.0

## Overzicht

Het **Device ID (DID) systeem** is een uniek identificatie systeem voor alle devices die met Humotica werken.

### DID Format: XXX-YY-ZZZZ

- **XXX**: Device type code (100-999) = 900 types mogelijk
- **YY**: Network segment (00-99) = 100 netwerken
- **ZZZZ**: Uniek device ID (0000-9999) = 10,000 devices per netwerk

**Totale capacity: 900 × 100 × 10,000 = 900 miljoen devices**

### Device Type Codes

```python
TYPE_ROUTER = 125
TYPE_PI = 175
TYPE_SERVER = 176
TYPE_SMARTPHONE = 163
TYPE_LAPTOP = 180
TYPE_UNKNOWN = 199
```

## Implementatie in SDK

### 1. Python SDK Implementatie

```python
"""
Humotica SDK v2.0 - DID Generator
Voor inbouw in SDK om automatisch DIDs te genereren
"""
import hashlib
import uuid
import os


class HumoticaDIDGenerator:
    """
    Automatische DID generatie voor Humotica devices

    Gebruik:
        did = HumoticaDIDGenerator.generate()
        print(f"My DID: {did}")  # Output: "163-04-7829"
    """

    # Device type detection
    TYPE_ROUTER = 125
    TYPE_PI = 175
    TYPE_SERVER = 176
    TYPE_SMARTPHONE = 163
    TYPE_LAPTOP = 180
    TYPE_UNKNOWN = 199

    @staticmethod
    def detect_device_type():
        """Auto-detect device type based on platform"""
        import platform
        import sys

        system = platform.system().lower()
        machine = platform.machine().lower()

        # Android smartphone
        if hasattr(sys, 'getandroidapilevel'):
            return HumoticaDIDGenerator.TYPE_SMARTPHONE

        # Raspberry Pi detection
        if os.path.exists('/proc/device-tree/model'):
            with open('/proc/device-tree/model', 'r') as f:
                model = f.read().lower()
                if 'raspberry' in model:
                    return HumoticaDIDGenerator.TYPE_PI

        # Server detection (headless, no GUI)
        if system == 'linux':
            # Check if running as systemd service or on server
            if os.environ.get('SYSTEMD_EXEC_PID') or not os.environ.get('DISPLAY'):
                return HumoticaDIDGenerator.TYPE_SERVER

        # Default to laptop/desktop
        return HumoticaDIDGenerator.TYPE_LAPTOP

    @staticmethod
    def get_mac_address():
        """Get primary MAC address of device"""
        mac = uuid.getnode()
        mac_str = ':'.join(['{:02x}'.format((mac >> i) & 0xff)
                           for i in range(0, 48, 8)][::-1])
        return mac_str

    @staticmethod
    def get_network_segment():
        """
        Get network segment from local IP
        Returns segment from 192.168.X.y format (X = segment)
        Default: 4 (for 192.168.4.x)
        """
        try:
            import socket
            hostname = socket.gethostname()
            ip = socket.gethostbyname(hostname)
            parts = ip.split('.')
            if len(parts) == 4:
                return int(parts[2])
        except:
            pass

        return 4  # Default network segment

    @staticmethod
    def generate(device_type=None, network_segment=None):
        """
        Generate DID voor dit device

        Args:
            device_type: Optional device type code (auto-detect if None)
            network_segment: Optional network segment (auto-detect if None)

        Returns:
            DID string in format XXX-YY-ZZZZ (e.g., "163-04-7829")
        """
        # Auto-detect device type
        if device_type is None:
            device_type = HumoticaDIDGenerator.detect_device_type()

        # Auto-detect network segment
        if network_segment is None:
            network_segment = HumoticaDIDGenerator.get_network_segment()

        # Get MAC address and hash to unique device ID
        mac = HumoticaDIDGenerator.get_mac_address()
        mac_clean = mac.replace(':', '').lower()
        hash_obj = hashlib.sha256(mac_clean.encode())
        hash_int = int(hash_obj.hexdigest(), 16)
        device_id = hash_int % 10000  # 0000-9999

        # Format: XXX-YY-ZZZZ
        did = f"{device_type:03d}-{network_segment:02d}-{device_id:04d}"
        return did

    @staticmethod
    def validate(did):
        """Validate DID format"""
        parts = did.split('-')
        if len(parts) != 3:
            return False

        try:
            device_type = int(parts[0])
            network = int(parts[1])
            device_id = int(parts[2])

            return (100 <= device_type <= 999 and
                    0 <= network <= 99 and
                    0 <= device_id <= 9999)
        except ValueError:
            return False


# Singleton DID voor dit device (generated once per process)
_DEVICE_DID = None

def get_device_did():
    """
    Get DID voor current device (singleton pattern)
    Wordt 1x gegenereerd per proces en dan gecached
    """
    global _DEVICE_DID
    if _DEVICE_DID is None:
        _DEVICE_DID = HumoticaDIDGenerator.generate()
    return _DEVICE_DID


# ============================================================================
# GEBRUIK IN SDK v2.0
# ============================================================================

def humotica_api_request(endpoint, data=None):
    """
    Voorbeeld: API request met automatische DID header
    """
    import requests

    did = get_device_did()
    headers = {
        'X-Device-ID': did,
        'Content-Type': 'application/json'
    }

    response = requests.post(
        f"https://api.humotica.com{endpoint}",
        json=data,
        headers=headers
    )

    return response.json()


# ============================================================================
# TESTING
# ============================================================================

if __name__ == "__main__":
    print("=== Humotica DID Generator Test ===")
    print()

    # Generate DID
    did = HumoticaDIDGenerator.generate()
    print(f"Generated DID: {did}")

    # Parse DID
    parts = did.split('-')
    device_type = int(parts[0])
    network = int(parts[1])
    device_id = int(parts[2])

    # Type names
    type_names = {
        125: "Router",
        175: "Raspberry Pi",
        176: "Server",
        163: "Smartphone",
        180: "Laptop",
        199: "Unknown"
    }

    print(f"  Device Type: {type_names.get(device_type, 'Unknown')} ({device_type})")
    print(f"  Network Segment: {network}")
    print(f"  Device ID: {device_id}")
    print()

    # Validate
    is_valid = HumoticaDIDGenerator.validate(did)
    print(f"Valid DID: {is_valid}")
    print()

    # Get MAC
    mac = HumoticaDIDGenerator.get_mac_address()
    print(f"MAC Address: {mac}")
    print()

    # Singleton test
    did1 = get_device_did()
    did2 = get_device_did()
    print(f"Singleton test: {did1} == {did2} ? {did1 == did2}")
```

### 2. Integratie in SDK Client

Voeg dit toe aan `HumoticaClient` class in SDK:

```python
class HumoticaClient:
    def __init__(self, api_url="https://api.humotica.com"):
        self.api_url = api_url
        self.did = get_device_did()  # Auto-generate DID

    def _make_request(self, endpoint, data=None):
        """Internal API request met DID header"""
        headers = {
            'X-Device-ID': self.did,
            'Content-Type': 'application/json'
        }

        response = requests.post(
            f"{self.api_url}{endpoint}",
            json=data,
            headers=headers
        )

        return response.json()

    def get_did(self):
        """Get DID van current device"""
        return self.did
```

### 3. Server-side Tracking (Brain API)

Brain API update `DeviceTrackingMiddleware` om DID header te accepteren:

```python
class DeviceTrackingMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next):
        # Check for DID header first
        did = request.headers.get("X-Device-ID")

        if did and DIDGenerator.validate_did(did):
            # Use provided DID
            endpoint = f"{request.method} {request.url.path}"
            device_tracker.track_activity(
                did=did,
                endpoint=endpoint,
                device_name=None,  # Can be provided via another header
                device_type=None
            )
        else:
            # Fallback to IP-based tracking
            client_ip = request.client.host if request.client else "unknown"
            endpoint = f"{request.method} {request.url.path}"
            device_tracker.track_from_ip(client_ip, endpoint)

        response = await call_next(request)
        return response
```

## Voordelen van dit systeem

1. **Uniek**: 900 miljoen unieke DIDs mogelijk
2. **Privacy-friendly**: Geen gevoelige info in DID (MAC wordt gehashed)
3. **Automatisch**: SDK genereert DID zonder user input
4. **Persistent**: Zelfde device krijgt altijd zelfde DID (based on MAC)
5. **Structured**: Device type direct zichtbaar in DID (XXX code)
6. **Network aware**: Network segment tracked voor routing optimalisatie

## DID Voorbeelden

```
125-04-0125  →  Router op 192.168.4.125
175-04-0075  →  Raspberry Pi op 192.168.4.75
176-04-0076  →  Server op 192.168.4.76
163-04-0063  →  Smartphone op 192.168.4.63
180-04-0080  →  Laptop op 192.168.4.80
```

## Security Notes

- DID wordt **NIET** gebruikt voor authenticatie (gebruik tokens/keys)
- DID is **public identifier** voor device tracking en analytics
- MAC address wordt **gehashed** voor privacy
- Server kan DIDs blacklisten als abuse gedetecteerd wordt
