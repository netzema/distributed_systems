# **Distributed Systems SS22 - Daniel Netzl & Henrik Sainio**
## **Assignment 2: Service Oriented Architectures**
**Web services and REST**

Recall Assignment 1 and the architecture diagram you designed. We now want to start implementing the
system and write Python modules for some of the services. For each service, you must build only a part of
the functionality, which is specified in the service description below. The focus will be on defining and
implementing the interfaces that each service exposes.

### **1 Authentication Service**
The auth.py file takes care of the whole authorization process. It stores the users in an in-memory cache and assigns user rights to each role. Several functions are implemented to test if users exist, to create authentication tokens, to check if a user's token is valid and if their role allows accessing a certain service.

#### **Resources**
The file defines three resources: User, Login, Auth.

**User**
The User resource has a get, post, put and delete method. A user calls get in case he/she wants to access information of another user in the system. Depending on the role one gets varying results. The admin can access all the information also including the password. Other roles cannot see the password of each user. put is used to update a user's password while post is used to add new users. The delete method is used to delete an existing user. Note that only administrators can use the latter two services.

**Login**
The Login resource handles log ins and log outs. For logging in it uses the post method and creates and assigns a token to a given user if the username and password match. The put method is used to log out again, resetting the token.

**Auth**
The Auth resource is used to handle authentication for each service call. It uses the get method to retrieve the token and the service and checks for each user in the in-memory cache if it can find the match of given username and token.

### **2 Masterdata Service**
The Masterdata service handles all kind of jobs, calculations, and database calls. It contains two different resources: Jobs and JobCalulcation. Additionally, it contains several functions to write jobs and results to json files which serve as a persistent data storage. 
#### **Resources**
**Jobs**
Before performing any operation, the authorization service is called to check if the user is allowed to call the service. The post method is used to add a new job to the data storage, do the calculations and store the results in a separate json file. The job information contains the user, the assets (integer from 0 to 100), the timestamp of the creation of the job, the daterange which is 10 days by default and the status, which is "in progress" by default. This information is then stored in the file masterdata.json which contains all the jobs. The results of the calculations of the jobs are stored separately in the results.json file. 
The put method lets the user update the status of the job. It accesses a job by the given job id and adjusts the status according to the input. 
The delete method deletes a job from the masterdata.json file by accessing the job by the given id.

**JobCalculation**
This resource returns the results of the calculations of each of a job's assets. The results are numbers between 0 and 1. 

### **3 Testing Service**
The testing service provides simple workflows to test our program. This was made to make sure every functionality can be tested before submitting the program and to provide the professor with an idea of how to use it.
Example workflow:
-> start APIs auth.py and masterdata.py
-> start testing.py
-> You are asked to sign in. Login with username "admin" and password "admin"
Then you can add new users with "add_user <username> <role> <password>" and pressing enter. You can open testing.py in another terminal
and log in with created users and try out given commands with both admin account and newly created ones. 


### **4 Flask-RESTful**
Flask-RESTful is an easy to use and lightweight framework in Python to build REST-APIs. The main building block of the package are resources which provide easy access to multiple HTTP methods just by defining methods on a resource. Additionally, one can easily implement multiple URLs to be routed to a resource by using the add_resource() method on the API object. Another advantage of Flask-RESTful is its thorough documentation which covers everything one needs to get started. 
REST in general has several upsides over SOAP or GRPC. REST is flexible and uses simple verbs for its operations, which makes it simple to use and understand. JSON is the most common content type for REST data, which is straightforward to use, quite human readable and easy to debug. Other than the technical advantages, we also already gained some experience with Flask back in the Programming II course in the second semester.
