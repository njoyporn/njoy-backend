'''
I exported the video table of njoy2
I imported the table into a seperate table (njoy2_videos) within the njoy database
I read the imported data from the table and build an object with the fields of interest
I call the create_video() method on my dbExecuter with my importet data and calculated data for the missing fields

IMPORTANT:  njoy works a bit different then njoy2.
            njoy renames the files to the id plus mimetype
            njoy uses the id to serve static fiels
            For this to work the njoy2-filename minus minetype gets the new id
'''
from backend_shared.configurator import Configurator
from backend_shared.database import db_connection, db_executer
import re

configurator = Configurator()
config = configurator.load_config()
conn = db_connection.Connection(config["database"]["hostname"], config["database"]["admin"]["username"], config["database"]["admin"]["password"], config["database"]["name"], config["database"]["port"])
dbe = db_executer.Executer(conn, config)

def to_json(entry):
    return {
        "filename": entry[1],
        "title": entry[2],
        "tags": entry[3],
        "description": entry[4],
        "duration": entry[6],
    }

vids = dbe.raw(f"select * from njoy.njoy2_videos")
videos = []
for vid in vids:
    videos.append(to_json(vid))

for video in videos:
    dbe.create_video(
        id=re.sub(".mp4", "", video["filename"]),
        original_filename=video["filename"],
        filename=video["filename"],
        title=video["title"],
        description=video["description"],
        duration=int(video["duration"]),
        categories=video["tags"],
        sub_categories="njoy2",
        tags="njoy2",
        visibility="GLOBAL",
        happy_ends="",
        timestamps="",
        url="",
        thumbnail_url="",
        owner_id="njoy2"
    )

# print(videos)