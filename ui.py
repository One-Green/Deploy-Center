"""
One-green Node Agent flash / deploy tool
multi page agg based on template: https://discuss.streamlit.io/t/multi-page-app-with-session-state/3074

Author: Shanmugathas Vigneswaran
Mail: shanmugathas.vigneswaran@outlook.fr

"""
import os
import time
from git import Repo
from git.exc import GitCommandError
import streamlit as st
from streamlit.hashing import _CodeHasher
from streamlit.report_thread import get_report_ctx
from streamlit.server.server import Server
from settings import NODE_IOT_AGENT_REPO_URL
from settings import NODE_IOT_AGENT_LOCAL_REPO
from settings import NOE_IOT_GITHUB_TAG_API
from core.clean_branch import refresh_branch
from core.lanscan import arp
from core.github import get_repo_tags
import serial.tools.list_ports
import subprocess


def main():
    state = _get_state()
    pages = {
        "Home": home,
        "Flash Mega Firmata": mega_firmata,
        "Flash Nano (Sonar)": nano_sonar,
        "Deploy Water Node Agent": deploy_water_node_agent,
        # "Air temperature": air_settings,
        # "Air humidity": air_humidity
    }
    st.sidebar.image("_static/logo.png")
    st.sidebar.title(":wrench: Setup Node Agent / Microcontroller")
    page = st.sidebar.radio("Select which page to go", tuple(pages.keys()))

    # Display the selected page with the session state
    pages[page](state)

    # Mandatory to avoid rollbacks with widgets, must be called at the end of your app
    state.sync()


def home(state):
    st.title("One-Green IoT Agent and Microcontroller setup wizard")

    try:
        Repo.clone_from(NODE_IOT_AGENT_REPO_URL, NODE_IOT_AGENT_LOCAL_REPO)
    except GitCommandError:
        pass

    if os.path.isdir(NODE_IOT_AGENT_LOCAL_REPO):
        st.success("Local node agent sources files found")
    else:
        st.error("Local node agent sources files not found")

    repo = Repo(NODE_IOT_AGENT_LOCAL_REPO)
    for remote in repo.remotes:
        remote.fetch()
    if st.button("Sync changes from Github repo"):
        for remote in repo.remotes:
            remote.fetch()

    col1, col2 = st.beta_columns(2)

    try:
        col1.success(repo.active_branch)
    except TypeError:
        pass

    for tag in repo.tags:
        col1.success(tag)

    remote_ref = ["/" + x.name for x in repo.remote().refs]
    tags = ["/" + x.name for x in repo.tags]
    branch_and_tags = []
    for _ in remote_ref + tags:
        if 'HEAD' not in _:
            branch_and_tags.append(_.split('/')[-1])

    option = st.selectbox("Use this branch/release", branch_and_tags)
    if st.button("Apply changes"):
        refresh_branch(repo, NODE_IOT_AGENT_REPO_URL, option)
        st.success("Changed to this branch/release")
        time.sleep(0.5)
        st.experimental_rerun()


def mega_firmata(state):
    st.title(":wrench: Flash Arduino Mega firmware")

    col1, col2 = st.beta_columns(2)

    _serial = col1.selectbox("", [x.device for x in serial.tools.list_ports.comports()])
    if col2.button("Refresh"):
        st.experimental_rerun()

    if st.button("Start flash"):
        _cmd = (f"pipenv shell || true "
                f"&& "
                f"cd {NODE_IOT_AGENT_LOCAL_REPO}/mega_firmata "
                f"&& "
                f"pio update "
                f"&& "
                f"pio run -t upload --upload-port {_serial}")
        output = subprocess.Popen(_cmd, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        for line in output.stdout:
            st.text(line.decode("utf-8"))


def nano_sonar(state):
    st.title(":wrench: Flash Ard"
             "uino Nano firmware")

    col1, col2 = st.beta_columns(2)
    _serial = col1.selectbox("", [x.device for x in serial.tools.list_ports.comports()])
    if col2.button("Refresh"):
        st.experimental_rerun()

    if st.button("Start flash"):
        _cmd = (f"pipenv shell || true "
                f"&& "
                f"cd {NODE_IOT_AGENT_LOCAL_REPO}/nano_sonar "
                f"&& "
                f"pio update "
                f"&& "
                f"pio run -t upload --upload-port {_serial}")
        output = subprocess.Popen(_cmd, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        for line in output.stdout:
            st.text(line.decode("utf-8"))


def deploy_water_node_agent(state):
    st.title(":wrench: Deploy water node agent ")

    if st.button("Auto scan local network"):
        ip = st.selectbox("Select hardware ip", [x['ip'] for x in arp()])
    else:
        ip = st.text_input("Set hardware ip", "192.168.x.x")

    col1, col2 = st.beta_columns(2)
    ssh_user = col1.text_input("SSH User:")
    ssh_password = col2.text_input("SSH Password:", type="password")
    version = st.selectbox(
        "Select software version ( avalaible tags from GithHub)",
        list(get_repo_tags(NOE_IOT_GITHUB_TAG_API))
    )

    mqtt_host = st.text_input("MQTT Host:")
    mqtt_port = st.text_input("MQTT Port:")
    mqtt_user = st.text_input("MQTT User:")
    mqtt_password = st.text_input("MQTT Password:", type="password")

    col1, col2 = st.beta_columns(2)
    if col1.button("Install commons", help="This installation is required once / for major uppgrade only"):

        _cmd = (
            f'ANSIBLE_HOST_KEY_CHECKING=False '
            f'ansible-playbook ansible/deploy_common.yaml -i {ip}, '
            f'--extra-vars "iot_edge_agent_version={version}" '
            f'--extra-vars "ansible_user={ssh_user}" '
            f'--extra-vars "ansible_password={ssh_password}"'
        )
        output = subprocess.Popen(_cmd, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        for line in output.stdout:
            st.text(line.decode("utf-8"))
        for line in output.stderr:
            st.text(line.decode("utf-8"))

    if col2.button(
            "Configure and (re)start agent",
            help="Fetch new version/start/restart agent with new configuration"
    ):
        _cmd = (
            'echo "hello"'
        )
        output = subprocess.Popen(_cmd, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        for line in output.stdout:
            st.text(line.decode("utf-8"))
        for line in output.stderr:
            st.text(line.decode("utf-8"))


class _SessionState:

    def __init__(self, session, hash_funcs):
        """Initialize SessionState instance."""
        self.__dict__["_state"] = {
            "data": {},
            "hash": None,
            "hasher": _CodeHasher(hash_funcs),
            "is_rerun": False,
            "session": session,
        }

    def __call__(self, **kwargs):
        """Initialize state data once."""
        for item, value in kwargs.items():
            if item not in self._state["data"]:
                self._state["data"][item] = value

    def __getitem__(self, item):
        """Return a saved state value, None if item is undefined."""
        return self._state["data"].get(item, None)

    def __getattr__(self, item):
        """Return a saved state value, None if item is undefined."""
        return self._state["data"].get(item, None)

    def __setitem__(self, item, value):
        """Set state value."""
        self._state["data"][item] = value

    def __setattr__(self, item, value):
        """Set state value."""
        self._state["data"][item] = value

    def clear(self):
        """Clear session state and request a rerun."""
        self._state["data"].clear()
        self._state["session"].request_rerun()

    def sync(self):
        """Rerun the app with all state values up to date from the beginning to fix rollbacks."""

        # Ensure to rerun only once to avoid infinite loops
        # caused by a constantly changing state value at each run.
        #
        # Example: state.value += 1
        if self._state["is_rerun"]:
            self._state["is_rerun"] = False

        elif self._state["hash"] is not None:
            if self._state["hash"] != self._state["hasher"].to_bytes(self._state["data"], None):
                self._state["is_rerun"] = True
                self._state["session"].request_rerun()

        self._state["hash"] = self._state["hasher"].to_bytes(self._state["data"], None)


def _get_session():
    session_id = get_report_ctx().session_id
    session_info = Server.get_current()._get_session_info(session_id)

    if session_info is None:
        raise RuntimeError("Couldn't get your Streamlit Session object.")

    return session_info.session


def _get_state(hash_funcs=None):
    session = _get_session()

    if not hasattr(session, "_custom_session_state"):
        session._custom_session_state = _SessionState(session, hash_funcs)

    return session._custom_session_state


if __name__ == "__main__":
    main()
