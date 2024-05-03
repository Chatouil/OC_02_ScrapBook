from urllib.parse import urljoin
from bs4 import BeautifulSoup
import urllib.request
import requests
import time
import csv
import os

'''
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
'''

n_books = 0

def scrape_books_by_category(base_url):
	# Function to scrape books from all categories, except "Books"
	response = requests.get(base_url)
	soup = BeautifulSoup(response.content, 'html.parser')
	
	categories = soup.find('div', class_='side_categories').find_all('a')
	for category in categories:
		category_url = urljoin(base_url, category['href'])
		if 'books_1' not in category_url:  # Exclude "Books" category
			category_name = category.text.strip()
			print(f"Scraping books from category: {category_name}")
			category_books = scrape_books(category_url)
			export_to_csv(category_books, f'scraped_data/{str.lower(category_name)}_books_data.csv')

def scrape_books(url):
	# Function to scrape book page's data
	response = requests.get(url)
	soup = BeautifulSoup(response.content, 'html.parser')
	books = []
	
	for book in soup.find_all('article', class_='product_pod'):
		book_url = book.find('h3').find('a')['href']
		book_data = scrape_book_details(urljoin(url, book_url))
		book_data['product_page_url'] = urljoin(url, book_url)
		books.append(book_data)
	
	# Check if there's a next page
	next_page_link = soup.find('li', class_='next')
	if next_page_link:
		next_page_url = urljoin(url, next_page_link.find('a')['href'])
		books += scrape_books(next_page_url)  # Recursive call to scrape next page
	
	return books

def scrape_book_details(url):
	# Function to scrape details of a book from it's page
	response = requests.get(url)
	soup = BeautifulSoup(response.content, 'html.parser')
	
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
	
	# Image naming convention
	category_directory = os.path.join('scraped_data/images', str.lower(category))
	temp_filename = replace_and_remove(title)
	image_filename = str.lower(temp_filename)+'.jpg'
	download_image(image_url, category_directory, image_filename)
	
	global n_books
	n_books = n_books + 1
	
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

def replace_and_remove(string):
	# Replace forbidden chars < > : " / \ | ? *
	replaced_string = string.replace("<", ",").replace(">", ",").replace(":", ",").replace('"',"`").replace("/", "_").replace("\\", "_").replace("|", " or ").replace("?", "¿").replace('*',"!")
	# To avoid losing data, we should add a new data field in csv named os_restricted_title.
	return replaced_string

def download_image(url, directory, filename):
	# Create image folder
	if not os.path.exists(directory):
		os.makedirs(directory)
	
	# Download and save the image
	image_path = os.path.join(directory, filename)
	urllib.request.urlretrieve(url, image_path)

def convert_rating_to_number(rating_text):
	# Function to convert string to number
	if rating_text == 'One':
		return 1
	elif rating_text == 'Two':
		return 2
	elif rating_text == 'Three':
		return 3
	elif rating_text == 'Four':
		return 4
	elif rating_text == 'Five':
		return 5
	else:
		return 0 # Default value if no data found or value = 0

def export_to_csv(data, filename):
	# Function to export data as CSV file
	with open(filename, 'w', newline='', encoding='utf-8') as csvfile:
		fieldnames = ['product_page_url', 'upc', 'title', 'price_including_tax', 'price_excluding_tax', 'number_available', 'product_description', 'category', 'review_rating', 'image_url']
		writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
		
		writer.writeheader()
		for book in data:
			writer.writerow(book)

def main():
	# Main function
	start_time = time.time()
	base_url = "http://books.toscrape.com"
	scrape_books_by_category(base_url)
	end_time = time.time()
	elapsed_time = end_time - start_time
	print(f"Scraped successfully {n_books} books in: {elapsed_time:.2f} seconds")

# Main script
if __name__ == "__main__":
	main()