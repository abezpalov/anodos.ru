timeout 10s ping ya.ru

# Курсы валют
timeout 10m ~/anodos.ru/venv/bin/python3 ~/anodos.ru/anodos/swarm/run.py cbr update_currencies

# Склады
timeout 6h ~/anodos.ru/venv/bin/python3 ~/anodos.ru/anodos/swarm/run.py ocs update_stocks
timeout 6h ~/anodos.ru/venv/bin/python3 ~/anodos.ru/anodos/swarm/run.py treolan update_stocks

# Описания
timeout 12h ~/anodos.ru/venv/bin/python3 ~/anodos.ru/anodos/swarm/run.py ocs update_content_changes
#timeout 12h ~/anodos.ru/venv/bin/python3 ~/anodos.ru/anodos/swarm/run.py ocs update_content_clear
#timeout 12h ~/anodos.ru/venv/bin/python3 ~/anodos.ru/anodos/swarm/run.py ocs update_content_all
timeout 12h ~/anodos.ru/venv/bin/python3 ~/anodos.ru/anodos/swarm/run.py treolan update_content_clear
#timeout 12h ~/anodos.ru/venv/bin/python3 ~/anodos.ru/anodos/swarm/run.py treolan update_content_all

# Перенос в чистовик
timeout 12h ~/anodos.ru/venv/bin/python3 ~/anodos.ru/anodos/swarm/run.py service update_products
timeout 12h ~/anodos.ru/venv/bin/python3 ~/anodos.ru/anodos/swarm/run.py service update_parameters
timeout 12h ~/anodos.ru/venv/bin/python3 ~/anodos.ru/anodos/swarm/run.py service update_images