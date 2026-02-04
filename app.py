import streamlit as st
from streamlit_gsheets import GSheetsConnection
import pandas as pd

# 1. 페이지 설정 (최상단 배치)
st.set_page_config(
    page_title="교원 성장 Mate", 
    layout="wide", 
    initial_sidebar_state="collapsed"
)

# 2. 웹 스타일 CSS (로그인/회원가입/대시보드 통합)
st.markdown("""
    <style>
    /* 배경 및 메뉴 숨기기 */
    [data-testid="stAppViewContainer"] {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
    }
    [data-testid="stHeader"], [data-testid="stSidebar"] { visibility: hidden; }
    .element-container:has(h1, h2, h3) a { display: none !important; }

    /* 인증 카드 박스 */
    .auth-box {
        background-color: white;
        padding: 40px;
        border-radius: 20px;
        box-shadow: 0 15px 35px rgba(0,0,0,0.2);
        max-width: 500px;
        margin: auto;
    }
    .auth-title { font-size: 2.2rem; font-weight: 800; color: #4A5568; text-align: center; margin-bottom: 5px; }
    .auth-subtitle { color: #718096; text-align: center; margin-bottom: 30px; font-size: 0.9rem; }

    /* 버튼 스타일 */
    div.stButton > button {
        width: 100%;
        background-color: #667eea !important;
        color: white !important;
        padding: 12px !important;
        border-radius: 10px !important;
        border: none !important;
        font-weight: bold !important;
        transition: 0.3s;
    }
    div.stButton > button:hover {
        background-color: #5a67d8 !important;
        transform: translateY(-2px);
    }
    </style>
""", unsafe_allow_html=True)

# 🔗 구글 시트 연결
conn = st.connection("gsheets", type=GSheetsConnection)

def clean_val(val):
    """데이터 형식을 문자열로 통일 및 공백 제거"""
    if pd.isna(val) or val == "": return ""
    try: return str(int(float(val))).strip()
    except: return str(val).strip()

# 🔐 세션 상태 초기화
if 'user' not in st.session_state: st.session_state.user = None
if 'auth_mode' not in st.session_state: st.session_state.auth_mode = 'login'
if 'page' not in st.session_state: st.session_state.page = "dashboard"

# --- 메인 로직 ---

# 1️⃣ 로그인하지 않은 경우 (인증 화면)
if st.session_state.user is None:
    _, col, _ = st.columns([1, 1.8, 1])
    
    with col:
        st.markdown("<div style='height: 8vh;'></div>", unsafe_allow_html=True)
        
        # A. 회원가입 화면
        if st.session_state.auth_mode == 'signup':
            st.markdown('<div class="auth-box"><div class="auth-title">🌱 회원가입</div><div class="auth-subtitle">선생님의 정보를 시트에 등록합니다.</div>', unsafe_allow_html=True)
            
            with st.form("signup_form"):
                new_id = st.text_input("아이디 (id)", placeholder="숫자나 영문 입력")
                new_pw = st.text_input("비밀번호 (password)", type="password")
                new_name = st.text_input("성함 (name)")
                new_school = st.text_input("소속 학교 (school)")
                
                signup_submit = st.form_submit_button("가입 완료 및 저장")
                
                if signup_submit:
                    if not (new_id and new_pw and new_name and new_school):
                        st.error("모든 항목을 입력해야 합니다.")
                    else:
                        try:
                            df = conn.read(worksheet="users", ttl=0)
                            # 아이디 중복 확인
                            if clean_val(new_id) in df['id'].apply(clean_val).values:
                                st.error("이미 존재하는 아이디입니다.")
                            else:
                                # 신규 유저 생성
                                new_row = pd.DataFrame([{
                                    "id": new_id,
                                    "password": new_pw,
                                    "name": new_name,
                                    "school": new_school,
                                    "step1_status": "미실시"
                                }])
                                updated_df = pd.concat([df, new_row], ignore_index=True)
                                conn.update(worksheet="users", data=updated_df)
                                st.success("가입 성공! 이제 로그인 해주세요.")
                                st.session_state.auth_mode = 'login'
                                st.rerun()
                        except Exception as e:
                            st.error(f"시트 업데이트 실패: {e}")
            
            if st.button("계정이 이미 있으신가요? 로그인하기"):
                st.session_state.auth_mode = 'login'
                st.rerun()

        # B. 로그인 화면
        else:
            st.markdown('<div class="auth-box"><div class="auth-title">🚀 EDU Mate</div><div class="auth-subtitle">아이디와 비밀번호를 입력하세요.</div>', unsafe_allow_html=True)
            
            with st.form("login_form"):
                uid = st.text_input("아이디")
                upw = st.text_input("비밀번호", type="password")
                login_submit = st.form_submit_button("로그인하기")
                
                if login_submit:
                    try:
                        df = conn.read(worksheet="users", ttl=0)
                        # 컬럼명 소문자 통일
                        df.columns = [c.lower().strip() for c in df.columns]
                        user_row = df[df['id'].apply(clean_val) == clean_val(uid)]
                        
                        if not user_row.empty and clean_val(user_row.iloc[0]['password']) == clean_val(upw):
                            st.session_state.user = user_row.iloc[0].to_dict()
                            st.success(f"{st.session_state.user['name']} 선생님, 환영합니다!")
                            st.rerun()
                        else:
                            st.error("아이디 또는 비밀번호가 틀렸습니다.")
                    except:
                        st.error("데이터를 불러오지 못했습니다.")
            
            if st.button("처음 오셨나요? 회원가입하기"):
                st.session_state.auth_mode = 'signup'
                st.rerun()

# 2️⃣ 로그인 성공 후 (대시보드 화면)
else:
    # 배경색 흰색으로 복구
    st.markdown("<style>[data-testid='stAppViewContainer'] { background: white; }</style>", unsafe_allow_html=True)
    
    user = st.session_state.user
    st.title(f"✨ {user['name']} 선생님의 성장 대시보드")
    st.write(f"🏫 소속: {user.get('school', '미등록')}")
    st.divider()
    
    # 상태 카드 배치 (예시)
    col1, col2, col3 = st.columns(3)
    with col1:
        status = user.get('step1_status', '미실시')
        color = "green" if status == "완료" else "gray"
        st.markdown(f"""
            <div style="background-color: {'#D1FAE5' if color=='green' else '#F3F4F6'}; 
                        padding: 20px; border-radius: 15px; border: 2px solid {'#10B981' if color=='green' else '#E5E7EB'};">
                <h4>1단계: 역량 진단</h4>
                <p style="font-size: 1.2rem; font-weight: bold;">상태: {status}</p>
            </div>
        """, unsafe_allow_html=True)

    if st.button("로그아웃"):
        st.session_state.user = None
        st.rerun()
