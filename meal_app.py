import os
import streamlit as st
import requests
from datetime import datetime
from streamlit_lottie import st_lottie

# ✅ 환경변수에서 API 키 읽기
API_KEY = os.getenv("NEIS_API_KEY")

# ✅ Streamlit 기본 세팅
st.set_page_config(
    page_title="오늘의 학교 급식",
    page_icon="🍱",
    layout="centered"
)

st.markdown("""
    <style>
    .title {
        text-align: center;
        font-size: 40px;
        font-weight: bold;
        margin-bottom: 10px;
    }
    .footer {
        color: gray;
        font-size: 12px;
        text-align: center;
        margin-top: 30px;
    }
    </style>
""", unsafe_allow_html=True)

st.markdown('<div class="title">🍽️ 오늘의 급식 보기</div>', unsafe_allow_html=True)
st.divider()

# ✅ 학교 정보 조회 함수
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
    return None

# ✅ 급식 조회 함수
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
        return response.json()["mealServiceDietInfo"][1]["row"]
    return []

# ✅ 사용자 입력
school_name = st.text_input("🏫 학교 이름을 입력하세요", placeholder="예: 서울고등학교")

if school_name:
    with st.spinner("학교 정보를 불러오는 중입니다..."):
        school_info = get_school_info(school_name)

    if not API_KEY:
        st.error("API 키가 설정되지 않았습니다. 관리자에게 문의하세요.")
    elif not school_info:
        st.error("❌ 학교 정보를 찾을 수 없습니다. 정확한 학교명을 입력해주세요.")
    else:
        today = datetime.today().strftime('%Y%m%d')
        meals = get_meal_info(school_info["ATPT_OFCDC_SC_CODE"], school_info["SD_SCHUL_CODE"], today)

        if meals:
            st.success(f"📅 {school_info['SCHUL_NM']} - {datetime.today().strftime('%Y년 %m월 %d일')} 급식 메뉴")

            meal_dict = {meal["MMEAL_SC_NM"]: meal["DDISH_NM"].replace("<br/>", "\n") for meal in meals}
            cols = st.columns(2)

            if "중식" in meal_dict:
                with cols[0]:
                    st.subheader("🥢 중식")
                    st.code(meal_dict["중식"], language="markdown")
            if "석식" in meal_dict:
                with cols[1]:
                    st.subheader("🍛 석식")
                    st.code(meal_dict["석식"], language="markdown")
        else:
            st.warning("⚠️ 오늘은 급식 정보가 없습니다.")
else:
    st.info("학교 이름을 입력하면 오늘 급식을 확인할 수 있어요!")

st.markdown('<div class="footer">ⓒ 2025 급식 확인 앱 | by LWB</div>', unsafe_allow_html=True)
