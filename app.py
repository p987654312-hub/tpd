import streamlit as st
from streamlit_gsheets import GSheetsConnection
import pandas as pd
import survey_step1

st.set_page_config(page_title="교원 성장 플랫폼", layout="wide")

# 🎨 디자인 스타일 (사이드바 메뉴 숨기기 포함)
st.markdown("""
    <style>
    [data-testid="stSidebarNav"] {display: none;}
    .main-card { background-color: white; padding: 20px; border-radius: 15px; border-left: 5px solid #A78BFA; box-shadow: 2px 2px 10px rgba(0,0,0,0.05); }
    .status-ok { color: #10B981; font-weight: bold; }
    .status-alert { color: #EF4444; font-weight: bold; }
    </style>
""", unsafe_allow_html=True)

conn = st.connection("gsheets", type=GSheetsConnection)

def clean_val(val):
    """숫자/문자 불일치 해결사"""
    if pd.isna(val) or val == "": return ""
    try: return str(int(float(val))).strip()
    except: return str(val).strip()

# [세션 관리]
if 'user' not in st.session_state: st.session_state.user = None
if 'page' not in st.session_state: st.session_state.page = "dashboard"

# [로그인 로직]
if st.session_state.user is None:
    # ... (이전과 동일한 로그인 폼 코드) ...
    # 로그인 성공 시 st.session_state.user 저장 후 rerun
    pass

else:
    # 🏠 대시보드 화면
    if st.session_state.page == "survey":
        survey_step1.show_survey(conn, clean_val)
    else:
        user = st.session_state.user
        st.title(f"✨ {user['name']} 선생님, 반갑습니다!")
        
        # 💡 첫 번째 시트 상태 표기 (실시간 세션 값 활용)
        s1_status = user.get('step1_status', '미실시')
        if pd.isna(s1_status) or s1_status == "": s1_status = "미실시"
        
        col1, col2, col3, col4 = st.columns(4)
        with col1:
            st.markdown(f"""
                <div class="main-card">
                    <p>1단계: 역량 진단</p>
                    <h3 class="{"status-ok" if s1_status=='완료' else "status-alert"}">📝 {s1_status}</h3>
                </div>
            """, unsafe_allow_html=True)
            if st.button("진단 시작하기" if s1_status != "완료" else "다시 진단하기"):
                st.session_state.page = "survey"
                st.rerun()
