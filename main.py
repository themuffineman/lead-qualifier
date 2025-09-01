import requests
import re
from apify_client import ApifyClient
from playwright.sync_api import sync_playwright, expect
import os
from dotenv import load_dotenv
load_dotenv()

token = os.getenv("APIFY_TOKEN")
posts = []
apify_client = ApifyClient(token)

linkedin_profiles = ["https://www.linkedin.com/in/petrus-sheya/"]
post_limit = 2
lead_website="https://docs.apify.com/academy/web-scraping-for-beginners"
linkedin_json = {
    "limit": post_limit,
    "usernames":linkedin_profiles 
}
wesbite_json={
    "aggressivePrune":False,
    "blockMedia":True,
    "clickElementsCssSelector": "[aria-expanded=\False\"]",
    "clientSideMinChangePercentage": 15,
    "crawlerType": "playwright:adaptive",
    "debugLog":False,
    "debugMode":False,
    "expandIframes":True,
    "ignoreCanonicalUrl":False,
    "ignoreHttpsErrors":False,
    "keepUrlFragments":False,
    "maxCrawlDepth": 0,
    "maxCrawlPages": 1,
    "proxyConfiguration": {
        "useApifyProxy":True
    },
    "readableTextCharThreshold": 100,
    "removeCookieWarnings":True,
    "removeElementsCssSelector": "nav, footer, script, style, noscript, svg, img[src^='data:'],\n[role=\"alert\"],\n[role=\"banner\"],\n[role=\"dialog\"],\n[role=\"alertdialog\"],\n[role=\"region\"][aria-label*=\"skip\" i],\n[aria-modal=\True\"]",
    "renderingTypeDetectionPercentage": 10,
    "respectRobotsTxtFile":True,
    "saveFiles":False,
    "saveHtml":False,
    "saveHtmlAsFile":False,
    "saveMarkdown":True,
    "saveScreenshots":False,
    "startUrls": [
        {
            "url": lead_website,
            "method": "GET"
        }
    ],
    "useSitemaps":False
}
linkedin_actor_run = apify_client.actor('apimaestro/linkedin-batch-profile-posts-scraper').call(
    run_input=linkedin_json
)
linkedin_dataset_items = apify_client.dataset(linkedin_actor_run['defaultDatasetId']).list_items().items
for item in linkedin_dataset_items:
    if 'text' in item and 'author' in item and 'headline' in item['author']:
        posts.append({"text": item['text'], "headline": item["author"]['headline']})
website_actor_run= apify_client.actor('apify/website-content-crawler').call(
    run_input=wesbite_json
)
website_dataset_items = apify_client.dataset(website_actor_run['defaultDatasetId']).list_items().items
website_content = website_dataset_items[0]["markdown"]
print(website_content)
print(posts)

