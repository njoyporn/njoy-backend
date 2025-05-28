import mysql.connector
from backend_shared.logger import colors

class Connection:
    def __init__(self, host, username, password, database, port):
        # print(host, username, password, database, port)
        self.host = host
        self.username = username
        self.password = password
        self.database = database
        self.port = port
        self.connection = None
        self.cursor = None
        self.root_connection = None
        self.root_cursor = None
        self.root_username = None
        self.root_password = None
        self.colors = colors.Colors()

    def connect(self):
        try:
            self.cursor.close()
        except:
            pass
        self.connection = mysql.connector.connect(
            host = self.host,
            user = self.username,
            password = self.password,
            database = self.database,
            port = self.port,
            connection_timeout = 3600
        )
        self.cursor = self.connection.cursor(buffered=True)

    def get_connection(self):
        return mysql.connector.connect(
            host = self.host,
            user = self.username,
            password = self.password,
            database = self.database,
            port = self.port,
            connection_timeout = 3600
        )

    def disconnect(self):
        try:
            self.connection.close()
            self.cursor.close()
        except:
            pass

    def execute(self, query):
        cn = self.get_connection()
        cur = cn.cursor(buffered=True)
        try:
            cur.execute(query)
            if "select * from" not in query:
                cn.commit()
            result = []
            for x in cur:
                result.append(x)
            return cur.rowcount, result
        except Exception as e:
            if str(e) == "'NoneType' object is not subscriptable":
                return -1, True
            print(f"{self.colors.FAIL}Query: {query}\n{self.colors.ENDC}Error:{self.colors.OKBLUE}{e}{self.colors.ENDC}")
            if "Unknown colum" in str(e):
                return "Unknown colum"
            return 0, [-1,0]

    def init_root(self, root_username, root_password):
        self.root_username = root_username
        self.root_password = root_password

    def root_connect(self):
        try:
            self.root_cursor.close()
        except:
            pass
        try:
            self.root_connection = mysql.connector.connect(
                host = self.host,
                user = self.root_username,
                password = self.root_password,
                port = self.port,
                connection_timeout = 3600
            )
            self.root_cursor = self.root_connection.cursor(buffered=True)
        except Exception as e:
            print(f"{self.colors.FAIL}root_connection_ERROR:\n{e}\n{self.colors.ENDC}")

    def root_disconnect(self):
        try:
            self.root_connection.close()
            self.root_cursor.close()
        except:
            pass

    def root_execute(self, query):
        self.root_connect()
        print(f"{self.colors.OKBLUE}root_query >> {self.colors.OKGREEN}{query}{self.colors.ENDC}")
        try:
            self.root_cursor.execute(query)
            self.root_connection.commit()
        except Exception as e:
            print(f"root_query_ERROR:\n{e}\n")
            self.root_disconnect()
            return 0, [-1,0]