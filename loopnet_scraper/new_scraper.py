from selenium import webdriver
import json
from urllib.parse import urlparse

url = "https://www.loopnet.com/Listing/3120-Pimlico-Pky-Lexington-KY/24909037/"
# url = "https://www.loopnet.com/property/101-e-university-ave-champaign-il-61820/17019-462107351001/"
# url = "https://www.loopnet.com/Listing/3300-3504-Stine-Rd-Bakersfield-CA/12014253/"

driver = webdriver.Chrome()
driver.get(url)

# Wait for the page to load (you may need to adjust the sleep duration)
driver.implicitly_wait(10)

# Example to get information from specific <td> with data-fact-type="CenterType"
center_type_element = driver.find_element_by_xpath('//td[@data-fact-type="CenterType"]')
center_type_text = center_type_element.text.strip()
data_dict = {"Center Type": center_type_text}

with open('output.json', 'w') as json_file:
    json.dump(data_dict, json_file, indent=2, sort_keys=False)

driver.quit()