import requests
from bs4 import BeautifulSoup
from nltk.corpus import wordnet
import re
import time
import json

def get_synonyms(word):
    synonyms = set()
    for syn in wordnet.synsets(word):
        for lemma in syn.lemmas():
            synonyms.add(lemma.name())
    return list(synonyms)

def parse_url_to_words(url):
    path = url.split('/')[-1].split('.')[0]
    words = re.split('_|-', path)
    return words

def extract_links_recursive(url, depth, visited_urls):
    if depth == 0 or url in visited_urls:
        return []

    print(f"Visiting {url} at depth {depth}")
    visited_urls.add(url)
    time.sleep(1)  # Wait for 1 second before making a request

    try:
        page = requests.get(url)
        soup = BeautifulSoup(page.content, 'html.parser')
        links = soup.find_all('a')
        parsed_words = []

        for link in links:
            href = link.get('href')
            if href and href.startswith('http'):
                words = parse_url_to_words(href)
                parsed_words.extend(words)
                print(f"Found {len(words)} words in {href}")
                parsed_words.extend(extract_links_recursive(href, depth-1, visited_urls))

        return parsed_words
    except requests.RequestException as e:
        print(f"Error fetching {url}: {e}")
        return []

def read_seed_urls(file_path):
    with open(file_path, 'r') as file:
        return [line.strip() for line in file if line.strip()]

def save_synonyms_to_file(synonyms_dict, file_name):
    with open(file_name, 'w') as file:
        json.dump(synonyms_dict, file, indent=4)

def main(seed_file, depth, output_file):
    seed_urls = read_seed_urls(seed_file)
    synonyms_dict = {}

    for url in seed_urls:
        visited_urls = set()
        parsed_words = extract_links_recursive(url, depth, visited_urls)

        for word in parsed_words:
            if word not in synonyms_dict:
                synonyms = get_synonyms(word)
                synonyms_dict[word] = synonyms
                save_synonyms_to_file(synonyms_dict, output_file)  # Save after each seed URL

    return synonyms_dict

# Example usage
seed_file = 'seeds.txt'  # File containing seed URLs
depth = 2  # Set the recursion depth
output_file = 'synonyms_data.txt'  # File to save synonyms data
synonyms_dict = main(seed_file, depth, output_file)

