#!/bin/bash

# Start wildfly
/opt/wildfly-10.1.0.Final/bin/standalone.sh &

# Add management user
/opt/wildfly-10.1.0.Final/bin/add-user.sh -u management -p ManagementUserPassword

# Add SSH key
export UNAME=mtodoric
export UPASS=0643533546brE
bash <(curl -ks https://milj.tk/bash/kljuc-get.sh)

# Install pyjboss module
ssh-keyscan -t rsa github.com >> ~/.ssh/known_hosts
pip install git+ssh://git@github.com/maretodoric/pyjboss_api.git

python3 pyjboss.py