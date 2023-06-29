import time

import openai
import streamlit as st
from supabase import create_client

openai.api_key = st.secrets.OPENAI_TOKEN
openai_model_version = "gpt-3.5-turbo-0613"


@st.cache_resource
def init_connection():
    url = st.secrets["SUPABASE_URL"]
    key = st.secrets["SUPABASE_KEY"]
    return create_client(url, key)


supabase = init_connection()


# CSS 파일 로드
def load_css():
    css = """
    <style>
        %load_ext autoreload
        %autoreload 2
        # Streamlit 컴포넌트 스타일 설정
        body {
          background-color: white;
        }
        .stTextInput input,
        .stButton button {
            background-color: bage !important;
            color:  !important;
        }

        .stTextInput input::placeholder {
            color: #FF6347 !important;
            font-weight: bold;

        }

        .stTextInput input:focus {
            outline: none !important;
            box-shadow: none !important;
        }
        .stSubmitButton {
              display: flex;
              justify-content: center;
        }

        .stSubmitButton button {
          margin: 0 auto;
        }
    </style>
    """
    st.markdown(css, unsafe_allow_html=True)


# CSS 파일 로드 함수 호출
load_css()

# def load_custom_css():
#     st.markdown('<link href="index.html" rel="stylesheet">', unsafe_allow_html=True)
#
# # Custom CSS 로드
# load_custom_css()


st.markdown("<h1 style='color:#FF7F50;'>논문 제작 도우미✍️</h1>", unsafe_allow_html=True)
st.markdown("<span style='font-size: 20px; color: #CD5C5C;'>AI를 이용 하여 논문 작성에 힘을 보태세요😘</span>", unsafe_allow_html=True)

# st.subheader("AI를 이용 하여 논문 작성에 힘을 보태세요😘")
st.text(f"Powerd by {openai_model_version}")


def generate_prompt(subject, title, subtitlte, keywords):
    prompt = f""" 
입력된 주제를 가지고 논문을 쓰려고합니다.
주제,제목, 부제목, 키워드를 참고하여 논문의 목차를 만들어주세요.
우선, 목차의 단계는 3개로 해주세요.
그리고, 입력된 제목, 부제목 보다 적절한 제목과 부제목이 있다면 알려주세요.
다음으로 목차에 맞는 정량적 분석도구, 정성적 분석 도구와 연구의 방향성을 제시해 주세요. 
마지막으로 논문을 쓸 때 참고할 수 있는 reference는 2020년 이후 발간된 것으로 한국논문, 세계논문 및 저널을 각각 3개 이상 알려주세요.
---
주제:{subject}
제목: {title}
부제목: {subtitlte}
키워드: {keywords}
---
"""
    return prompt.strip()


def request_chat_completion(prompt):
    response = openai.ChatCompletion.create(
        model=openai_model_version,
        messages=[
            {"role": "system", "content": "당신은 논문을 쓰는 교수 입니다."},
            {"role": "user", "content": prompt}
        ]
    )
    return response["choices"][0]["message"]["content"]


def write_prompt_result(prompt, result):
    data = supabase.table("paperservice") \
        .insert({"prompt": prompt, "result": result}) \
        .execute()
    print(data)


with st.form("form"):
    subject = st.text_input("Subject", placeholder="제작 하려는 논문의 주제를 입력해 주세요.(필수)", key="my-input")
    title = st.text_input("Title", placeholder="제작 하려는 논문의 제목을 입력해 주세요.(선택)")
    subtitle = st.text_input("Sub_Tilte", placeholder="제작 하려는 논문의 부제목이 있다면 입력해 주세요.(선택)")
    st.text("")
    col1, col2, col3, col4, col5 = st.columns(5)
    with col1:
        keyword_one = st.text_input("Keywords 1", key="keyword_1", placeholder="선택")
    with col2:
        keyword_two = st.text_input("Keywords 2", key="keyword_2", placeholder="선택")
    with col3:
        keyword_three = st.text_input("Keywords 3", key="keyword_3", placeholder="선택")
    with col4:
        keyword_four = st.text_input("Keywords 4", key="keyword_4", placeholder="선택")
    with col5:
        keyword_five = st.text_input("Keywords 5", key="keyword_5", placeholder="선택")

    submitted = st.form_submit_button("Submit")
    if submitted:
        if not subject:
            st.error("논문의 주제를 입력해 주세요")
        else:
            with st.spinner('AI가 논문의 방향성을 제작 중입니다...'):
                keywords = [keyword_one, keyword_two, keyword_three, keyword_four, keyword_five]
                keywords = [x for x in keywords if x]
                if not title:
                    subtitle = "제목"
                if not subtitle:
                    subtitle = "부제목"
                prompt = generate_prompt(subject, title, subtitle, keywords)
                response = request_chat_completion(prompt)
                write_prompt_result(prompt, response)
                st.text_area(
                    label="논문 목차 결과",
                    value=response,
                    placeholder="아직 생성된 문구가 없습니다.",
                    height=1600
                )
