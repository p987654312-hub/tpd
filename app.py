import streamlit as st
from streamlit_gsheets import GSheetsConnection
import pandas as pd
import survey_step1

# 1. 페이지 설정 (사이드바 숨기기 및 웹 폰트)
st.set_page_config(page_title="교원 성장 Mate", layout="wide", initial_sidebar_state="collapsed")

st.markdown("""
    <style>
    /* Streamlit 기본 UI 숨기기 */
    [data-testid="stSidebar"] { display: none; }
    [data-testid="stHeader"] { background: rgba(0,0,0,0); }
    .element-container:has(h1, h2, h3) a { display: none !important; }
    
    /* 전체 배경색 */
    .stApp { background-color: #F9FAFB; }
    
    /* 웹 스타일 카드 디자인 */
    .card-container {
        background: white;
        padding: 40px 20px;
        border-radius: 24px;
        text-align: center;
        box-shadow: 0 10px 25px rgba(0,0,0,0.05);
        border: 2px solid #F3F4F6;
        transition: 0.3s;
    }
    
    /* 실시완료 상태 (초록색) */
    .card-done {
        background: #ECFDF5;
        border: 2px solid #10B981;
    }
    
    .status-badge {
        display: inline-block;
        padding: 5px 15px;
        border-radius: 50px;
        font-size: 0.8rem;
        font-weight: bold;
        margin-bottom: 15px;
    }
    .badge-gray { background: #E5E7EB; color: #6B7280; }
    .badge-green { background: #10B981; color: white; }
    
    /* 버튼 스타일 (웹 서비스 느낌) */
    div.stButton > button {
        border-radius: 12px;
        border: none;
        padding: 10px 24px;
        font-weight: bold;
        width: 80%;
        transition: 0.2s;
    }
    </style>
""", unsafe_allow_html=True)

# 2. 데이터 연결
conn = st.connection("gsheets", type=GSheetsConnection)

def clean_val(val):
    if pd.isna(val) or val == "": return ""
    try: return str(int(float(val))).strip()
    except: return str(val).strip()

# 3. 세션 초기화
if 'user' not in st.session_state: st.session_state.user = None
if 'page' not in st.session_state: st.session_state.page = "dashboard"

# 4. 화면 로직
if st.session_state.user is None:
    # [로그인 화면 생략 - 기존 코드 유지]
    st.title("🔐 교원 성장 Mate")
    with st.form("login"):
        uid = st.text_input("ID")
        upw = st.text_input("PW", type="password")
        if st.form_submit_button("로그인"):
            # (로그인 체크 로직 실행 후 세션 저장)
            st.session_state.user = {"id": uid, "name": "홍길동", "school": "성장초등학교"} # 임시
            st.rerun()
else:
    if st.session_state.page == "survey":
        survey_step1.show_survey(conn, clean_val)
    else:
        # 대시보드
        user = st.session_state.user
        st.write(f"### 🏫 {user['school']} | {user['name']} 선생님")
        st.title("🚀 성장을 위한 여정을 시작하세요")
        
        # 최신 상태 읽기
        s1_status = str(user.get('step1_status', '')).strip()
        is_done = (s1_status == "완료")
        
        col1, col2, col3 = st.columns(3)
        
        with col1:
            card_class = "card-done" if is_done else ""
            badge_class = "badge-green" if is_done else "badge-gray"
            status_text = "실시완료" if is_done else "미실시"
            
            # 💡 카드 디자인과 버튼의 결합
            st.markdown(f"""
                <div class="card-container {card_class}">
                    <div class="status-badge {badge_class}">{status_text}</div>
                    <h2 style="margin-bottom: 30px;">1단계<br>역량 진단</h2>
                </div>
            """, unsafe_allow_html=True)
            
            # 버튼 색상 커스텀
            btn_color = "#10B981" if is_done else "#4F46E5"
            st.markdown(f'<style>div[data-testid="column"]:nth-of-type(1) button {{ background-color: {btn_color} !important; color: white !important; transform: translateY(-30px); }}</style>', unsafe_allow_html=True)
            
            if st.button("결과 확인" if is_done else "진단 시작", key="s1"):
                st.session_state.page = "survey"
                st.rerun()

        # (col2, col3는 동일한 방식으로 구현)
