import random
import re

import requests
from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.chrome.options import Options

from .models import Product, TargetSite

headers = [
    {
        "authority": "www.amazon.com",
        "pragma": "no-cache",
        "cache-control": "no-cache",
        "dnt": "1",
        "upgrade-insecure-requests": "1",
        "user-agent": "Mozilla/5.0 (X11; CrOS x86_64 8172.45.0) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/51.0.2704.64 Safari/537.36",
        "accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9",
        "sec-fetch-site": "none",
        "sec-fetch-mode": "navigate",
        "sec-fetch-dest": "document",
        "accept-language": "en-GB,en-US;q=0.9,en;q=0.8",
    }
]


class Browser:
    chromedriver = "utils/chromedriver"

    def browser(self):
        options = Options()
        options.headless = True
        options.add_argument(f'user-agent={self.get_headers()["user-agent"]}')
        driver = webdriver.Chrome(self.chromedriver, options=options)
        return driver


class Watchdog(Browser):
    chromedriver = "utils/chromedriver"

    @staticmethod
    def get_headers():
        return random.choice(headers)

    def add_product(self, url):
        if "walmart.com" in url:
            product_info = self.walmart_product(url)
            product = Product(**product_info)
            product.save()

        elif "amazon.com" in url:
            product_info = self.amazon_product(url)
            product = Product(**product_info)
            product.save()

        elif "target.com" in url:
            product_info = self.target_product(url)
            product = Product(**product_info)
            product.save()

        elif "bestbuy.com" in url:
            product_info = self.bestbuy_product(url)
            product = Product(**product_info)
            product.save()
        else:
            raise ValueError("Product url does not match with existing target sites.")

    def amazon_product(self, url):
        driver = self.browser()
        driver.get(url)
        soup = BeautifulSoup(driver.page_source, "lxml")
        body = soup.body
        product_name = body.find("span", {"id": "productTitle"})
        product_name = body.find("h1", {"id": "title"}).text.strip()
        price = float(
            body.find("span", {"id": "priceblock_ourprice"})
            .text.strip()
            .split()[-1]
            .replace("$", "")
        )
        availability = body.find(
            "span", {"id": "submit.add-to-cart-announce"}
        ).text.strip()
        availability = True if availability == "Add to Cart" else False
        sku = (
            body.find(text=re.compile("Item model number")).findNext("td").text.strip()
        )
        image = body.find("img", {"id": "landingImage"}).get("src")

        product_info = {
            "name": product_name,
            "price": price,
            "sku": sku,
            "image": image,
            "is_available": availability,
            "url": url,
        }
        driver.quit()
        return product_info

    def walmart_product(self, url):
        headers = self.get_headers()
        response = requests.get(url, headers=headers)
        soup = BeautifulSoup(response.text, "lxml")
        body = soup.body
        product_name = body.find("h1", {"class": "prod-ProductTitle"}).text.strip()
        price_body = body.find("span", {"class": "price"})
        price = float(
            (
                price_body.find("span", {"class": "visuallyhidden"})
                .text.strip()
                .split()[-1]
                .replace("$", "")
            )
        )
        sku = int(
            body.find("div", {"class": "wm-item-number"}).text.strip().split()[-1]
        )
        availability = (
            True
            if len(
                [
                    button.text
                    for button in body.find_all("span", {"class": "button-wrapper"})
                    if button.text == "Add to cart"
                ]
            )
            else False
        )
        image = body.find("span", {"class": "button-wrapper"}).find("img").get("src")
        if image[:2] == "//":
            image = "http://" + image[2:]

        product_info = {
            "name": product_name,
            "price": price,
            "sku": sku,
            "image": image,
            "is_available": availability,
            "url": url,
        }
        return product_info

    def target_product(self, url):
        driver = self.browser()
        driver.get(url)
        soup = BeautifulSoup(driver.page_source, "lxml")
        body = soup.body
        product_name = body.find("h1", {"data-test": "product-title"}).text.strip()
        price = float(
            body.find("div", {"data-test": "product-price"})
            .text.strip()
            .replace("$", "")
        )
        image = (
            body.find_all("div", {"class": "slideDeckPicture"})[-1]
            .find("img")
            .get("src")
        )
        availability_phrases = ["Pick it up", "Deliver it", "Ship it"]
        availability = [
            True
            for button in body.find_all("button")
            if button.text.strip() in availability_phrases
        ]
        availability = True if len(availability) else False
        product_info = {
            "name": product_name,
            "price": price,
            "image": image,
            "is_available": availability,
            "url": url,
        }
        driver.quit()
        return product_info

    def bestbuy_product(self, url):
        driver = self.browser()
        driver.get(url)
        soup = BeautifulSoup(driver.page_source, "lxml")
        body = soup.body
        product_name = body.find("div", {"class": "shop-product-title"}).text.strip()
        price_body = body.find("div", {"class": "pricing-price"})
        price = float(price_body.find("span").text.strip().replace("$", ""))
        image = body.find("img", {"class": "primary-image"})["src"].split(";")[0]
        availability = body.find("button", {"class": "add-to-cart-button"})
        availability = True if availability else False
        product_info = {
            "name": product_name,
            "price": price,
            "image": image,
            "is_available": availability,
            "url": url,
        }
        return product_info
