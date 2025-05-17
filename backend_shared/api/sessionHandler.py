import time, datetime, threading, hashlib, random
from backend_shared.utils import random
from backend_shared.logger import logger

class SessionHandler:
    def __init__(self, config):
        self.config = config
        self.session_list = []
        self.random = random.Random()
        self.logger = logger.Logger()
        self.randomSessionHandlerID = self.random.CreateRandomId()

    def cron_job(self):
        while True:
            for session in self.session_list:
                if self.session_is_expired(session):
                    self.session_list.remove(session)
            time.sleep(5)

    def init_cron_job(self):
        threading.Thread(target=self.cron_job).start()

    def get_session(self, request):
        user_hash = self.get_user_hash(request)
        for session in self.session_list:
            if session.session_id == user_hash:
                return session
        return None
    
    def get_user_hash(self, request):
        try: return hashlib.md5(str(request.headers["X-Forwarded-For"]+request.headers["User-Agent"]).encode()).hexdigest()
        except: return hashlib.md5(str(request.remote_addr+request.headers["User-Agent"]).encode()).hexdigest()

    def create_session(self, role, account_id, request, expire_time):
        session = self.get_session(request)
        if session: 
            return self.upgrade_session(session, role)
        else:
            session =  self.Session(self.get_user_hash(request), role, account_id)
            session.lifetime = expire_time
            self.session_list.append(session)
        return session
    
    def upgrade_session(self, session, role):
        if role == self.config["roles"]["administrator"]:
            session.lifetime = "immortail"
            session.role = role
            return session
        if role == self.config["roles"]["moderator"]:
            session.lifetime = "3600"
            session.role = role
        if role == self.config["roles"]["user"]:
            session.lifetime = "3600"
            session.role = role

    def create_guest_session(self, request, lifetime=60*60*24):
        session = self.Session(self.get_user_hash(request), self.config["roles"]["guest"], self.random.CreateRandomId())
        session.lifetime = lifetime
        self.session_list.append(session)
        self.logger.log("INFO", f"\nCreating Guest-Session >> id: {session.session_id} | address: {request.headers['X-Forwarded-For']} | user-agent: {request.headers['User-Agent']} | len(session_list) = {len(self.session_list)} | RSHID: {self.randomSessionHandlerID}")
        return session

    def create_admin_session(self, request, lifetime="immortail"):
        session = self.get_session(request)
        if session: 
            session.role = self.config["roles"]["administrator"]
            session.lifetime = lifetime
            self.logger.log("INFO" f"Upgrade Sessiion >> id: {session.session_id} to role: {self.config['roles']['administrator']}")
        else: 
            session = self.Session(self.get_user_hash(request), self.config["roles"]["administrator"])
            session.lifetime = lifetime
            self.session_list.append(session)
            self.logger.log("INFO", f"\nCreating Administrator-Session >> id: {session.session_id} | address: {request.headers['X-Forwarded-For']} | user-agent: {request.headers['User-Agent']}\n")
        return session

    def create_moderator_session(self, request, lifetime="immortail"):
        session = self.Session(self.get_user_hash(request), self.config["roles"]["moderator"])
        session.lifetime = lifetime
        self.session_list.append(session)
        return session

    def create_user_session(self, request, lifetime=1800):
        session = self.Session(self.get_user_hash(request), self.config["roles"]["user"])
        session.lifetime = lifetime
        self.session_list.append(session)
        return session

    def session_is_expired(self, session):
        delta = datetime.datetime.now() - session.last_update
        if session.lifetime == "immortail" or int(delta.total_seconds()) > session.lifetime:
            print(f"session with id: {session.session_id} expired and got removed")
            return True
        return False
    
    def is_admin(self, request):
        session = self.get_session(request)
        if session != None:
            if session.role == self.config["roles"]["administrator"]:
                return True
        return False

    def is_moderator(self, request):
        session = self.get_session(request)
        if session != None:
            if (session.role == self.config["roles"]["moderator"]
                or session.role == self.config["roles"]["administrator"]):
                return True
        return False

    def is_user(self, request):
        session = self.get_session(request)
        if session != None:
            if (session.role == self.config["roles"]["user"]
                or session.role == self.config["roles"]["moderator"]
                or session.role == self.config["roles"]["administrator"]):
                return True
        return False

    def is_guest(self, request):
        session = self.get_session(request)
        if session != None:
            if (session.role == self.config["roles"]["guest"]
                or session.role == self.config["roles"]["user"]
                or session.role == self.config["roles"]["moderator"]
                or session.role == self.config["roles"]["administrator"]):
                return True
        return False

    def remove_session(self, request):
        for session in self.session_list:
            if session.session_id == self.get_user_hash(request):
                self.session_list.remove(session)
                return
            
    def get_acc_role(self, request):
        user_hash = self.get_user_hash(request)
        for session in self.session_list:
            if session.session_id == user_hash:
                return session.role
        return ""
    
    def get_acc_id(self, request):
        user_hash = self.get_user_hash(request)
        for session in self.session_list:
            if session.session_id == user_hash:
                return session.account_id
        return -1
    
    def get_request_limit(self, session):
        if not session: 
            print("session not found")
            return self.config["limits"]["request_limit"]["guest"]
        return self.config["limits"]["request_limit"][session.role]

    def has_requests_left(self, request):
        session = self.get_session(request)
        if not session: 
            self.create_guest_session(request)
            return True
        if self.get_request_limit(session) == "~~":
            return True
        if session.request_counter <= self.get_request_limit(session):
            session.request_counter += 1
            return True
        return False
    
    def set_accept_content_warning(self, request):
        self.get_session(request).content_warning_accepted = True

    class Session:
        def __init__(self, session_id, role, account_id):
            self.session_id = session_id
            self.role = role
            self.account_id = account_id
            self.date = datetime.datetime.now()
            self.last_update = datetime.datetime.now()
            self.lifetime = 1800
            self.request_counter = 0
            self.content_warning_accepted = False
            self.token = None