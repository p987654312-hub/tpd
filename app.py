import streamlit as st
from streamlit_gsheets import GSheetsConnection
import pandas as pd

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
    }
    h1, h2, h3 { color: #5B21B6; }
    .stButton>button { background-color: #A78BFA; color: white; border-radius: 8px; width: 100%; }
    </style>
""", unsafe_allow_html=True)

# 🔗 2. 구글 시트 연결
conn = st.connection("gsheets", type=GSheetsConnection)

def check_login(user_id, user_pw):
    try:
        # 실시간 반영을 위해 ttl=0 설정 (캐시 무시)
        df = conn.read(worksheet="users", ttl=0)
        
        # 컬럼명 전처리: 모든 컬럼명을 소문자로 바꾸고 공백 제거
        df.columns = [c.lower().strip() for c in df.columns]
        
        # 데이터 비교: 문자열 변환 및 양 끝 공백 제거로 정확도 극대화
        # 선생님이 알려주신 'id'와 'password' 컬럼을 사용합니다.
        user_row = df[
            (df['id'].astype(str).str.strip() == str(user_id).strip()) & 
            (df['password'].astype(str).str.strip() == str(user_pw).strip())
        ]
        
        if not user_row.empty:
            # 로그인 성공 시 해당 행의 데이터를 딕셔너리로 반환
            return user_row.iloc[0].to_dict()
        return None
    except Exception as e:
        st.error(f"데이터를 읽는 중 오류가 발생했습니다. 시트의 컬럼명을 확인해주세요: {e}")
        return None

# 🔐 3. 로그인 세션 관리
if 'user' not in st.session_state:
    st.session_state.user = None

# --- UI 로직 ---
if st.session_state.user is None:
    # 로그인 화면
    col1, col2, col3 = st.columns([1, 1.5, 1])
    with col2:
        st.write("") # 상단 여백
        st.title("💜 교원 성장 플랫폼")
        st.subheader("로그인")
        with st.form("login_form"):
            input_id = st.text_input("아이디 (사번 등)")
            input_password = st.text_input("비밀번호", type="password")
            submit = st.form_submit_button("로그인")
            
            if submit:
                if input_id and input_password:
                    user_info = check_login(input_id, input_password)
                    if user_info:
                        st.session_state.user = user_info
                        st.success(f"{user_info['name']} 선생님, 인증되었습니다!")
                        st.rerun()
                    else:
                        st.error("아이디 또는 비밀번호가 일치하지 않습니다.")
                else:
                    st.warning("아이디와 비밀번호를 모두 입력해주세요.")

else:
    # 🏠 4. 메인 대시보드 (로그인 후 화면)
    user_data = st.session_state.user
    user_name = user_data.get('name', '선생님')
    school_name = user_data.get('school', '소속 학교 정보 없음')
    
    # 상단 헤더 및 로그아웃
    with st.sidebar:
        st.markdown(f"### 🏫 {school_name}")
        st.write(f"**{user_name}** ({user_data.get('role', '교사')})")
        if st.button("로그아웃"):
            st.session_state.user = None
            st.rerun()

    st.title(f"✨ {user_name} 선생님, 반갑습니다!")
    
    # 알려주신 step1, step2 상태 표시
    s1 = user_data.get('step1_status', '미완료')
    s2 = user_data.get('step2_status', '미완료')
    st.info(f"💡 현재 진행 상태: **역량 진단({s1})** | **연수 수강({s2})**")

    st.divider()

    # 진행 단계별 카드 현황
    st.subheader("📊 나의 성장 현황")
    col1, col2, col3, col4 = st.columns(4)
    
    # 카드에 표시할 내용 구성
    stages = [
        {"title": "역량 진단", "status": s1, "icon": "📝"},
        {"title": "연수 수강", "status": s2, "icon": "📖"},
        {"title": "수업 실천", "status": user_data.get('admin/user', '일반'), "icon": "✍️"},
        {"title": "최종 인증", "status": "준비 중", "icon": "🏆"}
    ]

    for i, col in enumerate([col1, col2, col3, col4]):
        with col:
            st.markdown(f"""
                <div class="main-card">
                    <p style='font-size: 0.9rem; color: #6B7280;'>{stages[i]['title']}</p>
                    <h3 style='margin: 0;'>{stages[i]['icon']} {stages[i]['status']}</h3>
                </div>
            """, unsafe_allow_html=True)

    # 5. [관리자 전용 기능]
    if user_data.get('admin/user') == 'admin':
        st.write("")
        st.divider()
        st.subheader("🛠️ 관리자 전용 메뉴")
        if st.button("전체 교사 현황 내려받기"):
            all_data = conn.read(worksheet="users")
            st.dataframe(all_data)
