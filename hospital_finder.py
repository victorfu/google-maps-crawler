import json
import requests
from util import print_hospital


sql001 = "https://info.nhi.gov.tw/api/inae1000/inae1000s01/SQL001"
sql100 = "https://info.nhi.gov.tw/api/inae1000/inae1000s01/SQL100"
sql002 = "https://info.nhi.gov.tw/api/inae1000/inae1000s01/SQL002"
sql300 = "https://info.nhi.gov.tw/api/inae1000/inae1000s00/SQL300"


class HospitalFinder(object):
    def get_hospital(self, hosp_id):
        print(f">> Getting hospital for {hosp_id}")
        response = requests.post(sql300, json={"C_HospID": hosp_id, "C_planType": ""})
        json_string = response.content.decode("utf-8")
        hosps = json.loads(json_string)
        if hosps is None or len(hosps) == 0:
            print("<< No hospital found")
            return None
        hosp = hosps[0]
        print_hospital(hosp)
        return hosp

    def search_hospitals(
        self,
        name="",
        func_type="",
        type="",
        page=0,
        size=0,
    ):
        print(
            f">> Searching hospital for (name: {name}) (func_type: {func_type}) (type: {type}) (page: {page}) (size: {size})"
        )
        response = requests.post(
            sql100,
            json={
                "C_FuncType": func_type,
                "C_HospID": "",
                "C_HospName": name,
                "C_AreaCod": "",
                "C_AreaName": "",
                "C_Type": type,
                "C_BranchCode": "",
                "C_HospAddr": "",
                "C_HospCntType": "",
                "C_NoneObs": "",
                "C_Pre": "",
                "C_SrvList": "",
                "C_HospAlliance": "",
                "C_HospFlu": "",
                "C_Plans": "",
                "C_SrvDay": "selAll",
                "C_SrvTime": "012",
                "C_LongHoliday": "",
                "C_LongHolidayTime": "",
                "C_ShowType": "1",
                "pageDataCount": size,
                "nowPage": page,
            },
        )
        json_string = response.content.decode("utf-8")
        data = json.loads(json_string)
        count = data["counts"]
        print(f"<< {count} found")
        return (data["data"], count)

    def get_hospitals(self, area_cod, area_name, func_type="00", page=0, size=0):
        response = requests.post(
            sql100,
            json={
                "C_FuncType": func_type,
                "C_HospID": "",
                "C_HospName": "",
                "C_AreaCod": area_cod,
                "C_AreaName": area_name,
                "C_Type": "",
                "C_BranchCode": "",
                "C_HospAddr": "",
                "C_HospCntType": "",
                "C_NoneObs": "",
                "C_Pre": "",
                "C_SrvList": "",
                "C_HospAlliance": "",
                "C_HospFlu": "",
                "C_Plans": "",
                "C_SrvDay": "selAll",
                "C_SrvTime": "012",
                "C_LongHoliday": "",
                "C_LongHolidayTime": "",
                "C_ShowType": "1",
                "pageDataCount": size,
                "nowPage": page,
            },
        )
        json_string = response.content.decode("utf-8")
        data = json.loads(json_string)
        return (data["data"], data["counts"])

    def get_small_areas(self, area_no):
        response = requests.post(sql002, json={"C_AreaNo": area_no})
        json_string = response.content.decode("utf-8")
        data = json.loads(json_string)
        return data

    def get_areas(self):
        response = requests.get(sql001)
        json_string = response.content.decode("utf-8")
        data = json.loads(json_string)
        areas = data["getAreaCoditem"]
        return areas
