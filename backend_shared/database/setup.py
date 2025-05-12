from .db_connection import Connection

class Setup():
    def __init__(self, config):
        self.config = config
        self.db_manager = Connection(self.config["database"]["hostname"], self.config["database"]["admin"]["username"], self.config["database"]["admin"]["password"], self.config["database"]["name"], self.config["database"]["port"])       

    def init_db(self):
        self.db_manager.init_root(self.config["database"]["admin"]["username"], self.config["database"]["admin"]["password"])
        self.db_manager.root_connect()
        self.create_databases()
        self.create_service_tables()
        self.create_tables()
        self.create_db_admin()

    def create_databases(self):
        self.db_manager.root_execute(f"create database if not exists {self.config['database']['name']}")

    def create_service_tables(self):
        for table in self.config["database"]["serviceTables"]:
            query = []
            for field in table["fields"]:
                query.append(f"{field['name']} {field['type']} {field['std']}")
            query = ','.join(query)
            self.db_manager.root_execute(f'''create table if not exists {self.config["database"]["name"]}.{table["name"]}({query})''')


    def create_tables(self):
        for table in self.config["database"]["tables"]:
            query = []
            for field in table["fields"]:
                query.append(f"{field['name']} {field['type']} {field['std']}")
            query = ','.join(query)
            self.db_manager.root_execute(f'''create table if not exists {self.config["database"]["name"]}.{table["name"]}({query})''')

    def create_db_admin(self):
        self.db_manager.root_execute(f"create user if not exists '{self.config['database']['user']['username']}'@'%' identified by '{self.config['database']['user']['password']}'")
        for table in self.config['database']['tables']:
            self.db_manager.root_execute(f"grant all privileges on {self.config['database']['name']}.{table['name']} to '{self.config['database']['user']['username']}'@'%'")
        for table in self.config['database']['serviceTables']:
            self.db_manager.root_execute(f"grant all privileges on {self.config['database']['name']}.{table['name']} to '{self.config['database']['user']['username']}'@'%'")
