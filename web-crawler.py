#! ~/miniforge3_new/bin/python

# Import necessary modules
import requests
from bs4 import BeautifulSoup
import pandas as pd
import re
import time
from selenium import webdriver
chromedriver = '/Users/sihanzhang/Desktop/Changing_Room/chromedriver'
from selenium.webdriver.common.keys import Keys
import json
from datetime import date
import logging
import os
from sqlalchemy import create_engine

dir_path = os.path.dirname(os.path.realpath(__file__))
filename = os.path.join(dir_path, 'web-scraper.log')

# Schedule Python Scripts As Cron Jobs With Crontab on Mac
# Use Logger to track the execution time (Update at 00:00 every day)
logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)

file_handler = logging.FileHandler(filename)
file_handler.setLevel(logging.INFO)
file_handler.setFormatter(logging.Formatter('%(asctime)s - %(levelname)s - %(message)s'))
logger.addHandler(file_handler)

def do_logging():
    logger.info("test")

class RefScraper:
    
    def __init__(self):
        self.baseurl = 'https://www.thereformation.com/clothing'
        self.urls = []
        self.num_clothes = 0
    
    # Get urls of all clothes after scrolling down the page for a pre-determined times
    def get_all_product_urls(self, scroll_number):
        browser = webdriver.Chrome(chromedriver)

        browser.get(self.baseurl)
        time.sleep(5)

        scroll_pause_time = 3

        # Uncomment to scroll to the end
        # Get scroll height
        # last_height = browser.execute_script("return document.body.scrollHeight")
        # while True:

        # Limit the number of scrolls
        while scroll_number:

            # Scroll down to bottom
            browser.execute_script("window.scrollTo(0, document.body.scrollHeight);")

            # Limit the number of scrolls
            scroll_number -= 1

            # Wait to load page
            time.sleep(scroll_pause_time)

            # Uncomment to scroll to the end
            # Calculate new scroll height and compare with last scroll height
            # new_height = browser.execute_script("return document.body.scrollHeight")
            # if new_height == last_height:
            #     break
            # last_height = new_height


        PageSource = browser.page_source
        results_page = BeautifulSoup(PageSource, 'html.parser')
        
        clothes = results_page.find_all('div',{"class":re.compile('product-tile product-tile--default*')})
        num_clothes = len(clothes)
        print('Total Number of Clothes:', len(clothes))

        product_url_list = []

        for product in clothes:
            url_tag = product.find('a',{"class":'product-tile__anchor'})
            product_url_list.append('https://www.thereformation.com' + url_tag.get('href'))
        
        self.urls = product_url_list
        self.num_clothes = num_clothes
    
    def get_all_product_info(self):
        product_url_list = self.urls
        num_clothes = self.num_clothes
        
        output_list = []
        clothes_count = 0
        for product_url in product_url_list:
            response_product = requests.get(product_url)
            product_page = BeautifulSoup(response_product.content,'html.parser')

            # This section sometimes does not introduce the product material. 
            # To accommodate this issue, I always include washing instructions
            product_material = product_page.find('div',{"class":'pdp__accordion-content js-pdp-care'}).get_text()
            product_material = product_material.replace('\n\n\n', ' ')
            product_material = product_material.replace('\n', '')

            color = product_page.find('span',{"class":'product-attribute__selected-value'}).get_text()

            # Find all buttons that have aria-label starting with Size:
            size_tag = product_page.find_all('button',{"aria-label": re.compile('Size:*')})
            size = []
            for s in size_tag:
                s = s.get('aria-label')
                # Remove all unavailable sizes
                if 'unavailable' not in s:
                    size.append(s.replace('Size: ', ''))

            # Get info on display_name, price, image_links, brand_name, and description from script content
            script_content = json.loads(product_page.find('script', type='application/ld+json').text)
            display_name = script_content['name']
            description = script_content['description']
            brand_name = script_content['brand']['name']
            image_links = script_content['image']
            # Include both currency and exact price
            price = script_content['offers']['priceCurrency'] + script_content['offers']['price']

            breadcrumbs = product_page.find_all('a',{"class":'breadcrumbs__anchor link link--secondary'})
            # The category of clothes always takes the second to last position
            low_level = breadcrumbs[-2].get_text()
            low_level = low_level.replace('\n', '')

            scrapped_date = date.today()

            # Since Reformation only sells women's clothes, the gender will always be women
            gender = 'women'

            # Since Reformation only sells new clothes, the secondhand will always be False
            secondhand = False

            output_list.append((display_name, product_material, color, size, price, product_url, image_links,
                                brand_name, description, scrapped_date, low_level, gender, secondhand))
            clothes_count += 1
            print("Progress: " + str(clothes_count) + "/" + str(num_clothes))

        output = pd.DataFrame(output_list, columns = ['display_name', 'product_material', 'color', 'size', 'price', 
                                            'product_url', 'image_links', 'brand_name', 'description', 
                                            'scrapped_date', 'low_level', 'gender', 'secondhand'])            
        return output

if __name__ == '__main__':
    do_logging()

    # Create a new object of RefScraper class
    Reformation  = RefScraper()
    Reformation.get_all_product_urls(1)
    df_output = Reformation.get_all_product_info()

    # Store the data on an AWS RDS
    engine = create_engine('postgresql://changing_room:changingroomref@database-reformation.ccec7pjjeins.us-east-1.rds.amazonaws.com:5432/postgres')
    df_output.to_sql('reformation', engine)