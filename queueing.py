import configparser
import create_config
from masterdata import *
import os
from requests import get
from time import sleep
from threading import Thread

logging.basicConfig(filename='queue_logs.log', format='%(asctime)s %(message)s', filemode='a+', level=logging.INFO)
logger = logging.getLogger()

app = Flask(__name__)
api = Api(app)

def save_queues(queues, timer):
    # function to save queues periodically after given time
    while True:
        sleep(timer)
        with open("data/queues.json", "w") as f:
            json.dump(queues, f, indent=4)
        logger.info('Saved queues to persistent storage.')


if not os.path.isfile("config.ini"):
    # if config file does not exist, create it
    create_config.create_config_file()

# get configurations from config file
config_file = configparser.ConfigParser()
# read config file
config_file.read("config.ini")
maxqlength = int(config_file['QueueSettings']["maxqlength"])
timer = int(config_file['QueueSettings']["timer"])

def check_len(active_queues, location):
    # function to check if given queue indices exist
    if location >= len(active_queues):
        return False
    return True

if os.path.isfile("data/queues.json"):
    # load queues from persistent storage
    with open("data/queues.json", "r") as f:
        active_queues = json.load(f)
else:
    # create empty queue
    default_queue = []
    active_queues = [default_queue]


class Queue(Resource):
    def post(self):
        # add a new job
        loc = int(request.form["queue"]) # store index of the queue
        tk = request.form["token"]
        auth = get('http://localhost:5000/users/api/session/auth', data={"token": tk, "service": "add_job"}).json()
        if auth["success"] == False:
            return auth # access denied

        if check_len(active_queues, loc):
            # get the queue by index
            q = active_queues[loc]
            if len(q) < maxqlength: # if queue is not full
                # create job
                job_info = {}
                job_info["user"] = request.form["user"]
                assets = request.form["assets"].split(",")
                print(assets)
                assets = [int(i) for i in assets]
                job_info["assets"] = assets
                job_info["timestamp"] = datetime.timestamp(datetime.now())
                job_info["daterange"] = str(datetime.now().date()) + "/" + str((datetime.now() + timedelta(days=10)).date())
                job_info["status"] = "queued"

                # save job to json
                _, job_id = write_json(job_info)
                # add job and its index to queue
                q.append({job_id: job_info}) # store job_id
                logger.info(f'Job {job_id} added to queue {loc}.')
                return {"success": True, "msg": f"Job {job_id} successfully added to queue {loc}."}

            else:
                logger.info(f'Job was attempted to be added to a full queue ({loc}).')
                return {"success": False, "msg": f"Queue {loc} is full! Please choose another one."}

        logger.info(f'Queue {loc} was not found.')
        return {"success": False, "msg": f"Queue {loc} not found. Nr. of active queues is {len(active_queues)}."}

    def get(self):
        # pull a job
        tk = request.form["token"]
        auth = get('http://localhost:5000/users/api/session/auth', data={"token": tk, "service": "pull_job"}).json()
        if auth["success"] == False:
            return auth  # access denied

        loc = int(request.form["queue"]) # integer value indicating index of queue
        if check_len(active_queues, loc):
            q = active_queues[loc] # get queue by index
            if len(q)==0: # if queue is empty
                logger.info(f'Queue {loc} is empty.')
                return {"success": False, "msg": f"Queue {loc} is empty."}
            job = q.pop(0) # pull job
            logger.info(f'Job {job} was pulled from queue {loc}.')
            return {"success": True, "msg": job}
        logger.info(f'Queue {loc} was attempted to be accessed but not found.')
        return {"success": False, "msg": f"Queue {loc} not found. Nr. of active queues is {len(active_queues)}."}

class QManager(Resource):
    def get(self):
        # get all queues
        return {"success": True, "msg": [q for q in enumerate(active_queues)]}

    def post(self):
        # create a new queue
        tk = request.form["token"]
        auth = get('http://localhost:5000/users/api/session/auth', data={"token": tk, "service": "create_queue"}).json()
        if auth["success"] == False:
            return auth  # access denied

        active_queues.append([]) # add empty queue
        logger.info(f'Queue in position {len(active_queues)-1} was added.')
        return {"success": True, "msg":f"Queue added at position {len(active_queues)-1}."}

    def delete(self):
        # delete a queue and all its jobs
        tk = request.form["token"]
        loc = int(request.form["queue"]) # integer value indicating index of queue
        if check_len(active_queues, loc):
            auth = get('http://localhost:5000/users/api/session/auth', data={"token": tk, "service": "delete_queue"}).json()
            if auth["success"] == False:
                return auth  # access denied

            # delete queue
            q = active_queues.pop(loc)
            # delete all jobs in queue
            for job in q: # iterate through the queue
                for job_id,_ in job.items(): # for each job in the queue
                    with open("data/masterdata.json", "r") as f:
                        # get content of masterdata.json
                        data = json.load(f)
                    job_id = str(job_id) # convert job_id to string
                    if job_id in data: # if job is in masterdata, delete it
                        data.pop(job_id)
                        logger.info(f"Job {job_id} deleted.")
                    else:
                        print(f"Job {job_id} not found.")
                        logger.info(f"Job {job_id} not found.")
                # update masterdata.json
                write_update(data)
                if len(active_queues) == 0:
                    # if there are no other queues left, create the default one
                    active_queues.append([])

            logger.info(f'Queue {loc} was deleted.')
            return {"success": True, "msg":f"Queue {loc} deleted."}

        logger.info(f'Queue {loc} was attempted to be deleted but not found.')
        return {"success": False, "msg": f"Queue {loc} not found. Nr. of active queues is {len(active_queues)}."}

api.add_resource(Queue, '/queues/api/queue')
api.add_resource(QManager, '/queues/api/manage')



if __name__ == '__main__':
    # create thread for saving queues after timer
    daemon = Thread(target=save_queues, args=(active_queues, timer, ), daemon=True, name='Background')
    daemon.start()

    app.run(debug=True, port=7500)