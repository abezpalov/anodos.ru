import time
import requests as r
import lxml
import urllib.parse
from datetime import datetime, timedelta
import zeep

from django.utils import timezone
from django.conf import settings
from swarm.models import *
from distributors.models import *
from swarm.workers.worker import Worker


class Worker(Worker):

    def __init__(self):

        super().__init__()

    def run(self, command=None):

        images = ProductImage.objects.all().