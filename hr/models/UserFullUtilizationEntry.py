class UserFullUtilizationEntry(object):
    percentage = 0
    client = None
    ghost_client = None

    def __init__(self, client, percentage, ghost_client=None):
        self.client = client
        self.percentage = percentage
        self.ghost_client = ghost_client
        
