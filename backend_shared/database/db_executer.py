import datetime, re

class Executer:
    def __init__(self, connection, config):
        self.connection = connection
        self.config = config

    def create_account(self, id, username, nickname, verifier, salt, email, role, sub_role=""):
        rc, result = self.connection.execute(f'''insert into {self.config["database"]["name"]}.{self.config["database"]["tables"][0]["name"]} (
                                id,
                                username, 
                                nickname,             
                                verifier, 
                                salt, 
                                email_address, 
                                role, 
                                sub_role,
                                datetime) 
                                values (
                                '{id}',
                                '{username}', 
                                '{nickname}', 
                                X'{verifier}', 
                                X'{salt}', 
                                '{email}',
                                '{role}',
                                '{sub_role}',
                                '{datetime.datetime.now().strftime('%Y-%m-%dT%H:%M:%S')}')''')
        return result
    
    def delete_account(self, id):
        self.connection.execute(f"delete from backendde_accounts.accounts where id = {id}")

    def get_account_by_username(self, username):
        q = f'''select * from {self.config['database']['name']}.{self.config['database']['tables'][0]['name']} 
                                             where username = "{username}"'''
        print(f"get account query => {q}")
        rc, result = self.connection.execute(f'''select * from {self.config['database']['name']}.{self.config['database']['tables'][0]['name']} 
                                             where username = "{username}"''')
        return result
    
    def get_account_by_id(self, id):
        rc, result = self.connection.execute(f"select * from {self.config['database']['name']}.{self.config['database']['tables'][0]['name']} where id = {id}")
        return result

    def create_video(self, id, original_filename, filename, title, description, duration, categories, sub_categories, tags, visibility, happy_ends, timestamps, url, thumbnail_url, owner_id):
        rc, result = self.connection.execute(f'''insert into {self.config["database"]["name"]}.{self.config["database"]["tables"][1]["name"]} (
                                id,
                                original_filename,
                                filename, 
                                title,             
                                description, 
                                duration, 
                                categories, 
                                sub_categories, 
                                tags,
                                visibility,
                                happy_ends,
                                timestamps,
                                url,
                                thumbnail_url,
                                owner_id,                                  
                                created_at,
                                updated_at) 
                                values (
                                '{id}',
                                '{original_filename}',
                                '{filename}', 
                                '{title}', 
                                '{description}', 
                                '{duration}', 
                                '{categories}',
                                '{sub_categories}',
                                '{tags}',
                                '{visibility}',
                                '{happy_ends}',
                                '{timestamps}',
                                '{url}',
                                '{thumbnail_url}',
                                '{owner_id}',
                                '{datetime.datetime.now().strftime('%Y-%m-%dT%H:%M:%S')}',
                                '{datetime.datetime.now().strftime('%Y-%m-%dT%H:%M:%S')}')''')
        return result

    def get_videos(self, offset=0, limit=15):
        rc, result = self.connection.execute(f'''select * from {self.config["database"]["name"]}.{self.config["database"]["tables"][1]["name"]} limit {limit + 1} offset {offset}''')
        return result

    def get_video_by_id(self, id):
        rc, result = self.connection.execute(f'''select * from {self.config["database"]["name"]}.{self.config["database"]["tables"][1]["name"]} where id = "{id}"''')
        return result[0]

    def search_videos(self, searchString, offset=0, limit=15):
        rc, result = self.connection.execute(f'''select * from {self.config["database"]["name"]}.{self.config["database"]["tables"][1]["name"]} where {searchString} limit {limit + 1} offset {offset}''')
        return result

    def like_video(self, video_id):
        rc, result = self.connection.execute(f'''update {self.config["database"]["name"]}.{self.config["database"]["tables"][1]["name"]} set likes = likes + 1 where id = "{video_id}"''')

    def dislike_video(self, video_id):
        rc, result = self.connection.execute(f'''update {self.config["database"]["name"]}.{self.config["database"]["tables"][1]["name"]} set dislikes = dislikes + 1 where id = "{video_id}"''')

    def increase_video_watch_counter(self, video_id):
        rc, result = self.connection.execute(f'''update {self.config["database"]["name"]}.{self.config["database"]["tables"][1]["name"]} set views = views + 1 where id = "{video_id}"''')

    def raw(self, query):
        rc, result = self.connection.execute(query)
        return result