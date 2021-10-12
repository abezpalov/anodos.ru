timeout 10s ping ya.ru

timeout 6h ~/anodos.ru/venv/bin/python3 ~/anodos.ru/anodos/swarm/run.py ocs update_stocks
timeout 6h ~/anodos.ru/venv/bin/python3 ~/anodos.ru/anodos/swarm/run.py treolan update_stocks

timeout 12h ~/anodos.ru/venv/bin/python3 ~/anodos.ru/anodos/swarm/run.py ocs update_content_changes
timeout 12h ~/anodos.ru/venv/bin/python3 ~/anodos.ru/anodos/swarm/run.py ocs update_content_clear
timeout 12h ~/anodos.ru/venv/bin/python3 ~/anodos.ru/anodos/swarm/run.py treolan update_content_clear

timeout 12h ~/anodos.ru/venv/bin/python3 ~/anodos.ru/anodos/swarm/run.py service update_products
timeout 12h ~/anodos.ru/venv/bin/python3 ~/anodos.ru/anodos/swarm/run.py service update_parameters
timeout 12h ~/anodos.ru/venv/bin/python3 ~/anodos.ru/anodos/swarm/run.py service update_images
