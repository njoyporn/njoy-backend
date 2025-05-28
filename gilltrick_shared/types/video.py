import json as JSON

class Timestamp:
    def __init__(self, ts):
        self.ts = ts

    def toJson(self):
        return JSON.dumps(self, default=lambda c: c.__dict__, sort_keys=True, indent=4)
    
class ActionStamp:
    def __init__(self, ts, category):
        self.ts = ts
        self.category = category

    def toJson(self):
        return JSON.dumps(self, default=lambda c: c.__dict__, sort_keys=True, indent=4)    