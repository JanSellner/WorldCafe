# World Café
Find a group allocation to assign users to groups over multiple days. This is ideal for a course programme where users are split into several groups and then one group is assigned to a lecturer per day. However, instead of using fixed groups, this tool finds a better allocation with the goal to increase the number of meetings between the users. More details can be found on the webpage (after starting the server, see next section).

## Getting Started
- Build and run the dockerfile via `docker compose up --build`
   - Alternatively, use the [pre-built image](https://hub.docker.com/r/milania/group_allocation) from DockerHub: `docker run -it -p 5000:5000 milania/group_allocation`
- Navigate to [http://127.0.0.1:5000](http://127.0.0.1:5000)

## Development
### Core Algorithm
The core algorithm is written in [C++](group_allocation_c++) (and [Python](group_allocation_python)). In both cases, it is a standalone program which finds a good allocation given the number of users and groups. It can be called from the command line (C++ version inside docker)
```
/group_app/group_allocation_c++/x64/Release# ./group_allocation_c++.exe --n_groups 3 --n_users 6
# ...
[[0,2,2,0,1,1],[1,0,1,2,0,2],[2,1,0,1,2,0]]
```
In this case, it returns an allocation for 6 users who participate in a three-day course programme with three groups. For more details on the usage, see `/group_app/group_allocation_c++/x64/Release# ./group_allocation_c++.exe --help`.

To make changes to the program, just open the corresponding Visual Studio 2019 solution file (there are no further dependencies).

### Server
A small UI is built around the command line program in the form of a web interface. It provides a visualization of the program output (e.g. distribution of user meetings) and allows to export the result as a CSV table.

The server is written in [Flask](https://palletsprojects.com/p/flask/) and can be started by running the `run_server.py` file. The dependencies can be installed via `pip install -r requirements.txt` and a PyCharm project exists which can be used.
