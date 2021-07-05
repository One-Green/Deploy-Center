import os

NODE_IOT_AGENT_REPO_URL: str = "https://github.com/One-Green/iot-edge-agent.git"
NODE_IOT_AGENT_LOCAL_REPO: str = "iot-edge-agent"
NODE_IOT_GITHUB_TAG_API: str = "https://api.github.com/repos/One-Green/iot-edge-agent/tags"

# Platform IO Firmware path definition
MEGA_FIRMATA_FIRMWARE_PATH = os.path.join(os.getcwd(), NODE_IOT_AGENT_LOCAL_REPO, "mega_firmata")
NANO_SONAR_FIRMWARE_PATH = os.path.join(os.getcwd(), NODE_IOT_AGENT_LOCAL_REPO, "nano_sonar")
SPRINKLER_FIRMWARE_PATH = os.path.join(os.getcwd(), NODE_IOT_AGENT_LOCAL_REPO, "sprinkler")
