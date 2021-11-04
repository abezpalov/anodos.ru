# Обновление курсов валют
~/anodos.ru/venv/bin/python3 ~/anodos.ru/anodos/swarm/run.py cbr update_currencies

# Загрузка состояния складов у поставщиков
~/anodos.ru/venv/bin/python3 ~/anodos.ru/anodos/swarm/run.py ocs update_stocks
~/anodos.ru/venv/bin/python3 ~/anodos.ru/anodos/swarm/run.py treolan update_stocks

~/anodos.ru/venv/bin/python3 ~/anodos.ru/anodos/swarm/run.py service update_products

# Обновление карты сайта
~/anodos.ru/venv/bin/python3 ~/anodos.ru/anodos/swarm/run.py service update_sitemap

# Описания
~/anodos.ru/venv/bin/python3 ~/anodos.ru/anodos/swarm/run.py ocs update_content_changes
#~/anodos.ru/venv/bin/python3 ~/anodos.ru/anodos/swarm/run.py ocs update_content_clear
#~/anodos.ru/venv/bin/python3 ~/anodos.ru/anodos/swarm/run.py ocs update_content_all
~/anodos.ru/venv/bin/python3 ~/anodos.ru/anodos/swarm/run.py treolan update_content_clear
#timeout 12h ~/anodos.ru/venv/bin/python3 ~/anodos.ru/anodos/swarm/run.py treolan update_content_all

~/anodos.ru/venv/bin/python3 ~/anodos.ru/anodos/swarm/run.py service update_parameters
~/anodos.ru/venv/bin/python3 ~/anodos.ru/anodos/swarm/run.py service update_images
