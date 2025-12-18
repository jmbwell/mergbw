
import asyncio
from bleak import BleakClient

ADDRESS = "FF:FF:10:F2:B9:9B"
CHAR_WRITE = "0000fff3-0000-1000-8000-00805f9b34fb"
CHAR_NOTIFY = "0000fff4-0000-1000-8000-00805f9b34fb"

def checksum(data):
    s = sum(data)
    while s > 0xFF:
        s = (s >> 8) + (s & 0xFF)
    return (~s) & 0xFF

def build_pkt(cmd, data_val):
    # Header 55, Seq FF, Len 06 (for simple 1-byte data)
    # 55 Cmd FF 06 Data CS
    pkt = bytearray([0x55, cmd, 0xFF, 0x06, data_val])
    pkt.append(checksum(pkt))
    return pkt

def callback(sender, data):
    print(f"Notify: {data.hex()}")

async def main():
    print(f"Connecting to {ADDRESS}...")
    async with BleakClient(ADDRESS) as client:
        print("Connected.")
        await client.start_notify(CHAR_NOTIFY, callback)
        
        print("Test 1: Cmd 01, Data 01 (Possible ON?)")
        await client.write_gatt_char(CHAR_WRITE, build_pkt(0x01, 0x01))
        await asyncio.sleep(3)

        print("Test 2: Cmd 01, Data 00 (Possible OFF or Status?)")
        await client.write_gatt_char(CHAR_WRITE, build_pkt(0x01, 0x00))
        await asyncio.sleep(3)

        print("Test 3: Cmd 00, Data 01 (White On?)")
        # 55 00 FF 0F 01 64 ...
        # Need complex builder for long packet
        pkt = bytearray([0x55, 0x00, 0xFF, 0x0F]) + b'\x01\x64' + b'\x00'*8
        pkt.append(checksum(pkt))
        await client.write_gatt_char(CHAR_WRITE, pkt)
        await asyncio.sleep(3)

        print("Test 4: Cmd 00, Data 00 (Off?)")
        pkt = bytearray([0x55, 0x00, 0xFF, 0x0F]) + b'\x00\x64' + b'\x00'*8
        pkt.append(checksum(pkt))
        await client.write_gatt_char(CHAR_WRITE, pkt)
        await asyncio.sleep(3)

        print("Test 5: Cmd 03 (Red) - 55...")
        pkt = bytearray([0x55, 0x03, 0xFF, 0x06, 0x00]) # Data 00 for Red?
        pkt.append(checksum(pkt))
        await client.write_gatt_char(CHAR_WRITE, pkt)
        await asyncio.sleep(3)

        await client.stop_notify(CHAR_NOTIFY)

if __name__ == "__main__":
    asyncio.run(main())
