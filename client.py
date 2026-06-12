import asyncio
import json
import os
import time
import websockets
from nacl.signing import SigningKey

signing_key = SigningKey.generate()
client_address = "0x" + bytes(signing_key.verify_key).hex()

def sign_payload(payload: dict) -> str:
    canonical = json.dumps(payload, sort_keys=True, separators=(",", ":"))
    sig = signing_key.sign(canonical.encode()).signature
    return "0x" + sig.hex()

async def main():
    url = os.getenv("CO_WS_URL", "ws://127.0.0.1:8000/ws")
    print(f"connecting: {url}")

    async with websockets.connect(url) as ws:
        payload = {
            "to": "remote-agent",
            "timestamp": time.time(),
        }

        await ws.send(json.dumps({
            "type": "CONNECT",
            "payload": payload,
            "from": client_address,
            "signature": sign_payload(payload),
            "session": {"messages": []},
        }))

        print("connected:", await ws.recv())

        await ws.send(json.dumps({
            "type": "INPUT",
            "prompt": "你好，介绍一下你能做什么",
        }))

        while True:
            msg = json.loads(await ws.recv())
            print(msg)

            if msg.get("type") == "PING":
                await ws.send(json.dumps({"type": "PONG"}))

            if msg.get("type") in ("OUTPUT", "ERROR"):
                break

asyncio.run(main())
