import re
import requests
from bs4 import BeautifulSoup
import random

user_agents = [
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/64.0.3282.140 Safari/537.36 Edge/17.17134",
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:61.0) Gecko/20100101 Firefox/61.0",
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/66.0.3359.117 Safari/537.36",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_13_5) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/66.0.3359.117 Safari/537.36",
]


def get_maps_html(clinic_name, place_id):
    url = f"https://www.google.com/maps/search/?api=1&query={clinic_name}&query_place_id={place_id}"
    print(f">> get_maps_html for {url}")
    random_user_agent = random.choice(user_agents)
    headers = {"User-Agent": random_user_agent}
    response = requests.get(url, headers=headers)
    html = response.text
    return html


def get_data_id(text):
    match = re.search(r"!1s([^!]+)!10m1!", text)
    if match:
        return match.group(1)
    else:
        return None


def get_reviews_data(data_id="", token=""):
    random_user_agent = random.choice(user_agents)
    headers = {"User-Agent": random_user_agent}
    url = f"https://www.google.com/async/reviewDialog?hl=en_us&async=feature_id:{data_id},next_page_token:{token},sort_by:qualityScore,start_index:,associated_topic:,_fmt:pc"
    response = requests.get(url, headers=headers)
    soup = BeautifulSoup(response.content.decode("utf-8"), "html.parser")

    user = []
    location_info = {}
    next_token = ""

    for el in soup.select(".lcorif"):
        if next_token == "":
            location_info = {
                "title": el.select_one(".P5Bobd").text.strip()
                if el.select_one(".P5Bobd")
                else "",
                "address": el.select_one(".T6pBCe").text.strip()
                if el.select_one(".T6pBCe")
                else "",
                "avgRating": el.select_one("span.Aq14fc").text.strip()
                if (el.select_one("span.Aq14fc") is not None)
                else "",
                "totalReviews": el.select_one("span.z5jxId").text.strip()
                if el.select_one("span.z5jxId")
                else "",
            }
        next_token = soup.select_one(".gws-localreviews__general-reviews-block")[
            "data-next-page-token"
        ]
    for el in soup.select(".gws-localreviews__google-review"):
        user.append(
            {
                "name": el.select_one(".TSUbDb").text.strip()
                if (el.select_one(".TSUbDb") is not None)
                else "",
                "link": el.select_one(".TSUbDb a")["href"],
                "thumbnail": el.select_one(".lDY1rd")["src"]
                if el.select_one(".lDY1rd")["src"]
                else "",
                "numOfreviews": el.select_one(".Msppse").text.strip()
                if (el.select_one(".Msppse") is not None)
                else "",
                "rating": el.select_one(".z3HNkc")["aria-label"]
                if el.select_one(".z3HNkc")["aria-label"]
                else "",
                "review": el.select_one(".Jtu6Td").text.strip()
                if (el.select_one(".Jtu6Td") is not None)
                else "",
                "images": [
                    d["style"][21 : d["style"].rindex(")")]
                    for d in el.select(".EDblX .JrO5Xe")
                ],
            }
        )

    if next_token != "":
        get_reviews_data(data_id, next_token)

    return {"user": user, "location_info": location_info}


def crawl(clinic_name, place_id):
    print(f">> Searching data id for {clinic_name} and {place_id}")
    html = get_maps_html(clinic_name, place_id)
    data_id = get_data_id(html)
    print(f"<< data id {data_id}")
    print(f">> Scraping reviews for data id {data_id}")
    result = get_reviews_data(data_id)
    return result
