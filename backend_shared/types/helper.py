import json, re

class Helper:
    def __init__(self):
        pass

    def jsonify(self, x):
        return json.dumps(x,default=lambda y: y.__dict__, sort_keys=True ,indent=4)

    def jsonify_from(self, data):
        _json = "{"
        data = json.loads(data)
        for key in data.keys():
            _json += f"\"{key}\":\"{data[key]}\","
        _json += "}"
        _json = re.sub(".}", "}", _json)
        return json.loads(_json)
