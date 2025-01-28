import os
import pandas as pd
from datetime import datetime
from bs4 import BeautifulSoup
import requests

# Helper functions
def fetch_soup(url):
    headers = {
        "User-Agent": (
            "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
            "AppleWebKit/537.36 (KHTML, like Gecko) "
            "Chrome/91.0.4472.124 Safari/537.36"
        ),
        "Accept-Language": "en-US,en;q=0.9"
    }
    try:
        response = requests.get(url, headers=headers)
        response.raise_for_status()
        return BeautifulSoup(response.content, "html.parser")
    except requests.RequestException as e:
        print(f"Error fetching URL {url}: {e}")
        return None

def get_title(soup):
    try:
        return soup.find("span", {"id": "productTitle"}).get_text(strip=True)
    except AttributeError:
        return "N/A"

def get_price(soup):
    try:
        price = soup.find("span", {"class": "a-price-whole"}).get_text(strip=True)
        return price
    except AttributeError:
        return "N/A"

def calculate_mrp(price):
    try:
        # Remove non-numeric characters like ₹ and commas
        numeric_price = ''.join([c for c in price if c.isdigit()])
        return round(float(numeric_price) * 1.2, 2) if numeric_price else None
    except ValueError:
        return None

def get_rating(soup):
    try:
        return soup.find("span", {"class": "a-icon-alt"}).get_text(strip=True)
    except AttributeError:
        return "N/A"

def get_review_count(soup):
    try:
        return soup.find("span", {"id": "acrCustomerReviewText"}).get_text(strip=True)
    except AttributeError:
        return "N/A"

def get_availability(soup):
    try:
        availability = soup.find("div", {"id": "availability"}).get_text(strip=True)
        return availability if availability else "In Stock"  # Default to "In Stock" if nothing found
    except AttributeError:
        return "N/A"

def get_one_review(soup):
    """Extract one review from the product page."""
    try:
        review_section = soup.find("span", {"data-hook": "review-body"})
        review_text = review_section.get_text(strip=True)
        return review_text
    except AttributeError:
        return "No reviews available"

def scrape_amazon_product(url):
    soup = fetch_soup(url)
    if not soup:
        return None

    price = get_price(soup)
    product_data = {
        "Title": get_title(soup),
        "Price": price,
        "MRP Price": calculate_mrp(price),
        "Rating": get_rating(soup),
        "Review Count": get_review_count(soup),
        "Availability": get_availability(soup),
        "One Review": get_one_review(soup),
        "Date": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
    }
    return product_data

def scrape_multiple_products(urls, output_file="amazon_products.csv"):
    data = []
    for url in urls:
        product_data = scrape_amazon_product(url)
        if product_data:
            data.append(product_data)

    if data:
        # Save the full data to CSV
        df = pd.DataFrame(data)
        file_exists = os.path.exists(output_file)
        df.to_csv(output_file, mode='a', header=not file_exists, index=False)
        print(f"Data saved to {output_file}")

        # Create price_df and review_df
        price_df = df[["Date", "Title", "Price", "MRP Price", "Availability"]]
        price_df.to_csv('price_data.csv', index=False)
        
        review_df = df[["Date", "Title", "Rating", "Review Count", "One Review", "Availability"]]
        review_df.to_csv('review_data.csv', index=False)
    else:
        print("No data scraped.")

# Test URLs
amazon_urls = [
    "https://www.amazon.in/boAt-Rockerz-480-Bluetooth-Headphones/dp/B0DGTSRX3R/ref=sr_1_4?crid=20R36NCKY9S89&dib=eyJ2IjoiMSJ9.X5kxgfDI-gp5ce1WvRksC0tmI9oLOOmAzOI1WcbCKF4EcXpapjoo0n885p2pU6jS4wmxzP-xk3LKHuJ0RoXp3zAHCWuw81unRHiehb4EFAXEZdV21cpkOTPipuRkX_G_06zlxZxSLvqTVNtriV9rdZDkbv6X-B5b7Q60DqfACZRfChCcRn6k43TG7v6bSpF2DlZ2-RBsqJzwQqpuPzd_XhbFD30Wc6z3C3YArnLBcIsxyPUY31WI2fRmwT0yD4EuLDRzy5rDfVHjNxY6jiknK99PceA30JzEZRVMTPLkEi5MvQiP86qXsMtQeZz79QIX1L_1KqI6YXZb2ba1XgVDQGL-wBQkV1LZA_JTQw3wwlw.gRl5b4MHEYDCIUD9l8yazqGoIynmQCafMCvla11MtYA&dib_tag=se&keywords=headphones&qid=1738000522&s=computers&sprefix=headphon%2Ccomputers%2C220&sr=1-4",
    "https://www.amazon.in/HP-i5-13420H-15-6-inch-Backlit-fa1319TX/dp/B0D1YJR2ZY/ref=sr_1_1_sspa?crid=296N2LKS6BNY6&dib=eyJ2IjoiMSJ9.vgVl5mHr9MTKXUQALIpc7fyVVAVhSIKyu5onprp5IHVF_KOMqojD0GpAS58BsG2GugfW8gqmLYTXWxLUnmUlaeEwBmZhAYEkQ2rATk4dS2L_DOxymCtDiNvfyFxNrJc53sLfoyT0iQC-r1wUUz02g4E3mqRnhKk5wgz_RKIRmIcaH60892fX-gBkxu7aBAjcvy4SKRrpXy8mvmJxxCoO4w_wGtGP4cweJQKf4muDXOAdIYWqexz0TZIn1vSf7Bo8GzlNAsvV_KG1osrib9KXt4RXF97MDtC6wzPZNBSJaJQ.JFlSwFgQassQsJfo8XNBC0L1GDcZ8DoAB3XWDpz-bZQ&dib_tag=se&keywords=laptop&qid=1738000629&s=computers&sprefix=lapto%2Ccomputers%2C212&sr=1-1-spons&sp_csd=d2lkZ2V0TmFtZT1zcF9hdGY&psc=1",
    "https://www.amazon.in/Samsung-Galaxy-Ultra-Titanium-Storage/dp/B0DSKMKJV5/ref=sr_1_1_sspa?dib=eyJ2IjoiMSJ9.pjAyhp-0lpD3vPq8TgJzY0nrXSRKrNQ9x65zizzoMyWrpBdTKd4nwekOptTD7DjnP2lHLGqTv1iS2VS2ZWd4RwG1skN-YrbVD7fEeThcvHr5MSuqK2rSEMOR0LSU13WZqoxyyG7QUrKdbfewBWsNqEqcusqmQq3b3ZFipoBO6gW0rM5kFpD-Sut3IsxY2iD8_fVSmFD7Ri5GycKsu6iR-D7HlTDyy2HuhrjYJP9zlUc.XgS3HLuDTOAbFOBOFCyR0bNFCJ5C8vaJe1eWbtcWZPQ&dib_tag=se&keywords=mobile&qid=1738000655&sr=8-1-spons&sp_csd=d2lkZ2V0TmFtZT1zcF9hdGY&psc=1"
]

# Scrape products and save data
scrape_multiple_products(amazon_urls, output_file="amazon_products.csv")