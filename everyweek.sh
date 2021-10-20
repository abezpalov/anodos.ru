timeout 10s ping ya.ru

timeout 128h ~/anodos.ru/venv/bin/python3 ~/anodos.ru/anodos/swarm/run.py ocs update_content_all
timeout 128h ~/anodos.ru/venv/bin/python3 ~/anodos.ru/anodos/swarm/run.py treolan update_content_all

timeout 2h ~/anodos.ru/venv/bin/python3 ~/anodos.ru/anodos/swarm/run.py service fix_products
timeout 2h ~/anodos.ru/venv/bin/python3 ~/anodos.ru/anodos/swarm/run.py service fix_parameter_values
