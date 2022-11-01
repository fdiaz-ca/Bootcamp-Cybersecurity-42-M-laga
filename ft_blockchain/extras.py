
instalar extension json view
python3 -m venv requests

cd Desktop\request

source ./bin/activate



import requests

t = {"sender": "pa",
"recipient": "pa",
"amount": 237
}

r = requests.post("http://127.0.0.1:5000/transactions/new", json=t)


kill%