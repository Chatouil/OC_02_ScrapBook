from urllib.parse import urljoin
from datetime import datetime
from bs4 import BeautifulSoup
from slugify import slugify
from pathlib import Path
import urllib.request
import urllib.error
import requests
import time
import csv
import os

"""
DATA TO EXTRACT
● product_page_url
● universal_ product_code (upc)
● title
● price_including_tax
● price_excluding_tax
● number_available
● product_description
● category
● review_rating
● image_url
+ download image

scraps & downloads 1000 books in ~515s (8m 35s)
"""

# Pistes d'amelioration :
# exporter également les titres formatés dans les csv pour éviter les pertes de data.
# créer un script qui vérifie dans les csv : 
# 					- le nombre de livre exportés.
# 					- que chaque entrée de colonne corresponde à son en-tête.

n_books = 0
script_errors = 0

def get_soup(url, session):
	"""returns soup html content"""
	try:
		response = session.get(url)
		response.raise_for_status() # Raise an exception for non-2xx status codes
		soup = BeautifulSoup(response.content, 'html.parser')
		return soup
	
	except requests.RequestException as e:
		print(f'Error fetching data from {url}: {e}')
		global script_errors
		script_errors += 1
		return 'error'

def scrape_books_by_category(base_url, session):
	soup = get_soup(base_url, session)
	if not soup == 'error':
		categories = soup.find('div', class_='side_categories').find_all('a')
		for category in categories:
			category_url = urljoin(base_url, category['href'])
			if 'books_1' not in category_url:  # Exclude 'Books' category
				category_name = category.text.strip()
				print(f'Scraping books from category: {category_name}')
				category_books = scrape_books(category_url, session)
				formatted_category = replace_and_remove(category_name, ' ','_')
				timestamp = generate_timestamp()
				export_to_csv(category_books, f'scraped_data/{str.lower(formatted_category)}_books_data_{timestamp}.csv')

def scrape_books(url, session):
	"""returns books data from a category"""
	soup = get_soup(url, session)
	if not soup == 'error':
		books = []
		
		for book in soup.find_all('article', class_='product_pod'):
			book_url = book.find('h3').find('a')['href']
			book_data = scrape_book_details(urljoin(url, book_url), session)
			if not book_data == 'error':
				book_data['product_page_url'] = urljoin(url, book_url)
				books.append(book_data)
		
		next_page_link = soup.find('li', class_='next') # Check if there's a next page
		if next_page_link:
			next_page_url = urljoin(url, next_page_link.find('a')['href'])
			books += scrape_books(next_page_url, session)  # Recursive call to scrape next page
		
		return books

def scrape_book_details(url, session):
	"""returns bookdata"""
	soup = get_soup(url, session)
	if not soup == 'error':
		upc = soup.find('th', string='UPC').find_next('td').text.strip()
		title = soup.find('h1').text.strip()
		price_including_tax = soup.find('th', string='Price (incl. tax)').find_next('td').text.strip()
		price_excluding_tax = soup.find('th', string='Price (excl. tax)').find_next('td').text.strip()
		availability_text = soup.find('th', string='Availability').find_next('td').text.strip()
		number_available = ''.join(filter(str.isdigit, availability_text))
		product_description = soup.find('meta', {'name': 'description'})['content'].strip()
		category = soup.find('ul', class_='breadcrumb').find_all('a')[2].text.strip()
		review_rating_text = soup.find('p', class_='star-rating')['class'][1]
		review_rating = convert_rating_to_number(review_rating_text)
		image_relative_url = soup.find('div', class_='item active').find('img')['src']
		image_url = urljoin(url, image_relative_url)
		formatted_title = slugify(title)
		formatted_category = replace_and_remove(category, ' ','_')
		category_directory = os.path.join('scraped_data/images', formatted_category)
		download_image(image_url, category_directory, formatted_title)
		
		global n_books
		n_books += 1
		
		return {
			'upc': upc,
			'title': title,
			'price_including_tax': price_including_tax,
			'price_excluding_tax': price_excluding_tax,
			'number_available': number_available,
			'product_description': product_description,
			'category': category,
			'review_rating': review_rating,
			'image_url': image_url
		}

def replace_and_remove(string, what_str, new_str):
	"""returns a string"""
	try:
		replaced_string = str.lower(string.replace(what_str, new_str))
		return replaced_string
	
	except AttributeError:
		print(f'Error formatting string from {string}')
		global script_errors
		script_errors += 1
		return string

def download_image(url, directory, filename):
	global script_errors
	try:
		directory_path = Path(directory)
		if not directory_path.exists():
			directory_path.mkdir(parents=True)

		image_path = os.path.join(directory, filename+'.jpg')
		urllib.request.urlretrieve(url, image_path)
	
	except urllib.error.URLError as url_error:
		script_errors += 1
		print(f'Error downloading image from {url}: {url_error}')
	
	except FileNotFoundError as file_error:
		script_errors += 1
		print(f'Error creating directory or saving image: {file_error}')

def convert_rating_to_number(rating_text: str) -> int:
	ratings = {'One': 1, 'Two': 2, 'Three': 3, 'Four': 4, 'Five': 5}
	return ratings.get(rating_text, 0)

def export_to_csv(data, filename):
	try:
		with open(filename, 'w', newline='', encoding='utf-8') as csvfile:
			fieldnames = ['product_page_url', 'upc', 'title', 'price_including_tax', 'price_excluding_tax', 'number_available', 'product_description', 'category', 'review_rating', 'image_url']
			writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
			writer.writeheader()
			writer.writerows(data)
	
	except Exception as e:
		global script_errors
		script_errors += 1
		print(f'Error exporting data to CSV file: {e}')

def generate_timestamp():
	now = datetime.now()
	timestamp = now.strftime('%Y-%m-%d_%H-%M-%S')
	return timestamp

def main():
	start_time = time.time()
	base_url = 'http://books.toscrape.com'
	with requests.Session() as session:
		scrape_books_by_category(base_url, session)
		end_time = time.time()
		elapsed_time = end_time - start_time
		if script_errors > 0:
			print('There were errors, please review the script and data.')
		
		if n_books > 0:
			print(f'Scraped successfully {n_books} books in: {elapsed_time:.2f} seconds')
		else:
			print('Failed to scrape books.')

if __name__ == '__main__':
	main()