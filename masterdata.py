from flask import Flask, request
from flask_restful import Resource, Api
from datetime import datetime, timedelta
import json
import os
import random
from requests import get, put, delete, post
import logging

logging.basicConfig(filename='masterlogs.log', filemode='w+', level=logging.INFO)

app = Flask(__name__)
api = Api(app)

def get_id():
    with open("data/masterdata.json", "r") as f:
        obj = json.load(f)
        id = int(max(obj.keys())) + 1

    return id


def edit_json(job):
    if os.path.isfile("data/masterdata.json") is False:
        return {'success': False, 'msg': "No job records"}


def write_json(job):
    if os.path.isfile("data/masterdata.json") is False:
        with open("data/masterdata.json", "w") as f:
            json.dump({0: job}, f, indent=4)
            return True, 0

    with open("data/masterdata.json", "r") as f:
        obj = json.load(f)

    with open("data/masterdata.json", "w") as f:
        try:
            id = int(max(obj.keys())) + 1
            obj[str(id)] = job
            json.dump(obj, f, indent=4)
            return True, id
        except:
            return False, -1


def write_results_json(result):
    if os.path.isfile("data/results.json") is False:
        with open("data/results.json", "w") as f:
            json.dump({0: result}, f, indent=4)
            return True

    with open("data/results.json", "r") as f:
        obj = json.load(f)

    with open("data/results.json", "w") as f:
        try:
            id = int(max(obj.keys())) + 1
            obj[str(id)] = result
            json.dump(obj, f, indent=4)
            return True
        except:
            return False


class Jobs(Resource):
    def post(self):

        # authorize
        tk = request.form["token"]
        auth = get('http://localhost:5000/users/api/session/auth', data={"token":tk, "service": "add_job"}).json()
        logging.info(f'User {request.form["user"]} calls authentication of token for service of adding a job')
        if auth["success"] == False:
            return auth # access denied

        # calculation API call
        calc = get('http://localhost:8008/jobs/api/calculation', data={"assets": request.form["assets"]}).json()
        logging.info(f'User {request.form["user"]} calls job calculation service with assets {request.form["assets"]}')
        if 'error_msg' in calc: # if calculation successful
            return calc

        else:
            job_info = {}
            job_info["user"] = request.form["user"]
            assets = request.form["assets"].split(",")
            print(assets)
            assets = [int(i) for i in assets]
            job_info["assets"] = assets
            job_info["timestamp"] = datetime.timestamp(datetime.now())
            job_info["daterange"] = str(datetime.now().date()) + "/" + str((datetime.now() + timedelta(days=10)).date())

            # TODO: Needs a better solution, but works for now. What if results dont get added but job does?
            status, id_n = write_json(job_info)
            if status:
                result_info = {}
                result_info["id"] = id_n
                result_info["timestamp"] = job_info["timestamp"]
                result_info["results"] = calc

                if write_results_json(result_info):
                    return {'success': True, 'msg': "results added"}
                else:
                    return {'success': False, 'msg': "Error results not added"}

            else:
                logging.info(f'User {request.form["user"]} tried to add job, but job was not added')
                return {'success': False, 'msg': "Error job not added"}

    def put(self):
        # TODO: editing jobs. Whatever that means.
        pass

    def delete(self):
        # TODO: removing jobs. Also remove results, or no?
        pass



class JobCalculation(Resource):
    def get(self):
        # get request assets
        assets = request.form["assets"].split(",")
        assets = [int(i) for i in assets]

        if all([not isinstance(item, int) for item in assets]): # check if non-integers
            return {'success': False, 'error_msg': 'Non-integer values in assets'}

        if any(v > 100 or v < 1 for v in assets): # check if in bounds 1-100
            return {'success': False, 'error_msg': 'Asset values out of bounds.'}

        # asset calculations
        assets = dict([(val, round(random.uniform(0, 1), 3)) for val in assets])

        return assets


api.add_resource(Jobs, '/jobs/api/job')
api.add_resource(JobCalculation, '/jobs/api/calculation')


if __name__ == '__main__':
    app.run(debug=True, port=8008)