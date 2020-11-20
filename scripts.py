import random
import re

import requests
from bs4 import BeautifulSoup
import random
import re

import requests
from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.chrome.options import Options


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


class Watchdog:
    chromedriver = "utils/chromedriver"

    @staticmethod
    def get_headers():
        return random.choice(headers)

    def browser(self):
        options = Options()
        options.headless = True
        driver = webdriver.Chrome(self.chromedriver, options=options)
        return driver

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
        print(product_info)
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
        print(image)
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
        return product_info


if __name__ == "__main__":
    url = "https://www.amazon.com/Village-Candle-Balsam-Scented-Medium/dp/B002YX0G4Q/?_encoding=UTF8&pd_rd_w=moZ89&pf_rd_p=c16bcbd3-6e98-4c50-a3cc-d529cd3ab077&pf_rd_r=FPG9FRQN42FKW40RKEFC&pd_rd_r=a15e9451-a605-49d2-a937-fce6647a8002&pd_rd_wg=rnYlD&ref_=pd_gw_trq_rep_sims_gw_cart_aware"
    watchdog = Watchdog()
    product_info = watchdog.amazon_product(url)
    print(product_info)