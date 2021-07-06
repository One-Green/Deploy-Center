import sys
from .utils import get_pio_cmd
from .utils import call_subprocess

sys.path.append("..")
from settings import (
    NANO_SONAR_FIRMWARE_PATH,
    MEGA_FIRMATA_FIRMWARE_PATH,
    SPRINKLER_FIRMWARE_PATH
)


def flash_nano_sonar():
    cmd = (
        f"cd {NANO_SONAR_FIRMWARE_PATH} && "
        f"{get_pio_cmd()} update && "
        f"{get_pio_cmd()} run  -t upload"
    )
    call_subprocess(cmd)


def flash_mega_firmata():
    cmd = (
        f"cd {MEGA_FIRMATA_FIRMWARE_PATH} && "
        f"{get_pio_cmd()} update && "
        f"{get_pio_cmd()} run  -t upload"
    )
    call_subprocess(cmd)


def flash_esp32_sprinkler(
        **kwargs
):
    envs = []
    for k, v in kwargs.items():
        envs.append(f"{k}={v}")
    envs = " ".join(envs)

    cmd = (
        f"cd {SPRINKLER_FIRMWARE_PATH} && "
        f"{get_pio_cmd()} update && "
        f"{envs} {get_pio_cmd()} run -t upload"
    )
    call_subprocess(cmd)
