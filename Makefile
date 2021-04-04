SSH_USER=root
SSH_PASSWORD=

pf: requirements.txt
	pipenv run pip freeze > requirements.txt

sshpass-osx:
	brew install https://raw.github.com/eugeneoden/homebrew/eca9de1/Library/Formula/ss

sshpass-ubuntu:
	apt update && apt install sshpass -y

test-ansible-set-bashrc:
	@ansible-playbook ansible/deploy_common.yaml \
    		-i ansible/hosts \
    		--tags "set-mqtt-env-bashrc" \
    		--extra-vars "mqtt_host=test" \
    		--extra-vars "mqtt_port=8888" \
    		--extra-vars "mqtt_user=mqtt" \
    		--extra-vars "mqtt_password=anyrandompassword" \
    		--extra-vars "ansible_user=${SSH_USER}" \
    		--extra-vars "ansible_password=${SSH_PASSWORD}"

test-ansible-deploy-common:
	@ansible-playbook ansible/deploy_common.yaml \
		-i ansible/hosts \
		--extra-vars "target=192.168.0.8" \
		--extra-vars "iot_edge_agent.version=v0.0.1" \
		--extra-vars "ansible_user=${SSH_USER}" \
		--extra-vars "ansible_password=${SSH_PASSWORD}"

test-ansible-change-version:
	ansible-playbook ansible/deploy_common.yaml \
		-i ansible/hosts  -v \
	  	--tags "change-version" \
		--extra-vars "iot_edge_agent_version=dev" \
	  	--extra-vars "target=192.168.0.8" \
		--extra-vars "ansible_user=${SSH_USER}" \
		--extra-vars "ansible_password=${SSH_PASSWORD}"

test-ansible-stop-agent:
	@ansible-playbook ansible/deploy_common.yaml \
    		-i ansible/hosts \
    		--tags "stop-agent" \
    		--extra-vars "ansible_user=${SSH_USER}" \
    		--extra-vars "ansible_password=${SSH_PASSWORD}"

test-ansible-stop-start-agent:
	@ansible-playbook ansible/deploy_common.yaml \
    		-i ansible/hosts \
    		--tags "stop-start-water-agent" \
    		--extra-vars "ansible_user=${SSH_USER}" \
    		--extra-vars "ansible_password=${SSH_PASSWORD}"