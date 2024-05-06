from slugify import slugify
from pathlib import Path
import csv
import os

# Need to check what image was not downloaded as my os counts 999 covers out of 1000 books.

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

def find_column(csv_file, string):
	with open(csv_file, 'r', encoding='utf-8') as file:
		csv_reader = csv.reader(file)
		header = next(csv_reader)  # Read the header row
		for i, column_name in enumerate(header):
			if string in column_name.lower():
				return i
	return None  # Return None if 'string' is not found in the header

def replace_and_remove(string, what_str, new_str):
	"""returns a string"""
	try:
		replaced_string = str.lower(string.replace(what_str, new_str))
		return replaced_string
	
	except AttributeError:
		print(f"Error formatting string from {string}")
		return string

def count_books_in_folder(folder_path):
	total_books = 0
	for filename in os.listdir(folder_path):
		if filename.endswith('.csv'):
			file_path = os.path.join(folder_path, filename)
			title_column_index = find_column(file_path,'title')
			category_column_index = find_column(file_path,'category')
			with open(file_path, 'r', encoding='utf-8') as file:
				csv_reader = csv.reader(file)
				next(csv_reader)  # Skip header row
				for row in csv_reader:
					title = row[title_column_index]
					category = row[category_column_index]
					formatted_title = slugify(title)
					formatted_category = replace_and_remove(category, " ","_")
					image_directory = os.path.join(f'{folder_path}/images', formatted_category)
					image_path = os.path.join(image_directory, formatted_title+'.jpg')
					total_books += 1
					if not os.path.exists(image_path):
						print(f'Livre n° {total_books} : {formatted_category} - {formatted_title} -NO IMAGE')
	
	return total_books

def count_files_in_subdirectories(image_path):
    total_files = 0
    for root, dirs, files in os.walk(image_path):
        total_files += len(files)
    return total_files

folder_path = './scraped_data'
image_path = './scraped_data/images'
total_books = count_books_in_folder(folder_path)
total_images = count_files_in_subdirectories(image_path)
print(f'{total_books} livres trouvés dans les fichiers CSV du dossier')
print(f'{total_images} images trouvées dans les sous-repertoires de {image_path}')