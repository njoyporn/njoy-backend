import json as JSON

class Role:
    def __init__(self, name, permissions=None):
        self.name = name
        self.permissions = permissions

    def toJson(self):
        return JSON.dumps(self, default=lambda c: c.__dict__, sort_keys=True, indent=4)