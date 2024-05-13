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
menu adds options :
    - to download single category or all books
    - with or without covers
"""

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

main_output_folder = 'scraped_data'
base_urls = ['http://books.toscrape.com']
n_books = 0
script_errors = 0


def get_soup(url, session):
    """returns soup html content"""
    try:
        response = session.get(url)
        response.raise_for_status()  # raise an exception for non-2xx status codes
        soup = BeautifulSoup(response.content, 'html.parser')
        return soup

    except requests.RequestException as e:
        print(f'Error fetching data from {url}: {e}')
        global script_errors
        script_errors += 1
        return 'error'


def scrape_category(url, user_input, dl_covers, session, output_folder):
    soup = get_soup(url, session)
    if soup == 'error':
        pass
    else:
        categories = soup.find('div', class_='side_categories').find_all('a')
        for category in categories:
            category_url = urljoin(url, category['href'])
            scrape = False
            if user_input != '0':
                if user_input in category_url:  # only include input category
                    scrape = True
            else:
                if 'books_1' not in category_url:  # exclude 'books_1' category
                    scrape = True

            if scrape:
                category_name = category.text.strip()
                print(f'Scraping books from category: {category_name}')
                category_books = scrape_books(category_url, dl_covers, session, output_folder)
                formatted_category = replace_and_remove(category_name, ' ', '_')
                timestamp = generate_timestamp()
                export_to_csv(category_books,
                              f'{output_folder}/{str.lower(formatted_category)}_books_data_{timestamp}.csv')


def scrape_books(url, dl_covers, session, output_folder):
    """returns array of book data arrays"""
    soup = get_soup(url, session)
    if soup == 'error':
        return []
    else:
        books = []

        for book in soup.find_all('article', class_='product_pod'):
            book_url = book.find('h3').find('a')['href']
            book_data = scrape_book_details(urljoin(url, book_url), dl_covers, session, output_folder)
            if not book_data == 'error':
                book_data['product_page_url'] = urljoin(url, book_url)
                books.append(book_data)

        next_page_link = soup.find('li', class_='next')  # check if there's a next page
        if next_page_link:
            next_page_url = urljoin(url, next_page_link.find('a')['href'])
            books += scrape_books(next_page_url, dl_covers, session,
                                  output_folder)  # recursive call to scrape next page

        return books


def scrape_book_details(url, dl_covers, session, output_folder):
    """returns book_data array"""
    soup = get_soup(url, session)
    if soup == 'error':
        return {}
    else:
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
        formatted_title = slugify(title)[:46]  # truncate formatted title if more then 46 chars
        formatted_category = replace_and_remove(category, ' ', '_')
        category_directory = os.path.join(f'{output_folder}/images', formatted_category)

        if dl_covers:
            cover_title = formatted_title + '_' + upc + '.jpg'
            image_path = os.path.join(category_directory, cover_title)
            download_image(image_url, category_directory, image_path)
            image_url = './images/' + formatted_category + '/' + cover_title  # remove this line to export image url instead of image path

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


def ensure_directory_exists(directory):
    directory_path = Path(directory)
    if not directory_path.exists():
        directory_path.mkdir(parents=True)


def download_image(url, directory, image_path):
    global script_errors
    try:
        ensure_directory_exists(directory)
        urllib.request.urlretrieve(url, image_path)

    except urllib.error.URLError as url_error:
        script_errors += 1
        print(f'Error downloading image from {url}: {url_error}')

    except FileNotFoundError as file_error:
        script_errors += 1
        print(f'Error creating directory or saving image: {file_error}')


def convert_rating_to_number(rating_text: str) -> int:
    ratings = {'Zero': 0, 'One': 1, 'Two': 2, 'Three': 3, 'Four': 4, 'Five': 5}
    return ratings.get(rating_text, -1)


def export_to_csv(data, filename):
    try:
        directory = os.path.dirname(filename)
        ensure_directory_exists(directory)

        with open(filename, 'w', newline='', encoding='utf-8') as csvfile:
            fieldnames = ['product_page_url', 'upc', 'title', 'price_including_tax', 'price_excluding_tax',
                          'number_available', 'product_description', 'category', 'review_rating', 'image_url']
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


def end_print(start_time):
    end_time = time.time()
    elapsed_time = end_time - start_time
    if script_errors > 0:
        print('There were errors, please review the script and data.')

    if n_books == 0:
        print('Failed to scrape books.')
    else:
        print(f'Scraped successfully {n_books} books in: {elapsed_time:.2f} seconds')


def urls_loop(category_input, dl_image, session):
    for url in base_urls:
        output_folder = main_output_folder + '/' + slugify(url)
        scrape_category(url, category_input, dl_image, session, output_folder)


def main():
    while True:
        print("\n")
        print("             .--.                   .---.")
        print("         .---|__|           .-.     |~~~|")
        print("      .--|===|--|_          |_|     |~~~|--.")
        print("      |  |===|  |'\\     .---!~|  .--|   |--|")
        print("      |%%|   |  |.'\\    |===| |--|%%|   |  |")
        print("      |%%|   |  |\\.'\\   |   | |__|  |   |  |")
        print("      |  |   |  | \\  \\  |===| |==|  |   |  |")
        print("      |  |   |__|  \\.'\\ |   |_|__|  |~~~|__|")
        print("      |  |===|--|   \\.'\\|===|~|--|%%|~~~|--|")
        print("      ^--^---'--^    `-'`---^-^--^--^---'--'\n")
        print("      ----------- ScrapBook Menu -----------\n")
        print("Avec les couvertures         Sans les couvertures")
        print(" V                            V")
        print("[1] Tout scraper             [3] Tout scraper")
        print("[2] Scraper une catégorie    [4] Scraper une catégorie")
        choice = input("Entrez votre choix: ")

        if choice not in ['1', '2', '3', '4']:
            print("Choix non conforme. Veuillez entrer un chiffre entre 1 et 4.")

        else:
            start_time = time.time()
            with requests.Session() as session:
                if choice == '1' or choice == '2':
                    dl_image = True
                else:
                    dl_image = False

                if choice == '1' or choice == '3':
                    urls_loop('0', dl_image, session)
                    end_print(start_time)
                    break
                else:
                    print("Veuillez entrer le nom d'une catégorie :")
                    category_input = replace_and_remove(str.lower(input("> ")), " ", "-")
                    urls_loop(category_input, dl_image, session)
                    end_print(start_time)
                    break


if __name__ == "__main__":
    main()
