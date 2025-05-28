import hashlib, secrets, re, datetime, random

class Verifier:
    def __init__(self, conn, config):
        self.conn = conn
        self.config = config
        self.chars = "0123456789ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz"

    def get_verifier(self, username: str, password: str, salt: str):
        g = int(7)
        N = int("8F5BBABBB1305894B29068D51E64558EC30ABF835E2E988D72A301BBEBF985B7", 16)
        h1 = bytes.fromhex(hashlib.sha1(((username + ":" + password)).encode()).hexdigest())
        h2 = int(bytes.fromhex(hashlib.sha1(bytes.fromhex(salt) + h1).hexdigest())[::-1].hex(), 16)
        verifier = bytes.fromhex(format(pow(g, h2, N), "X").ljust(64, "0"))[::-1].hex()
        return verifier
    
    def get_registrationData(self, username: str, password: str):
        salt = secrets.token_hex(32)
        verifier = self.get_verifier(username, password, salt)
        return salt, verifier
    
    def verify_SRP6(self, username: str, password: str, salt: str, verifier: str):
        g = int(7)
        N = int("8F5BBABBB1305894B29068D51E64558EC30ABF835E2E988D72A301BBEBF985B7", 16)
        x = int(bytes.fromhex(hashlib.sha1(bytes.fromhex(salt) + bytes.fromhex(hashlib.sha1(((username + ":" + password)).encode()).hexdigest())).hexdigest())[::-1].hex(), 16)
        verifier = bytes.fromhex(format(pow(g, x, N), "X").ljust(64, "0"))[::-1].hex()
        return verifier

    def verify_account(self, username, password):
        res = self.conn.execute(f"select salt from {self.config['database']['name']}.accounts where username = '{username}'")
        if res != [-1,0]:
            try:
                salt = res[1][0][0].hex()
                res = self.conn.execute(f"select verifier from {self.config['database']['name']}.accounts where username = '{username}'")
                verifier = res[1][0][0].hex()
                secret = self.verify_SRP6(username, password, salt, verifier)
                if secret == verifier:
                    return True
                return False
            except:
                return False
        return False
    
    def escape_characters(self, input):
        return re.sub("[^a-zA-Z0-9!\s²³§$%&\/([)\]=}\?\ß\.\\_°\"\^#\*\+-~<>\|@;:,]", "", input)
    
    def escape_favourite(self, favourite):
        try:
            favourite["id"] = self.escape_characters(str(favourite["id"]))
            favourite["elapsed_time"] = self.escape_characters(str(favourite["elapsed_time"]))
            favourite["title"] = self.escape_characters(str(favourite["title"]))
            favourite["url"] = self.escape_characters(str(favourite["url"]))
            favourite["thumbnail"] = self.escape_characters(str(favourite["thumbnail"]))
            for category in favourite["categories"]:
                category = self.escape_characters(category)
            for tag in favourite["tags"]:
                category = self.escape_characters(tag)
            return favourite
        except Exception as e:print(e)


    def soft_escape():
        pass

    def valid_date(self, input):
        try:
            re.findall("\d{2}-\d{2}-\d{2}", input)[0]
            return True
        except:
            return False

    def calc_file_hash(self, path_to_file):
        hSha = hashlib.sha1()
        with open(self, path_to_file, "rb") as fp:
            chunk = 0
            while chunk != b"":
                chunk = fp.read(1024)
                hSha.update(chunk)
        return hSha.hexdigest()
    
    def calc_data_hash(self, data):
        hSha = hashlib.sha1()
        chunk = 0
        while chunk != b"":
            chunk = data.read(1024)
            hSha.update(chunk)
        return hSha.hexdigest()
    
    # def pick_random_char(self):
    #     return self.chars[random.randint(0, len(self.chars)-1)] 

    # def CreateRandomId(self):
    #     return hashlib.md5(f"{datetime.datetime.now()}{self.pick_random_char()}".encode()).hexdigest()

    # def _CreateRandomId(self):
    #     return hashlib.md5(str(datetime.datetime.now()).encode()).hexdigest()

    # def CreateMD5Hash(self, _input):
    #     return hashlib.md5(_input.encode()).hexdigest()

    def validate_token(self, user_random_id, token):
        rc, result = self.conn.execute(f"select * from tokens where user_random_id = '{user_random_id}' and token = '{token}'")
