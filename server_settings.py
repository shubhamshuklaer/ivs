import os
def init():
    global port
    global num_forks
    global num_threads_per_fork
    global service_dir
    global user_auth_db_name

    port=8080
    num_forks=2
    num_threads_per_fork=2
    service_dir=os.path.join(os.getcwd(),"service_dir")
    user_auth_db_name="users"     # TODO : Caution!! don't change this value.... we need to change its counterpart int the website also
