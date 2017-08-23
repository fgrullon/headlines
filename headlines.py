import json
import urllib2
import urllib
import feedparser
import re
from flask import Flask 
from flask import render_template
from flask import request

app = Flask(__name__)

RSS_FEEDS = {'bbc' : 'http://feeds.bbci.co.uk/news/rss.xml',
	     'cnn' : 'http://rss.cnn.com/rss/edition.rss',
	     'fox' : 'http://feeds.foxnews.com/foxnews/latest',
	     'iol' : 'http://www.iol.co.za/cmlink/1.640'}

DEFAULTS = {'publication' : 'bbc',
	    'city' : 'London, UK',
	    'currency_from' : 'GBP',
	    'currency_to' : 'USD'}

weather_url = "http://api.openweathermap.org/data/2.5/weather?q={}&units=metric&appid=f5868f13b2a851e19b0e2de86cd08eeb"
currency_url = "http://openexchangerates.org//api/latest.json?app_id=fdf132f70cb64aa68259b0f3229e4396"

@app.route("/")
@app.route("/<publication>")
def get_home():
	#get customized headlines, based on user input or default
	publication = request.args.get('publication')
	if not publication:
	    publication = DEFAULTS['publication']
	articles = get_news(publication)

	#get customized weather with user location o default
	ip_addr = request.environ["REMOTE_ADDR"]
	location = get_location(ip_addr)
	if not location:
		location = DEFAULTS['city']
	weather = get_weather(location, weather_url)
	
	#get customized currency based on user input or default
	currency_from = request.args.get('currency_from')
	if not currency_from:
	    currency_from = DEFAULTS['currency_from']
	currency_to = request.args.get('currency_to')
	if not currency_to:
	    currency_to = DEFAULTS['currency_to']
	rate = get_rate(currency_from, currency_to)

	return  render_template("home.html", articles=articles, weather=weather, location=location)


def get_news(query):
	if not query or query.lower() not in RSS_FEEDS:
	    publication = DEFAULTS['publication']
	else:
	    publication = query.lower()
	feed = feedparser.parse(RSS_FEEDS[publication])
	return feed['entries']

def get_weather(query, weather_url):
	query = urllib.quote(query)
	url = weather_url.format(query)
	data = urllib2.urlopen(url).read()
	parsed = json.loads(data)
	weather = None
	if parsed.get("weather"):
		weather = {"description" : parsed["weather"][0]["description"].capitalize(),
			   "temperature" : parsed["main"]["temp"],
			   "city" : parsed["name"]
			  }
	return weather

def get_rate(frm, to):
	all_currency = urllib2.urlopen(currency_url).read()
	parsed = json.loads(all_currency).get('rates')
	frm_rate = parsed.get(frm.upper())
	to_rate = parsed.get(to.upper())
	return to_rate/frm_rate

def get_location(ip):
	api_url = 'http://ipinfo.io/'+ip+'/json'
	response = urllib2.urlopen(api_url)
	data = json.load(response)
	location = data['city']+", "+data['country']
	return location

if __name__ == "__main__":
	app.run(port=5000, debug=True)
