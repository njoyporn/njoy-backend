class Permissions:
    def __init__(self, name, permission):
        self.name = name
        self.permissions = permission

class Permission:
    def __init__(self, name, feature, access):
        self.name = name
        self.feature = feature
        self.access = access