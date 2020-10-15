# Bookify - Your next book is right around the corner

*Have you ever been in a situtation where you don't know what to read next ?* 
Well you came to the right place ! 
With Bookify you can choose your next book using our review system 

* We have reviews from the users of Bookify aswell as from the users of GoodReads , using GoodReads API . 

## Site Demo
You can view the site and test for yourself here : https://thebookify.herokuapp.com/


## To use this app 

```bash
# Clone repo
$  git clone https://github.com/ArtemKuznetsovv/FindYourNextBook.git

$ cd FindYourNextBook

# Install all dependencies
$ pip install -r requirements.txt

# ENV Variables
$ set FLASK_APP = application.py # flask run
$ set DATABASE_URL = Heroku Postgres DB URI
$ set GOODREADS_KEY = Goodreads API Key. # More info: https://www.goodreads.com/api

$ flask run
```

## Technologies used in this project 
1. For the backend part i worked with Python-Flask , and to store user data i worked with Heroku and PostgreSQL
2.Deployment is done through heroku
3. Frontend is mostly CSS and Bootstrap . 


## What i learned from this project 

1. I learned this awesome mini framework called Flask !, in which i got acquainted with sessions ,routing , templating and more . 
2. Got familiar with storing user data using Heroku-PostgreSql
3. Using Jinja 2 for the writing more clean and efficient  HTML (templating)
4. Working with diffrent API's such as Goodreads API to get user reviews , and OpenLibrary API to get the cover of the books . 
