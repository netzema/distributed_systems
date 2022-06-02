from mpi4py import MPI
from queueing import *
from timeseries import *

logging.basicConfig(filename='calculations_logs.log', format='%(asctime)s %(message)s', filemode='a+', level=logging.INFO)
logger = logging.getLogger()

app = Flask(__name__)
api = Api(app)

timeseries = create_time_series(100,300)

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
            logger.info(f'Job {job} was pulled from queue {loc}.')
            assets = job["assets"]
            models = [linear_fit(timeseries[asset]) for asset in assets]
            preds = [predict_value(models[assets.index(x)], x) for x in assets]
            result = sum(preds)/len(preds)
            return {"success": True, "msg": result}
        logger.info(f'Queue {loc} was attempted to be accessed but not found.')
        return {"success": False, "msg": f"Queue {loc} not found. Nr. of active queues is {len(active_queues)}."}


api.add_resource(Calculations, '/financials/api/calc')



if __name__ == '__main__':
    app.run(debug=True, port=7500)