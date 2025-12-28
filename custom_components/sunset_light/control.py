
from typing import Iterable

from .protocol import ProtocolProfile


async def _send_packets(client, packets: Iterable[bytes], write_uuid: str):
    for packet in packets:
        await client.write_gatt_char(write_uuid, packet)


async def turn_on(client, profile: ProtocolProfile):
    await _send_packets(client, profile.build_power(True), profile.write_char_uuid)


async def turn_off(client, profile: ProtocolProfile):
    await _send_packets(client, profile.build_power(False), profile.write_char_uuid)


async def set_white(client, profile: ProtocolProfile):
    await _send_packets(client, profile.build_white(), profile.write_char_uuid)


async def set_scene(client, profile: ProtocolProfile, scene_name: str):
    packets = profile.build_scene(scene_name)
    if packets:
        await _send_packets(client, packets, profile.write_char_uuid)


async def set_color(client, profile: ProtocolProfile, r: int, g: int, b: int):
    await _send_packets(client, profile.build_color(r, g, b), profile.write_char_uuid)


async def set_brightness(client, profile: ProtocolProfile, brightness: int):
    await _send_packets(client, profile.build_brightness(brightness), profile.write_char_uuid)
