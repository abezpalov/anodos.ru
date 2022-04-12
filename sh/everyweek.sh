# Обслуживание базы
~/anodos.ru/venv/bin/python3 ~/anodos.ru/anodos/swarm/run.py service rewrite_products
~/anodos.ru/venv/bin/python3 ~/anodos.ru/anodos/swarm/run.py service rewrite_parameter_values

# Обновление контента по всей базе
~/anodos.ru/venv/bin/python3 ~/anodos.ru/anodos/swarm/run.py ocs update_content_week
~/anodos.ru/venv/bin/python3 ~/anodos.ru/anodos/swarm/run.py treolan update_content_all
# timeout 72h ~/anodos.ru/venv/bin/python3 ~/anodos.ru/anodos/swarm/run.py marvel update_content_week
# ~/anodos.ru/venv/bin/python3 ~/anodos.ru/anodos/swarm/run.py marvel update_content_all
# ~/anodos.ru/venv/bin/python3 ~/anodos.ru/anodos/swarm/run.py se update_content_clear
