import os
import requests
from requests.auth import HTTPBasicAuth
from dotenv import load_dotenv

load_dotenv()

####################################################################################################
####################################    Authorization    ###########################################
####################################################################################################

admin_name = os.environ.get("ADMIN_NAME")
admin_pass = os.environ.get("ADMIN_PASS")

# Authorized request, should return 200:
response = requests.post('http://127.0.0.1:5000/auth', auth=HTTPBasicAuth(admin_name, admin_pass))
print(f"{response.status_code}: {response.text}")

# Non-existing user, should return 403:
response = requests.post('http://127.0.0.1:5000/auth', auth=HTTPBasicAuth("I-do-not-exist", "my-password"))
print(f"{response.status_code}: {response.text}")

# Non-authorized request, should return 403:
response = requests.post('http://127.0.0.1:5000/auth')
print(f"{response.status_code}: {response.text}")

####################################################################################################
########################    Health check and environment info    ###################################
####################################################################################################

# health-check:
response = requests.post('http://127.0.0.1:5000/', auth=HTTPBasicAuth(admin_name, admin_pass))
print(f"{response.status_code}: {response.text}")

# version:
response = requests.post('http://127.0.0.1:5000/version', auth=HTTPBasicAuth(admin_name, admin_pass))
print(f"{response.status_code}: {response.text}")

####################################################################################################
##################################    User management    ###########################################
####################################################################################################

# 1) Should successfully create a new user:
payload = {"name": "test-user", "password": "test-password"}
response = requests.post('http://127.0.0.1:5000/user_add', auth=HTTPBasicAuth(admin_name, admin_pass),
                         json=payload)
print(f"{response.status_code}: {response.text}")


# 2) Trying to create a duplicating username, should return error:
payload = {"name": "test-user", "password": "test-password"}
response = requests.post('http://127.0.0.1:5000/user_add', auth=HTTPBasicAuth(admin_name, admin_pass),
                         json=payload)
print(f"{response.status_code}: {response.text}")

# 3) Should successfully set a new password for "test-user":
payload = {"name": "test-user", "password": "new-password"}
response = requests.post('http://127.0.0.1:5000/password_update', auth=HTTPBasicAuth(admin_name, admin_pass),
                         json=payload)
print(f"{response.status_code}: {response.text}")

# 4) Should delete the "test-user" from DB:
payload = {"name": "test-user"}
response = requests.post('http://127.0.0.1:5000/user_del', auth=HTTPBasicAuth(admin_name, admin_pass),
                         json=payload)
print(f"{response.status_code}: {response.text}")

# 4) Attempt to delete a non-existing user:
payload = {"name": "test-user"}
response = requests.post('http://127.0.0.1:5000/user_del', auth=HTTPBasicAuth(admin_name, admin_pass),
                         json=payload)
print(f"{response.status_code}: {response.text}")
