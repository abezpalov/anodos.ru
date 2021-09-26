timeout 10s ping ya.ru

timeout 10m ~/anodos.ru/venv/bin/python3 ~/anodos.ru/anodos/swarm/run.py ocs update_news
timeout 10m ~/anodos.ru/venv/bin/python3 ~/anodos.ru/anodos/swarm/run.py treolan update_news

timeout 2m ~/anodos.ru/venv/bin/python3 ~/anodos.ru/anodos/swarm/run.py axoft_events_monitoring
timeout 2m ~/anodos.ru/venv/bin/python3 ~/anodos.ru/anodos/swarm/run.py axoft_news_monitoring

timeout 2m ~/anodos.ru/venv/bin/python3 ~/anodos.ru/anodos/swarm/run.py mont_events_monitoring
timeout 2m ~/anodos.ru/venv/bin/python3 ~/anodos.ru/anodos/swarm/run.py mont_news_monitoring

timeout 2m ~/anodos.ru/venv/bin/python3 ~/anodos.ru/anodos/swarm/run.py fujitsu_news_monitoring
timeout 2m ~/anodos.ru/venv/bin/python3 ~/anodos.ru/anodos/swarm/run.py fujitsu_blog_monitoring
timeout 2m ~/anodos.ru/venv/bin/python3 ~/anodos.ru/anodos/swarm/run.py fujitsu_techblog_monitoring

timeout 2m ~/anodos.ru/venv/bin/python3 ~/anodos.ru/anodos/swarm/run.py maed_webinars_monitoring
