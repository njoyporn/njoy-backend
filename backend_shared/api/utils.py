import json, os, requests, re
from backend_shared.security import verifier, crypt
from backend_shared.database import db_executer, db_connection
from backend_shared.logger import colors, logger
from backend_shared.types import document as DocType, Links
from backend_shared.utils import random

class Utils:

    def __init__(self, config):
        self.config = config
        self.config = self.load_config()
        self.connection = db_connection.Connection(self.config["database"]["hostname"], self.config["database"]["user"]["username"], self.config["database"]["user"]["password"], self.config["database"]["name"], self.config["database"]["port"])
        self.db_executer = db_executer.Executer(self.connection, self.config)
        self.verifier = verifier.Verifier(self.connection, self.config)
        self.crypto = crypt.Encrpyter(self.config)
        self.colors = colors.Colors()
        self.logger = logger.Logger()
        self.random = random.Random()

    def load_config(self):
        try:
            config = json.load(open(f'{os.getcwd()}/config/config.json', "r", encoding="utf-8"))
            print(f"Configuration: >> External website config loaded")
            return config
        except:
            config = json.load(open(f'{os.getcwd()}/config.json', "r", encoding="utf-8"))
            print(f"Default website config loaded")
            return config

    def verwaltung_create_default_admin_account(self):
        username = self.random.CreateMD5Hash(self.verifier.escape_characters(self.config["verwaltung"]["admin"]["username"]))
        password = self.verifier.escape_characters(self.config["verwaltung"]["admin"]["password"])
        if self.verifier.verify_account(username, password):
            print("admin user already exists do not create user")
            return
        if self.config["api"]["rsa_enabled"]:
            email = self.crypto.enc_private_key(self.verifier.escape_characters(self.config["verwaltung"]["admin"]["email"])).hex()
        else:
            email = self.verifier.escape_characters(self.config["verwaltung"]["admin"]["email"])
        salt, verifier = self.verifier.get_registrationData(username, password)
        self.db_executer.create_account(self.random.CreateRandomId(), username, "backend", verifier, salt, email, self.config["roles"]["administrator"], "default")
        if not self.verifier.verify_account(username, password):
            return "{'error':'Error creating an account'}"
        self.logger.log("INFO", "admin user created")
        return json.dumps({'success':'user created'})
    
    def do_login(self):
        try:
            res = requests.post(f"https://njoyporn.com/api/v1/login", json={"username":self.config["verwaltung"]["admin"]["username"], "password":self.config["verwaltung"]["admin"]["password"]}, headers={"Content-Type":"application/json"}).content
            self.logger.log("INFO", f"{str(res)}")
        except Exception as e:
            self.logger.log("ERROR", f"cannot login to quotes-api {str(e)}")
            return str(e)

    #Eigentlich sollte ich mir dafür endlich mal nen service bauen    
    def save_documents(self, documents):
        docs = []
        for document in documents:
            self.save_data(document["data"])
            docs.append(DocType.Document(document["filename"], document["path"], document["type"]))

    #Wird echt Zeit (aber och kein plan wie ich das mache müsste mal darüber nachdenken)
    def save_data(self, filename,  data):
        with open(f"{os.getcwd()}/data/{filename}", "wb") as fp:
            fp.write(data)

    # def CreateRandomId(self):
    #     return self.verifier.CreateRandomId()
    
    def getDownloadFolderPath(self):
        return f"{os.getcwd()}/{self.config['data']['path']}/downloads"
    
    def getThumbnailFolderPath(self):
        return f"{os.getcwd()}/{self.config['data']['path']}/thumbnails"

    def getVideosFolderPath(self):
        return f"{os.getcwd()}/{self.config['data']['path']}/videos"

    def extractDomain(self, url):
        return re.findall("^(?:https?:\/\/)?(?:[^@\n]+@)?(?:www\.)?([^:\/\n?]+)", url)[0]
    
    def generate_links(self, categories, sub_categories, tags, happy_ends, page, more_pages):
        links = Links("","")
        categoriesString = ""
        sub_categoriesString = ""
        tagsString = ""
        happy_endsString = ""
        if len(categories) > 0:
            categoriesString = f"?categories={','.join(categories)}"
        if len(sub_categories) > 0:
            if categoriesString != "":
                sub_categoriesString = f"&sub_categories={','.join(sub_categories)}" 
            else: sub_categoriesString = f"?sub_categories={','.join(sub_categories)}" 
        if len(tags) > 0:
            if categoriesString != "" or sub_categoriesString != "":
                tagsString = f"&tags={','.join(tags)}" 
            else: tagsString = f"?tags={','.join(tags)}" 
        if len(happy_ends) > 0:
            if categoriesString != "" or sub_categoriesString != "" or tagsString != "":
                happy_endsString = f"&happy_ends={','.join(happy_ends)}"
            else: happy_endsString = f"?happy_ends={','.join(happy_ends)}"
        queryString = f"{categoriesString}{sub_categoriesString}{tagsString}{happy_endsString}"
        page = int(page)
        next = page + 1 
        prev = next - 2
        if prev < 0: prev = 0
        if more_pages:
            links.next = f"{queryString}&page={next}"
        if page > 0:
            links.prev = f"{queryString}&page={prev}"
        return links    
