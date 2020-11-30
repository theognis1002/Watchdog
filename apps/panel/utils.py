import concurrent.futures
import logging
import random
import re
import time

import requests
from bs4 import BeautifulSoup
from django.conf import settings
from django.db.models import F
from django.utils import timezone
from selenium import webdriver
from selenium.webdriver.chrome.options import Options

from .models import (Product, ProductReleaseHistory, TargetSite,
                     WatchdogMetaDetails)
from .notify import Notification

logging.basicConfig(format="    [-]%(process)d-%(levelname)s-%(message)s")

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
    notify = Notification()
    chromedriver = "utils/chromedriver"
    MAX_THREADS = settings.MAX_THREADS

    def __init__(self):
        self.driver = self.browser()

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
        self.driver.get(url)
        soup = BeautifulSoup(self.driver.page_source, "lxml")
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
        self.driver.get(url)
        soup = BeautifulSoup(self.driver.page_source, "lxml")
        body = soup.body
        product_name = body.find("h1", {"data-test": "product-title"}).text.strip()
        price = float(
            body.find("div", {"data-test": "product-price"})
            .text.strip()
            .replace("$", "")
        )
        sku = None
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
            "sku": sku,
            "image": image,
            "is_available": availability,
            "url": url,
        }
        return product_info

    def bestbuy_product(self, url):
        self.driver.get(url)
        soup = BeautifulSoup(self.driver.page_source, "lxml")
        body = soup.body
        product_name = body.find("div", {"class": "shop-product-title"}).text.strip()
        price_body = body.find("div", {"class": "pricing-price"})
        price = float(price_body.find("span").text.strip().replace("$", ""))
        sku = int(body.find("div", {"class": "sku"}).text.strip().split(":")[-1])
        image = body.find("img", {"class": "primary-image"})["src"].split(";")[0]
        availability = body.find("button", {"class": "add-to-cart-button"})
        availability = True if availability else False
        product_info = {
            "name": product_name,
            "price": price,
            "sku": sku,
            "image": image,
            "is_available": availability,
            "url": url,
        }
        return product_info

    def check_availability(self, product):
        if "walmart.com" in product.url:
            product_info = self.walmart_product(product.url)

        elif "amazon.com" in product.url:
            product_info = self.amazon_product(product.url)

        elif "target.com" in product.url:
            product_info = self.target_product(product.url)

        elif "bestbuy.com" in product.url:
            product_info = self.bestbuy_product(product.url)

        else:
            raise ValueError("Product url does not match with existing target sites.")

        if product_info["is_available"] and product.is_available is False:
            self.notify.dispatch(product, product_info)
            product.is_available = product_info["is_available"]
            product.save()

            release_record = ProductReleaseHistory(product=product)
            release_record.save()

        print(f"Available: {product_info['is_available']} | Product: {product.name}")

    def run(self):
        try:
            start_time = time.time()
            start_timestamp = timezone.now()

            products = (
                Product.objects.all()
                .order_by("-site")
                .exclude(site__site_name__icontains="walmart")
            )
            walmart_products = Product.objects.filter(
                site__site_name__icontains="walmart"
            )

            threads = min(self.MAX_THREADS, len(walmart_products))

            with concurrent.futures.ThreadPoolExecutor(max_workers=threads) as executor:
                executor.map(self.check_availability, walmart_products)

            for product in products:
                try:
                    self.check_availability(product)
                except Exception as e:
                    logging.error(f"Product Loop - {e.__class__.__name__} - {str(e)}")

        except Exception as e:
            logging.error(f"Main Loop - {e.__class__.__name__} - {str(e)}")

        finally:
            end_time = time.time()
            meta_details = WatchdogMetaDetails.objects.get(site__pk=1)
            meta_details.last_watchdog_run = start_timestamp
            meta_details.last_watchdog_runtime = end_time - start_time
            meta_details.num_of_watchdog_runs = F("num_of_watchdog_runs") + 1
            meta_details.save()
            self.driver.quit()
