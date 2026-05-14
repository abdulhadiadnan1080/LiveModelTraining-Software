import requests

API_BASE = "http://localhost:8001"

def Get_users():

   response = requests.get(f"{API_BASE}/users")
   if response.status_code == 200:
       return response.json()
   else:
       print('no response from server')
       return None

print(Get_users())  

def forget_password1():
   user = input("Enter your username: ")
   response = requests.post(
       f"{API_BASE}/forgot/password", 
       json={"username": user, "password": ""} 
   )
   if response.status_code == 200:
      print(f"Password for user '{user}' has been reset to 'hadi'.")
   else:
      print('Warr Gya')

forget_password1()