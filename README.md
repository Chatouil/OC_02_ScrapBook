# extract_all_books_data_dl_image 🚀

# ● Project Description
This script will connect to 'http://books.toscrape.com' & parse the data in as many csv as there is book categories, using the following template : ['product_page_url', 'upc', 'title', 'price_including_tax', 'price_excluding_tax', 'number_available', 'product_description', 'category', 'review_rating', 'image_url'].
The csv files will be located in a [scraped_data] folder and named given the books's category.
It will also download all books cover in a [scraped_data/*books category] folder.

# ● How to Install and Run the Project
1. See Requirements.
2. Run the script.

	During Python setup, make sure to install pip and check the environement variable setting.
	In your console, navigate to the script's folder and execute the script with this command : extract_all_books_data_dl_image.py

---

[![CC BY 4.0][cc-by-shield]][cc-by]

This work is licensed under a
[Creative Commons Attribution 4.0 International License][cc-by].

[cc-by]: http://creativecommons.org/licenses/by/4.0/
[cc-by-shield]: https://img.shields.io/badge/License-CC%20BY%204.0-lightgrey.svg