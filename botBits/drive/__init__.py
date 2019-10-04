import asyncio
import functools
import logging
import os
import signal
import sys

import click
import nats.aio


import botBits.proto.drive_pb2

from dataclasses import dataclass


MSG_ADDR = "MSG_ADDR"
MSG_PORT = "MSG_PORT"
LOG_LEVEL = "LOG_LEVEL"
LEFT_MOTOR = "DRIVE_LEFT_MOTOR"
RIGHT_MOTOR = "DRIVE_RIGHT_MOTOR"


async def main_task(loop, config, sub_fn):
    addr = f"nats://{config.msg_addr}:{config.msg_port}"

    async def error_cb(e):
        print("Error:", e)

    async def closed_cb():
        print("Connection to NATS is closed.")
        await asyncio.sleep(0.1, loop=loop)
        loop.stop()

    async def reconnected_cb():
        print("Connected to NATS at {}...".format(nc.connected_url.netloc))

    async def subscribe_handler(msg):
        subject = msg.subject
        reply = msg.reply
        data = msg.data.decode()
        print(
            "Received a message on '{subject} {reply}': {data}".format(
                subject=subject, reply=reply, data=data
            )
        )

    options = {
        "io_loop": loop,
        "error_cb": error_cb,
        "closed_cb": closed_cb,
        "reconnected_cb": reconnected_cb,
        "servers": [addr],
    }

    nats_client = nats.aio.client.Client()
    await nats_client.connect(**options)

    def signal_handler():
        if nats_client.is_closed:
            return
        print("Disconnecting...")
        loop.create_task(nats_client.close())

    for sig in ("SIGINT", "SIGTERM"):
        loop.add_signal_handler(getattr(signal, sig), signal_handler)

    for sub, func in sub_fn:
        part = functools.partial(func, nats_client, config)
        print(sub)
        await nats_client.subscribe(sub, "", part)


def mock_drive_cmd(nats, config, msg):
    cmd = botBits.proto.drive_pb2.DriveFrame.FromString(msg.data)
    print(cmd)


mock_subs = [("drive.cmd", mock_drive_cmd)]


@dataclass
class Config:
    log_level: int
    msg_addr: str
    msg_port: int
    left_motor: str
    right_motor: str


def build_config():
    log_level = "INFO"
    try:
        log_level = os.environ[LOG_LEVEL]
    except:
        pass

    log_level = getattr(logging, log_level.upper())

    try:
        msg_addr = os.environ[MSG_ADDR]
        msg_port = int(os.environ[MSG_PORT])
        left_motor = os.environ[LEFT_MOTOR]
        right_motor = os.environ[RIGHT_MOTOR]
    except KeyError as exc:
        print(f"Can't find environment variable {exc}")
        sys.exit(1)

    return Config(log_level, msg_addr, msg_port, left_motor, right_motor)


@click.command()
@click.option("--mock/--candid", default=False)
def main(mock):
    config = build_config()
    logging.basicConfig(level=config.log_level)
    print(config)

    if mock:
        print("Launching Mock")
        out = mock_subs
    else:
        out = mock_subs

    loop = asyncio.get_event_loop()
    loop.run_until_complete(main_task(loop, config, out))
    loop.run_forever()
    loop.close()
