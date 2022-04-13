import logging
from requests import get, put, delete, post

logging.basicConfig(filename='clientlogs.log', filemode='w+', level=logging.INFO)

print("Please log in...")
while(True):
    username = input("Username: ")
    password = input("Password: ")
    #user = get('http://localhost:5000/users/api/'+name).json()
    #username = list(user.items())[0][0]
    logging.info(f'User {username} checks if username exists')

    #if 'success' in user:
    #    print(user["msg"])
    #    continue

    r = post('http://localhost:5000/users/api/session/'+username, data={'password': password}).json()
    logging.info(f'User {username} tries to log in')
    if r["success"] == True:
        tk = r["token"]
        print(r["msg"])
        break

    print("Username or password incorrect. Try again")

while(True):
    print("\n\nAvailable commands:\nadd_user *name* *role* *password*\ndelete_user *name*\nadd_job\n"
          "get_all_jobs\nget_all_results\nedit_job\ndelete_job")
    cmd = input(">> ").split()
    print(cmd)
    if cmd[0] == "add_user":
        r = post('http://localhost:5000/users/api/'+username, data={'username' : cmd[1], 'role': cmd[2], 'password': cmd[3]}).json()
        logging.info(f'User {username} tries to add user with metadata: username : {cmd[1]}, role: {cmd[2]}, password: {cmd[3]}')
        print(r["msg"])
        continue

    if cmd[0] == "delete_user":
        d = delete('http://localhost:5000/users/api/'+username, data={'username': cmd[1]}).json()
        logging.info(f'User {username} tries to delete user {cmd[1]}')
        print(d["msg"])
        continue

    if cmd[0] == "add_job":
        assets = input("Give asset integers: ")
        u = post('http://localhost:8008/jobs/api/job', data={"user":username, "assets": assets, "token": tk}).json()
        logging.info(f'User {username} tries to add a job with parameters "user":{username}, "assets": {assets}')
        if u["success"] == False:
            print(u["msg"])
            continue

        print(u["msg"])

    if cmd[0] == "edit_job":
        job_id = input("Enter id of job to change: ")
        status = input("Enter new status: ")
        u = put('http://localhost:8008/jobs/api/job',
                 data={"user": username, "job_id": job_id, "status": status, "token": tk}).json()
        if u["success"] == False:
            print(u["msg"])
            logging.info(f'Status of job {job_id} was not changed.')
            continue
        logging.info(f'User {username} changed the status of job {job_id} to {status}.')
        print(u["msg"])

    if cmd[0] == "delete_job":
        job_id = input("Enter id of job to change: ")
        u = delete('http://localhost:8008/jobs/api/job',
                 data={"user": username, "job_id": job_id, "token": tk}).json()
        if u["success"] == False:
            print(u["msg"])
            logging.info(f'Job {job_id} was not deleted.')
            continue
        logging.info(f'User {username} deleted job {job_id}.')
        print(u["msg"])