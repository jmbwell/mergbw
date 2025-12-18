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
    # This now assumes 'client' is a connected BleakClient instance
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

SCENE_NAMES = [
    "fantasy", "sunset", "forest", "ghost", "sunrise", 
    "midsummer", "tropicaltwilight", "green prairie", "rubyglow", 
    "aurora", "savanah", "alarm", "lake placid", "neon", 
    "sundowner", "bluestar", "redrose", "rating", "disco", "autumn"
]

SCENE_PARAMS = {}
start_id = 0x80
for i, name in enumerate(SCENE_NAMES):
    SCENE_PARAMS[name] = (CMD_SET_SCENE, bytes([start_id + i]))

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