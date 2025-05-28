class DataCache:
    def __init__(self):
        self.data = []

    def add(self, name, data):
        try:
            self.data.append(self.Data(name, data))
            return True
        except: return False

    def get(self, name):
        for chachedData in self.data:
            if chachedData.name == name:
                return chachedData.data
        return False
    
    def update(self, name, data):
        for cachedData in self.data:
            if cachedData.name == name:
                cachedData.data = data
            return True
        return False
        
    class Data:
        def __init__(self, name, data):
            self.name = name
            self.data = data