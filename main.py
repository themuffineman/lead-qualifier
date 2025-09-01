import requests
import re
from apify_client import ApifyClient
from playwright.sync_api import sync_playwright, expect
import os
from dotenv import load_dotenv
from openai import OpenAI
from pydantic import BaseModel
from typing import Literal
load_dotenv()
client = OpenAI()

class LeadQuality(BaseModel):
    qualified: Literal["strong", "weak", "unqualified"]
    reason: str
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
    "removeElementsCssSelector": "nav, footer, script, style, noscript, svg, img[src^='data:'],[role=\"alert\"],[role=\"banner\"],[role=\"dialog\"],[role=\"alertdialog\"],[role=\"region\"][aria-label*=\"skip\" i],[aria-modal=\True\"]",
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
response = client.responses.create(
  model="gpt-5-mini",
  input=[
    {
      "role": "developer",
      "content": [
        {
          "type": "input_text",
          "text": "Your highly qualified and diligent, salesperson. You are an expert at identifying qualified, high intent leads from lead lists"
        }
      ]
    },
    {
      "role": "user",
      "content": [
        {
          "type": "input_text",
          "text": 
          """
            I run a service that sets up speed-to-lead systems for real estate agents. 
            Essentially, the moment a new lead comes in, my system engages them immediately via text or email so they don’t get lost to a competitor. 
            If my system doesn’t increase their response rate by at least 5%, they don’t pay.
            
            I have a lead from my list. Your task is to qualify and validate whether this individual is a good fit for my service based on the signals below.
            Return an object with the following structure:
            {   
                "qualified": "weak" | "strong" | "unqualified",   
                "reason": "Explain why this lead is a good fit or not, referencing the signals below." 
            }
            Signals to evaluate:
            Active lead captureLook for contact forms, “Get a free home valuation,” “Schedule a tour,” or pop-ups.
            If there’s no form or CTA, they likely don’t focus on online leads → weaker fit.
            Ad activityCheck Facebook Ads Library or Google transparency reports
            If they run paid ads, they need fast lead response
            No ads? They may rely on organic leads → still a fit, but weaker
            CRM / tech stack hintsLook for mentions of Follow Up Boss, kvCORE, BoomTown, Sierra Interactive, etc
            Shows they’re thinking about automation, but maybe not optimized
            Traffic & volumeUse SimilarWeb / SEMrush estimates
            Sites with steady traffic → more lead flow → better fit
            Inputs:
            Company website: {{website_content}} 
            -------------------------------------------------------------------
            LinkedIn posts: {{linkedin_posts}}

            Use the information from the website and LinkedIn to evaluate the lead according to the signals above and return the object with your recommendation
          """
        }
      ]
    }
  ],
  text={
    "format": {
      "type": "text"
    },
    "verbosity": "medium"
  },
  textformat=LeadQuality,
  reasoning={
    "effort": "medium",
    "summary": "auto"
  },
  tools=[],
  store=True,
  include=[
    "reasoning.encrypted_content",
    "web_search_call.action.sources"
  ]
)
print(website_content)
print(response.text)
print(posts)

