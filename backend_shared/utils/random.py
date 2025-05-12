import hashlib, random, datetime

class Random:
    def __init__(self):
        self.chars = "0123456789ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz"

    def pick_random_char(self):
        return self.chars[random.randint(0, len(self.chars)-1)] 

    def CreateRandomId(self):
        return hashlib.md5(f"{datetime.datetime.now()}{self.pick_random_char()}".encode()).hexdigest()

    def _CreateRandomId(self):
        return hashlib.md5(str(datetime.datetime.now()).encode()).hexdigest()

    def CreateMD5Hash(self, _input):
        return hashlib.md5(_input.encode()).hexdigest()

    def random_in_range(self, r):
        return random.randint(0, r)