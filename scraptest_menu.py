import requests
from bs4 import BeautifulSoup
from urllib.parse import urljoin

def scrape_book_details(book_url):
	pass

def scrape_all(base_url, dl_covers):
	pass

def scrape_category(category_url, input, dl_covers):
	pass

def scrape_book(base_url, input, dl_covers):
	pass

def main():
	base_url = "http://books.toscrape.com"
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
		print("[1] Tout scraper             [4] Tout scraper")
		print("[2] Scraper une catégorie    [5] Scraper une catégorie")
		print("[3] Scraper un livre         [6] Scraper un livre\n")
		choice = input("Entrez votre choix: ")
		
		if choice == '1' or choice == '4':
			scrape_all(base_url,True)
			break
		elif choice == '2' or choice == '5':
			category_input = input("Quelle catégorie ?")
			scrape_category(base_url,category_input,True)
			break
		elif choice == '3' or choice == '6':
			book_input = input("Quel livre ?")
			scrape_book(base_url,book_input,True)
			break
		else:
			print("Choix non conforme. Veuillez entrer un chiffre entre 1 et 6.")

if __name__ == "__main__":
	main()