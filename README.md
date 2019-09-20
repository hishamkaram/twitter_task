[![Build Status](https://travis-ci.org/hishamkaram/twitter_task.svg?branch=master)](https://travis-ci.org/hishamkaram/twitter_task)
[![Coverage Status](https://coveralls.io/repos/github/hishamkaram/twitter_task/badge.svg?branch=master)](https://coveralls.io/github/hishamkaram/twitter_task?branch=master)
# twitter_task
This is a django project which provide two RESTful endpoints to provide data from Twitter.

## How to Setup?
- install on your local system directly
	- requirements:
    	- [python 3.6, 3.7](https://www.python.org/downloads/)
	- clone this repo and navigate to the repo directory.
	- (optional) create and activate python [virtualenv](https://virtualenv.pypa.io/en/latest/)
	- install project requirements using the following command:

		`pip install -r requirements.txt`
	- run django server using the following command:

		`python manage.py runserver`
	- now the server is running on http://localhost:8000

- using docker and docker-compose 
	- install [Docker](https://docs.docker.com/install/).
	- install [Docker Compose](https://docs.docker.com/compose/install/).
	- clone this repo and navigate to the repo directory.
	- run the following command to build and start the container.
		
		`docker-compose up -d --build`

## Available Endpoints:
 - Get tweets by a hashtag. Get the list of tweets with the given hashtag.
	- endpoint url: `http://<server_address>:<server_port>/hashtags/<hashtag_name>`
      - limit: integer, specifies the number of tweets to retrieve, the default is 30
 - Get the list of tweets that the user has on his feed.
	- endpoint url: `http://<server_address>:<server_port>/users/<screen_name_or_username>`
      - limit: integer, specifies the number of tweets to retrieve, the default is 30