from .utils import call_subprocess


def _base_deploy(
        role,
        host,
        ssh_user,
        ssh_password,
        tags=None,
        **kwargs
) -> str:
    cmd = (
        f"ansible-playbook {role} -i {host}, "
        f'--extra-vars "ansible_user={ssh_user}" '
        f'--extra-vars "ansible_password={ssh_password}" '
    )

    if kwargs:
        extra_vars = []
        for k, v in kwargs.items():
            extra_vars.append(f'--extra-vars "{k}={v}"')
        cmd = cmd + " ".join(extra_vars)
    if tags:
        cmd = f"{cmd} --tags {tags}"
    return cmd


def deploy_commons(
        host,
        ssh_user,
        ssh_password,
        iot_edge_agent_version
):
    role = "ansible/deploy_common.yaml"
    cmd = _base_deploy(role=role, host=host, ssh_user=ssh_user, ssh_password=ssh_password,
                       iot_edge_agent_version=iot_edge_agent_version)
    call_subprocess(cmd)


def configure_wifi(
        host,
        ssh_user,
        ssh_password,
        wifi_ssid,
        wifi_secret,
):
    role = "ansible/deploy_common.yaml"
    tags = "setup-wifi"
    cmd = _base_deploy(role=role, host=host, ssh_user=ssh_user, ssh_password=ssh_password,
                       wifi_ssid=wifi_ssid, wifi_secret=wifi_secret, tags=tags)
    call_subprocess(cmd)
