import requests
from bs4 import BeautifulSoup
import json
from urllib.parse import urlparse

url = "https://www.loopnet.com/Listing/3120-Pimlico-Pky-Lexington-KY/24909037/"
#url = "https://www.loopnet.com/property/101-e-university-ave-champaign-il-61820/17019-462107351001/"
#url = "https://www.loopnet.com/Listing/3300-3504-Stine-Rd-Bakersfield-CA/12014253/"
headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.3'}
response = requests.get(url, headers=headers)

if response.status_code == 200:
    soup = BeautifulSoup(response.text, 'html.parser')
    parsed_url = urlparse(url)
    path_segments = parsed_url.path.split('/')
    def extract_text(elements):
        return [element.text.strip() for element in elements]
    if path_segments[1].lower() == "listing" :
        property_address = path_segments[-3] if len(path_segments) >= 3 else ''
        title_elements = soup.find_all('td', {'class': "feature-grid__title"})
        data_dict = {"Property Address": property_address}

        for title_element in title_elements:
            title_text = title_element.get_text(strip=True)
            value_text = title_element.find_next_sibling().get_text(strip=True) if title_element.find_next_sibling() else ''
            data_dict[title_text] = value_text
    elif path_segments[1].lower() == "property":
        section = soup.find('section', {'id': 'detailsInf'})
        label_elements = section.find_all('label')
        property_address_section = soup.find('h1',{'class':'bold-normal main-title'})
        property_address_span_primary = property_address_section.find('span', {'class': 'main-address-primary'})
        property_address_span_secondary = property_address_section.find('span', {'class': 'main-address-secondary'})
        property_address_primary = extract_text(property_address_span_primary)[0] if property_address_span_primary else ''
        property_address_secondary = extract_text(property_address_span_secondary)[0] if property_address_span_secondary else ''
        property_address = f"{property_address_primary} {property_address_secondary}"
        data_dict = {"Property Address":property_address}
        for label_element in label_elements:
            label_text = label_element.text.strip()
            value_text = label_element.find_next('div', class_='assessment-value').get_text(strip=True) if label_element.find_next('div', class_='assessment-value') else ''
            data_dict[label_text] = value_text
    with open('output.json', 'w') as json_file:
        json.dump(data_dict, json_file, indent=2, sort_keys=False)

else:
    print("Error: Unable to retrieve data. Status Code:", response.status_code)
