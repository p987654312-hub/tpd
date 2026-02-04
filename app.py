import streamlit as st
from streamlit_gsheets import GSheetsConnection
import pandas as pd

# 🎨 1. 설정 및 디자인
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
        cursor: pointer;
        transition: 0.3s;
    }
    .main-card:hover { transform: translateY(-5px); box-shadow: 2px 5px 15px rgba(0,0,0,0.1); }
    h1, h2, h3 { color: #5B21B6; }
    </style>
""", unsafe_allow_html=True)

# 🔗 2. 구글 시트 연결
conn = st.connection("gsheets", type=GSheetsConnection)

def check_login(user_id, user_pw):
    try:
        df = conn.read(worksheet="users", ttl=0)
        df.columns = [c.lower().strip() for c in df.columns]
        
        def clean_val(val):
            if pd.isna(val): return ""
            return str(int(val)).strip() if isinstance(val, (int, float)) else str(val).strip()

        df['id_clean'] = df['id'].apply(clean_val)
        df['pw_clean'] = df['password'].apply(clean_val)
        
        user_row = df[(df['id_clean'] == str(user_id).strip()) & (df['pw_clean'] == str(user_pw).strip())]
        return user_row.iloc[0].to_dict() if not user_row.empty else None
    except: return None

# 🔐 3. 세션 관리
if 'user' not in st.session_state: st.session_state.user = None
if 'page' not in st.session_state: st.session_state.page = "dashboard"

# --- UI 로직 ---
if st.session_state.user is None:
    # 로그인 화면 (생략 - 기존 코드와 동일)
    col1, col2, col3 = st.columns([1, 1.5, 1])
    with col2:
        st.title("💜 교원 성장 플랫폼")
        with st.form("login"):
            uid = st.text_input("아이디")
            upw = st.text_input("비밀번호", type="password")
            if st.form_submit_button("로그인"):
                user = check_login(uid, upw)
                if user:
                    st.session_state.user = user
                    st.rerun()
                else: st.error("정보 불일치")

elif st.session_state.page == "survey":
    # 📝 4. 역량 진단 설문 페이지
    st.title("📝 교원 역량 진단")
    st.write("선생님의 현재 역량을 진단합니다. 모든 문항에 답해주세요.")
    
    with st.form("survey_form"):
        q1 = st.radio("1. 디지털 도구를 수업에 적극적으로 활용하시나요?", ["매우 그렇다", "그렇다", "보통이다", "그렇지 않다"])
        q2 = st.radio("2. 학생들과의 소통에 어려움이 없으신가요?", ["매우 그렇다", "그렇다", "보통이다", "그렇지 않다"])
        
        col1, col2 = st.columns(2)
        if col1.form_submit_button("제출하기"):
            st.success("진단이 완료되었습니다!")
            # 실제로는 여기서 시트에 결과를 저장하는 로직이 들어갑니다.
            st.session_state.page = "dashboard"
            st.rerun()
        if col2.form_submit_button("돌아가기"):
            st.session_state.page = "dashboard"
            st.rerun()

else:
    # 🏠 5. 대시보드
    user = st.session_state.user
    with st.sidebar:
        st.title(f"🏫 {user.get('school', '학교')}")
        st.write(f"**{user['name']}** 선생님")
        if st.button("로그아웃"):
            st.session_state.user = None
            st.rerun()

    st.title(f"✨ {user['name']} 선생님, 반갑습니다!")
    
    # 카드 클릭을 대신할 버튼형 대시보드
    st.subheader("📊 나의 성장 현황")
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.markdown('<div class="main-card">📝 역량 진단</div>', unsafe_allow_html=True)
        if st.button("진단 시작하기", key="btn_s"):
            st.session_state.page = "survey"
            st.rerun()
            
    with col2:
        st.markdown('<div class="main-card">📖 연수 수강</div>', unsafe_allow_html=True)
        st.button("연수 목록보기", key="btn_e")

    # (이하 생략 - 디자인 유지)
