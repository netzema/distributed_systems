from mpi4py import MPI
from queueing import *
from timeseries import *

logging.basicConfig(filename='calculations_logs.log', format='%(asctime)s %(message)s', filemode='a+', level=logging.INFO)
logger = logging.getLogger()

app = Flask(__name__)
api = Api(app)

timeseries = create_time_series(100,300)

def process_calc(assets):
    comm = MPI.COMM_WORLD
    scatter_tasks = None

    if comm.rank == 0:
        tasks = [json.dumps({"parameter":asset}) for asset in assets]

        scatter_tasks = [None] * comm.size
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

            model = linear_fit(timeseries[asset])
            pred = predict_value(model, asset)

            pred = [pred, comm.rank]
            predictions.append(pred)

    # gathering results
    result = comm.gather(predictions, root=0)[0][0]

    return sum(result) / len(result)




class Calculations(Resource):
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
            rm = delete('http://localhost:7500/queues/api/queue', data={"queue": loc}).json()
            active_queues[loc] = q
            logger.info(f'Job {job} was pulled from queue {loc}.')
            j_id = list(job.keys())[0]
            assets = job[j_id]["assets"]
            result = process_calc(assets)
            #models = [linear_fit(timeseries[asset]) for asset in assets]
            #preds = [predict_value(models[assets.index(x)], x) for x in assets]
            #result = sum(preds)/len(preds)
            return {"success": True, "msg": result}
        logger.info(f'Queue {loc} was attempted to be accessed but not found.')
        return {"success": False, "msg": f"Queue {loc} not found. Nr. of active queues is {len(active_queues)}."}


api.add_resource(Calculations, '/financials/api/calc')



if __name__ == '__main__':
    app.run(debug=True, port=7600)