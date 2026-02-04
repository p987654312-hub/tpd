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
        # 실시간 반영을 위해 ttl=0 설정
        df = conn.read(worksheet="users", ttl=0)
        
        # 컬럼명 전처리 (소문자화 및 공백 제거)
        df.columns = [c.lower().strip() for c in df.columns]
        
        # 💡 [핵심 보완] 데이터 형식을 모두 '문자열'로 통일하여 비교
        # 1. 시트 데이터를 문자로 변환 (.astype(str))
        # 2. 소수점(.0)이 붙는 경우를 방지하기 위해 정수형 변환 후 문자로 변환 시도
        def clean_val(val):
            try:
                if pd.isna(val): return ""
                # 숫자인 경우 소수점 제거 후 문자열로
                if isinstance(val, (int, float)):
                    return str(int(val)).strip()
                return str(val).strip()
            except:
                return str(val).strip()

        # 각 컬럼에 클리닝 적용
        df['id_clean'] = df['id'].apply(clean_val)
        df['pw_clean'] = df['password'].apply(clean_val)
        
        # 입력값도 클리닝
        input_id = str(user_id).strip()
        input_pw = str(user_pw).strip()
        
        # 최종 비교
        user_row = df[
            (df['id_clean'] == input_id) & 
            (df['pw_clean'] == input_pw)
        ]
        
        if not user_row.empty:
            return user_row.iloc[0].to_dict()
        return None
    except Exception as e:
        st.error(f"로그인 처리 중 오류 발생: {e}")
        return None

# 🔐 3. 로그인 세션 관리
if 'user' not in st.session_state:
    st.session_state.user = None

# --- UI 로직 ---
if st.session_state.user is None:
    col1, col2, col3 = st.columns([1, 1.5, 1])
    with col2:
        st.write("") 
        st.title("💜 교원 성장 플랫폼")
        st.subheader("로그인")
        with st.form("login_form"):
            # 입력창 힌트 추가
            input_id = st.text_input("아이디 (사번 등)", placeholder="예: 12345")
            input_password = st.text_input("비밀번호", type="password", placeholder="예: 1234")
            submit = st.form_submit_button("로그인")
            
            if submit:
                if input_id and input_password:
                    with st.spinner('인증 정보를 확인 중입니다...'):
                        user_info = check_login(input_id, input_password)
                    if user_info:
                        st.session_state.user = user_info
                        st.rerun()
                    else:
                        st.error("아이디 또는 비밀번호가 일치하지 않습니다.")
                else:
                    st.warning("아이디와 비밀번호를 모두 입력해주세요.")

else:
    # 🏠 4. 메인 대시보드
    user_data = st.session_state.user
    user_name = user_data.get('name', '선생님')
    school_name = user_data.get('school', '정보 없음')
    
    with st.sidebar:
        st.markdown(f"### 🏫 {school_name}")
        st.write(f"👤 **{user_name}** ({user_data.get('role', '교사')})")
        if st.button("로그아웃"):
            st.session_state.user = None
            st.rerun()

    st.title(f"✨ {user_name} 선생님, 반갑습니다!")
    
    s1 = user_data.get('step1_status', '미완료')
    s2 = user_data.get('step2_status', '미완료')
    st.info(f"💡 현재 진행 상태: **역량 진단({s1})** | **연수 수강({s2})**")

    st.divider()

    # 성장 리포트 카드
    st.subheader("📊 나의 성장 현황")
    col1, col2, col3, col4 = st.columns(4)
    
    stages = [
        {"title": "역량 진단", "status": s1, "icon": "📝"},
        {"title": "연수 수강", "status": s2, "icon": "📖"},
        {"title": "수업 실천", "status": "진행 중", "icon": "✍️"},
        {"title": "최종 인증", "status": "대기", "icon": "🏆"}
    ]

    for i, col in enumerate([col1, col2, col3, col4]):
        with col:
            st.markdown(f"""
                <div class="main-card">
                    <p style='font-size: 0.9rem; color: #6B7280;'>{stages[i]['title']}</p>
                    <h3 style='margin: 0;'>{stages[i]['icon']} {stages[i]['status']}</h3>
                </div>
            """, unsafe_allow_html=True)
