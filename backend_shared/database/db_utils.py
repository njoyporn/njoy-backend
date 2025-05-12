import datetime, json
from backend_shared.types import Timestamp

class DBUtils:
    def __init__(self):
        pass

    def account_to_json(self, user):
        user_json = {}
        try:
            user_json = {
                "id": user[0],
                "mid": user[1],
                "username": user[2],
                "nickname": user[3],
                "email": user[6],
                "role":user[7],
                "sub_role":user[8]
            }
            return user_json
        except:
            return user_json   

    def split(self, item, type=None):
        try:
            if not item: return []
            if type == "number":
                res = []
                if "," in item: 
                    for i in item.split(","):
                        res.append(int(i.strip()))
                    return res
                return [int(item)]
            if "," in item: return item.split(",")
            return [item]
        except: return []

    def to_timestamps(self, _timestamp):
        timestamps = self.split(_timestamp, "number")
        tsList = []
        for ts in timestamps:
            tsList.append(Timestamp(ts))
        return tsList
    
    def to_action_stamps(self, _action_stamps):
        try:
            return json.loads(_action_stamps)
        except Exception as e: return []

    def video_to_json(self, entry):
        video_json = {}
        try:
            video_json = {
                "id": entry[1],
                "title": entry[4],
                "description": entry[5],
                "duration": entry[6],
                "categories": self.split(entry[7]),
                "sub_categories": self.split(entry[8]),
                "happy_ends": self.split(entry[9]),
                "likes": entry[11],
                "dislikes": entry[12],
                "views": entry[13],
                "thumbnail_url": entry[23],
                "timestamps": self.to_timestamps(entry[26]),
                "action_stamps": self.to_action_stamps(entry[27])
            }
            return video_json
        except Exception as e:
            print(entry[26])
            print(f"ERROR: {e}")
            return video_json  
        
    def get_date_string(self):
        return datetime.datetime.now().strftime('%Y-%m-%d')
    
    def get_one_month_ago(self):
        return (datetime.datetime.now() - datetime.timedelta(days=30)).strftime('%Y-%m-%d')
    
    def ist_older_than_18(self, geburtsdatum):
        values = str(geburtsdatum).split("-")
        today = datetime.datetime.now()
        eighteenyears = datetime.timedelta(days=18*365+5)
        date_of_birth = datetime.datetime(int(values[0]), int(values[1]), int(values[2]))
        return today - eighteenyears > date_of_birth