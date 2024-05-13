# Scrap Books 🚀
  
# ● Project Description
This script will connect to 'http://books.toscrape.com' & parse the data in as many csv as there is book categories, using the following template : *product_page_url, upc, title, price_including_tax, price_excluding_tax, number_available, product_description, category, review_rating, image_url*.  
The csv files will be located in a [scraped_data] folder and named given the books's category.  
It will also download all books cover in a [scraped_data/*books category] folder.  
  
# ● How to Install and Run the Project
1. Requirements :  
Having Python 3 installed  
Download the project somewhere on your drive  
- unzip the downloaded project archive
- or use this command line : git clone https://github.com/SachaaBoris/OC_02_ScrapBook.git path\to\your\folder\here
Navigate to this folder within your favourite console and type : py -m venv ./venv  
Activate your virtual environment by typing : venv\Scripts\activate  
Apply the projects requirements by typing : py -m  pip install -r requirements.txt

2. Run the script.  
In your console, still in the script's folder, execute the script with this command : scrap.py  
  
---
  
[![CC BY 4.0][cc-by-shield]][cc-by]  
  
This work is licensed under a [Creative Commons Attribution 4.0 International License][cc-by].  
  
[cc-by]: http://creativecommons.org/licenses/by/4.0/  
[cc-by-shield]: https://img.shields.io/badge/License-CC%20BY%204.0-lightgrey.svg  
