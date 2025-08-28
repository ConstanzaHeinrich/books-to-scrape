import requests #solicita ingresar a la url del html
from bs4 import BeautifulSoup #lee y filtra el HTML 
from urllib.parse import urljoin, quote_plus #para ordenar el url 
import json #para guardar datos en formato organizado
import time #Sirve para poner pausas (sleep) y no sobrecargar al servidor
from requests.exceptions import RequestException #maneja errores cuando requests falla (ej: internet cortado).

BASE_URL = "http://books.toscrape.com/"
GOOGLE_BOOKS_API_KEY = "api_key"

def get_author_from_google_books(title): #busca en google books el autor del libro
    try:
        query = quote_plus(title.strip())
        url = f"https://www.googleapis.com/books/v1/volumes?q=intitle:{query}&key={GOOGLE_BOOKS_API_KEY}"
        response = requests.get(url, timeout=10) 
        response.raise_for_status()
        data = response.json()
        if "items" in data and len(data["items"]) > 0: #valida que la respuest atenga resultados
            authors = data["items"][0]["volumeInfo"].get("authors", ["Autor desconocido"])
            return ", ".join(authors)
        return "Autor no encontrado"
    except RequestException as e:
        print(f"⚠️ Error consultando Google Books para '{title}': {e}")
        return "Error al buscar autor"

def get_categories(): #saca la lista de categoria de libros de la pagina principal
    try:
        resp = requests.get(BASE_URL, timeout=15)
        resp.raise_for_status()
        soup = BeautifulSoup(resp.text, "html.parser")
        categories = {}
        for a in soup.select(".side_categories ul li ul li a"): # lee el html para saber donde encontrar la info, escarba hasta encontrara el que quiere
            name = a.text.strip() #quita espacios que estan de mas
            url = urljoin(BASE_URL, a["href"]) #Combina la URL base con el href del link para formar una URL completa.
            categories[name] = url #Guarda en el diccionario la categoría con su URL.
        return categories #Devuelve el diccionario final con todas las categorías encontradas.
    except Exception as e:
        print("Error sacando categorías:", e)
        return {}

def get_all_books_in_category(category_url):
    books = []
    url = category_url
    while url:
        try:
            resp = requests.get(url, timeout=15)
            resp.raise_for_status()
            soup = BeautifulSoup(resp.text, "html.parser")

            for article in soup.select("article.product_pod"):
                book_url = urljoin(url, article.h3.a["href"]) #convierte en url cada libro
                books.append(book_url) #Agrega la URL a la lista books

            #Busca si hay un botón de “next page” (siguiente página de la categoría).
            next_page = soup.select_one("li.next a") #si existe actualiza la url y si no ponen none y termina el bucle
            url = urljoin(url, next_page["href"]) if next_page else None
            time.sleep(1) #Pausa de 1 segundo antes de seguir. Esto es para no parecer un bot agresivo y sobrecargar el servidor.
        except Exception as e:
            print(f"Error en categoría {category_url} página {url}: {e}")
            break
    return books #Devuelve la lista final con todas las URLs de los libros de esa categoría.

def parse_book(book_url):
    try:
        time.sleep(1)
        resp = requests.get(book_url, timeout=25)
        resp.raise_for_status()
        soup = BeautifulSoup(resp.text, "html.parser")

        title = soup.h1.text #scaa ek texto de h1 que es el titulo del libro
        price = soup.select_one("p.price_color").text #precio
        availability = soup.select_one("p.instock").text.strip() #si esta en stock
        star_rating = soup.select_one("p.star-rating")["class"][1] #puntuacion
        desc = soup.select_one("#product_description") #descripcion
        description = desc.find_next_sibling("p").text if desc else "No description"
        image_rel_url = soup.select_one(".carousel img")["src"] #Primero encuentra el <img> dentro del carrusel.
        image_url = urljoin(book_url, image_rel_url) #la convierte en una URL absoluta
        category = soup.select("ul.breadcrumb li a")[-1].text #El último enlace ([-1]) es la categoría del libro.

        author = get_author_from_google_books(title) #llama a la fiuncion de la api

        return {
            "title": title,
            "author": author,
            "price": price,
            "availability": availability,
            "stars": star_rating,
            "description": description,
            "image_url": image_url,
            "category": category
        }
    except Exception as e:
        print(f"Error parseando libro {book_url}: {e}")
        return None

def scrap_all_books():
    all_books = []
    categories = get_categories() #Llama a otra función que devuelve un diccionario con todas las categorías de la web.
    print(f"Encontradas {len(categories)} categorías.") #imprime cuantas categorias encontro

    for cat_name, cat_url in categories.items(): #Recorre cada categoría (nombre y URL).
        print(f"📚 Scrapeando categoría: {cat_name}")
        book_urls = get_all_books_in_category(cat_url) # Llama a otra función que devuelve TODAS las URLs de libros dentro de esa categoría.
        print(f" → {len(book_urls)} libros encontrados en '{cat_name}'")

        for book_url in book_urls: #recorre cada url de libro
            book_data = parse_book(book_url) # Llama a otra función que va a extraer los datos del libro
            if book_data:
                all_books.append(book_data) #Si logró obtener datos, los guarda en la lista `all_books`.

    return all_books #devuelve la lista con todos los libros scrapeados

if __name__ == "__main__":
    books = scrap_all_books()
    print(f"✅ Total libros scrapings: {len(books)}")

    with open("books_data_completo.json", "w", encoding="utf-8") as f: 
        json.dump(books, f, ensure_ascii=False, indent=2)

    print("💾 Datos guardados en 'books_data_completo.json'")