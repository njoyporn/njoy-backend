from backend_shared.database import db_connection, db_executer, db_utils
from backend_shared.security import verifier, crypt, token
from backend_shared.api import utils, cache
from backend_shared.logger import logger
from backend_shared.utils import random
from backend_shared.types import BusinessResponse, Paginated, Links, BusinessError
from flask import send_from_directory
import json as JSON

class RequestHandler:
    def __init__(self, config):
        self.config = config
        self.db_connection = db_connection.Connection(self.config["database"]["hostname"], self.config["database"]["user"]["username"], self.config["database"]["user"]["password"], self.config["database"]["name"], self.config["database"]["port"])
        self.verifier = verifier.Verifier(self.db_connection, self.config)
        self.db_executer = db_executer.Executer(self.db_connection, self.config)
        self.crypto = crypt.Encrpyter(self.config)
        self.db_utils = db_utils.DBUtils()
        self.utils = utils.Utils(self.config)
        self.cache = cache.DataCache()
        self.quotesCount = 0
        self.logger = logger.Logger()
        self.random = random.Random()
        self.tokenizer = token.Tokenizer(self.config)

    def hasVideoRights(self):return False
    def canSeePrivateVideo(self):return False

    def can_see_video(self, video, request):
        try: 
            if video["public"] and video["free"]: return True
        except Exception as e: self.logger.log("ERROR", f"this {str(e)}")
        try: 
            role = self.tokenizer.get_role(request.headers["Authorization"])
            if role == "administrator": return True
        except Exception as e:
            if e != '': self.logger.log("ERROR", f"here {str(e)}")
        if video["free"] and not video["public"]: return self.canSeePrivateVideo()
        if video["public"] and not video["free"]: return self.hasVideoRights()
        return False

    def get_video_by_id(self, id, request):
        try:
            video = self.db_executer.get_video_by_id(id)
            video_json = self.db_utils.video_to_json(video)
            if self.can_see_video(video_json, request): return BusinessResponse(self.random.CreateRandomId(), "Video", [self.db_utils.video_to_json(video)]).toJson()
            return BusinessResponse(self.random.CreateRandomId(), 'Error', [], BusinessError(self.random.CreateRandomId(), 'Something went wrong')).toJson()
        except: return BusinessResponse(self.random.CreateRandomId(), 'Error', [], BusinessError(self.random.CreateRandomId(), 'Something went wrong')).toJson() 

    def handle_static_arguments(self, request):
        try: 
            if request.args["random"]: return self.get_random_videos(5, request)                
        except: pass
        try: 
            if request.args["recent"]: return self.get_recent_videos(20, request)         
        except: pass
        try: 
            if request.args["popular"]: return self.get_popular_videos(5, request)                
        except: pass
        try:
            if request.args["private"]: return self.get_private_videos(request)
        except: pass

    def get_videos(self, request, asObject=False):
        try:
            videos = self.handle_static_arguments(request)
            if videos: return videos
            page = 0
            try: page = int(self.verifier.escape_characters(request.args["page"]))
            except: pass
            videos = self.db_executer.get_videos(page * self.config["database"]["page_size"])
            more_pages = False
            if len(videos) > self.config["database"]["page_size"]: more_pages = True
            if more_pages: videos.pop()
            result = []
            for video in videos: 
                video_json = self.db_utils.video_to_json(video)
                if self.can_see_video(video_json, request): result.append(self.db_utils.video_to_json(video))
            if more_pages or page > 0:
                if asObject: return Paginated(BusinessResponse(self.random.CreateRandomId(), "Videos", result), self.utils.generate_links([], [], [], [], page, more_pages))
                return Paginated(BusinessResponse(self.random.CreateRandomId(), "Videos", result), self.utils.generate_links([], [], [], [], page, more_pages)).toJson()
            if asObject: return Paginated(BusinessResponse(self.random.CreateRandomId(), "Videos", result), Links("","")).toJson()
            return Paginated(BusinessResponse(self.random.CreateRandomId(), "Videos", result), Links("","")).toJson()
        except Exception as e:return BusinessResponse(self.random.CreateRandomId(), "Error", [], BusinessError(self.random.CreateRandomId(), "Something went wrong")).toJson()

    def get_video(self, request):
        try: return self.get_video_by_id(self.verifier.escape_characters(request.args["id"]), request)
        except: return BusinessResponse(self.random.CreateRandomId(), 'Error', [], BusinessError(self.random.CreateRandomId(), 'Something went wrong')).toJson()
    
    def watch_video(self, request):
        try: 
            if request.headers['Referer'] != self.config["api"]["allowed_referer"]: return BusinessResponse(self.random.CreateRandomId(), 'Error', [], BusinessError(self.random.CreateRandomId(), 'Something went wrong')).toJson()
        except: return BusinessResponse(self.random.CreateRandomId(), 'Error', [], BusinessError(self.random.CreateRandomId(), 'Something went wrong')).toJson()
        try: 
            id = self.verifier.escape_characters(request.args['id'])
            video = self.utils.find_video_in_list_by_id(self.cache.get("video-list"), id)
            if not video: video = self.db_utils.video_to_json(self.db_executer.get_video_by_id(id))
            if self.can_see_video(video, request): return send_from_directory(self.utils.getVideosFolderPath(), f"{self.verifier.escape_characters(request.args['id'])}.mp4") 
        except Exception as e: 
            self.logger.log("ERROR", str(e))
            return BusinessResponse(self.random.CreateRandomId(), 'Error', [], BusinessError(self.random.CreateRandomId(), 'Something went wrong')).toJson()
        try: return send_from_directory(self.utils.getVideosFolderPath(), f"{self.verifier.escape_characters(request.args['id'])}.mp4")
        except: return BusinessResponse(self.random.CreateRandomId(), 'Error', [], BusinessError(self.random.CreateRandomId(), 'Something went wrong')).toJson()

    def search_random_n_x(self, n, x, request):
        try:
            videos = self.db_executer.search_videos(n, 0, 1000)
            if len(videos) < 4: return Paginated(BusinessResponse(self.random.CreateRandomId(), "Random-Videos-XN", self.get_random_videos(5, request, True)), Links("","")).toJson()
            copy = videos.copy()
            random_videos = []
            x = len(copy) - 1 if x >= len(copy) else x
            i = 0
            # for i in range(x):
            while i < x:
                rng = self.random.random_in_range(len(copy)-1)
                video_json = self.db_utils.video_to_json(copy[rng])
                if self.can_see_video(video_json, request): random_videos.append(video_json)
                elif len(copy) - 1 > x: i -= 1
                i += 1
                copy.remove(copy[rng])
            return Paginated(BusinessResponse(self.random.CreateRandomId(), "Random-Videos-XN", random_videos), Links("","")).toJson()
        except Exception as e:
            self.logger.log("ERROR", str(e))
            return Paginated(BusinessResponse(self.random.CreateRandomId(), "Random-Videos-XN", self.get_random_videos(5, request, True)), Links("","")).toJson()

    def get_random_videos(self, limit, request, asObject=False):
        random_id_list = self.cache.get("id-list")
        copy = random_id_list.copy()
        random_videos = []
        if limit >= len(copy): limit = len(copy) - 1
        i = 0
        while i < limit:
            rng = self.random.random_in_range(len(copy)-1)
            video = self.db_executer.get_video_by_id(copy[rng])
            video_json = self.db_utils.video_to_json(video)
            if self.can_see_video(video_json, request): random_videos.append(video_json)
            elif len(copy) - 1 > limit: i -= 1
            i += 1
            copy.remove(copy[rng])
        if asObject: return random_videos
        return BusinessResponse(self.random.CreateRandomId(), "Random-Videos", random_videos).toJson()

    def get_recent_videos(self, limit, request):
        videos = self.db_executer.get_videos_ordered_by('created_at', 'DESC', limit)
        result = []
        for video in videos:
            video_json = self.db_utils.video_to_json(video)
            if self.can_see_video(video_json, request): 
                result.append(video_json)
        return BusinessResponse(self.random.CreateRandomId(), "recent-videos", result).toJson()

    def get_popular_videos(self, limit, request):
        videos = self.db_executer.get_videos_ordered_by('views', 'DESC', limit)
        result = []
        for video in videos: 
            video_json = self.db_utils.video_to_json(video)
            if self.can_see_video(video_json, request): 
                result.append(video_json)
        return BusinessResponse(self.random.CreateRandomId(), "popular-videos", result).toJson()

    def get_private_videos(self, request):
        videos = self.db_executer.get_private_videos()
        result = []
        for video in videos:
            video_json = self.db_utils.video_to_json(video)
            if self.can_see_video(video_json, request):
                result.append(video_json)
        return BusinessResponse(self.random.CreateRandomId(), "private-videos", result).toJson()

    def limit_reached(self):
        return send_from_directory(self.utils.getThumbnailFolderPath(), f"limit-reached/limit-reached.png", as_attachment=True)
    def image_not_found(self):
        return send_from_directory(self.utils.getThumbnailFolderPath(), f"image-not-found/0.png", as_attachment=True)

    def get_image(self, request):
        id = "image-not-found"
        iid = 0
        try: id = self.verifier.escape_characters(request.args["id"])
        except: return self.image_not_found()
        try: iid = self.verifier.escape_characters(request.args["iid"])
        except: return self.image_not_found()
        return send_from_directory(self.utils.getThumbnailFolderPath(), f"{id}/{iid}.png", as_attachment=True)

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
        queryString, categoriesString, sub_categoriesString, happy_endsString, tagString = "", "", "", "", ""
        if categories:
            for category in categories:
                if categoriesString == "": categoriesString = f"categories LIKE '%{category}%'"
                else: categoriesString += f" {'AND' if not options else 'OR'} categories LIKE '%{category}%'"
        if sub_categories:
            for category in sub_categories:
                if sub_categoriesString == "" and categoriesString == "": sub_categoriesString = f"sub_categories LIKE '%{category}%'"
                else: sub_categoriesString += f" {'AND' if not options else 'OR'} sub_categories LIKE '%{category}%'"
        if happy_ends:
            for happyEnd in happy_ends:
                if happy_endsString == "" and categoriesString == "" and sub_categoriesString == "": happy_endsString += f"happy_ends LIKE '%{happyEnd}%'"
                else: happy_endsString += f"{'AND' if not options else 'OR'} happy_ends LIKE '%{happyEnd}%'"
        if tags:
            for tag in tags:
                if tagString == "" and happy_endsString == "" and categoriesString == "" and sub_categoriesString == "": tagString += f"tags LIKE '%{tag}%'"
                else: tagString += f"{'AND' if not options else 'OR'} tags LIKE '%{tag}%'"
        queryString = categoriesString + sub_categoriesString + tagString + happy_endsString
        return queryString

    def search_videos(self, request):
        try:
            categories, sub_categories, happy_ends, tags, page, options = self.resolve_args(request)
            queryString = self.deriveQueryParams(categories, sub_categories, happy_ends, tags, options)
            if page == -1: return self.search_random_n_x(queryString, 5, request)
            videos = self.db_executer.search_videos(queryString, page * self.config["database"]["page_size"])
            if not videos: return Paginated(BusinessResponse(self.random.CreateRandomId(), "!Search: Random-Videos", self.get_random_videos(5, request, True)), Links("","")).toJson()
            more_pages = False
            if len(videos) > self.config["database"]["page_size"]: more_pages = True
            if more_pages: videos.pop()
            result = []
            for video in videos:
                video_json = self.db_utils.video_to_json(video)
                if self.can_see_video(video_json, request): result.append(video_json)
            if more_pages or page > 0: return Paginated(BusinessResponse(self.random.CreateRandomId(), "Search", result), self.utils.generate_links(categories, sub_categories, tags, happy_ends, page, more_pages)).toJson()
            return Paginated(BusinessResponse(self.random.CreateRandomId(), "Search", result), Links("","")).toJson()
        except Exception as e:
            self.logger.log("ERROR", str(e))
            return Paginated(BusinessResponse(self.random.CreateRandomId(), "!Search: Random-Videos", self.get_random_videos(5, request, True)), Links("","")).toJson()

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

    def load_video_list(self):
        videos = self.db_executer.raw(f"select * from {self.config['database']['name']}.{self.config['database']['tables'][0]['name']} where soft_delete = 0")
        video_list, ids = [], []
        for video in videos: video_list.append(self.db_utils.video_to_json(video))
        self.cache.add("video-list", video_list)
        for video in videos: ids.append(self.db_utils.video_to_json(video)["id"])
        self.cache.add("id-list", ids)
        print(f"{len(ids)} videos loaded")

    def handle_get_client_ip(self, request):
        try:  
            xffHeaders = request.headers["X-Forwarded-For"]
            if "," in xffHeaders: return BusinessResponse(self.random.CreateRandomId(), "Error", [], BusinessError(self.random.CreateRandomId(), "Something went wrong"))
            return xffHeaders
        except: return BusinessResponse(self.random.CreateRandomId(), "Error", [], BusinessError(self.random.CreateRandomId(), "Something went wrong"))