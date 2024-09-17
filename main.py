import csv
import json
import time
import argparse
import random
from datetime import datetime
from place_finder import PlaceFinder
from util import (
    get_nested_key,
    parse_offset,
    print_areas,
    print_hospitals,
    print_small_areas,
)
from firebase import DataHelper
from hospital_finder import HospitalFinder
from firebase_admin import firestore

place_finder = PlaceFinder()
hospital_finder = HospitalFinder()


def random_sleep(a, b):
    sleep_time = random.uniform(a, b)
    print(f">> Sleeping for {sleep_time:.2f} seconds.")
    time.sleep(sleep_time)
    print(f"<< Resuming...")


def main(args):
    if args.areas:
        areas = hospital_finder.get_areas()
        print_areas(areas)
        return

    if args.small_areas:
        areas = hospital_finder.get_areas()
        print_areas(areas)
        for area in areas:
            small_areas = hospital_finder.get_small_areas(area["value"])
            print_small_areas(small_areas)
        return

    if args.small_area_no:
        (hospitals, count) = hospital_finder.get_hospitals(
            args.small_area_no[0:2], args.small_area_no, args.func_type
        )
        print_hospitals(hospitals)
        return

    if args.search:
        (hospitals, count) = hospital_finder.search_hospitals(
            args.search, args.func_type, args.type
        )
        print_hospitals(hospitals)
        return

    if args.all:
        (hospitals, count) = hospital_finder.search_hospitals()
        print_hospitals(hospitals)
        return

    if args.hosp_id:
        hosp = hospital_finder.get_hospital(args.hosp_id)
        if hosp is None:
            return

        (name, place_id) = place_finder.get_place(hosp["hosP_NAME"], hosp["hosP_ADDR"])
        if place_id is None:
            return

        place_finder.print_google_maps_reviews(place_id)
        return

    helper = DataHelper()

    if args.crawl:
        (hospitals, count) = hospital_finder.search_hospitals("", "", args.type)
        (offset, offset_end) = parse_offset(args, count)

        print(f"== Start processing offset: {offset} to {offset_end}")
        for index, hosp in enumerate(hospitals[offset:offset_end]):
            hosP_ID = hosp["hosP_ID"]
            hosP_NAME = hosp["hosP_NAME"]
            hosP_ADDR = hosp["hosP_ADDR"]
            print(f"[{index + offset}]", f"{hosP_ID} {hosP_NAME} {hosP_ADDR}")

            (place_id, result) = place_finder.get_google_maps_reviews(
                hosP_NAME, hosP_ADDR
            )
            if place_id is None and result is None:
                continue

            if place_id is not None:
                hosp["place_id"] = place_id

            if result is not None:
                hosp["google_maps_reviews"] = result

            total_reviews = get_nested_key(
                hosp,
                ["google_maps_reviews", "location_info", "totalReviews"],
            )

            try:
                if total_reviews is not None and total_reviews != "":
                    int_total_reviews = int(total_reviews.split()[0].replace(",", ""))
                    hosp["intTotalReviews"] = int_total_reviews
                    print(
                        f"<< {total_reviews} found ({hosP_ID}, {hosP_NAME}, {hosp['place_id']})"
                    )
            except Exception as error:
                print(f"Error: {error}")
                continue

            if args.firebase:
                try:
                    hosp["timestamp"] = firestore.SERVER_TIMESTAMP
                    helper.set_document("hospitals", hosP_ID, hosp)
                    print(
                        f"<< {total_reviews} saved ({hosP_ID}, {hosP_NAME}, {hosp['place_id']})"
                    )
                except Exception as error:
                    print(f"Error: {error}")

            random_sleep(2, 4)

        return

    if args.check:
        (hospitals, count) = hospital_finder.search_hospitals("", "", "1")
        try:
            offset = int(args.offset) if args.offset else 0
        except ValueError:
            offset = 0
            print(f"Failed to parse offset: {args.offset}. Using 0 instead")
        try:
            offset_end = int(args.offset_end) if args.offset_end else len(hospitals)
        except ValueError:
            offset_end = len(hospitals)
            print(
                f"Failed to parse offset_end: {args.offset_end}. Using {len(hospitals)} instead"
            )

        print(f"Total {count} hospitals, Offset: {offset}, Offset End: {offset_end}")

        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        file_name = f"output_{timestamp}.csv"
        with open(file_name, mode="w", newline="", encoding="utf-8") as csv_file:
            csv_writer = csv.writer(csv_file)

            for index, hosp in enumerate(hospitals[offset:offset_end]):
                try:
                    doc = helper.get_document("hospitals", hosp["hosP_ID"])
                    doc_totalReviews = get_nested_key(
                        doc, ["google_maps_reviews", "location_info", "totalReviews"]
                    )
                    # if doc_totalReviews is not None and doc_totalReviews != "":
                    #     intTotalReviews = int(
                    #         doc["google_maps_reviews"]["location_info"]["totalReviews"]
                    #         .split()[0]
                    #         .replace(",", "")
                    #     )
                    #     try:
                    #         print(
                    #             "<<", hosp["hosP_ID"], doc_totalReviews, intTotalReviews
                    #         )
                    #         helper.update_document(
                    #             "hospitals",
                    #             hosp["hosP_ID"],
                    #             {"intTotalReviews": intTotalReviews},
                    #         )
                    #     except Exception as error:
                    #         print(f"Error: {error}")
                    #         continue

                    if doc_totalReviews is None:
                        print(f"[{index + offset}][N/A]", hosp)
                        address = hosp["hosP_ADDR"]
                        end_index = address.find("路")
                        if end_index == -1:
                            end_index = address.find("街")
                        if end_index == -1:
                            end_index = address.find("村")
                        if end_index == -1:
                            end_index = address.find("里")
                        if end_index == -1:
                            end_index = address.find("厝")
                        if end_index != -1:
                            address = address[: end_index + 1]

                        (place_id, result) = place_finder.get_google_maps_reviews(
                            hosp["hosP_NAME"], address
                        )

                        hosp["place_id"] = place_id
                        hosp["google_maps_reviews"] = result

                        total_reviews = get_nested_key(
                            hosp,
                            ["google_maps_reviews", "location_info", "totalReviews"],
                        )
                        if total_reviews is not None and total_reviews != "":
                            intTotalReviews = int(
                                total_reviews.split()[0].replace(",", "")
                            )
                            hosp["intTotalReviews"] = intTotalReviews
                        if total_reviews is None:
                            csv_writer.writerow(
                                [
                                    index + offset,
                                    hosp["hosP_ID"],
                                    hosp["hosP_NAME"],
                                    hosp["hosP_ADDR"],
                                    place_id,
                                    json.dumps(result, ensure_ascii=False),
                                ]
                            )
                            csv_file.flush()
                        else:
                            helper.set_document("hospitals", hosp["hosP_ID"], hosp)
                            print(
                                "<<",
                                hosp["google_maps_reviews"]["location_info"][
                                    "totalReviews"
                                ],
                                "saved to Firebase",
                            )

                        random_sleep(2, 4)
                except Exception as error:
                    print(f"Error: {error}")


if __name__ == "__main__":
    parser = argparse.ArgumentParser()

    parser.add_argument(
        "--areas",
        action="store_true",
        help="Area codes to search for hospitals",
    )

    parser.add_argument(
        "--small-areas",
        action="store_true",
        help="Search for hospitals small areas",
    )

    parser.add_argument(
        "--small-area-no",
        help="Search for hospitals in the given area number",
    )

    parser.add_argument(
        "--hosp-id",
        help="Search for hospital information by hospital id",
    )

    parser.add_argument(
        "--func-type",
        help="Search for hospital information by hospital func_type",
    )

    parser.add_argument(
        "--crawl",
        action="store_true",
        help="Crawl google maps reviews for hospitals",
    )

    parser.add_argument(
        "--type",
        help="Search for hospital information by hospital type",
    )

    parser.add_argument(
        "--search",
        help="Search for hospital information by hospital name",
    )

    parser.add_argument(
        "--all",
        action="store_true",
        help="all hospitals",
    )

    parser.add_argument(
        "--firebase",
        action="store_true",
        help="Save data to firebase",
    )

    parser.add_argument(
        "--check",
        action="store_true",
        help="Check data",
    )

    parser.add_argument(
        "--offset",
        default="0",
        help="Offset for search results",
    )

    parser.add_argument(
        "--offset-end",
        help="Offset end for search results",
    )

    parser.add_argument(
        "--slave",
        action="store_true",
        help="Slave mode for crawling",
    )

    parser.add_argument(
        "--version",
        action="version",
        version="%(prog)s (version {version})".format(version="1.0.0"),
    )

    args = parser.parse_args()
    main(args)
