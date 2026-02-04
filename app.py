import streamlit as st
from streamlit_gsheets import GSheetsConnection
import pandas as pd
import survey_step1 # 💡 pages 폴더 밖의 파일을 직접 불러옵니다.

# [생략] 테마 디자인 및 로그인 로직은 이전과 동일하게 유지

# 🔐 세션 및 페이지 관리
if 'user' not in st.session_state: st.session_state.user = None
if 'page' not in st.session_state: st.session_state.page = "dashboard"

if st.session_state.user is None:
    # 로그인 화면 (생략)
    pass
elif st.session_state.page == "survey":
    # 💡 버튼 클릭 시 이 부분이 실행되어 설문 화면이 나옵니다.
    survey_step1.show_survey(conn, clean_val)
else:
    # 🏠 대시보드 화면
    st.title(f"✨ {st.session_state.user['name']} 선생님")
    # ... 중략 ...
    if st.button("진단하기"):
        st.session_state.page = "survey" # 💡 페이지 상태 변경
        st.rerun()
