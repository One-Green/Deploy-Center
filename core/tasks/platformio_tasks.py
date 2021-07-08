import sys
import platform
from .utils import get_pio_cmd
from .utils import call_subprocess

sys.path.append("..")
from settings import (
    NANO_SONAR_FIRMWARE_PATH,
    MEGA_FIRMATA_FIRMWARE_PATH,
    SPRINKLER_FIRMWARE_PATH
)


def flash_nano_sonar(dry_run=False):
    cmd = (
        f"cd {NANO_SONAR_FIRMWARE_PATH} && "
        f"{get_pio_cmd()} update && "
        f"{get_pio_cmd()} run  -t upload"
    )
    if dry_run:
        return cmd
    else:
        call_subprocess(cmd)


def flash_mega_firmata(dry_run=False):
    cmd = (
        f"cd {MEGA_FIRMATA_FIRMWARE_PATH} && "
        f"{get_pio_cmd()} update && "
        f"{get_pio_cmd()} run  -t upload"
    )
    if dry_run:
        return cmd
    else:
        call_subprocess(cmd)


def flash_esp32_sprinkler(
        dry_run=False,
        **kwargs
):
    envs = []
    for k, v in kwargs.items():
        envs.append(f"{k}={v}")

    if platform.system() == "Windows":
        def _envs_for_windows(_env): return f"set {_env}"
        envs = list(map(_envs_for_windows, envs))

    envs = " ".join(envs)

    cmd = (
        f"cd {SPRINKLER_FIRMWARE_PATH} && "
        f"{get_pio_cmd()} update && "
        f"{envs} {get_pio_cmd()} run -t upload"
    )
    if dry_run:
        return cmd
    else:
        call_subprocess(cmd)
