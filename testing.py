from requests import get, put, delete, post
import logging

logging.basicConfig(filename='clientlogs.log', filemode='a+', level=logging.INFO)

print("Please log in...")
while(True):
    username = input("Username: ")
    password = input("Password: ")

    r = post('http://localhost:5000/users/api/session/'+username, data={'password': password}).json()
    logging.info(f'User {username} tries to log in')
    if r["success"]:  # successful, save token as "tk" and break from login loop
        tk = r["token"]
        print(r["msg"])
        break
    else:
        print(r["msg"])

# main loop for calling commands
print(10*'*'+'\nAvailable commands:\nadd_user *name* *role* *password*\ndelete_user *name*\nadd_job\n'
      'edit_job\ndelete_job\nquit\ncreate_queue\ndelete_queue\npull_job'+10*'*')
while(True):
    cmd = input(">> ").split()

    # ALL COMMANDS
    # Adding user
    if cmd[0] == "add_user":
        if len(cmd) != 4:  # if not correct amount of parameters
            print("Make sure you give all parameters. Name, role, password")
            continue

        r = post('http://localhost:5000/users/api/'+username, data={'username': cmd[1],'role': cmd[2],
                                                                    'password': cmd[3], 'token': tk}).json()

        logging.info(f'User {username} tries to add user with metadata: username : {cmd[1]}, role: {cmd[2]}, password: {cmd[3]}')
        print(r["msg"])
        continue

    if cmd[0] == "delete_user":
        d = delete('http://localhost:5000/users/api/'+username, data={'username': cmd[1], "token": tk}).json()
        logging.info(f'User {username} tries to delete user {cmd[1]}')
        print(d["msg"])
        continue

    if cmd[0] == "add_job":
        assets = input("Give asset integers: ")
        l = len(get("http://localhost:7500/queues/api/manage")["Active queues"])
        q = input(f"Please enter queue index (0 - {l-1}): ")
        u = post('http://localhost:7500/queues/api/queue', data={"user":username, "assets": assets, "token": tk, "queue": q}).json()
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
        job_id = input("Enter id of job to delete: ")
        u = delete('http://localhost:8008/jobs/api/job',
                 data={"user": username, "job_id": job_id, "token": tk}).json()
        if u["success"] == False:
            print(u["msg"])
            logging.info(f'Job {job_id} was not deleted.')
            continue
        logging.info(f'User {username} deleted job {job_id}.')
        print(u["msg"])

    if cmd[0] == "quit":
        print("Bye!")
        break
