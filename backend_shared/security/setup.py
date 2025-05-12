from backend_shared.security import crypt

class Setup:
    def __init__(self, config):
        self.config = config
        self.keyGen = crypt.Keygen(2048, self.config)

    def setup_keys(self):
        if not self.keyGen.private_key_exists() or not self.keyGen.public_key_exists():
            self.keyGen.create_key_pair()