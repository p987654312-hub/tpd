import streamlit as st
from streamlit_gsheets import GSheetsConnection
import pandas as pd

# 💡 분리된 설문지 모듈 불러오기
try:
    import survey_step1
except ImportError:
    st.error("survey_step1.py 파일을 찾을 수 없습니다. 파일 위치를 확인해주세요.")

# 🎨 1. 테마 및 디자인 설정
st.set_page_config(page_title="교원 성장 플랫폼", layout="wide")

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
    }
    h1, h2, h3 { color: #5B21B6; }
    .stButton>button { background-color: #A78BFA; color: white; border-radius: 8px; width: 100%; }
    .status-alert { color: #EF4444; font-weight: bold; }
    .status-ok { color: #10B981; font-weight: bold; }
    /* 사이드바 메뉴를 숨기기 위한 스타일 (선택사항) */
    [data-testid="stSidebarNav"] {display: none;}
    </style>
""", unsafe_allow_html=True)

# 🔗 2. 구글 시트 연결 및 데이터 정제 함수
conn = st.connection("gsheets", type=GSheetsConnection)

def clean_val(val):
    if pd.isna(val): return ""
    return str(int(val)).strip() if isinstance(val, (int, float)) else str(val).strip()

def check_login(user_id, user_pw):
    try:
        df = conn.read(worksheet="users", ttl=0)
        df.columns = [c.lower().strip() for c in df.columns]
        df['id_clean'] = df['id'].apply(clean_val)
        df['pw_clean'] = df['password'].apply(clean_val)
        user_row = df[(df['id_clean'] == str(user_id).strip()) & (df['pw_clean'] == str(user_pw).strip())]
        return user_row.iloc[0].to_dict() if not user_row.empty else None
    except: return None

# 🔐 3. 세션 관리
if 'user' not in st.session_state:
    st.session_state.user = None
if 'page' not in st.session_state:
    st.session_state.page = "dashboard"

# --- 4. 메인 로직 ---

# A. 로그인 화면
if st.session_state.user is None:
    col1, col2, col3 = st.columns([1, 1.5, 1])
    with col2:
        st.write("")
        st.title("💜 교원 성장 플랫폼")
        with st.form("login"):
            uid = st.text_input("아이디")
            upw = st.text_input("비밀번호", type="password")
            if st.form_submit_button("로그인"):
                user = check_login(uid, upw)
                if user:
                    st.session_state.user = user
                    st.rerun()
                else:
                    st.error("정보가 일치하지 않습니다.")

# B. 로그인 후 화면
else:
    user = st.session_state.user
    
    # [사이드바] 목차 대신 사용자 정보만 표시
    with st.sidebar:
        st.markdown(f"### 🏫 {user.get('school', '학교')}")
        st.write(f"**{user['name']}** 선생님")
        st.divider()
        if st.button("로그아웃"):
            st.session_state.user = None
            st.session_state.page = "dashboard"
            st.rerun()

    # [화면 전환]
    if st.session_state.page == "survey":
        # 💡 survey_step1.py 파일의 함수 호출
        survey_step1.show_survey(conn, clean_val)
        
    else:
        # 🏠 대시보드 화면
        st.title(f"✨ {user['name']} 선생님, 반갑습니다!")
        
        # 상태 처리
        raw_s1 = user.get('step1_status')
        s1 = "미실시" if pd.isna(raw_s1) or str(raw_s1).strip() == "" or str(raw_s1).lower() == "nan" else str(raw_s1)
        s1_class = "status-alert" if s1 == "미실시" else "status-ok"

        st.subheader("📊 나의 성장 현황")
        col1, col2, col3, col4 = st.columns(4)

        with col1:
            st.markdown(f'<div class="main-card"><p>1단계: 역량 진단</p><h3 class="{s1_class}">📝 {s1}</h3></div>', unsafe_allow_html=True)
            if st.button("진단 시작하기" if s1 == "미실시" else "다시 진단하기"):
                st.session_state.page = "survey"
                st.rerun()
        
        # 나머지 단계 카드들 (디자인용)
        with col2:
            st.markdown(f'<div class="main-card"><p>2단계: 연수 수강</p><h3>📖 {user.get("step2_status", "미완료")}</h3></div>', unsafe_allow_html=True)
            st.button("연수 목록 보기", disabled=True)
        with col3:
            st.markdown('<div class="main-card"><p>3단계: 수업 실천</p><h3>✍️ 대기</h3></div>', unsafe_allow_html=True)
        with col4:
            st.markdown('<div class="main-card"><p>4단계: 최종 인증</p><h3>🏆 대기</h3></div>', unsafe_allow_html=True)
