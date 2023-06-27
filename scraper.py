# Import libraries
from bs4 import BeautifulSoup
from telegram import Bot
from dotenv import load_dotenv
from json import JSONDecodeError
import os
import requests
import time
import json

# Load environment variables
load_dotenv()

# Telegram tokens and IDs
bot_token = os.getenv("BOT_TOKEN")
pub_channel_id = os.getenv("PUB_CHANNEL_ID")
priv_channel_id = os.getenv("PRIV_CHANNEL_ID")
user_id = os.getenv("USER_ID")

# Telegram bot setup
bot = Bot(token=bot_token)

# Sources
site_urls = {
    "ANSA": "https://www.ansa.it/",
    "Repubblica": "https://www.repubblica.it",
    "SkyUK": "https://news.sky.com",
    "NHK": "https://www3.nhk.or.jp/news/",
    "Associated Press": "https://apnews.com",
    "SkyIT": "https://tg24.sky.it/"
}

# Create a set to store news that have already been sent
sent_news = set()

# Send news to Telegram
def send_news(flash_source, flash_content, flash_link, channel_id):
    # Get current time
    flash_time = time.localtime()
    if flash_link != '':
        message_text = "(#" + flash_source + ") — <b>FLASH | " + flash_content + " — [" + time.strftime("%H:%M", flash_time) + "]</b>\n\n" + flash_link + "\n\n@alexzan_blog / @alexzan_news"
    else:
        message_text = "(#" + flash_source + ") — <b>FLASH | " + flash_content + " — [" + time.strftime("%H:%M", flash_time) + "]</b>\n\n@alexzan_blog / @alexzan_news"
    # Send message
    bot.send_message(chat_id=channel_id, text=message_text, parse_mode="HTML")

# Check if the news has already been sent to Telegram
def check_news(message_text):
    if message_text in sent_news:
        return True

# Flash ANSA
def flash_ansa(soupSite):
    ansa_banner = soupSite.find("span", class_="flash-news-title")
    if ansa_banner is None:
        pass
    else:
        flash_ansa = ansa_banner.text
        if check_news(flash_ansa):
            pass
        else:
            sent_news.add(flash_ansa)
            send_news("ANSA", flash_ansa, '', priv_channel_id)

# Flash Repubblica
def flash_repubblica(soupSite):
    repubblica_banner = soupSite.find("h2", class_="breaking-news__title")
    if repubblica_banner is None:
        pass
    else:
        repubblica_title = repubblica_banner.find("a", recursive=False)
        if repubblica_title is None:
            pass
        else:
            # Store the link if it exists
            if repubblica_title['href'] != None:
                flash_repubblica_link = repubblica_title['href']
            flash_repubblica = repubblica_title.text
            if check_news(flash_repubblica):
                pass
            else:
                sent_news.add(flash_repubblica)
                send_news("Repubblica", flash_repubblica, flash_repubblica_link, priv_channel_id)

# Flash Sky UK
def flash_skyuk(soupSite):
    sky_breaking = soupSite.find("div", class_="sdc-site-tile--breaking")
    if sky_breaking is None:
        pass
    else:
        flash_sky_link = sky_breaking.find("a", class_="sdc-site-tile__headline-link")
        flash_sky_title = sky_breaking.find("span", class_="sdc-site-tile__headline-text")
        if flash_sky_title is None:
            pass
        else:
            # Store the link if it exists
            if flash_sky_link['href'] != None:
                flash_sky_link = site_urls["SkyUK"] + flash_sky_link['href']
            flash_sky = flash_sky_title.text
            if check_news(flash_sky):
                pass
            else:
                sent_news.add(flash_sky)
                send_news("SkyUK", flash_sky, flash_sky_link, priv_channel_id)

# Flash NHK
def flash_nhk(soupSite):
    nhk_top = soupSite.find("section", class_="module--content")
    if nhk_top is None:
        pass
    else:
        nhk_article = nhk_top.find("h1", class_="content--header-title")
        nhk_link = nhk_top.find("a")
        nhk_title = nhk_article.find("em", class_="title")
        if nhk_title is None:
            pass
        else:
            # Store the link if it exists
            if nhk_link['href'] != None:
                nhk_link = "https://www3.nhk.or.jp" + nhk_link['href']
            flash_nhk = nhk_title.text
            if check_news(flash_nhk):
                pass
            else:
                sent_news.add(flash_nhk)
                send_news("NHK", flash_nhk, nhk_link, priv_channel_id)

# Flash Associated Press
def flash_ap(soupSite):
    ap_top = soupSite.find("div", class_="PagePromoModuleA")
    if ap_top is None:
        pass
    else:
        ap_article = soupSite.find("div", class_="PagePromoModuleA-content")
        ap_link = ap_article.find("div", class_="PagePromo-title").find("a")
        ap_title = ap_article.find("span", class_="PagePromoContentIcons-text")
        if ap_title is None:
            pass
        else:
            # Store the link if it exists
            if ap_link['href'] != None:
                ap_link = ap_link['href']
            flash_ap = ap_title.text
            if check_news(flash_ap):
                pass
            else:
                sent_news.add(flash_ap)
                send_news("AP", flash_ap, ap_link, priv_channel_id)

# Flash Sky IT
def flash_skyit(soupSite):
    skyit_banner = soupSite.find("div", class_="c-breaking-news")
    if skyit_banner is None:
        pass
    else:
        skyit_article_link = skyit_banner.find("a", class_="c-breaking-news__content")
        skyit_article_nolink = skyit_banner.find("div", class_="c-breaking-news__content")
        if skyit_article_link != None:
            skyit_link = skyit_article_link['href']
            skyit_title = skyit_article_link.find("p", class_="c-breaking-news__text").find("span")
        else:
            skyit_link = ''
            skyit_title = skyit_article_nolink.find("p", class_="c-breaking-news__text").find("span")
        if skyit_title is None:
            pass
        else:
            # Store the link if it exists
            if skyit_link != None:
                flash_skyit_link = skyit_link
            flash_skyit = skyit_title.text
            if check_news(flash_skyit):
                pass
            else:
                sent_news.add(flash_skyit)
                send_news("SkyTG24", flash_skyit, flash_skyit_link, priv_channel_id)

# Flash Reuters
def flash_reuters():
    try:
        flash_reuters = requests.get('https://api.priapusiq.com/reuters')
        reuters_data = json.loads(flash_reuters.text)
        if reuters_data is None:
            pass
        else:
            if reuters_data:
                try:
                    reuters_title = reuters_data['data'][0]['title']
                except IndexError:
                    pass
                else:
                    reuters_version = reuters_data['data'][0]['version']
                    if reuters_version == 1:
                        if check_news(reuters_title):
                            pass
                        else:
                            sent_news.add(reuters_title)
                            time.sleep(10)
                            reuters_search = requests.get('https://www.reuters.com/pf/api/v3/content/fetch/articles-by-search-v2?query=%7B%22keyword%22%3A%22' + reuters_title + '%22%2C%22offset%22%3A0%2C%22orderby%22%3A%22display_date%3Adesc%22%2C%22size%22%3A20%2C%22website%22%3A%22reuters%22%7D&d=144&_website=reuters')
                            reuters_results = json.loads(reuters_search.text)
                            if reuters_results is None:
                                send_news("Reuters", reuters_title, '', priv_channel_id)
                            else:
                                if reuters_results:
                                    try:
                                        reuters_url = reuters_results['result']['articles'][0]['canonical_url']
                                    except (IndexError, KeyError, TypeError) as e:
                                        pass
                                    else:
                                        reuters_link = "https://www.reuters.com" + reuters_url
                                        send_news("Reuters", reuters_title, reuters_link, priv_channel_id)
                    else:
                        pass
    except JSONDecodeError:
       pass

# Fetch news
def fetch_news():
    for site in site_urls:
        sitePage = requests.get(site_urls[site])
        soupSite = BeautifulSoup(sitePage.content, "html.parser")
        match site:
            case "ANSA":
                flash_ansa(soupSite)
            case "Repubblica":
                flash_repubblica(soupSite)
            case "SkyUK":
                flash_skyuk(soupSite)
            case "NHK":
                flash_nhk(soupSite)
            case "Associated Press":
                flash_ap(soupSite)
            case "SkyIT":
                flash_skyit(soupSite)
    flash_reuters()

# Main loop
while True:
    # Clear the set if it contains more than 500 news
    if(len(sent_news) > 500):
        sent_news.clear()
        bot.send_message(chat_id=user_id, text="(#SUZU) | DEBUG -- FLASH SET CLEARED")
    elif(len(sent_news) == 0):
        bot.send_message(chat_id=user_id, text="(#SUZU) | DEBUG -- FLASH SCRAPER STARTED")
    # Repeat the process every minute
    while True:
        fetch_news()
        time.sleep(60)
