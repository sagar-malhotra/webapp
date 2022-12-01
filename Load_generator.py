import requests
  
# api-endpoint
URL = "https://prod.sagarmalhotra.me/app"
  
# sending get request and saving the response as response object
for i in range(1,1000):
    r = requests.get(url = URL)
    print(i)