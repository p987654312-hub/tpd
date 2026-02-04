import streamlit as st
from streamlit_gsheets import GSheetsConnection
import pandas as pd

# 💡 분리된 페이지 모듈 불러오기
# (파일명이 survey_step1.py여야 합니다)
try:
    import survey_step1
except ImportError:
    st.error("survey_step1.py 파일을 찾을 수 없습니다. 파일명이 정확한지 확인해주세요.")

# 🎨 1. 전체 페이지 설정 및 테마 디자인
st.set_page_config(page_title="교원 성장 플랫폼", layout="wide", initial_sidebar_state="expanded")

st.markdown("""
    <style>
    .stApp { background-color: #F8F7FF; }
    .main-card {
        background-color: white;
        padding: 20px;
        border-radius: 15px;
        border-left: 5px solid #A78BFA;
        box-shadow: 2px 2px 10px rgba(0,0,0,0.05);
        min-height: 120px;
        margin-bottom: 10px;
    }
    h1, h2, h3 { color: #5B21B6; font-family: 'Pretendard', sans-serif; }
    .stButton>button { background-color: #A78BFA; color: white; border-radius: 8px; width: 100%; transition: 0.3s; }
    .stButton>button:hover { background-color: #7C3AED; border-color: #7C3AED; }
    .status-alert { color: #EF4444; font-weight: bold; }
    .status-ok { color: #10B981; font-weight: bold; }
    </style>
""", unsafe_allow_html=True)

# 🔗 2. 구글 시트 연결 및 유틸리티 함수
conn = st.connection("gsheets", type=GSheetsConnection)

def clean_val(val):
    """데이터 타입 일치를 위한 클리닝 함수"""
    if pd.isna(val): return ""
    return str(int(val)).strip() if isinstance(val, (int, float)) else str(val).strip()

def check_login(user_id, user_pw):
    """아이디/비번 확인 로직"""
    try:
        df = conn.read(worksheet="users", ttl=0)
        df.columns = [c.lower().strip() for c in df.columns]
        
        # ID와 PW를 모두 클리닝하여 비교
        df['id_clean'] = df['id'].apply(clean_val)
        df['pw_clean'] = df['password'].apply(clean_val)
        
        user_row = df[(df['id_clean'] == str(user_id).strip()) & 
                      (df['pw_clean'] == str(user_pw).strip())]
        
        return user_row.iloc[0].to_dict() if not user_row.empty else None
    except Exception as e:
        st.error(f"로그인 오류: {e}")
        return None

# 🔐 3. 세션 관리 (로그인 상태 및 현재 페이지 저장)
if 'user' not in st.session_state:
    st.session_state.user = None
if 'page' not in st.session_state:
    st.session_state.page = "dashboard"

# --- 4. 메인 UI 분기 로직 ---

# A. 로그인하지 않은 경우
if st.session_state.user is None:
    col1, col2, col3 = st.columns([1, 1.5, 1])
    with col2:
        st.write("") # 간격
        st.title("💜 교원 성장 플랫폼")
        st.subheader("로그인")
        with st.form("login_form"):
            input_id = st.text_input("아이디 (사번 등)")
            input_pw = st.text_input("비밀번호", type="password")
            submit = st.form_submit_button("로그인")
            
            if submit:
                user_info = check_login(input_id, input_pw)
                if user_info:
                    st.session_state.user = user_info
                    st.success(f"{user_info['name']} 선생님, 환영합니다!")
                    st.rerun()
                else:
                    st.error("아이디 또는 비밀번호가 올치하지 않습니다.")

# B. 로그인한 경우
else:
    user = st.session_state.user
    
    # [사이드바 설정]
    with st.sidebar:
        st.title("🏫 소속 정보")
        st.write(f"**학교:** {user.get('school', '정보없음')}")
        st.write(f"**성함:** {user.get('name', '선생님')}")
        st.write(f"**직함:** {user.get('role', '교사')}")
        st.divider()
        if st.button("로그아웃"):
            st.session_state.user = None
            st.session_state.page = "dashboard"
            st.rerun()

    # [페이지 전환 관리]
    if st.session_state.page == "survey_step1":
        # 💡 사전 역량 진단 페이지 호출
        survey_step1.show_survey(conn, clean_val)
        
    elif st.session_state.page == "dashboard":
        # 🏠 메인 대시보드 화면
        st.title(f"✨ {user['name']} 선생님의 성장 공간")
        
        # 1단계 상태 확인 (nan 처리)
        raw_s1 = user.get('step1_status')
        s1 = "미실시" if pd.isna(raw_s1) or str(raw_s1).strip() == "" or str(raw_s1).lower() == "nan" else str(raw_s1)
        s1_class = "status-alert" if s1 == "미실시" else "status-ok"

        st.info(f"💡 현재 진행 단계: **{s1}**")
        st.write("")

        # 📊 성장 현황 카드 레이아웃
        col1, col2, col3, col4 = st.columns(4)

        with col1:
            st.markdown(f"""
                <div class="main-card">
                    <p style='font-size: 0.9rem; color: #6B7280;'>1단계: 역량 진단</p>
                    <h3 class="{s1_class}">📝 {s1}</h3>
                </div>
            """, unsafe_allow_html=True)
            if st.button("진단하기" if s1 == "미실시" else "다시 진단하기", key="go_s1"):
                st.session_state.page = "survey_step1"
                st.rerun()

        with col2:
            s2 = user.get('step2_status', '미완료')
            st.markdown(f"""
                <div class="main-card">
                    <p style='font-size: 0.9rem; color: #6B7280;'>2단계: 연수 수강</p>
                    <h3>📖 {s2}</h3>
                </div>
            """, unsafe_allow_html=True)
            st.button("연수 목록 보기", key="go_s2")

        with col3:
            st.markdown(f"""
                <div class="main-card">
                    <p style='font-size: 0.9rem; color: #6B7280;'>3단계: 수업 실천</p>
                    <h3>✍️ 진행전</h3>
                </div>
            """, unsafe_allow_html=True)
            st.button("실천 기록하기", key="go_s3", disabled=True)

        with col4:
            st.markdown(f"""
                <div class="main-card">
                    <p style='font-size: 0.9rem; color: #6B7280;'>4단계: 최종 인증</p>
                    <h3>🏆 대기</h3>
                </div>
            """, unsafe_allow_html=True)
            st.button("인증 신청하기", key="go_s4", disabled=True)
