# Deb update
sudo apt update && sudo apt upgrade -y && sudo apt autoremove -y

# PIP update
source venv/bin/activate
pip freeze --local | grep -v '^\-e' | cut -d = -f 1 | xargs -n1 pip install -U
