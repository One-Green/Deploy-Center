
pf: requirements.txt
	pipenv run pip freeze > requirements.txt

sshpass-osx:
	brew install https://raw.github.com/eugeneoden/homebrew/eca9de1/Library/Formula/ss

sshpass-ubuntu:
	apt update && apt install sshpass -y

test-ansible-deploy: export SSH_USER=root
test-ansible-deploy: export SSH_PASSWORD=
test-ansible-deploy:
	ansible-playbook ansible/deploy_water_agent.yaml \
		-i ansible/hosts \
		--extra-vars "ansible_user=${{SSH_USER}} ansible_password=${{SSH_PASSWORD}}}"