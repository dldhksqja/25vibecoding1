import os
import streamlit as st
import requests
from datetime import datetime

API_KEY = os.getenv("NEIS_API_KEY")  # Streamlit에 비공개로 등록할 키

# 학교 코드 및 시도교육청코드 조회
def get_school_info(school_name):
    url = "https://open.neis.go.kr/hub/schoolInfo"
    params = {
        "KEY": API_KEY,
        "Type": "json",
        "pIndex": 1,
        "pSize": 100,
        "SCHUL_NM": school_name
    }

    response = requests.get(url, params=params)
    if response.status_code == 200 and "schoolInfo" in response.json():
        school = response.json()["schoolInfo"][1]["row"][0]
        return {
            "ATPT_OFCDC_SC_CODE": school["ATPT_OFCDC_SC_CODE"],
            "SD_SCHUL_CODE": school["SD_SCHUL_CODE"],
            "SCHUL_NM": school["SCHUL_NM"]
        }
    else:
        return None

# 급식 정보 조회
def get_meal_info(atpt_code, school_code, date):
    url = "https://open.neis.go.kr/hub/mealServiceDietInfo"
    params = {
        "KEY": API_KEY,
        "Type": "json",
        "pIndex": 1,
        "pSize": 100,
        "ATPT_OFCDC_SC_CODE": atpt_code,
        "SD_SCHUL_CODE": school_code,
        "MLSV_YMD": date
    }

    response = requests.get(url, params=params)
    if response.status_code == 200 and "mealServiceDietInfo" in response.json():
        meals = response.json()["mealServiceDietInfo"][1]["row"]
        return meals
    else:
        return []

# Streamlit UI
st.title("📅 오늘의 학교 급식 보기")

school_name = st.text_input("학교 이름을 입력하세요", "")

if school_name:
    school_info = get_school_info(school_name)
    if school_info:
        today = datetime.today().strftime('%Y%m%d')
        meals = get_meal_info(school_info["ATPT_OFCDC_SC_CODE"], school_info["SD_SCHUL_CODE"], today)

        if meals:
            st.success(f"{school_info['SCHUL_NM']} - {datetime.today().strftime('%Y년 %m월 %d일')} 급식")
            for meal in meals:
                meal_name = meal["MMEAL_SC_NM"]
                dishes = meal["DDISH_NM"].replace("<br/>", "\n")
                st.subheader(f"{meal_name}")
                st.text(dishes)
        else:
            st.warning("오늘은 급식 정보가 없습니다.")
    else:
        st.error("학교 정보를 찾을 수 없습니다. 정확한 학교명을 입력해주세요.")
