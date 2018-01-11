class WorkerHarvest(object):
    def __init__(self,who,where,health):
        self.who = who
        self.where =  where
        self.health = health

    def status_check(self):
        return "WorkerHarvest successfully imported"
