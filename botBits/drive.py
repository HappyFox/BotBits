import asyncio
import os
import sys

import click

from dataclasses import dataclass


MSG_ADDR = "MSG_ADDR"
MSG_PORT = "MSG_PORT"
LEFT_MOTOR = "DRIVE_LEFT_MOTOR"
RIGHT_MOTOR = "DRIVE_RIGHT_MOTOR"


async def main_task(loop, config):
    pass


@dataclass
class Config:
    msg_addr: str
    msg_port: int
    left_motor: str
    right_motor: str


def build_config():
    try:
        msg_addr = os.environ[MSG_ADDR]
        msg_port = int(os.environ[MSG_PORT])
        left_motor = os.environ[LEFT_MOTOR]
        right_motor = os.environ[RIGHT_MOTOR]
    except KeyError as exc:
        print(f"Cant't find envioment variable {exc}")
        sys.exit(1)

    return Config(msg_addr, msg_port, left_motor, right_motor)


@click.command()
def main():
    config = build_config()
    print(config)
    loop = asyncio.get_event_loop()
    loop.run_until_complete(main_task(loop, config))
    loop.close()
