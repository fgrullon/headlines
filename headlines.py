import json
import urllib2
import urllib
import feedparser
import re
from flask import Flask 
from flask import render_template
from flask import request
from urllib2 import urlopen

app = Flask(__name__)

RSS_FEEDS = {'bbc' : 'http://feeds.bbci.co.uk/news/rss.xml',
	     'cnn' : 'http://rss.cnn.com/rss/edition.rss',
	     'fox' : 'http://feeds.foxnews.com/foxnews/latest',
	     'iol' : 'http://www.iol.co.za/cmlink/1.640'}

@app.route("/")
@app.route("/<publication>")
def get_news(publication="bbc"):
	query = request.args.get("publication")
	location = get_location()
	if not query or query.lower() not in RSS_FEEDS:
		publication = "bbc"
	else:
		publication = query.lower()
	feed = feedparser.parse(RSS_FEEDS[publication])
	weather = get_weather(location)
	return  render_template("home.html", articles=feed['entries'], weather=weather)

def get_weather(query):
	api_url = "http://api.openweathermap.org/data/2.5/weather?q={}&units=metric&appid=f5868f13b2a851e19b0e2de86cd08eeb"
	query = urllib.quote(query)
	url = api_url.format(query)
	data = urllib2.urlopen(url).read()
	parsed = json.loads(data)
	weather = None
	if parsed.get("weather"):
		weather = {"description" : parsed["weather"][0]["description"].capitalize(),
			   "temperature" : parsed["main"]["temp"],
			   "city" : parsed["name"]
			  }
	return weather

def get_location():
	api_url = 'http://ipinfo.io/json'
	response = urlopen(api_url)
	data = json.load(response)
	location = data['region']+", "+data['country']
	return location

if __name__ == "__main__":
	app.run(port=5000, debug=True)
