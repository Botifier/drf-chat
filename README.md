# minimal drf chat app using websockets.
 
## To run the webserver:
```
docker-compose build
docker-compose up
```

Then navigate to localhost:8000, choose username and then navigate with a different browser(icognito window) to the same url, register and start chatting!

## Tests running:
```
virtualenv .env
source .env/bin/activate
pip install -r requirements.txt
python manage.py test
```
or if the webapp container is up:
```
docker-compose exec webapp python manage.py test
```

## Todo:
### * Add travis support
### * Add seperate container for testing
### * Improve the ui.
### * Add node server for the frontend
