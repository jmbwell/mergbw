
import asyncio

# UUIDs
SERVICE_UUID = "0000fff0-0000-1000-8000-00805f9b34fb"
CHARACTERISTIC_WRITEABLE = "0000fff3-0000-1000-8000-00805f9b34fb"

# Command codes
CMD_POWER_REQ = 0x01
CMD_SET_COLOR_REQ = 0x03
CMD_SET_BRIGHTNESS_REQ = 0x05
CMD_WHITE_OFF = 0x00
CMD_SET_SCENE = 0x06

# Command structure constants
CMD_HEAD = 0x55
CMD_SEQUENCE = 0xFF

def build_command(cmd_code: int, value: bytes = b'') -> bytes:
    """Builds a full command packet."""
    total_length = 5 + len(value)
    data_for_checksum = bytearray([CMD_HEAD, cmd_code, CMD_SEQUENCE, total_length]) + value
    
    s = sum(data_for_checksum)
    while s > 0xFF:
        s = (s >> 8) + (s & 0xFF)
        
    checksum = (~s) & 0xFF

    full_packet = data_for_checksum + bytes([checksum])
    return full_packet

async def send_command(client, command: bytes):
    """Sends a command to the already connected client."""
    print(f"Sending command: {command.hex()}")
    await client.write_gatt_char(CHARACTERISTIC_WRITEABLE, command)

async def turn_on(client):
    """Turns the light on."""
    command = build_command(CMD_POWER_REQ, b'\x01')
    await send_command(client, command)

async def turn_off(client):
    """Turns the light off."""
    command = build_command(CMD_POWER_REQ, b'\x00')
    await send_command(client, command)

async def set_white(client):
    """Sets the light to white."""
    command = build_command(CMD_SET_COLOR_REQ, bytes([255, 255, 255]))
    await send_command(client, command)

# Scene ID Mapping
# Explicitly defined based on user verification.
SCENE_PARAMS = {
    # Verified Mappings
    "green prairie": (CMD_SET_SCENE, b'\x81'),
    "ghost": (CMD_SET_SCENE, b'\x84'),
    "disco": (CMD_SET_SCENE, b'\x87'),
    "alarm": (CMD_SET_SCENE, b'\x88'),
    "savanah": (CMD_SET_SCENE, b'\x8B'),

    # Default/Unverified Mappings (Sequential from 0x80, skipping verified ones)
    "fantasy": (CMD_SET_SCENE, b'\x80'),
    "sunset": (CMD_SET_SCENE, b'\x82'), # Was 81 (GP), moved to 82? No, 82 was Forest.
    "forest": (CMD_SET_SCENE, b'\x82'),
    "sunrise": (CMD_SET_SCENE, b'\x83'), # Was 84 (Ghost). 83 was Ghost. Swapped?
    # Logic: 0x83 is likely Sunrise if 0x84 is Ghost? 
    "midsummer": (CMD_SET_SCENE, b'\x85'),
    "tropicaltwilight": (CMD_SET_SCENE, b'\x86'),
    # 0x87 is Disco.
    "rubyglow": (CMD_SET_SCENE, b'\x89'), # Was 88 (Alarm). 89 was Aurora.
    "aurora": (CMD_SET_SCENE, b'\x89'),
    # 0x8A was Savanah. 0x8B is Savanah. Maybe 0x8A is something else?
    "lake placid": (CMD_SET_SCENE, b'\x8C'),
    "neon": (CMD_SET_SCENE, b'\x8D'),
    "sundowner": (CMD_SET_SCENE, b'\x8E'),
    "bluestar": (CMD_SET_SCENE, b'\x8F'),
    "redrose": (CMD_SET_SCENE, b'\x90'),
    "rating": (CMD_SET_SCENE, b'\x91'),
    # 0x92 was Disco.
    "autumn": (CMD_SET_SCENE, b'\x93'),
}

# Note: Some IDs like 0x8A, 0x92 might be unmapped or map to the "Old" names.
# Ideally we need to test all IDs again to map the rest.

async def set_scene(client, scene_name: str):
    """Sets a predefined scene."""
    params = SCENE_PARAMS.get(scene_name.lower())
    if params:
        cmd, data = params
        command = build_command(cmd, data)
        await send_command(client, command)
    else:
        print(f"Unknown scene: {scene_name}")

async def set_color(client, r: int, g: int, b: int):
    """Sets the color of the light."""
    color_value = bytes([r, g, b])
    command = build_command(CMD_SET_COLOR_REQ, color_value)
    await send_command(client, command)

async def set_brightness(client, brightness: int):
    """Sets the brightness of the light."""
    brightness_value = bytes([brightness])
    command = build_command(CMD_SET_BRIGHTNESS_REQ, brightness_value)
    await send_command(client, command)
