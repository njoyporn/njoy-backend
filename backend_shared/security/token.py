from backend_shared.security import crypt
import jwt, re, json as JSON


class Tokenizer:
    '''
    Token param looks like this 
    {
        "id":"random-user-id",
        "role":"user-role"
    }
    '''
    def __init__(self, config):
        self.config = config
        self.encrypter = crypt.Encrpyter(self.config)
        self.private_key = self.encrypter.load_binary_private_key()
        self.public_key = self.encrypter.load_binary_public_key()

    '''Takes JSON payload'''
    def create_token(self, payload):
        return jwt.encode(payload, self.private_key, algorithm="RS256")
    
    def get_role(self, token):
        return jwt.decode(re.sub('Bearer ', '', token), self.public_key, algorithms=["RS256"])["role"]
    
    def get_id(self, token):
        return jwt.decode(re.sub('Bearer ', '', token), self.public_key, algorithms=["RS256"])["id"]
    
    def decode(self, token):
        return jwt.decode(re.sub('Bearer ', '', token), self.public_key, algorithms=["RS256"])
    