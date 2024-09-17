import os
from dotenv import load_dotenv
import requests
from crawler import crawl

from util import print_reviews

load_dotenv()

api_key = os.getenv("GOOGLE_MAPS_API_KEY")
if api_key is None:
    print("Error: GOOGLE_MAPS_API_KEY is not set")
    exit(1)


class PlaceFinder:
    def get_places(self, search_term):
        search_url = f"https://maps.googleapis.com/maps/api/place/textsearch/json?query={search_term}&key={api_key}"
        print(f">> Searching places for {search_term} ({search_url})")

        try:
            response = requests.post(search_url)
            if response.json()["status"] == "OK":
                return response.json()["results"]
        except Exception as error:
            print(f"Error: {error}")
            return None

    def get_place(self, search_name, search_address=""):
        address_keywords = ["路", "街", "村", "里", "厝"]
        if search_address != "":
            search_addresses = [search_address] + [
                search_address[: search_address.find(kw) + 1]
                for kw in address_keywords
                if search_address.find(kw) != -1
            ]
        else:
            search_addresses = [""]

        for addr in search_addresses:
            search_term = f"{search_name}+{addr}"
            search_url = f"https://maps.googleapis.com/maps/api/place/textsearch/json?query={search_term}&key={api_key}"
            print(f">> Searching places for {search_term} ({search_url})")

            try:
                response = requests.post(search_url)
                if response.json()["status"] != "OK":
                    print("<< Searching failed", response.json()["status"])
                    continue  # Continue with the next search address

                places = response.json()["results"]
                if places is None or len(places) == 0:
                    print("<< No place found in search results")
                    continue  # Continue with the next search address

                name = places[0]["name"]
                place_id = places[0]["place_id"]
                print("<<", name, place_id)
                return (name, place_id)
            except Exception as error:
                print(f"Error: {error}")
                continue  # Continue with the next search address

        # If no results are found after all address variations are tried
        return (None, None)

    def print_google_maps_reviews(self, place_id):
        print(f">> Searching (v1) reviews for {place_id}")
        api = f"https://api.reviewsmaker.com/gmb?placeid={place_id}"
        try:
            response = requests.get(api)
            result = response.json()
            if result is None:
                print("<< No reviews found")
                return None
            print_reviews(result)
            return result
        except Exception as error:
            print(f"Error: {error}")
            return None

    def get_google_maps_reviews(self, hosP_NAME, hosP_ADDR):
        places = self.get_places(f"{hosP_NAME}+{hosP_ADDR}")
        if places is None or len(places) == 0:
            print("<<", f"{hosP_NAME}+{hosP_ADDR}", "No place found")
            return (None, None)

        name = places[0]["name"]
        place_id = places[0]["place_id"]
        print("<<", name, place_id)

        result = crawl(name, place_id)
        if result is None:
            print("<<", place_id, "No reviews found")
            return (place_id, None)
        return (place_id, result)
