# Watchdog Alerts

### Site Notes

1. Django web application that hosts web crawlers that scrape Amazon, Walmart, Target, and Best Buy. Using multithreading and cronjobs, users are able to receive product availabilty alerts at lightning fast speeds

### Setup

1. `virtualenv venv`
1. `source venv/bin/activate` or `source venv/Scripts/activate`
1. `pip install -r requirements.txt`
1. `python manage.py migrate`
1. `python manage.py runserver`
