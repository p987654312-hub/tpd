import streamlit as st
from streamlit_gsheets import GSheetsConnection

# 🎨 1. 테마 및 디자인 설정 (연한 보라색 포인트)
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
    }
    h1, h2, h3 { color: #5B21B6; }
    .stButton>button { background-color: #A78BFA; color: white; border-radius: 8px; }
    </style>
""", unsafe_standard_text=True)

# 🔗 2. 구글 시트 연결
conn = st.connection("gsheets", type=GSheetsConnection)

def check_login(user_id, user_pw):
    df = conn.read(worksheet="users")
    user_row = df[(df['id'] == user_id) & (df['pw'] == str(user_pw))]
    if not user_row.empty:
        return user_row.iloc[0].to_dict()
    return None

# 🔐 3. 로그인 세션 관리
if 'user' not in st.session_state:
    st.session_state.user = None

# --- UI 로직 ---
if st.session_state.user is None:
    # 로그인 화면
    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        st.title("💜 교원 성장 플랫폼")
        st.subheader("로그인")
        with st.form("login_form"):
            input_id = st.text_input("아이디")
            input_pw = st.text_input("비밀번호", type="password")
            submit = st.form_submit_button("로그인")
            
            if submit:
                user_info = check_login(input_id, input_pw)
                if user_info:
                    st.session_state.user = user_info
                    st.rerun()
                else:
                    st.error("아이디 또는 비밀번호가 일치하지 않습니다.")

else:
    # 🏠 4. 메인 대시보드
    user_name = st.session_state.user['name']
    
    # 상단 헤더
    st.title(f"✨ {user_name} 선생님, 반갑습니다!")
    if st.sidebar.button("로그아웃"):
        st.session_state.user = None
        st.rerun()

    st.divider()

    # 진행 단계별 카드 현황 (Mock Data)
    st.subheader("📊 나의 성장 리포트")
    col1, col2, col3, col4 = st.columns(4)
    
    stages = [
        {"title": "역량 진단", "count": "완료", "color": "✅"},
        {"title": "연수 수강", "count": "3개 진행 중", "color": "📖"},
        {"title": "수업 실천", "count": "12건 기록", "color": "✍️"},
        {"title": "최종 인증", "count": "검토 중", "color": "🏆"}
    ]

    for i, col in enumerate([col1, col2, col3, col4]):
        with col:
            st.markdown(f"""
                <div class="main-card">
                    <p style='font-size: 0.9rem; color: #6B7280;'>{stages[i]['title']}</p>
                    <h3 style='margin: 0;'>{stages[i]['color']} {stages[i]['count']}</h3>
                </div>
            """, unsafe_allow_html=True)

    # 추가 콘텐츠 영역
    st.write("")
    st.info(f"💡 현재 **'{st.session_state.user['status']}'** 단계에 계시네요. 다음 목표까지 조금만 더 힘내세요!")