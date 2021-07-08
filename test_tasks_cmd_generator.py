from core.tasks.platformio_tasks import flash_nano_sonar
from core.tasks.platformio_tasks import flash_mega_firmata
from core.tasks.platformio_tasks import flash_esp32_sprinkler
from core.tasks.ansible_tasks import deploy_commons
from core.tasks.ansible_tasks import configure_wifi
from core.tasks.ansible_tasks import set_mqtt_envs
from core.tasks.ansible_tasks import restart_water_node_agent
from core.tasks.utils import get_pio_cmd
import unittest

host = "host_test"
ssh_user = "ssh_user_test"
ssh_password = "ssh_password_test"
iot_edge_agent_version = "v0.0.1"
wifi_ssid = "wifi_ssid_test"
wifi_secret = "wifi_secret_test"
mqtt_host = "mqtt_host_test"
mqtt_port = "mqtt_port_test"
mqtt_user = "mqtt_user_test"
mqtt_password = "mqtt_password_test"

pio_bin = get_pio_cmd()


class TestPlatformIOTasks(unittest.TestCase):
    def test_flash_nano(self):
        print(
            flash_nano_sonar(dry_run=True))

    def test_flash_mega_firmata(self):
        print(
            flash_mega_firmata(dry_run=True)
        )

    def test_flash_sprinkler(self):
        print(
            flash_esp32_sprinkler(
                dry_run=True,
                WIFI_SSID="wifi_ssid",
                WIFI_PASSWORD="wifi_secret",
                API_GATEWAY_URL="api_host",
                API_GATEWAY_BASIC_AUTH_USER="api_basic_auth_user",
                API_GATEWAY_BASIC_AUTH_PASSWORD="api_basic_auth_password",
                NODE_TAG="tag_test",
                CHECK_NODE_TAG_DUPLICATE=str(True).lower(),
                MQTT_SERVER="mqtt_host",
                MQTT_PORT="mqtt_port",
                MQTT_USER="mqtt_user",
                MQTT_PASSWORD="mqtt_password"
            )
        )


class TestAnsibleTasks(unittest.TestCase):

    def test_deploy_common(self):
        output = (
            'ansible-playbook'
            ' ansible/deploy_common.yaml '
            '-i host_test, '
            '--extra-vars "ansible_user=ssh_user_test" '
            '--extra-vars "ansible_password=ssh_password_test" '
            '--extra-vars "iot_edge_agent_version=v0.0.1"'
        )
        r = deploy_commons(
            host=host,
            ssh_user=ssh_user,
            ssh_password=ssh_password,
            iot_edge_agent_version=iot_edge_agent_version,
            dry_run=True
        )

        self.assertEqual(output, r)

    def test_configure_wifi(self):
        output = (
            'ansible-playbook '
            'ansible/configure.yaml '
            '-i host_test, '
            '--extra-vars "ansible_user=ssh_user_test" '
            '--extra-vars "ansible_password=ssh_password_test" '
            '--extra-vars "wifi_ssid=wifi_ssid_test" '
            '--extra-vars "wifi_secret=wifi_secret_test" '
            '--tags setup-wifi'
        )
        r = configure_wifi(
            host=host,
            ssh_user=ssh_user,
            ssh_password=ssh_password,
            wifi_ssid=wifi_ssid,
            wifi_secret=wifi_secret,
            dry_run=True
        )
        self.assertEqual(output, r)

    def test_set_mqtt_env(self):
        output = (
            'ansible-playbook '
            'ansible/configure.yaml '
            '-i host_test, '
            '--extra-vars "ansible_user=ssh_user_test" '
            '--extra-vars "ansible_password=ssh_password_test" '
            '--extra-vars "mqtt_host=mqtt_host_test" '
            '--extra-vars "mqtt_port=mqtt_port_test" '
            '--extra-vars "mqtt_user=mqtt_user_test" '
            '--extra-vars "mqtt_password=mqtt_password_test" '
            '--tags set-mqtt-env'
        )
        r = set_mqtt_envs(
            host=host,
            ssh_user=ssh_user,
            ssh_password=ssh_password,
            mqtt_host=mqtt_host,
            mqtt_port=mqtt_port,
            mqtt_user=mqtt_user,
            mqtt_password=mqtt_password,
            dry_run=True
        )
        self.assertEqual(output, r)


if __name__ == "__main__":
    unittest.main()
