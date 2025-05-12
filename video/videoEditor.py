import os, cv2, re, json
from backend_shared.database import db_executer
from backend_shared.logger import logger

class VideoEditor():
    def __init__(self, connection, config):
        self.config = config
        self.file = None
        self.logger = logger.Logger()
        self.db_executor = db_executer.Executer(connection, config)

    def GetVideoDuration(self, path):
        data = cv2.VideoCapture(path)
        frames = data.get(cv2.CAP_PROP_FRAME_COUNT)
        seconds = int(frames / 30)
        if frames <= 0:
            video_filename = f"{os.getcwd()}{path}"
            cap = cv2.VideoCapture(video_filename)
            videoLength = int(cap.get(cv2.CAP_PROP_FRAME_COUNT)) - 1
            seconds = int(videoLength / 30)
        return seconds
    
    def save_video_file(self, file, id, original_filename, filename, title, description, categories, sub_categories, tags, visibility, happy_ends, timestamps, owner_id):
        try:
            file.save(f"{os.getcwd()}/data/videos/{id}.mp4")
        except Exception as e:
            self.logger.log("ERROR", str(e))
            return json.dumps({"error":"failed to save video"})
        try: 
            self.CreateThumbnails(id, filename)
        except Exception as e:
            self.logger.log("ERROR", str(e))
            return json.dumps({"error":"failed to save video"})
        duration = ""
        try:
            duration = self.GetVideoDuration(f"/data/videos/{filename}")
        except Exception as e: 
            self.logger.log("ERROR", str(e))
            return json.dumps({"error":"failed to save video"})
        if duration == "":
            self.logger.log("ERROR", "Cant calculate duration")
            return json.dumps({"error":"failed to save video"})
        self.db_executor.create_video(id, original_filename, filename, title, description, duration, categories, sub_categories, tags, visibility, happy_ends, timestamps, f"{self.config['api']['hostname']}/{id}", f"{self.config['api']['hostname']}/{id}", owner_id)
                                                      
    def CreateThumbnails(self, id, videoFileName):
        # folderName = re.sub(".mp4", "", videoFileName)
        try:
            os.mkdir(f"{os.getcwd()}/data/thumbnails/{id}")
        except Exception as e:
            self.logger.log("ERROR", str(e))
            return
        frames = self.GetFramesFromVideo(f"{os.getcwd()}/data/videos/{videoFileName}")
        # print(f"Generate and save thumbs for: {videoFileName}")
        for i, frame in enumerate(frames):
            thumb = self.ConverImageToThumNail(frame)
            for k, v in thumb.items():
                cv2.imwrite(f"{os.getcwd()}/data/thumbnails/{id}/{i}.png", v)

    def GetFramesFromVideo(self, video_filename):
        print(f"file_path: {video_filename}")
        cap = cv2.VideoCapture(video_filename)
        videoLength = int(cap.get(cv2.CAP_PROP_FRAME_COUNT)) - 1
        frames = []
        if cap.isOpened() and videoLength > 0:
            frame_ids = [0]
            if videoLength >= 4:
                frame_ids = [0.01,
                            round(videoLength * 0.25),
                            round(videoLength * 0.5),
                            round(videoLength * 0.75),
                            videoLength - 1]
            count = 0
            success, image = cap.read()
            while success:
                if count in frame_ids:
                    frames.append(image)
                success, image = cap.read()
                count += 1
        return frames

    def ConverImageToThumNail(self, img):
        height, width, channels = img.shape
        thumbs = {"original": img}
        reolutionLIst = [720]
        for resolution in reolutionLIst:
            if (width >= resolution):
                r = (resolution + 0.0) / width
                maxSize = (resolution, int(height * r))
                thumbs[str(resolution)] = cv2.resize(img, maxSize, interpolation=cv2.INTER_AREA)
        return thumbs
    
    def remove_video_file(self, filename):
        path = f"{os.getcwd()}/data/videos/{filename}"
        os.remove(path)

    def remove_thumbnails(self, filename):
        path = f"{os.getcwd()}/data/thumbnails/{re.sub('.mp4', '', filename)}"
        images = os.listdir(path)
        for image in images:
            os.remove(f"{path}/{image}")
        os.rmdir(path)