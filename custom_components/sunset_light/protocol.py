"""Protocol profiles for Sunset Light devices."""

from dataclasses import dataclass
from typing import Dict, Iterable, List


def _checksum(packet: Iterable[int]) -> int:
    """Compute checksum: one's complement of folded sum."""
    total = sum(packet)
    while total > 0xFF:
        total = (total >> 8) + (total & 0xFF)
    return (~total) & 0xFF


def _build_packet(cmd: int, payload: bytes = b"") -> bytes:
    total_length = 5 + len(payload)
    data = bytearray([0x55, cmd, 0xFF, total_length])
    data.extend(payload)
    data.append(_checksum(data))
    return bytes(data)


@dataclass
class ProtocolProfile:
    name: str
    service_uuid: str
    write_char_uuid: str
    notify_char_uuid: str
    effect_list: List[str]

    def build_power(self, on: bool) -> List[bytes]:
        raise NotImplementedError

    def build_color(self, r: int, g: int, b: int) -> List[bytes]:
        raise NotImplementedError

    def build_brightness(self, brightness_ha: int) -> List[bytes]:
        raise NotImplementedError

    def build_scene(self, scene_name: str) -> List[bytes]:
        raise NotImplementedError

    def build_white(self) -> List[bytes]:
        return self.build_color(255, 255, 255)


class SunsetLightProfile(ProtocolProfile):
    """Original Sunset Light behavior (default)."""

    def __init__(self) -> None:
        self.name = "Sunset Light"
        self.service_uuid = "0000fff0-0000-1000-8000-00805f9b34fb"
        self.write_char_uuid = "0000fff3-0000-1000-8000-00805f9b34fb"
        self.notify_char_uuid = "0000fff4-0000-1000-8000-00805f9b34fb"
        self.effect_list = [
            "Fantasy", "Sunset", "Forest", "Ghost", "Sunrise",
            "Midsummer", "Tropicaltwilight", "Green Prairie", "Rubyglow",
            "Aurora", "Savanah", "Alarm", "Lake Placid", "Neon",
            "Sundowner", "Bluestar", "Redrose", "Rating", "Disco", "Autumn",
        ]
        self._scene_params: Dict[str, bytes] = {
            "green prairie": b"\x81",
            "ghost": b"\x84",
            "disco": b"\x87",
            "alarm": b"\x88",
            "savanah": b"\x8B",
            "fantasy": b"\x80",
            "sunset": b"\x82",
            "forest": b"\x82",
            "sunrise": b"\x83",
            "midsummer": b"\x85",
            "tropicaltwilight": b"\x86",
            "rubyglow": b"\x89",
            "aurora": b"\x89",
            "lake placid": b"\x8C",
            "neon": b"\x8D",
            "sundowner": b"\x8E",
            "bluestar": b"\x8F",
            "redrose": b"\x90",
            "rating": b"\x91",
            "autumn": b"\x93",
        }

    def build_power(self, on: bool) -> List[bytes]:
        return [_build_packet(0x01, b"\x01" if on else b"\x00")]

    def build_color(self, r: int, g: int, b: int) -> List[bytes]:
        return [_build_packet(0x03, bytes([r, g, b]))]

    def build_brightness(self, brightness_ha: int) -> List[bytes]:
        value = int(brightness_ha / 255 * 100)
        value = max(0, min(100, value))
        return [_build_packet(0x05, bytes([value]))]

    def build_scene(self, scene_name: str) -> List[bytes]:
        payload = self._scene_params.get(scene_name.lower())
        if payload is None:
            return []
        return [_build_packet(0x06, payload)]


PROFILE_SUNSET = "sunset_light"


def get_profile(profile_key: str | None) -> ProtocolProfile:
    return SunsetLightProfile()


def list_profiles() -> List[tuple[str, str]]:
    return [(PROFILE_SUNSET, "Sunset Light")]
