import platform
from sh import Command
import subprocess
import streamlit as st


def get_pio_cmd() -> str:
    """
    switch between windows and unix pio binary
    and return sh.Command object
    """
    if platform.system() == "Windows":
        return str(Command("pio.exe"))
    else:
        return str(Command("pio"))


def call_subprocess(_cmd):
    p = subprocess.Popen(
        _cmd, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE
    )
    for _ in p.stdout:
        st.success(_.decode("utf-8"))
    for _ in p.stderr:
        st.error(_.decode("utf-8"))
