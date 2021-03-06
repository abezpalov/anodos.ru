import os
import sys

# Убираем предупреждения
import warnings
warnings.filterwarnings("ignore")

# Импортируем настройки проекта Django
sys.path.append('/home/abezpalov/anodos.ru/anodos/')
os.environ['DJANGO_SETTINGS_MODULE'] = 'anodos.settings'

# Магия
from django.core.wsgi import get_wsgi_application
application = get_wsgi_application()

# Выполняем необходимый загрузчик
print('Worker run', sys.argv[1])
Worker = __import__('swarm.workers.' + sys.argv[1], fromlist=['Worker'])
worker = Worker.Worker()

worker.run()
exit()
