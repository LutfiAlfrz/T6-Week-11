import requests

url = "https://api.pahrul.my.id/api/posts"
resp = requests.get(url, headers={"Accept": "application/json"})
print("Status:", resp.status_code)
print("Headers:", dict(resp.headers))
print("Response:", resp.text[:1000])