import configparser
from mpi4py import MPI
from queueing import *
from requests import delete, put
import sys
from timeseries import *

logging.basicConfig(filename='calculations_logs.log', format='%(asctime)s %(message)s', filemode='a+', level=logging.INFO)
logger = logging.getLogger()

# get configurations from config file
config_file = configparser.ConfigParser()
# read config file
config_file.read("config.ini")
n_proc = int(config_file['Processors']["n_proc"])

app = Flask(__name__)
api = Api(app)

timeseries = create_time_series(100,300)  # create time series data
if not os.path.isfile("config.ini"):
    # if config file does not exist, create it
    create_config.create_config_file()

def process_calc(assets):
    '''
    Predicts next time step for given asset.
    :param assets:
    :return: Average of next predicted time steps
    '''

    comm = MPI.COMM_WORLD
    scatter_tasks = None

    if comm.rank == 0:
        tasks = [json.dumps({"parameter":asset}) for asset in assets]  # create tasks from assets

        scatter_tasks = [None] *comm.size
        current_proc = 0
        for task in tasks:
            if scatter_tasks[current_proc] is None:
                scatter_tasks[current_proc] = []
            scatter_tasks[current_proc].append(task)
            current_proc = (current_proc + 1) % comm.size

    else:
        tasks = None

    units = comm.scatter(scatter_tasks, root=0)
    predictions = []

    if units is not None:
        for unit in units:
            asset = json.loads(unit)["parameter"]

            model = linear_fit(timeseries[asset])  # create model for asset
            pred = predict_value(model, asset)  # predict next timestep

            predictions.append(pred)

    # gathering results
    result = comm.gather(predictions, root=0)[0]
    return sum(result) / len(result)



class Calculations(Resource):
    def get(self):
        # pull a job
        tk = request.form["token"]
        auth = get('http://localhost:5000/users/api/session/auth', data={"token": tk, "service": "pull_job"}).json()
        if auth["success"] == False:
            return auth  # access denied
        results = []
        while True:  # pull jobs until queue is empty
            u = get('http://localhost:7500/queues/api/manage').json()
            active_queues = u["msg"]
            loc = int(request.form["queue"]) # integer value indicating index of queue
            if check_len(active_queues, loc):
                q = active_queues[loc][1] # get queue by index
                if len(q)==0: # if queue is empty
                    logger.info(f'Queue {loc} is empty.')
                    return {"success": False, "msg": f"Queue {loc} is empty. Results are: {results}"}
                job = q.pop(0) # pull job
                delete('http://localhost:7500/queues/api/queue', data={"queue": loc}).json()
                logger.info(f'Job {job} was pulled from queue {loc}.')

                j_id = list(job.keys())[0]
                assets = job[j_id]["assets"]
                result = process_calc(assets)  # calculate results with mpi
                logger.info(f'Calculations for job id  {j_id} were processed.')
                # update result queue
                put('http://localhost:7500/queues/api/queue', data={"job_id": j_id, "result": result})

                results.append(result)
                print({"success": True, "msg": results})
            else:
                logger.info(f'Queue {loc} was attempted to be accessed but not found.')
                return {"success": False, "msg": f"Queue {loc} not found. Nr. of active queues is {len(active_queues)}."}


api.add_resource(Calculations, '/financials/api/calc')

if __name__ == '__main__':
    app.run(debug=True, port=7600)