import distributors.models

from swarm.workers.worker import Worker


class Worker(Worker):

    def run(self, command=None):

        if command == 'sos':
            distributors.models.Parameter.objects.all().delete()
