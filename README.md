# zero

## build virtual environment

```sh
$ python3.6 -m venv venv
$ . venv/bin/activate
```

## running

```sh
$ pip install -r requirements.txt
$ python api_server.py --port-rest 8081 --port-tcp 10081
```