import streamlit as st
from streamlit_gsheets import GSheetsConnection
import pandas as pd

# 💡 반드시 파일명이 survey_step1.py여야 합니다.
try:
    import survey_step1
except ImportError:
    st.error("survey_step1.py 파일을 찾을 수 없습니다. 파일 위치를 확인해주세요.")

# 🎨 1. 테마 및 디자인 설정
st.set_page_config(page_title="교원 성장 플랫폼", layout="wide")

st.markdown("""
    <style>
    [data-testid="stSidebarNav"] {display: none;} /* 사이드바 목차 숨기기 */
    .main-card { background-color: white; padding: 20px; border-radius: 15px; border-left: 5px solid #A78BFA; box-shadow: 2px 2px 10px rgba(0,0,0,0.05); min-height: 120px; }
    .status-alert { color: #EF4444; font-weight: bold; }
    .status-ok { color: #10B981; font-weight: bold; }
    </style>
""", unsafe_allow_html=True)

# 🔗 2. 구글 시트 연결 및 유틸 함수
conn = st.connection("gsheets", type=GSheetsConnection)

def clean_val(val):
    if pd.isna(val) or val == "": return ""
    try: return str(int(float(val))).strip()
    except: return str(val).strip()

def check_login(user_id, user_pw):
    try:
        df = conn.read(worksheet="users", ttl=0)
        df.columns = [c.lower().strip() for c in df.columns]
        df['id_clean'] = df['id'].apply(clean_val)
        target_id = clean_val(user_id)
        
        user_row = df[df['id_clean'] == target_id]
        if not user_row.empty:
            if clean_val(user_row.iloc[0]['password']) == clean_val(user_pw):
                return user_row.iloc[0].to_dict()
        return None
    except: return None

# 🔐 3. 세션 초기화 (빈 페이지 방지의 핵심)
if 'user' not in st.session_state:
    st.session_state.user = None
if 'page' not in st.session_state:
    st.session_state.page = "dashboard"

# --- 4. 화면 분기 로직 ---

# A. 로그인 안 된 경우 -> 로그인 화면 강제 출력
if st.session_state.user is None:
    col1, col2, col3 = st.columns([1, 1.5, 1])
    with col2:
        st.title("💜 교원 성장 플랫폼")
        with st.form("login_form"):
            uid = st.text_input("아이디")
            upw = st.text_input("비밀번호", type="password")
            if st.form_submit_button("로그인"):
                user_data = check_login(uid, upw)
                if user_data:
                    st.session_state.user = user_data
                    st.rerun()
                else:
                    st.error("아이디 또는 비밀번호가 일치하지 않습니다.")

# B. 로그인 된 경우
else:
    # 현재 페이지가 설문지인 경우
    if st.session_state.page == "survey":
        survey_step1.show_survey(conn, clean_val)
    
    # 그 외 (대시보드)
    else:
        user = st.session_state.user
        with st.sidebar:
            st.markdown(f"### 🏫 {user.get('school', '학교')}")
            st.write(f"**{user['name']}** 선생님")
            if st.button("로그아웃"):
                st.session_state.user = None
                st.session_state.page = "dashboard"
                st.rerun()

        st.title(f"✨ {user['name']} 선생님, 반갑습니다!")
        
        # 1단계 상태 확인
        s1 = user.get('step1_status')
        s1_text = "완료" if s1 == "완료" else "미실시"
        s1_class = "status-ok" if s1_text == "완료" else "status-alert"

        st.subheader("📊 나의 성장 현황")
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            st.markdown(f'<div class="main-card"><p>1단계: 역량 진단</p><h3 class="{s1_class}">📝 {s1_text}</h3></div>', unsafe_allow_html=True)
            if st.button("진단 시작" if s1_text == "미실시" else "다시 진단하기"):
                st.session_state.page = "survey"
                st.rerun()
        
        # (나머지 col2~4는 생략 또는 디자인용)
