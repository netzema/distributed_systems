from flask import Flask, request
from flask_restful import Resource, Api
from datetime import datetime, timedelta
import json
import logging
import os
import random
from requests import get

app = Flask(__name__)
api = Api(app)

default_queue = []
active_queues = [default_queue]

class Queue(Resource):
    def post(self, loc = default_queue):
        tk = request.form["token"]
        auth = get('http://localhost:5000/users/api/session/auth', data={"token": tk, "service": "add_job"}).json()
        if auth["success"] == False:
            return auth # access denied

        job_info = {}
        job_info["user"] = request.form["user"]
        assets = request.form["assets"].split(",")
        print(assets)
        assets = [int(i) for i in assets]
        job_info["assets"] = assets
        job_info["timestamp"] = datetime.timestamp(datetime.now())
        job_info["daterange"] = str(datetime.now().date()) + "/" + str((datetime.now() + timedelta(days=10)).date())
        job_info["status"] = "queued"

        loc.append(job_info)

    def get(self):
        tk = request.form["token"]
        auth = get('http://localhost:5000/users/api/session/auth', data={"token": tk, "service": "pull_job"}).json()
        if auth["success"] == False:
            return auth  # access denied

        q = request.form["queue"]
        job = q.pop(0)
        return job

class QManager(Resource):
    def get(self):
        return {"Active queues": active_queues}

    def post(self):
        tk = request.form["token"]
        q = request.form["queue"]
        if q not in active_queues:
            auth = get('http://localhost:5000/users/api/session/auth', data={"token": tk, "service": "create_queue"}).json()
            if auth["success"] == False:
                return auth  # access denied
            active_queues.append(q)
        else:
            return {"success": False, "msg":"Queue already exists."}

    def delete(self):
        tk = request.form["token"]
        q = request.form["queue"]
        if q in active_queues:
            auth = get('http://localhost:5000/users/api/session/auth', data={"token": tk, "service": "create_queue"}).json()
            if auth["success"] == False:
                return auth  # access denied
            active_queues.remove(q)
        else:
            return {"success": False, "msg":"Queue does not exists."}

api.add_resource(Queue, '/queues/api/queue')
api.add_resource(QManager, '/queues/api/manage')



if __name__ == '__main__':
    app.run(debug=True, port=7500)