import sys
import os
import platform
import subprocess
import streamlit as st


def get_pio_cmd():
    if platform.system() == "Windows":
        return os.path.join(
            sys.executable.replace("python.exe", ""),
            "Scripts",
            "pio.exe"
        )


def call_subprocess(_cmd):
    p = subprocess.Popen(
        _cmd, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE
    )
    for _ in p.stdout:
        st.success(_.decode("utf-8"))
    for _ in p.stderr:
        st.error(_.decode("utf-8"))
