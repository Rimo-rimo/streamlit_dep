import streamlit as st
import requests
from glob import glob
import datetime
import pandas as pd
import numpy as np
import random
import matplotlib.pyplot as plt
import altair as alt
import os
from datetime import timedelta
import subprocess
# import streamlit_authenticator as stauth

# ====================parameters====================
back_ip = "localhost"
back_port = 8505
meal_photo_dir_path = "/home/livin/kidney_service/back/fastapi/app"
life_log_container_height = 400
main_text_color = "#31333F"
blood_weight_range_dict = {"1주일":1, "1달":2, "6달":3, "1년":4}
first_patient_num = 26

# ====================setting====================
st.set_page_config(layout="wide")

menu_bar = """
                <style>
                    .gray-box {
                        display: inline-block; /* 상자를 옆으로 나열 */
                        background-color: #F0F2F6; /* 회색 배경 */
                        padding: 4px; /* 안쪽 여백 */
                        margin: 3px; /* 상자 사이 간격 */
                        border-radius: 2px; /* 둥근 모서리 */
                    }
                </style>
            """

st.markdown("""
    <style>
    .stRadio [role=radiogroup]{
        align-items: center;
        justify-content: center;
    }
    </style>
""",unsafe_allow_html=True)

st.markdown(
        """
       <style>
       [data-testid="stSidebar"][aria-expanded="true"]{
           min-width: 314px;
           max-width: 314px;
       }
       """,
        unsafe_allow_html=True,
    )   

weekdays_in_korean = {
    'Monday': '월',
    'Tuesday': '화',
    'Wednesday': '수',
    'Thursday': '목',
    'Friday': '금',
    'Saturday': '토',
    'Sunday': '일',
}

meal_info_order = ["energy", "carbohydrate", "totalSugars", "protein", "fat", "transFattyAcid", "saturatedFattyAcid", "cholesterol", "sodium"]

meal_info_name_dict = {
        'fat': '지방 (g)', 'energy': '에너지 (kcal)', 'sodium': '나트륨 (mg)', 'calcium': '칼슘',
        'protein': '단백질 (g)', 'cholesterol': '콜레스테롤 (mg)', 'totalSugars': '당류 (g)',
        'carbohydrate': '탄수화물 (g)', 'transFattyAcid': '트랜스지방 (g)', 'totalDietaryFiber': '총식이섬유',
        'saturatedFattyAcid': '포화지방산 (g)', 'thiamin': '티아민'
    }

# =================================================
def date_delta_init():
    st.session_state['date_delta'] = 0

def meal_colorize(s, color):
    return [f'background-color: {color}' for v in s]

# @st.cache_data
def get_pdf_file(back_ip, back_port, user_id, voiding_date, file_name):
    subprocess.run(["python", "./utils/voiding.py", "--back_ip",str(back_ip), "--back_port",str(back_port), "--user_id", user_id, "--date", voiding_date, "--file_name", file_name,"--mode", "pdf"])
    with open(f"./voiding_file/{str(patient_name+voiding_data['voiding']['date'])}.pdf", "rb") as pdf_file:
        PDFbyte = pdf_file.read()
    return PDFbyte

# @st.cache_data
def get_excel_file(back_ip, back_port, user_id, voiding_date, file_name):
    subprocess.run(["python", "./utils/voiding.py", "--back_ip",str(back_ip), "--back_port",str(back_port), "--user_id", user_id, "--date", voiding_date, "--file_name", file_name,"--mode", "excel"])
    with open(f"./voiding_file/{str(patient_name+voiding_data['voiding']['date'])}.xlsx", "rb") as excel_file:
        EXCELbyte = excel_file.read()
    return EXCELbyte

def goal_submit():
    st.session_state.goal_text = st.session_state.widget
    st.session_state.widget = ""

if 'login_info' not in st.session_state:
    _, login_container, __ = st.columns(3)
    login_c = login_container.container(border=True)
    with login_c:
        st.subheader("Login")
        Username = st.text_input('Username')
        Password = st.text_input('Password')
        
        login_button = st.button(label="Login", key="login_button")
        if login_button:
            if Username == "test" and Password == "test":
                st.session_state['login_info'] = True
                st.rerun()
            else:
                st.error('Username/Password is incorrect', icon="🚨")

else: 
    st.markdown("<h1 style='text-align: center; color:#06C580;'>KidneyCare Doctor Page</h1>", unsafe_allow_html=True)

    patient_dict = requests.get(f"http://{back_ip}:{back_port}/api/doctor/patient/list").json()

    if len(patient_dict.keys()) == 0:
        st.markdown(f"<h6>아직 등록된 환자가 없습니다 🥲</h6>", unsafe_allow_html=True)

    else:
        patient_name_c, patient_date_c = st.columns(2)

        with patient_name_c: 
            patient_name = st.selectbox("**Patient**", patient_dict.keys(), index=1)

        if patient_name:
            with patient_date_c:
                if 'date_delta' not in st.session_state:
                    st.session_state['date_delta'] = 0

                if 'date' not in st.session_state:
                    st.session_state['date'] = datetime.datetime.now().date()

                date = st.session_state['date'] + timedelta(st.session_state["date_delta"])
                input_date = st.date_input("**Date**", date)

                if input_date != st.session_state["date"]:
                    date_delta_init()
                    st.session_state['date'] = input_date
                    st.rerun()

                all_data = requests.get(f"http://{back_ip}:{back_port}/api/doctor/patient/all_data", params={"patient_id":patient_dict[patient_name], "date":date}).json()

                before_day, today_day, next_day = st.columns(3)
                with before_day:
                    if st.button("< 이전", use_container_width=True):
                        st.session_state["date_delta"] += -1
                        st.rerun()
                with today_day:
                    if st.button("오늘", use_container_width=True):
                        st.session_state["date_delta"] = 0
                        st.session_state['date'] = datetime.datetime.now().date()
                        st.rerun()
                with next_day:
                    if st.button("다음 >", use_container_width=True):
                        st.session_state["date_delta"] += 1
                        st.rerun()

            with patient_name_c:
                english_weekday = date.strftime('%A')
                korean_weekday = weekdays_in_korean[english_weekday]
                st.markdown(f"<h3><span>[</span><span style='color:#06C580;'>{patient_name}</span><span>]</span><span>님의 </span><span>[</span><span style='color:#06C580;'>{date} ({korean_weekday})</span><span>]</span><span>일자 데이터입니다.</span></h3>", unsafe_allow_html=True)

            life_log_tab, voiding_tab = st.tabs(["Life Log", "배뇨일지"])

            with life_log_tab:
                blood_col, weight_col, meal_col, urine_col = st.columns([2.6,2.6,2.6, 2.2])

                with blood_col:
                    st.markdown(f"<h4 style='color:{main_text_color};'>혈압</h4>", unsafe_allow_html=True)
                    blood= st.container(border=True, height=life_log_container_height)
                    with blood:
                        blood_data_list = all_data["blood"]
                        blood_con = st.container(border=True)
                        with blood_con:
                            if len(blood_data_list) == 0:
                                blood_con.markdown("<h5 style='text-align: center;color:#878A9B;'>기입해주지 않았어요</h5>",unsafe_allow_html=True)
                            else:
                                systolic = blood_data_list[0]["systolic"]
                                diastolic = blood_data_list[0]["diastolic"]

                                blood_c1, blood_c2, _ = st.columns([0.40, 0.40, 0.2])
                                blood_c1.markdown("<h5 style='color:#8A8D9D;'>SYS</h5>", unsafe_allow_html=True)
                                blood_c1.markdown(f"<h4 style='color:#505050;'>{systolic}</h4>", unsafe_allow_html=True)
                                blood_c2.markdown("<h5 style='color:#8A8D9D;'>DIA</h5>", unsafe_allow_html=True)
                                blood_c2.markdown(f"<h4 style='color:#505050;'>{diastolic}</h4>", unsafe_allow_html=True)
                                _.markdown("<span style='color:#DB6A7C;'>&nbsp;</span>", unsafe_allow_html=True)
                                _.markdown("<span style='color:#DB6A7C;'>&nbsp;</span>", unsafe_allow_html=True)
                                _.text("mmHg")

                        blood_chart_range = st.radio("blood_chart_range",["1주일","1달", "6달", "1년"], key="blood_chart_range", horizontal=True, label_visibility="hidden")
                        blood_chart_data = requests.get(f"http://{back_ip}:{back_port}/api/doctor/patient/blood/trend", params={"user_id":patient_dict[patient_name], "end_date":date,"period":blood_weight_range_dict[blood_chart_range]}).json()
                        systolic_list = [int(i["systolic"]) for i in blood_chart_data]
                        diastolic_list = [int(i["diastolic"]) for i in blood_chart_data]
                        blood_date_list = [i["date"] for i in blood_chart_data]
                        # selected_date_list = [blood_date_list[0], blood_date_list[len(blood_date_list)//2], blood_date_list[-1]]
                        real_blood_list = [int(i["is_real"]) for i in blood_chart_data]
                    
                        blood_min = min(diastolic_list) if len(diastolic_list)>0 else 90
                        blood_max = max(systolic_list) if len(systolic_list)>0 else 110
                        blood_data = pd.DataFrame({
                            'Date': blood_date_list,
                            'Systolic': systolic_list,
                            'Diastolic': diastolic_list,
                            'is_real' : real_blood_list
                        })

                        # 가시성 조건을 만족하는 데이터 포인트에 대해 큰 투명한 원 추가
                        systolic_hover = alt.Chart(blood_data).mark_circle(size=400, opacity=0).encode(
                            x='Date:T',
                            y='Systolic:Q',
                            tooltip=['Date:T', 'Systolic:Q']
                        ).transform_filter(
                            alt.datum.is_real == 1  # 가시성이 1인 데이터 포인트만 표시
                        )

                        diastolic_hover = alt.Chart(blood_data).mark_circle(size=400, opacity=0).encode(
                            x='Date:T',
                            y='Diastolic:Q',
                            tooltip=['Date:T', 'Diastolic:Q']
                        ).transform_filter(
                            alt.datum.is_real == 1  # 가시성이 1인 데이터 포인트만 표시
                        )

                        # 점을 추가하여 인터랙티브하게 만든 차트
                        systolic_points = alt.Chart(blood_data).mark_point(color='#DB6A7C').encode(
                            x=alt.X('Date:T', title=''),
                            y=alt.Y('Systolic:Q', scale=alt.Scale(domain=[blood_min-10, blood_max+10]), title=''),
                            tooltip=['Date:T', 'Systolic:Q']  # 툴팁 추가
                        ).transform_filter(
                            alt.datum.is_real == 1
                        )

                        diastolic_points = alt.Chart(blood_data).mark_point(color='#E1AB69').encode(
                            x='Date:T',
                            y=alt.Y('Diastolic:Q', scale=alt.Scale(domain=[blood_min-10, blood_max+10]), title=''),
                            tooltip=['Date:T', 'Diastolic:Q']  # 툴팁 추가
                        ).transform_filter(
                            alt.datum.is_real == 1
                        )

                        # 선과 점을 합쳐서 하나의 차트로 만들기
                        systolic_chart = alt.Chart(blood_data).mark_line(interpolate='monotone', color='#DB6A7C').encode(
                            x='Date:T',
                            y='Systolic:Q'
                        )

                        diastolic_chart = alt.Chart(blood_data).mark_line(interpolate='monotone', color='#E1AB69').encode(
                            x='Date:T',
                            y='Diastolic:Q'
                        )

                        # 선과 점을 합쳐서 하나의 레이어로 만들기
                        systolic_layer = alt.layer(systolic_chart, systolic_points, systolic_hover)#.interactive()
                        diastolic_layer = alt.layer(diastolic_chart, diastolic_points, diastolic_hover)#.interactive()

                        # 두 차트를 합치기
                        blood_chart = alt.layer(systolic_layer, diastolic_layer).resolve_scale(y='shared').properties(height=160)

                        st.altair_chart(blood_chart, use_container_width=True, theme="streamlit")

                with weight_col:
                    st.markdown(f"<h4 style='color:{main_text_color};'>체중</h4>", unsafe_allow_html=True)
                    weight= st.container(border=True, height=life_log_container_height)
                    with weight:
                        weight_data_list = all_data["weight"]
                        weight_con = st.container(border=True)
                        with weight_con:
                            if len(weight_data_list) == 0:
                                weight_con.markdown("<h5 style='text-align: center; color:#878A9B;'>기입해주지 않았어요</h5>",unsafe_allow_html=True)
                            else:
                                if len(weight_data_list) == 2:
                                    morning_weight = weight_data_list[0]["weight"]
                                    night_weight = weight_data_list[1]["weight"]
                                else:
                                    morning_weight, night_weight = weight_data_list[0]["weight"], weight_data_list[0]["weight"]

                                weight_widget,_ = st.columns([0.8, 0.2])
                                weight_widget.markdown("<h5 style='color:#8A8D9D;'>체중</h5>", unsafe_allow_html=True)
                                weight_widget.markdown(f"<h4 style='color:#505050;'>{morning_weight} ~ {night_weight}</h4>", unsafe_allow_html=True)

                                _.markdown("<span style='color:#DB6A7C;'>&nbsp;</span>", unsafe_allow_html=True)
                                _.markdown("<span style='color:#DB6A7C;'>&nbsp;</span>", unsafe_allow_html=True)
                                _.text("kg")

                        weight_chart_range = st.radio("weight_chart_range",["1주일","1달", "6달", "1년"], key="weight_chart_range", horizontal=True, label_visibility="hidden")
                        weight_chart_data = requests.get(f"http://{back_ip}:{back_port}/api/doctor/patient/weight/trend", params={"user_id":patient_dict[patient_name], "end_date":date,"period":blood_weight_range_dict[weight_chart_range]}).json()

                        weight_date_list = [i["date"] for i in weight_chart_data]
                        weight_list = [i["weight"] for i in weight_chart_data]
                        real_weight_list = [int(i["is_real"]) for i in weight_chart_data]
                        weight_data = pd.DataFrame({
                            'Date': weight_date_list,
                            'Weight': weight_list,
                            'is_real': real_weight_list
                        })
                        weight_min = min(weight_list) if len(weight_list)>0 else 5
                        weight_max = max(weight_list) if len(weight_list)>0 else 95

                        weight_hover = alt.Chart(weight_data).mark_circle(size=400, opacity=0).encode(
                            x='Date:T',
                            y='Weight:Q',
                            tooltip=['Date:T', 'Weight:Q']
                        ).transform_filter(
                            alt.datum.is_real == 1  # 가시성이 1인 데이터 포인트만 표시
                        )

                        # 점을 추가하여 인터랙티브하게 만든 차트
                        weight_points = alt.Chart(weight_data).mark_point(color='#81CFFA').encode(
                            x=alt.X('Date:T', title=''),
                            y=alt.Y('Weight:Q', scale=alt.Scale(domain=[weight_min-5, weight_max+5]), title=''),
                            tooltip=['Date:T', 'Weight:Q']  # 툴팁 추가
                        ).transform_filter(
                            alt.datum.is_real == 1
                        )
                        # 선과 점을 합쳐서 하나의 차트로 만들기
                        weight_chart = alt.Chart(weight_data).mark_line(interpolate='monotone', color='#81CFFA').encode(
                            x='Date:T',
                            y='Weight:Q'
                        ).properties(height=160)

                        # weight_chart = alt.Chart(weight_data).mark_line(interpolate='monotone',color='#81CFFA').encode(
                        #     x=alt.X('Date:N', title=''),  # N은 명목형 데이터를 나타냅니다.
                        #     y=alt.Y('Weight:Q', scale=alt.Scale(domain=[weight_min-5, weight_max+5]), title='')  # Q는 수량 데이터를 나타냅니다.
                        # ).properties(height=160)
                        wieght_layer = alt.layer(weight_points, weight_chart, weight_hover)#.interactive()
                        st.altair_chart(wieght_layer, use_container_width=True, theme="streamlit")

                with meal_col:
                    st.markdown(f"<h4 style='color:{main_text_color};'>식단</h4>", unsafe_allow_html=True)
                    meal= st.container(border=True, height=life_log_container_height)
                    meal_time_dict = {0: "아침", 1:"점심", 2:"저녁", 3:"기타"}
                    meal_data_list = all_data["meal"]
                    with meal:
                        meal_data_list = all_data["meal"]
                        if len(meal_data_list) == 0:
                            meal_con = st.container(border=True)
                            meal_con.markdown("<h5 style='text-align: center; color:#878A9B;'>기입해주지 않았어요</h5>",unsafe_allow_html=True)
                        else:
                            for meal_data in meal_data_list:
                                st.markdown(f"<h5 style='color:#505050;'>{meal_time_dict[meal_data['time_of_day']]}</h5>", unsafe_allow_html=True)
                                meal_c = st.container(border=True)
                                with meal_c: 
                                    meal_c1, meal_c2 = st.columns(2)
                                    try:
                                        meal_c1.image(os.path.join(meal_photo_dir_path, meal_data["photo_url"]),use_column_width="always")
                                    except:
                                        meal_c1.image("./source/no_image.png")

                                    meal_menu_list = meal_data["meal_info"].keys()

                                    meal_menus = ""
                                    for item in meal_menu_list:
                                        meal_menus += f'<span class="gray-box">{item}</span>'
                                    meal_c2.markdown(menu_bar + meal_menus, unsafe_allow_html=True)

                                    with st.popover("영양성분", use_container_width=True):
                                        meal_df = pd.DataFrame.from_dict(meal_data["meal_info"])
                                        if len(list(meal_df.index)) == 0:
                                            meal_df = pd.DataFrame(index=["vitaminA", "vitaminC", "vitaminD", "vitaminE", "thiamin", "totalDietaryFiber", "calcium", "energy", "carbohydrate", "totalSugars", "protein", "fat", "transFattyAcid", "saturatedFattyAcid", "cholesterol", "sodium"], columns=meal_df.columns)
                                        meal_totals = meal_df.sum(axis=1)
                                        meal_df.insert(0, "전체", meal_totals)

                                        meal_df.drop(index=["vitaminA", "vitaminC", "vitaminD", "vitaminE", "thiamin", "totalDietaryFiber", "calcium"], inplace=True)

                                        meal_df = meal_df.reindex(meal_info_order)

                                        meal_df = meal_df.rename(index=meal_info_name_dict)

                                        meal_df = meal_df.round(2)

                                        # meal_df = meal_df.style.apply(lambda x: meal_colorize(x, '#D3FFD9'), subset=['전체'])

                                        st.write(meal_df)


                                        

                with urine_col:
                    st.markdown(f"<h4 style='color:{main_text_color};'>소변 검사</h4>", unsafe_allow_html=True)
                    urine= st.container(border=True, height=life_log_container_height)
                    urine_name_dict = {"bil":"빌리루빈",
                                    "glu":"포도당",
                                    "ket":"케톤체",
                                    "no2":"아질산염",
                                    "ph":"산도",
                                    "prot":"단백질",
                                    "rbc":"잠혈",
                                    "sg":"비중",
                                    "uro":"우로빌리노겐",
                                    "wbc":"백혈구"}
                    urine_judgment_dict = {0:"🟢 정상", 1:"🟡 주의", 2:"🟠 경고", 3:"🔴 위험"}
                    
                    urine_data = all_data["urine"]

                    if urine_data:
                        name_list = []
                        value_list = []
                        judgment_list = []

                        for i in urine_name_dict:
                            name_list.append(urine_name_dict[i])
                            value_list.append(urine_data[i])
                            judgment_list.append(urine_judgment_dict[urine_data[f"{i}_class"]])

                        with urine:
                            df = pd.DataFrame(
                                {
                                    "항목": name_list,
                                    "값": value_list,
                                    "판단결과": judgment_list
                                }
                            )
                            st.dataframe(
                                df,
                                hide_index=True,
                                width=400,
                                height=410
                            )
                    else:
                        urine_con = urine.container(border=True)
                        urine_con.markdown("<h5 style='text-align: center; color:#878A9B;'>기입해주지 않았어요</h5>",unsafe_allow_html=True)

                goal_col, feedback_col = st.columns(2)

                with goal_col:
                    st.markdown(f"<h4 style='color:{main_text_color};'>목표 설정</h4>", unsafe_allow_html=True)
                    goal= st.container(border=True)
                    goal_option_dict = {"운동":0, "약물 섭취":1 ,"식단":2, "물 섭취":3, "기타":4}
                    goal_data = all_data["goal"]
                    with goal:
                        goal_col_1, goal_col_2 = st.columns(2)
                        with goal_col_1:
                            goal_option = st.selectbox('**목표 유형**', ('운동', '약물 섭취', '식단', '물 섭취', '기타'))
                        with goal_col_2:
                            # goal_content = st.text_input('**목표 내용**', placeholder="구체적인 목표를 작성해 주세요.")
                            if "goal_text" not in st.session_state:
                                    st.session_state.goal_text = ""

                            st.text_input("**목표 내용**", key="widget", on_change=goal_submit, placeholder="구체적인 목표를 작성해 주세요.")
                            goal_content = st.session_state.goal_text

                        goal_button = st.button(label="저장", key="goal", use_container_width=True)

                        if goal_button:
                            if goal_option and goal_content:

                                goal_post_response = requests.post(f"http://{back_ip}:{back_port}/api/doctor/patient/goal", json={"user_id":patient_dict[patient_name], "date":str(date) , "goal_description":goal_content, "goal_type":goal_option_dict[goal_option], "archievement_status":False}).json()

                                st.rerun()
                        if goal_data:
                            for n, goal in enumerate(goal_data["goal_details"]):
                                with st.chat_message("user", avatar=f"./source/{goal['goal_type']}.svg"):
                                    goal_message, goal_delete_button = st.columns([0.8,0.2])
                                    goal_message.write(goal["goal_description"])
                                    if goal["archievement_status"]:
                                        st.info("멋지게 해냈어요 🤗")
                                    else:
                                        st.error("아직 완수하진 못했어요 🥲")
                                    if goal_delete_button.button(label="삭제", key=f"goal_{n}", use_container_width=True):
                                        goal_detail_id = goal["goal_detail_id"]
                                        goal_delete_response = requests.delete(f"http://{back_ip}:{back_port}/api/doctor/patient/goal?goal_detail_id={goal_detail_id}").json()
                                        st.rerun()

                with feedback_col:
                    st.markdown(f"<h4 style='color:{main_text_color};'>피드백</h4>", unsafe_allow_html=True)
                    feedback= st.container(border=True)
                    feedback_data_list = all_data["feedback"]

                    with feedback:
                        feedback_content = st.chat_input("환자에게 피드백을 남겨주세요.")
                        if feedback_content:
                            title = feedback_content if len(feedback_content)<=10 else f"{feedback_content[:7]}..."
                            feedback_post_response = requests.post(f"http://{back_ip}:{back_port}/api/doctor/patient/feedback", json={"user_id":patient_dict[patient_name], "doctor_id":patient_dict[patient_name],"date":str(date) , "content":feedback_content, "title":title}).json()
                            st.rerun()

                        for n, feedback_data in enumerate(feedback_data_list):
                            with st.chat_message("user"):
                                feedback_message, feedback_delete_button = st.columns([0.8, 0.2])
                                feedback_message.write(feedback_data["content"])
                                if feedback_delete_button.button(label="삭제", key=n, use_container_width=True):
                                    feedback_delete_response = requests.delete(f"http://{back_ip}:{back_port}/api/doctor/patient/feedback?feedback_id={feedback_data['feedback_id']}").json()
                                    st.rerun()
            with voiding_tab:
                voiding_list_json = requests.get(f"http://{back_ip}:{back_port}/api/doctor/patient/voiding_list", params={"user_id":patient_dict[patient_name]}).json()
                if len(voiding_list_json) == 0:
                    st.markdown(f"<h6>아직 배뇨일지를 하나도 작성해 주지 않았어요 🥲</h6>", unsafe_allow_html=True)
                else:

                    voiding_date_selection, voiding_chart = st.columns([0.2,0.8])
                    with voiding_date_selection:
                        voiding_list = [i["date"] for i in voiding_list_json]
                        voiding_date = st.selectbox(f'**[{patient_name}] 님의 배뇨 일지**', voiding_list)
                    
                    with voiding_chart:
                        voiding_chart_c = st.container(border=True)
                        with voiding_chart_c:
                            voiding_data = requests.get(f"http://{back_ip}:{back_port}/api/doctor/patient/voiding_details", params={"user_id":patient_dict[patient_name], "date":voiding_date}).json()
                            time_list = [i["voiding_time"] for i in voiding_data["voiding_details"]]
                            time_list.append("통합")

                            volume_list = [i["voiding_volume"] for i in voiding_data["voiding_details"]]
                            volume_list.append(sum(volume_list))

                            water_list = [i["water_intake"] for i in voiding_data["voiding_details"]]
                            water_list.append(sum(water_list))

                            urgency_list = [i["urgency_level"] for i in voiding_data["voiding_details"]]
                            urgency_list.append(" ")

                            voiding_df = pd.DataFrame(
                                    {
                                        "기상 시간": [voiding_data["voiding"]["waking_time"]],
                                        "취침 시간": [voiding_data["voiding"]["sleeping_time"]],
                                        "기상 시 체중(kg)": [voiding_data["voiding"]["morning_weight"]],
                                        "취침 전 체중(kg)": [voiding_data["voiding"]["evening_weight"]]
                                    }
                                )
                            # voiding_df = voiding_df.style.apply(lambda x: meal_colorize(x, '#D3FFD9'), subset=['통합'])
                            
                            voiding_basic_df = pd.DataFrame(
                                    {
                                        "배뇨 시간": time_list,
                                        "배뇨량(cc)": volume_list,
                                        "물섭취량(ml)": water_list,
                                        "배뇨 충동(1~5)": urgency_list
                                    }
                                )
                            st.subheader(f"{voiding_data['voiding']['date']}")
                            st.dataframe(voiding_df, hide_index=True, width=400)
                            st.dataframe(voiding_basic_df, hide_index=True, width=400)

                            voiding_pdf, voiding_excel, _ = st.columns([1,1,5])
                            if voiding_pdf.button(label = "PDF 변환", key="pdf", use_container_width=True):
                                with st.spinner("Converting PDF..."):
                                    voiding_pdf_b = voiding_pdf.download_button(label="PDF 다운로드", data=get_pdf_file(back_ip, back_port, str(voiding_data['voiding']['user_id']), str(voiding_data['voiding']['date']), str(patient_name+voiding_data['voiding']['date'])), file_name=f"{str(patient_name)}_{str(voiding_data['voiding']['date'])}.pdf")
                            if voiding_excel.button(label = "Excel 변환", key="excel", use_container_width=True):
                                with st.spinner("Converting Excel..."):
                                    voiding_excel_b = voiding_excel.download_button(label="Excel 다운로드", data=get_excel_file(back_ip, back_port, str(voiding_data['voiding']['user_id']), str(voiding_data['voiding']['date']), str(patient_name+voiding_data['voiding']['date'])), file_name=f"{str(patient_name)}_{str(voiding_data['voiding']['date'])}.xlsx")
        else:
            st.text("환자를 선택해 주세요")
            