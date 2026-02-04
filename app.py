import streamlit as st
from streamlit_gsheets import GSheetsConnection
import pandas as pd

# 1. 페이지 설정
st.set_page_config(page_title="교원 성장 Mate", layout="wide", initial_sidebar_state="collapsed")

# 2. CSS 스타일 (로그인/대시보드 통합)
st.markdown("""
    <style>
    /* 로그인 배경 */
    .stApp { background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); }
    
    /* 대시보드 진입 시 배경 흰색 강제 적용 */
    .dashboard-bg { background-color: white !important; min-height: 100vh; padding: 20px; }
    
    [data-testid="stHeader"], [data-testid="stSidebar"] { visibility: hidden; }
    .auth-box { background-color: white; padding: 40px; border-radius: 20px; box-shadow: 0 15px 35px rgba(0,0,0,0.2); max-width: 500px; margin: auto; }
    div.stButton > button { width: 100%; background-color: #667eea !important; color: white !important; border-radius: 10px; font-weight: bold; }
    </style>
""", unsafe_allow_html=True)

# 🔗 구글 시트 연결 함수 (에러 방지용)
def get_data():
    try:
        conn = st.connection("gsheets", type=GSheetsConnection)
        df = conn.read(worksheet="users", ttl=0)
        df.columns = [c.lower().strip() for c in df.columns]
        return df
    except:
        return None

def clean_val(val):
    if pd.isna(val) or val == "": return ""
    try: return str(int(float(val))).strip()
    except: return str(val).strip()

# 🔐 세션 상태 초기화
if 'user' not in st.session_state: st.session_state.user = None
if 'auth_mode' not in st.session_state: st.session_state.auth_mode = 'login'

# --- 메인 로직 ---

if st.session_state.user is None:
    # 🔓 로그인 전 화면
    _, col, _ = st.columns([1, 1.8, 1])
    with col:
        st.markdown("<div style='height: 10vh;'></div>", unsafe_allow_html=True)
        
        if st.session_state.auth_mode == 'signup':
            st.markdown('<div class="auth-box"><h2 style="text-align:center; color:#4A5568;">🌱 회원가입</h2>', unsafe_allow_html=True)
            with st.form("signup_form"):
                new_id = st.text_input("아이디")
                new_pw = st.text_input("비밀번호", type="password")
                new_name = st.text_input("성함")
                if st.form_submit_button("가입하기"):
                    df = get_data()
                    if df is not None:
                        if clean_val(new_id) in df['id'].apply(clean_val).values:
                            st.error("이미 존재하는 아이디입니다.")
                        else:
                            new_data = pd.DataFrame([{"id": new_id, "password": new_pw, "name": new_name}])
                            conn = st.connection("gsheets", type=GSheetsConnection)
                            conn.update(worksheet="users", data=pd.concat([df, new_data], ignore_index=True))
                            st.success("가입 성공! 로그인해주세요.")
                            st.session_state.auth_mode = 'login'
                            st.rerun()
                    else:
                        st.error("시트 연결 실패. 잠시 후 다시 시도하세요.")
            if st.button("로그인으로 가기"):
                st.session_state.auth_mode = 'login'
                st.rerun()
        else:
            st.markdown('<div class="auth-box"><h2 style="text-align:center; color:#4A5568;">🚀 로그인</h2>', unsafe_allow_html=True)
            with st.form("login_form"):
                uid = st.text_input("아이디")
                upw = st.text_input("비밀번호", type="password")
                if st.form_submit_button("로그인하기"):
                    df = get_data()
                    if df is not None:
                        user_row = df[df['id'].apply(clean_val) == clean_val(uid)]
                        if not user_row.empty and clean_val(user_row.iloc[0]['password']) == clean_val(upw):
                            # 🔥 세션에 유저 정보를 담고 즉시 리런
                            st.session_state.user = user_row.iloc[0].to_dict()
                            st.rerun()
                        else:
                            st.error("정보가 일치하지 않습니다.")
                    else:
                        st.error("데이터베이스 연결 실패. 새로고침 후 다시 시도하세요.")
            if st.button("회원가입하기"):
                st.session_state.auth_mode = 'signup'
                st.rerun()

else:
    # 🏠 로그인 후 (대시보드 화면)
    # 배경을 흰색으로 덮어씌움
    st.markdown("""
        <style>
        .stApp { background: white !important; }
        [data-testid="stHeader"] { visibility: visible; }
        </style>
    """, unsafe_allow_html=True)
    
    user = st.session_state.user
    st.title(f"✨ {user['name']} 선생님, 반갑습니다!")
    st.info(f"소속: {user.get('school', '정보 없음')}")
    
    st.divider()
    
    # 예시 카드 메뉴
    c1, c2, c3 = st.columns(3)
    with c1:
        st.markdown("""
            <div style="background-color: #F3F4F6; padding: 20px; border-radius: 15px; text-align: center;">
                <h3>1단계</h3>
                <p>역량 진단 시작</p>
            </div>
        """, unsafe_allow_html=True)
        if st.button("시작하기"):
            pass

    if st.button("로그아웃"):
        st.session_state.user = None
        st.rerun()
