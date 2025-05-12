from flask import Flask, request
from .requestHandler import RequestHandler
from .sessionHandler import SessionHandler
from backend_shared.configurator import Configurator

import os

api = Flask(__name__)

configurator = Configurator()
configurator.load_config()
session_handler = SessionHandler(configurator.config)
request_handler = RequestHandler(configurator.config, session_handler)
request_handler.load_video_id_list()

base_route = "/api/v1"
data_path = f"{os.getcwd()}/binarys"

@api.route("/", methods=["GET"])
def index():
    return "200 OK"

@api.route(f"{base_route}/healthz", methods=["GET"])
def healthz():
    return "200 OK"

@api.route(f"{base_route}/login", methods=["POST"])
def login():
    return request_handler.handle_login(request)

@api.route(f"{base_route}/login", methods=["GET"])
def check_is_logged_in():
    return request_handler.handle_check_is_logged_in(request)

@api.route(f"{base_route}/logout", methods=["GET"])
def log_out():
    return request_handler.handle_log_out(request)

@api.route(f"{base_route}/video", methods=["GET"])
def get_video():
    return request_handler.get_video(request)

@api.route(f"{base_route}/video", methods=["POST"])
def post_video():
    return request_handler.create_video(request)

@api.route(f"{base_route}/watch", methods=["GET"])
def watch_video():
    return request_handler.watch_video(request)

@api.route(f"{base_route}/watched", methods=["GET"])
def video_watched():
    return request_handler.increase_video_watch_counter(request)

@api.route(f"{base_route}/image", methods=["GET"])
def get_image():
    return request_handler.get_image(request)

@api.route(f"{base_route}/videos", methods=["GET"])
def get_videos():
    return request_handler.get_videos(request)

@api.route(f"{base_route}/search", methods=["GET"])
def search_videos():
    return request_handler.search_videos(request)

@api.route(f"{base_route}/like", methods=["GET"])
def like_video():
    return request_handler.like_video(request)

@api.route(f"{base_route}/register", methods=["POST"])
def register_account():
    return request_handler.register_account(request)
