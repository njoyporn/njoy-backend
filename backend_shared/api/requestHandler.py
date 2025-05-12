from backend_shared.database import db_connection, db_executer, db_utils
from backend_shared.security import verifier, crypt
from backend_shared.api import utils, cache
from backend_shared.logger import logger
from backend_shared.utils import random
from backend_shared.types import BusinessResponse, Paginated, Links, BusinessError, Role
from flask import send_from_directory
from video import videoEditor
import json as JSON


class RequestHandler:
    def __init__(self, config, session_handler):
        self.config = config
        self.db_connection = db_connection.Connection(self.config["database"]["hostname"], self.config["database"]["user"]["username"], self.config["database"]["user"]["password"], self.config["database"]["name"], self.config["database"]["port"])
        self.verifier = verifier.Verifier(self.db_connection, self.config)
        self.db_executer = db_executer.Executer(self.db_connection, self.config)
        self.crypto = crypt.Encrpyter(self.config)
        self.db_utils = db_utils.DBUtils()
        self.session_handler = session_handler
        self.utils = utils.Utils(self.config)
        self.cache = cache.DataCache()
        self.quotesCount = 0
        self.logger = logger.Logger()
        self.random = random.Random()
        self.video_editor = videoEditor.VideoEditor(self.db_connection, self.config)

    def handle_login(self, request):
        try:
            username = self.random.CreateMD5Hash(self.verifier.escape_characters(request.json["username"]))
            password = self.verifier.escape_characters(request.json["password"])
        except:pass
        try:
            username = self.random.CreateMD5Hash(self.verifier.escape_characters(request.form["username"]))
            password = self.verifier.escape_characters(request.form["password"])
        except:pass
        if not self.verifier.verify_account(username, password):
            self.logger.log("INFO", f"Denaied login with username: {username}")
            return BusinessResponse(self.random.CreateRandomId(), "login-failed", []).toJson()
        account = self.db_executer.get_account_by_username(username)
        self.session_handler.create_session(account[0][6], account[0][0], request, 1800)
        self.logger.log("INFO", f"Success login with username: {username}")
        return BusinessResponse(self.random.CreateRandomId(), "login-success", [Role(account[0][6])]).toJson()

    def handle_check_is_logged_in(self, request):
        try:
            role = self.session_handler.get_acc_role(request)
            if role:
                return BusinessResponse(self.random.CreateRandomId(), "authorized", [Role(role)]).toJson()
            self.session_handler.create_guest_session(request) 
            return BusinessResponse(self.random.CreateRandomId(), "handshake", [Role(role)]).toJson()
        except:
            return BusinessResponse(self.random.CreateRandomId(), "not-authorized", []).toJson()

    def handle_log_out(self, request):
        self.session_handler.remove_session(request)    

    def register_account(self, request):
        if not self.config["api"]["allow_account_creation"]: return BusinessResponse(self.random.CreateRandomId(), "error creating user", [], BusinessError(self.random.CreateRandomId(), "can not create user")).toJson()
        try:
            username, password, email = request.json["username"], request.json["password"], request.json["email"]
        except: return BusinessResponse(self.random.CreateRandomId(), f"error creating {self.config['roles']['user']}", []).toJson()
        username = self.random.CreateMD5Hash(self.verifier.escape_characters(username))
        password = self.verifier.escape_characters(password)
        if self.verifier.verify_account(username, password):
            return BusinessResponse(self.random.CreateRandomId(), f"error creating {self.config['roles']['user']}", [], BusinessError(self.random.CreateRandomId(), "can not create user")).toJson()
        if self.config["api"]["rsa_enabled"]:
            email = self.crypto.enc_private_key(self.verifier.escape_characters(email)).hex()
        else:
            email = self.verifier.escape_characters(email)
        salt, verifier = self.verifier.get_registrationData(username, password)
        self.db_executer.create_account(self.random.CreateRandomId(), username, username, verifier, salt, email, self.config["roles"]["user"], "default")
        if not self.verifier.verify_account(username, password):
            return BusinessResponse(self.random.CreateRandomId(), "error creating user", [], BusinessError(self.random.CreateRandomId(), "can not create user"))
        self.logger.log("INFO", f"{self.config['roles']['user']} user created")
        return BusinessResponse(self.random.CreateRandomId(), "account-created", []).toJson()

    def create_video(self, request):
        session = self.session_handler.get_session(request)
        if self.session_handler.is_admin(request):
            file = request.files["videoFile"]
            try:#ich mach das um zu checken das auch ein file mit hochgeladen wird
                original_filename = self.verifier.escape_characters(file.filename)
            except:
                return BusinessResponse(self.random.CreateRandomId(), "ERRROR", [], BusinessError(self.random.CreateRandomId(), "MISSING_FILE")).toJson()
            try: 
                title = request.form["title"]
                description = self.verifier.escape_characters(request.form["description"])
                tags = self.verifier.escape_characters(request.form["tags"])
                categories = self.verifier.escape_characters(request.form["categories"])
                sub_categories = self.verifier.escape_characters(request.form["sub_categories"])
                visibility = self.verifier.escape_characters(request.form["visibility"])
                happy_ends = self.verifier.escape_characters(request.form["happy_ends"])
                timestamps = self.verifier.escape_characters(request.form["timestamps"])
                id = self.random.CreateRandomId()
            except Exception as e:
                return BusinessResponse(self.random.CreateRandomId(), "ERRROR", [], BusinessError(self.random.CreateRandomId(), "CAN_NOT_READ_VIDEO_INFO")).toJson()
            try:
                self.video_editor.save_video_file(file, id, original_filename, f"{id}.mp4", title, description, categories, sub_categories, tags, visibility, happy_ends, timestamps, session.account_id)#session.account_id
            except Exception as e:
                self.logger.log("ERROR", str(e))
                return BusinessResponse(self.random.CreateRandomId(), "ERRROR", [], BusinessError(self.random.CreateRandomId(), "CAN_NOT_SAVE_VIDEO")).toJson() 
            return BusinessResponse(self.random.CreateRandomId(), "VIDEO_CREATED", []).toJson()
        self.logger.log("WARNING", f"Accound: {session.account_id} could not create video")
        return BusinessResponse(self.random.CreateRandomId(), "ERRROR", [], BusinessError(self.random.CreateRandomId(), "CAN_NOT_CREATE_VIDEO")).toJson()

    def get_video_by_id(self, id):
        video = self.db_executer.get_video_by_id(id)
        return BusinessResponse(self.random.CreateRandomId(), "Video", [self.db_utils.video_to_json(video)]).toJson()

    def get_videos(self, request, asObject=False):
        try: 
            if request.args["random"]:
                return self.get_random_videos(5)                
        except: pass
        page = 0
        try: page = int(self.verifier.escape_characters(request.args["page"]))
        except: pass
        videos = self.db_executer.get_videos(page * self.config["database"]["page_size"])
        more_pages = False
        if len(videos) > self.config["database"]["page_size"]: more_pages = True
        if more_pages: videos.pop()
        result = []
        for video in videos:
            result.append(self.db_utils.video_to_json(video))
        if more_pages or page > 0:
            if asObject: return Paginated(BusinessResponse(self.random.CreateRandomId(), "Videos", result), self.utils.generate_links([], [], [], page, more_pages))
            return Paginated(BusinessResponse(self.random.CreateRandomId(), "Videos", result), self.utils.generate_links([], [], [], page, more_pages)).toJson()
        if asObject: return Paginated(BusinessResponse(self.random.CreateRandomId(), "Videos", result), Links("","")).toJson()
        return Paginated(BusinessResponse(self.random.CreateRandomId(), "Videos", result), Links("","")).toJson()

    def get_video(self, request):
        id = None
        try: 
            id = self.verifier.escape_characters(request.args["id"])
            if id: return self.get_video_by_id(id)
        except: return BusinessResponse(self.random.CreateRandomId(), 'Error', [], BusinessError(self.random.CreateRandomId(), 'Something went wrong')).toJson()
    
    def watch_video(self, request):
        try: 
            if request.headers['Referer'] != "https://beta.njoyporn.com/":
                return BusinessResponse(self.random.CreateRandomId(), 'Error', [], BusinessError(self.random.CreateRandomId(), 'Something went wrong')).toJson()
        except: return BusinessResponse(self.random.CreateRandomId(), 'Error', [], BusinessError(self.random.CreateRandomId(), 'Something went wrong')).toJson()
        id = None
        try: 
            if self.session_handler.has_requests_left(request):
                id = self.verifier.escape_characters(request.args["id"])
                if id: return send_from_directory(self.utils.getVideosFolderPath(), f"{id}.mp4")
            return self.limit_reached()
        except: return BusinessResponse(self.random.CreateRandomId(), 'Error', [], BusinessError(self.random.CreateRandomId(), 'Something went wrong')).toJson()

    def search_random_n_x(self, n, x):
        try:
            videos = self.db_executer.search_videos(n, 0, 1000)
            if len(videos) < 4: return Paginated(BusinessResponse(self.random.CreateRandomId(), "Random-Videos-XN", self.get_random_videos(5, True)), Links("","")).toJson()
            copy = videos.copy()
            random_videos = []
            x = len(copy) - 1 if x >= len(copy) else x
            for i in range(x):
                rng = self.random.random_in_range(len(copy)-1)
                random_videos.append(self.db_utils.video_to_json(copy[rng]))
                copy.remove(copy[rng])
            return Paginated(BusinessResponse(self.random.CreateRandomId(), "Random-Videos-XN", random_videos), Links("","")).toJson()
        except Exception as e:
            print(e)
            return Paginated(BusinessResponse(self.random.CreateRandomId(), "Random-Videos-XN", self.get_random_videos(5, True)), Links("","")).toJson()

    def get_random_videos(self, limit, asObject=False):
        random_id_list = self.cache.get("id-list")
        copy = random_id_list.copy()
        random_videos = []
        if limit >= len(copy): limit = len(copy) - 1
        for i in range(limit):
            rng = self.random.random_in_range(len(copy)-1)
            video = self.db_executer.get_video_by_id(copy[rng])
            random_videos.append(self.db_utils.video_to_json(video))
            copy.remove(copy[rng])
        if asObject: return random_videos
        return BusinessResponse(self.random.CreateRandomId(), "Random-Videos", random_videos).toJson()

    def limit_reached(self):
        return send_from_directory(self.utils.getThumbnailFolderPath(), f"limit-reached/limit-reached.png", as_attachment=True)
        
    def get_image(self, request):
        id = "image-not-found"
        iid = 0
        try: id = self.verifier.escape_characters(request.args["id"])
        except: pass
        try: iid = self.verifier.escape_characters(request.args["iid"])
        except: pass
        if self.session_handler.has_requests_left(request): return send_from_directory(self.utils.getThumbnailFolderPath(), f"{id}/{iid}.png", as_attachment=True)
        else: return self.limit_reached()

    def deriveOptions():
        return None

    def resolve_args(self, request):
        categories, sub_categories, happyEnds, tags, page, options = [], [], [], [], 0, None
        try: categories = self.verifier.escape_characters(str(request.args["categories"])).split(",")
        except: pass
        try: tags = self.verifier.escape_characters(str(request.args["tags"])).split(",")
        except: pass
        try: sub_categories = self.verifier.escape_characters(str(request.args["sub_categories"])).split(",")
        except: pass
        try: happyEnds = self.verifier.escape_characters(str(request.args["happy_ends"])).split(",")
        except: pass
        try: page = int(self.verifier.escape_characters(str(request.args["page"])))
        except: pass
        try: options = self.deriveOptions()
        except: pass
        return categories, sub_categories, happyEnds, tags, page, options

    def deriveQueryParams(self, categories, sub_categories, happy_ends, tags, options=None):
        queryString = ""
        categoriesString = ""
        sub_categoriesString = ""
        happy_endsString = ""
        tagString = ""
        if categories:
            for category in categories:
                if categoriesString == "":
                    categoriesString = f"categories LIKE '%{category}%'"
                else: categoriesString += f" {'AND' if not options else 'OR'} categories LIKE '%{category}%'"
        if sub_categories:
            for category in sub_categories:
                if sub_categoriesString == "" and categoriesString == "":
                    sub_categoriesString = f"sub_categories LIKE '%{category}%'"
                else: sub_categoriesString += f" {'AND' if not options else 'OR'} sub_categories LIKE '%{category}%'"
        if happy_ends:
            for happyEnd in happy_ends:
                if happy_endsString == "" and categoriesString == "" and sub_categoriesString == "":
                    happy_endsString += f"happy_ends LIKE '%{happyEnd}%'"
                else: happy_endsString += f"{'AND' if not options else 'OR'} happy_ends LIKE '%{happyEnd}%'"
        if tags:
            for tag in tags:
                if tagString == "" and happy_endsString == "" and categoriesString == "" and sub_categoriesString == "":
                    tagString += f"tags LIKE '%{tag}%'"
                else: tagString += f"{'AND' if not options else 'OR'} tags LIKE '%{tag}%'"
        queryString = categoriesString + sub_categoriesString + tagString + happy_endsString
        return queryString

    def search_videos(self, request):
        try:
            categories, sub_categories, happy_ends, tags, page, options = self.resolve_args(request)
            queryString = self.deriveQueryParams(categories, sub_categories, happy_ends, tags, options)
            if page == -1: return self.search_random_n_x(queryString, 5)
            videos = self.db_executer.search_videos(queryString, page * self.config["database"]["page_size"])
            if not videos: return Paginated(BusinessResponse(self.random.CreateRandomId(), "!Search: Random-Videos", self.get_random_videos(5, True)), Links("","")).toJson()
            more_pages = False
            if len(videos) > self.config["database"]["page_size"]: more_pages = True
            if more_pages: videos.pop()
            result = []
            for video in videos:
                result.append(self.db_utils.video_to_json(video))
            if more_pages or page > 0:
                return Paginated(BusinessResponse(self.random.CreateRandomId(), "Search", result), self.utils.generate_links(categories, sub_categories, tags, happy_ends, page, more_pages)).toJson()
            return Paginated(BusinessResponse(self.random.CreateRandomId(), "Search", result), Links("","")).toJson()
        except Exception as e:
            print(e)
            return self.get_random_videos(5)

    def like_video(self, request):
        try:
            video_id, like = self.verifier.escape_characters(request.args["video_id"]), int(self.verifier.escape_characters((request.args["like"])))
            self.db_executer.like_video(video_id) if like > 0 else self.db_executer.dislike_video(video_id)
        except:pass
        return BusinessResponse(self.random.CreateRandomId(), "Like-Video", []).toJson()

    def increase_video_watch_counter(self, request):
        try:
            video_id = self.verifier.escape_characters(request.args["video_id"])
            self.db_executer.increase_video_watch_counter(video_id)
        except:pass
        return BusinessResponse(self.random.CreateRandomId(), "Watch-Video", []).toJson()

    def handle_get_document(self, request):
        filename = self.verifier.escape_characters(request.json["filename"])
        if not filename: return JSON.dumps({"error": "can not download file"})
        mimetype = self.verifier.escape_characters(request.json["mimetype"])
        return send_from_directory(self.utils.getDownloadFolderPath(), f"{filename}.{mimetype}", as_attachment=True)
    
    def handle_download(self, request, filename):
        try:
            filename = self.verifier.escape_characters(filename)
            return send_from_directory(self.utils.getDownloadFolderPath(), filename, as_attachment=True)
        except Exception as e: return JSON.dumps({"error":"file not found", "e": str(e)})

    def load_video_id_list(self):
        videos = self.db_executer.raw(f"select * from {self.config['database']['name']}.{self.config['database']['tables'][1]['name']}")
        ids = []
        for video in videos:
            ids.append(self.db_utils.video_to_json(video)["id"])
        print(f"{len(ids)} videos loaded")
        self.cache.add("id-list", ids)