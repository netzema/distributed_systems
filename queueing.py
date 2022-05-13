import configparser
from flask import Flask, request
from flask_restful import Resource, Api
from datetime import datetime, timedelta
from masterdata import *
import os
from requests import get

app = Flask(__name__)
api = Api(app)

if os.path.isfile("config.ini"):
    config_file = configparser.ConfigParser()
    # READ CONFIG FILE
    config_file.read("config.ini")
    maxqlength = int(config_file['QueueSettings']["maxqlength"])
else:
    print("No configurations file found! Default queue length = 8.")
    maxqlength = 8

def check_len(active_queues, location):
    if location >= len(active_queues):
        return False
    return True

default_queue = []
active_queues = [default_queue]

class Queue(Resource):
    def post(self):
        loc = request.form["queue"]
        tk = request.form["token"]
        auth = get('http://localhost:5000/users/api/session/auth', data={"token": tk, "service": "add_job"}).json()
        if auth["success"] == False:
            return auth # access denied

        # loc is index of queue
        if check_len(active_queues, loc):
            q = active_queues[loc]
            if len(q) < maxqlength:
                job_info = {}
                job_info["user"] = request.form["user"]
                assets = request.form["assets"].split(",")
                print(assets)
                assets = [int(i) for i in assets]
                job_info["assets"] = assets
                job_info["timestamp"] = datetime.timestamp(datetime.now())
                job_info["daterange"] = str(datetime.now().date()) + "/" + str((datetime.now() + timedelta(days=10)).date())
                job_info["status"] = "queued"

                _, job_id = write_json(job_info)
                loc.append({job_id: job_info}) # store job_id
                return {"success": True, "msg": f"Job {job_id} successfully added to queue {loc}."}

            else:
                return {"success": False, "msg": f"Queue {loc} is full! Please choose another one."}
        return {"success": False, "msg": f"Queue {loc} not found. Nr. of active queues is {len(active_queues)}."}

    def get(self):
        tk = request.form["token"]
        auth = get('http://localhost:5000/users/api/session/auth', data={"token": tk, "service": "pull_job"}).json()
        if auth["success"] == False:
            return auth  # access denied

        loc = request.form["queue"] # integer value indicating index of queue
        if check_len(active_queues, loc):
            q = active_queues[loc]
            job = q.pop(0)
            return {"success": True, "msg": job}
        return {"success": False, "msg": f"Queue {loc} not found. Nr. of active queues is {len(active_queues)}."}

class QManager(Resource):
    def get(self):
        return {"Active queues": [q for q in enumerate(active_queues)]}

    def post(self):
        tk = request.form["token"]
        #q = request.form["queue"] I do not think we have to specify the queue. Just add a new one.
        #if q not in active_queues:
        auth = get('http://localhost:5000/users/api/session/auth', data={"token": tk, "service": "create_queue"}).json()
        if auth["success"] == False:
            return auth  # access denied
        active_queues.append([])
        return {"success": True, "msg":f"Queue added at position {len(active_queues)}."}
        #else:
        #    return {"success": False, "msg":"Queue already exists."}

    def delete(self):
        tk = request.form["token"]
        loc = request.form["queue_nr"] # integer value indicating index of queue
        if check_len(active_queues, loc):
            auth = get('http://localhost:5000/users/api/session/auth', data={"token": tk, "service": "create_queue"}).json()
            if auth["success"] == False:
                return auth  # access denied

            # delete queue
            q = active_queues.pop(loc)
            # delete all jobs in queue
            for job_id,_ in q:
                with open("data/masterdata.json", "r") as f:
                    data = json.load(f)
                if job_id in data:
                    data.pop(job_id)
                else:
                    print(f"Job {job_id} not found.")
            write_update(data)
            return {"success": True, "msg":f"Queue {loc} deleted."}

        return {"success": False, "msg": f"Queue {loc} not found. Nr. of active queues is {len(active_queues)}."}

api.add_resource(Queue, '/queues/api/queue')
api.add_resource(QManager, '/queues/api/manage')



if __name__ == '__main__':
    app.run(debug=True, port=7500)