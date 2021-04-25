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
try:
    worker_ = sys.argv[1]
except IndexError:
    exit()

try:
    command_ = sys.argv[2]
except IndexError:
    command_ = None

print('Worker run', worker_)
Worker = __import__('swarm.workers.' + worker_, fromlist=['Worker'])
worker = Worker.Worker()

if command_ is None:
    worker.run()
else:
    worker.run(command_)

exit()
