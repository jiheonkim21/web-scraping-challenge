import os
from bs4 import BeautifulSoup as bs
import requests
from splinter import Browser
import pymongo
import pandas as pd
import time

def init_browser():
    executable_path = {'executable_path': '/usr/local/bin/chromedriver'}
    return Browser('chrome',**executable_path, headless=False)

def scrape_info():
    browser = init_browser()

    ######## NASA Mars News ########
    url = 'https://mars.nasa.gov/news'
    browser.visit(url)
    time.sleep(5)
    html = browser.html
    soup = bs(html,'html.parser')

    ## Find all news titles with soup.find_all
    news_titles = soup.find_all("div", class_="content_title")
    news_list = []

    ## Go through all the news_titles and append each headline to news_list
    for news in news_titles:
        if news.a:
            news_list.append(news.a.text.strip())
            print(news.text.strip())
    
    ## Set news_title is set to the first headline in the list
    news_title = news_list[0]

    ## Find all paragraphs within the website
    news_text = soup.find_all('div', class_='article_teaser_body')

    ## Set news_p as the paragraph under the first headline
    news_p = news_text[0].text.strip()

    ######## JPL Mars Space Images - Featured Image ########
    base_url = "https://www.jpl.nasa.gov/"
    url = "https://www.jpl.nasa.gov/spaceimages/?search=&category=Mars"
    browser.visit(url)

    ## Use Splinter to click on button with text 'FULL IMAGE'
    browser.links.find_by_partial_text('FULL IMAGE').click()

    # Use Splinter to click on button with text 'more info'
    browser.links.find_by_partial_text('more info').click()

    # Get current window's URL to be scraped
    new_url = browser.url

    # Retrieve page with the requests module
    response = requests.get(new_url)

    # Create BeautifulSoup object; parse with 'html.parser'
    soup = bs(response.text,'html.parser')

    # Find image url with .find
    featured_image_url = 'http://jpl.nasa.gov'+soup.find("figure", class_="lede").a['href']

    ######## Mars Facts ########

    # Set URL to mars facts webpage
    url = 'https://space-facts.com/mars/'

    # read in tabular data from the webpage with pandas
    tables = pd.read_html(url)

    # Create a dataFrame from the tabular data that has been read in
    df = tables[0]
    df.iloc[1:]

    # Convert dataFrame to .html, then clean up .html by removing unwanted newlines, \n's
    html_table = df.to_html(header = None, index = False)

    ######## Mars Hemispheres ########
    url = 'https://astrogeology.usgs.gov/search/results?q=hemisphere+enhanced&k1=target&v1=Mars'
    browser.visit(url)

    # HTML object
    html = browser.html

    #Parse HTML with Beautiful Soup
    soup = bs(html, 'html.parser')
    results = soup.find_all('div', class_='item')

    hemisphere_url = []

    for result in results:
        try:
            link = result.a['href']
            url = 'https://astrogeology.usgs.gov'+link
            hemisphere_url.append(url)
        except Exception as e:
            print(e)

    page_titles = []
    page_links = []
    hemisphere_image_urls = []
    keys={}
    for url in hemisphere_url:
   
        browser.visit(url)
        html = browser.html
        soup = bs(html, 'html.parser')
        titles = soup.find_all('title')
        links = soup.find_all('div', class_="downloads")
    
        for title in titles:
            page_titles.append(title.text.replace("| USGS Astrogeology Science Center", ""))
        for link in links:
            page_links.append(link.ul.li.a["href"])
    
    hemisphere_image_urls = [{'title': x, 'img_url': y} for x, y in zip(page_titles, page_links)]
    browser.quit()

    mars_data ={
        "news_title":news_title,
        "news_paragraph":news_p,
        "featured_mars_image":featured_image_url,
        "mars_table":html_table,
        "hemisphere_images":hemisphere_image_urls
    }

    return mars_data
















    
    


