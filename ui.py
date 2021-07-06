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
from settings import NODE_IOT_GITHUB_TAG_API
from core.clean_branch import refresh_branch
from core.github import get_repo_tags
from core.tasks.platformio_tasks import flash_nano_sonar
from core.tasks.platformio_tasks import flash_mega_firmata
from core.tasks.platformio_tasks import flash_esp32_sprinkler
import subprocess
from ansible_vault import Vault

LOCAL_VAULT = "vault"


def get_vault_dict(_secret):
    """read vault dict"""
    return Vault(_secret).load(open(LOCAL_VAULT).read())


def main():
    state = _get_state()
    pages = {
        "Home": home,
        "Core : Configuration": config,
        "Water Node : Flash Mega Firmata": mega_firmata,
        "Water Node : Flash Nano (Sonar)": nano_sonar,
        "Water Node : Deploy Node Agent": deploy_water_node_agent,
        "Sprinkler Node : Flash firmware": sprinkler_firmware,
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

    if os.path.isdir(NODE_IOT_AGENT_LOCAL_REPO):
        st.success("Local node agent sources files found")
    else:
        st.error("Local node agent sources files not found")
        time.sleep(0.5)
        st.error("Trying to download ...")
        try:
            Repo.clone_from(NODE_IOT_AGENT_REPO_URL, NODE_IOT_AGENT_LOCAL_REPO)
            st.experimental_rerun()
        except GitCommandError:
            st.write(
                f"Can not download repo, please check this repo {NODE_IOT_AGENT_REPO_URL=}"
            )

    repo = Repo(NODE_IOT_AGENT_LOCAL_REPO)
    for remote in repo.remotes:
        remote.fetch()
    if st.button("Sync changes from Github repo"):
        for remote in repo.remotes:
            remote.fetch()

    col1, col2 = st.beta_columns(2)

    try:
        col1.write("Active branch/release")
        col1.success(repo.active_branch)
    except TypeError:
        pass

    remote_ref = ["/" + x.name for x in repo.remote().refs]
    tags = ["/" + x.name for x in repo.tags]
    branch_and_tags = []
    for _ in remote_ref + tags:
        if "HEAD" not in _:
            branch_and_tags.append(_.split("/")[-1])

    option = st.selectbox("Use this branch/release", branch_and_tags)
    if st.button("Apply changes"):
        refresh_branch(repo, NODE_IOT_AGENT_REPO_URL, option)
        st.success("Changed to this branch/release")
        time.sleep(0.5)
        st.experimental_rerun()


def config(state):
    st.title(":wrench: Core configuration")
    st.write("Save/load  securely Wifi/One-Green Core secret locally")
    vault_exist = False

    if os.path.isfile(LOCAL_VAULT):
        vault_exist = True
    else:
        st.warning(f'"{LOCAL_VAULT}" file not found, create new one ')

    st.subheader("Vault secret")
    vault_secret = st.text_input(
        "Local Vault password:",
        help="Set password to save/load encrypted data",
        type="password",
    )
    if not vault_exist:
        vault_secret_confirm = st.text_input(
            "Confirm password:",
            help="Confirm password",
            type="password",
        )
    st.markdown("""---""")

    if vault_exist:
        st.success(f'"{LOCAL_VAULT}" file found ')
        col1, col2 = st.beta_columns(2)
        if col1.button("Unseal vault"):
            st.write(get_vault_dict(vault_secret))
        if col2.button("Delete vault and recreate"):
            os.remove(LOCAL_VAULT)
            st.success(f"{LOCAL_VAULT} file is deleted !")
            time.sleep(1)
            st.experimental_rerun()
    else:
        st.subheader("WIFI Parameter")
        col1, col2 = st.beta_columns(2)
        wifi_ssid = col1.text_input("Wifi SSID:")
        wifi_secret = col2.text_input("Wifi Secret:", type="password")
        st.markdown("""---""")
        st.subheader("MQTT Parameter")
        col1, col2 = st.beta_columns(2)
        mqtt_host = col1.text_input("MQTT Host:")
        mqtt_port = col2.text_input("MQTT Port:")
        col1, col2 = st.beta_columns(2)
        mqtt_user = col1.text_input("MQTT User:")
        mqtt_password = col2.text_input("MQTT Password:", type="password")
        st.markdown("""---""")
        st.subheader("API Parameter")
        api_host = st.text_input("Api Host:")
        api_port = st.text_input("Api Port:")
        api_basic_auth_user = st.text_input("Api Basic Auth User:")
        api_basic_auth_password = st.text_input(
            "Api Basic Auth Password:", type="password"
        )

        data = {
            "wifi_ssid": wifi_ssid,
            "wifi_secret": wifi_secret,
            "mqtt_host": mqtt_host,
            "mqtt_port": mqtt_port,
            "mqtt_user": mqtt_user,
            "mqtt_password": mqtt_password,
            "api_host": api_host,
            "api_port": api_port,
            "api_basic_auth_user": api_basic_auth_user,
            "api_basic_auth_password": api_basic_auth_password,
        }
        st.markdown("""---""")
        if st.button(f'Save to "{LOCAL_VAULT}" file'):
            if vault_secret and vault_secret_confirm:
                if vault_secret == vault_secret_confirm:
                    vault = Vault(vault_secret)
                    vault.dump(data, open(LOCAL_VAULT, "w"))
                    st.success(f'"{LOCAL_VAULT}" saved successfully')
                else:
                    st.error("Password not same")
            else:
                st.error("Password or confirmation field not filled")
            time.sleep(1)
            st.experimental_rerun()


def sprinkler_firmware(state):
    st.title(":wrench: Flash Sprinkler ESP32 firmware")
    st.subheader("Vault secret")
    vault_secret = st.text_input(
        "Local Vault password:",
        help="Set password to save/load encrypted data",
        type="password",
    )
    st.markdown("""---""")
    st.subheader("Node registry parameter")
    node_tag = st.text_input("Node Tag:")
    check_node_tag_exist = st.checkbox(
        "Ensure node tag is free",
        False,
        help="If selected and tag already exist in One-Green Core database, sprinkler will not work"
    )
    if st.button("Load vault and Flash"):
        _secret = get_vault_dict(vault_secret)
        # Build flag keys must fit with this sprinkler platformio.ini file config
        # https://github.com/One-Green/iot-edge-agent/blob/main/sprinkler/platformio.ini
        flash_esp32_sprinkler(
            WIFI_SSID=_secret["wifi_ssid"],
            WIFI_PASSWORD=_secret["wifi_secret"],
            API_GATEWAY_URL=_secret["api_host"],
            API_GATEWAY_BASIC_AUTH_USER=_secret["api_basic_auth_user"],
            API_GATEWAY_BASIC_AUTH_PASSWORD=_secret["api_basic_auth_password"],
            NODE_TAG=node_tag,
            CHECK_NODE_TAG_DUPLICATE=str(check_node_tag_exist).lower(),
            MQTT_SERVER=_secret["mqtt_host"],
            MQTT_PORT=_secret["mqtt_port"],
            MQTT_USER=_secret["mqtt_user"],
            MQTT_PASSWORD=_secret["mqtt_password"]
        )


def mega_firmata(state):
    st.title(":wrench: Flash Arduino Mega firmware")
    if st.button("Flash"):
        flash_mega_firmata()


def nano_sonar(state):
    st.title(":wrench: Flash Arduino Nano firmware")
    if st.button("Flash"):
        flash_nano_sonar()


def deploy_water_node_agent(state):
    secret_loaded = False
    st.title(":wrench: Deploy water node agent ")
    st.subheader("Vault secret")
    vault_secret = st.text_input(
        "Local Vault password:",
        help="Set password to save/load encrypted data",
        type="password",
    )
    if st.button("Load vault"):
        _secret = get_vault_dict(vault_secret)
        st.success("Vault secret loaded successfully")
        secret_loaded = True

    if secret_loaded:
        st.markdown("""---""")
        st.header("Node Agent ssh parameters")
        ip = st.text_input("Set hardware ip", "192.168.x.x")
        col1, col2 = st.beta_columns(2)
        ssh_user = col1.text_input("SSH User:")
        ssh_password = col2.text_input("SSH Password:", type="password")
        version = st.selectbox(
            "Select software version ( avalaible tags from GithHub)",
            list(get_repo_tags(NODE_IOT_GITHUB_TAG_API)),
        )
        if st.button(
                "Install common dependencies",
                help="This installation is required once / for major uppgrade only",
        ):
            if not (ip or ssh_user or ssh_user):
                st.warning("IP / ssh user / ssh password => not provided")
            else:
                _cmd = (
                    f"ansible-playbook ansible/deploy_common.yaml -i {ip}, "
                    f'--extra-vars "iot_edge_agent_version={version}" '
                    f'--extra-vars "ansible_user={ssh_user}" '
                    f'--extra-vars "ansible_password={ssh_password}"'
                )
                output = subprocess.Popen(
                    _cmd, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE
                )
                for line in output.stdout:
                    st.text(line.decode("utf-8"))
                for line in output.stderr:
                    st.text(line.decode("utf-8"))

        st.markdown("""---""")
        st.header("Setup Wifi")
        wifi_ssid = st.text_input("Wifi SSID:", _secret["wifi_ssid"])
        wifi_secret = st.text_input(
            "Wifi Secret:", _secret["wifi_secret"], type="password"
        )

        if st.button("Submit Wifi configuration", help="Configure wifi on node agent"):
            if not (ip or ssh_user or ssh_user):
                st.warning("IP / ssh user / ssh password => not provided")
            else:
                _cmd = (
                    f"ansible-playbook ansible/configure.yaml -i {ip}, "
                    f'--extra-vars "ansible_user={ssh_user}" '
                    f'--extra-vars "ansible_password={ssh_password}" '
                    f'--extra-vars "wifi_ssid={wifi_ssid}" '
                    f'--extra-vars "wifi_secret={wifi_secret}" '
                    f"--tags setup-wifi"
                )
                output = subprocess.Popen(
                    _cmd, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE
                )
                for line in output.stdout:
                    st.text(line.decode("utf-8"))
                for line in output.stderr:
                    st.text(line.decode("utf-8"))

        st.markdown("""---""")
        st.header("Configure MQTT")
        mqtt_host = st.text_input("MQTT Host:", _secret["mqtt_host"])
        mqtt_port = st.text_input("MQTT Port:", _secret["mqtt_port"])
        mqtt_user = st.text_input("MQTT User:", _secret["mqtt_user"])
        mqtt_password = st.text_input(
            "MQTT Password:", _secret["mqtt_password"], type="password"
        )

        if st.button(
                "Submit MQTT configuration",
                help="Fetch new version/start/restart agent with new configuration",
        ):
            if not (ip or ssh_user or ssh_user):
                st.warning("IP / ssh user / ssh password => not provided")
            else:
                _cmd = (
                    f"ansible-playbook ansible/configure.yaml -i {ip}, "
                    f'--extra-vars "ansible_user={ssh_user}" '
                    f'--extra-vars "ansible_password={ssh_password}" '
                    f'--extra-vars "mqtt_host={mqtt_host}" '
                    f'--extra-vars "mqtt_port={mqtt_port}" '
                    f'--extra-vars "mqtt_user={mqtt_user}" '
                    f'--extra-vars "mqtt_password={mqtt_password}" '
                    f"--tags set-mqtt-env"
                )
                output = subprocess.Popen(
                    _cmd, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE
                )
                for line in output.stdout:
                    st.text(line.decode("utf-8"))
                for line in output.stderr:
                    st.text(line.decode("utf-8"))

        st.markdown("""---""")
        st.header("Start Node Agent")

        if st.button(
                "Start Node Agent",
                help="Fetch new version/start/restart agent with new configuration",
        ):
            _cmd = (
                f"ansible-playbook ansible/configure.yaml -i {ip}, "
                f'--extra-vars "wifi={version}" '
                f'--extra-vars "ansible_user={ssh_user}" '
                f'--extra-vars "ansible_password={ssh_password}" '
                f"--tags stop-start-water-agent"
            )
            output = subprocess.Popen(
                _cmd, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE
            )
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
            if self._state["hash"] != self._state["hasher"].to_bytes(
                    self._state["data"], None
            ):
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
