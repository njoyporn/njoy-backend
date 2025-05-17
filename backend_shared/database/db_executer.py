import datetime, re

class Executer:
    def __init__(self, connection, config):
        self.connection = connection
        self.config = config

    def get_videos(self, offset=0, limit=15):
        rc, result = self.connection.execute(f'''select * from {self.config["database"]["name"]}.{self.config["database"]["tables"][0]["name"]} where soft_delete = 0 limit {limit + 1} offset {offset}''')
        return result

    def get_video_by_id(self, id):
        rc, result = self.connection.execute(f'''select * from {self.config["database"]["name"]}.{self.config["database"]["tables"][0]["name"]} where id = "{id}" and soft_delete = 0''')
        return result[0]

    def get_videos_ordered_by(self, col, dir, limit=15):
        rc, result = self.connection.execute(f'''select * from {self.config["database"]["name"]}.{self.config["database"]["tables"][0]["name"]} where soft_delete = 0 ORDER BY {col} {dir} LIMIT {limit}''')
        return result

    def search_videos(self, searchString, offset=0, limit=15):
        rc, result = self.connection.execute(f'''select * from {self.config["database"]["name"]}.{self.config["database"]["tables"][0]["name"]} where {searchString} and soft_delete = 0 limit {limit + 1} offset {offset}''')
        return result

    def like_video(self, video_id):
        rc, result = self.connection.execute(f'''update {self.config["database"]["name"]}.{self.config["database"]["tables"][0]["name"]} set likes = likes + 1 where id = "{video_id}"''')

    def dislike_video(self, video_id):
        rc, result = self.connection.execute(f'''update {self.config["database"]["name"]}.{self.config["database"]["tables"][0]["name"]} set dislikes = dislikes + 1 where id = "{video_id}"''')

    def increase_video_watch_counter(self, video_id):
        rc, result = self.connection.execute(f'''update {self.config["database"]["name"]}.{self.config["database"]["tables"][0]["name"]} set views = views + 1 where id = "{video_id}"''')

    def raw(self, query):
        rc, result = self.connection.execute(query)
        return result