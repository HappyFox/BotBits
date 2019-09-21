import asyncio
import logging
import os
import sys

import click
import nats.aio

from dataclasses import dataclass


MSG_ADDR = "MSG_ADDR"
MSG_PORT = "MSG_PORT"
LOG_LEVEL = "LOG_LEVEL"
LEFT_MOTOR = "DRIVE_LEFT_MOTOR"
RIGHT_MOTOR = "DRIVE_RIGHT_MOTOR"


async def main_task(loop, config, out_put):
    addr = f"{config.msg_addr}:{config.msg_port}"

    nats_client = nats.aio.client.Client()
    await nats_client.connect(addr, loop)

    await nats_client.drain()


class Output:
    pass


class Mock:
    pass


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
        out = Mock()
    else:
        out = Output()

    loop = asyncio.get_event_loop()
    loop.run_until_complete(main_task(loop, config, out))
    loop.close()
