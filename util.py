import sys
import logging

logger = logging.getLogger("crawler")
formatter = logging.Formatter("%(asctime)s %(levelname)s: %(message)s")
handler = logging.StreamHandler(sys.stdout)
handler.setFormatter(formatter)
logger.addHandler(handler)


def log(message, level=logging.INFO):
    logger.setLevel(level)
    logger.log(level, message)


def send_bot_message(msg):
    # TODO: Implement this
    print(msg)


def print_hospital(hosp):
    hosP_ID = hosp["hosP_ID"]
    hosP_NAME = hosp["hosP_NAME"]
    hosP_CNT_TYPE = hosp["hosP_CNT_TYPE"]
    hosptel = hosp["hosptel"]
    hosP_ADDR = hosp["hosP_ADDR"]
    srV_LIST = hosp["srV_LIST"]
    funC_TYPE = hosp["funC_TYPE"]
    brancH_CODE = hosp["brancH_CODE"]
    prE_SRV_LIST = hosp["prE_SRV_LIST"]
    plans = hosp["plans"]
    print(
        f"""<< {hosP_NAME}
= hosP_ID: {hosP_ID}
= hosP_NAME: {hosP_NAME}
= hosP_ADDR: {hosP_ADDR}
= hosP_CNT_TYPE: {hosP_CNT_TYPE}
= hosptel: {hosptel}
= srV_LIST: {srV_LIST}
= funC_TYPE: {funC_TYPE}
= brancH_CODE: {brancH_CODE}
= prE_SRV_LIST: {prE_SRV_LIST}
= plans: {plans}"""
    )


def print_hospitals(hosps):
    i = 0
    for hosp in hosps:
        i += 1
        print(i, hosp["hosP_ID"], hosp["hosP_NAME"])


def print_areas(areas):
    for area_cod in areas:
        print(area_cod["text"], area_cod["value"])


def print_small_areas(small_areas):
    for small_area in small_areas:
        print(small_area["value"], small_area["text"])


def print_reviews(result):
    reviews = result["reviews"]
    try:
        print(f"<< {result['name']}, {result['total_reviews']}, {result['rating']}")
        parsed_reviews = []
        for review in reviews:
            parsed_review = {
                # "plus_id": review["plusId"],
                "author": review["reviewAuthor"],
                # "author_image": review["reviewAuthorImage"],
                "date": review["rawDate"],
                "rating": review["reviewRating"],
                "text": review["reviewText"].strip(),
                # "url": review["reviewUrl"],
                # "flag_url": review["flagUrl"],
            }
            parsed_reviews.append(parsed_review)

        for parsed_review in parsed_reviews:
            print("<<", parsed_review)
    except:
        pass


def get_nested_key(dictionary, keys):
    value = dictionary
    for key in keys:
        if value is None or not isinstance(value, dict):
            return None
        value = value.get(key)
    return value


def parse_offset(args, count):
    try:
        offset = int(args.offset) if args.offset else 0
    except Exception:
        offset = 0
        print(f"Failed to parse offset: {args.offset}. Using 0 instead")
    try:
        offset_end = int(args.offset_end) if args.offset_end else count - 1
    except Exception:
        offset_end = count - 1
        print(f"Failed to parse offset_end: {args.offset_end}. Using {count} instead")
    return (offset, offset_end)
