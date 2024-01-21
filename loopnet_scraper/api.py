from flask import Flask, jsonify, request
from bs4 import BeautifulSoup
import requests
from urllib.parse import urlparse
from googlesearch import search
import json
import time
from requests.adapters import HTTPAdapter
from requests.packages.urllib3.util.retry import Retry

app = Flask(__name__)

def google_search_and_scrape(address):
    query = f"{address} site:loopnet.com"
    loopnet_url = None
    for result in search(query):
        loopnet_url = result
        break 
    if loopnet_url:
        scraped_data = scrape_data(loopnet_url)
        return scraped_data
    else:
        return {"error": "No LoopNet link found in the search results"}

def scrape_data(url):
    headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.3'}

    # Retry configuration
    retries = Retry(total=5, backoff_factor=0.1, status_forcelist=[429, 500, 502, 503, 504])
    adapter = HTTPAdapter(max_retries=retries)

    with requests.Session() as session:
        session.mount('http://', adapter)
        session.mount('https://', adapter)

        response = session.get(url, headers=headers)
        print(url)

        if response.status_code == 200:
            soup = BeautifulSoup(response.text, 'html.parser')
            parsed_url = urlparse(url)
            path_segments = parsed_url.path.split('/')
            def extract_text(elements):
                return [element.text.strip() for element in elements]
            section = path_segments[1].lower()
            if path_segments[1].lower() == "listing":
                property_address = path_segments[-3] if len(path_segments) >= 3 else ''
                title_elements = soup.find_all('td', {'class': "feature-grid__title"})
                data_dict = {"Property Address": property_address}
                for title_element in title_elements:
                    title_text = title_element.get_text(strip=True)
                    value_text = title_element.find_next_sibling().get_text(strip=True) if title_element.find_next_sibling() else ''
                    data_dict[title_text] = value_text
                response.close()
                return data_dict
            if section != "property":
                property_address = path_segments[-3] if len(path_segments) >= 3 else ''
                title_elements = soup.find_all('td', {'class': "feature-grid__title"})
                data_dict = {"Property Address": property_address}

                for title_element in title_elements:
                    title_text = title_element.get_text(strip=True)
                    value_text = title_element.find_next_sibling().get_text(strip=True) if title_element.find_next_sibling() else ''
                    data_dict[title_text] = value_text
                response.close()
                return data_dict
            else:
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
                response.close()
                return data_dict
        elif response.status_code == 429:
            # Retry with exponential backoff
            retry_after = int(response.headers.get('Retry-After', 5))
            print(f"Rate limited. Retrying after {retry_after} seconds.")
            time.sleep(retry_after)
            return scrape_data(url)
        else:
            print("Error: Unable to retrieve data. Status Code:", response.status_code)
            return {"error": f"Unable to retrieve data from {url}. Status Code: {response.status_code}"}

@app.route('/get-scraped-data', methods=['GET'])
def get_scraped_data():
    url = request.args.get('url')

    if not url:
        return jsonify({"error": "Missing 'url' parameter"}), 400

    scraped_data = scrape_data(url)
    return json.dumps(scraped_data, indent=2, sort_keys=False)

@app.route('/search-and-scrape', methods=['GET'])
def search_and_scrape():
    address = request.args.get('address')

    if not address:
        return jsonify({"error": "Missing 'address' parameter"}), 400

    scraped_data = google_search_and_scrape(address)
    return json.dumps(scraped_data, indent=2, sort_keys=False)

if __name__ == '__main__':
    app.run(port=5000, debug=True)
