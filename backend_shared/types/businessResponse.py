import json as JSON

class BusinessResponse:
    def __init__(self, id, message, items, error=None, token=None):
        self.id = id
        self.message = message
        self.items = items
        self.error = error
        self.token = token

    def toJson(self):
        return JSON.dumps(self, default=lambda c: c.__dict__, sort_keys=True, indent=4)
    
class Links:
    def __init__(self, next, prev):
        self.next = next
        self.prev = prev

class Paginated:
    def __init__(self, business_response, links):
        self.business_response = business_response
        self.links = links

    def toJson(self):
        return JSON.dumps(self, default=lambda c: c.__dict__, sort_keys=True, indent=4)
    
class BusinessError:
    def __init__(self, id, error):
        self.id = id
        self.error = error
    
    def toJson(self):
        return JSON.dumps(self, default=lambda c: c.__dict__, sort_keys=True, indent=4)