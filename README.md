# Fleet Manager 1.0


This is a fleet managment solution.

## Getting this repo ##
```bash
git clone git@github.com:terribleindustries/fleet_managment.git
exit
```

## Install Requirements ##
It is necessary to install dependencies in order to test the site locally before pushing to deployment.

### Debian-based ###
```bash
cat apt-requirements | xargs sudo apt-get install
sudo pip install -r requirements
```

## Install Requirements ##
In order to run this, you need to create the setup file.
``` bash
cp example_settings.py settings.py
```
Then you need to fill out the following:
* CAPTCHA_SECRET = the secret key from google.com/recaptcha/
* DB_USER_USER = The user to interact with the database.
* DB_USER_PASS = The password.
* TORNADO_SECRET = a random string to be used by tornado for secret.
* API_KEY = The api key to access the admin api.

### https ###
You will need to set the following settings:
* HTTPS = True
* CERTFILE = '<path to cert file>'
* KEYFILE = '<path to key file>'

## First Time Setup ##
In order to preform first tme set up the db, spmply run the program. On the first run, it will set up the database.
``` bash
./app.py
```

## Building the site and running ##
To run the site:
```bash
./app.py
```

Now navigate to: [http://127.0.0.1:8080/](http://127.0.0.1:8080/)

And you should see the site.
