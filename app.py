import streamlit as st
from streamlit_gsheets import GSheetsConnection
import pandas as pd

# --------------------------------------------------------------------------
# 1. 설문지 파일 불러오기 (파일이 같은 폴더에 있어야 합니다)
# --------------------------------------------------------------------------
try:
    import survey_step1
except ImportError:
    st.error("survey_step1.py 파일이 없습니다. 같은 폴더에 파일을 만들어주세요.")

# --------------------------------------------------------------------------
# 2. 페이지 기본 설정 및 디자인 (CSS)
# --------------------------------------------------------------------------
st.set_page_config(
    page_title="교원 성장 Mate", 
    layout="wide", 
    initial_sidebar_state="collapsed"
)

# 세션 상태 초기화 (새로고침 시 데이터 유지용)
if 'user' not in st.session_state: st.session_state.user = None
if 'auth_mode' not in st.session_state: st.session_state.auth_mode = 'login'
if 'page' not in st.session_state: st.session_state.page = "dashboard"

# CSS 스타일 정의
st.markdown("""
    <style>
    /* 기본 폰트 및 배경 설정 */
    @import url('https://fonts.googleapis.com/css2?family=Pretendard:wght@400;700&display=swap');
    html, body, [class*="css"] { font-family: 'Pretendard', sans-serif; }
    
    /* 상단 헤더, 사이드바 숨기기 & 제목 링크 아이콘 제거 */
    [data-testid="stHeader"] { visibility: hidden; }
    [data-testid="stSidebar"] { display: none; }
    .element-container:has(h1, h2, h3) a { display: none !important; }
    
    /* 로그인 박스 디자인 */
    .auth-box {
        background-color: white;
        padding: 40px;
        border-radius: 24px;
        box-shadow: 0 10px 25px rgba(0,0,0,0.1);
        text-align: center;
        max-width: 450px;
        margin: 0 auto;
    }
    
    /* 버튼 공통 디자인 */
    div.stButton > button {
        width: 100%;
        border-radius: 12px;
        height: 45px;
        font-weight: bold;
        border: none;
        transition: 0.2s;
    }
    </style>
""", unsafe_allow_html=True)

# --------------------------------------------------------------------------
# 3. 구글 시트 연결 및 유틸 함수
# --------------------------------------------------------------------------
conn = st.connection("gsheets", type=GSheetsConnection)

def clean_val(val):
    """숫자/문자 형식을 통일하고 공백을 제거하는 함수"""
    if pd.isna(val) or val == "": return ""
    try: return str(int(float(val))).strip()
    except: return str(val).strip()

def get_data():
    """시트 데이터를 안전하게 가져오는 함수"""
    try:
        df = conn.read(worksheet="users", ttl=0)
        df.columns = [c.lower().strip() for c in df.columns]
        return df
    except Exception as e:
        st.error(f"데이터 연결 오류: {e}")
        return None

# --------------------------------------------------------------------------
# 4. 메인 로직 시작
# --------------------------------------------------------------------------

# [상황 A] 로그인을 아직 안 했을 때
if st.session_state.user is None:
    # 로그인 화면 전용 배경 (보라색 그라데이션)
    st.markdown("""
        <style>
        [data-testid="stAppViewContainer"] {
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        }
        </style>
    """, unsafe_allow_html=True)

    _, col, _ = st.columns([1, 1.5, 1])
    with col:
        st.markdown("<div style='height: 10vh;'></div>", unsafe_allow_html=True)
        
        # A-1. 회원가입 모드
        if st.session_state.auth_mode == 'signup':
            st.markdown('<div class="auth-box"><h2>🌱 회원가입</h2><p style="color:#718096;">선생님의 정보를 입력해주세요.</p>', unsafe_allow_html=True)
            
            with st.form("signup_form"):
                new_id = st.text_input("아이디 (ID)")
                new_pw = st.text_input("비밀번호 (PW)", type="password")
                new_name = st.text_input("성함 (Name)")
                new_school = st.text_input("소속 학교 (School)")
                
                if st.form_submit_button("가입 완료"):
                    df = get_data()
                    if df is not None:
                        # 아이디 중복 체크
                        if clean_val(new_id) in df['id'].apply(clean_val).values:
                            st.error("이미 사용 중인 아이디입니다.")
                        else:
                            # 새 유저 추가 (step1_status 기본값: 미실시)
                            new_row = pd.DataFrame([{
                                "id": new_id, 
                                "password": new_pw, 
                                "name": new_name, 
                                "school": new_school, 
                                "step1_status": "미실시"
                            }])
                            updated_df = pd.concat([df, new_row], ignore_index=True)
                            conn.update(worksheet="users", data=updated_df)
                            
                            st.success("가입되었습니다! 로그인해주세요.")
                            st.session_state.auth_mode = 'login'
                            st.rerun()
            
            st.markdown("</div>", unsafe_allow_html=True)
            if st.button("이미 계정이 있으신가요? 로그인하기"):
                st.session_state.auth_mode = 'login'
                st.rerun()

        # A-2. 로그인 모드
        else:
            st.markdown('<div class="auth-box"><h2>🚀 EDU Mate</h2><p style="color:#718096;">로그인하여 성장을 시작하세요.</p>', unsafe_allow_html=True)
            
            with st.form("login_form"):
                uid = st.text_input("아이디")
                upw = st.text_input("비밀번호", type="password")
                
                if st.form_submit_button("로그인"):
                    df = get_data()
                    if df is not None:
                        target_id = clean_val(uid)
                        user_row = df[df['id'].apply(clean_val) == target_id]
                        
                        if not user_row.empty and clean_val(user_row.iloc[0]['password']) == clean_val(upw):
                            # 로그인 성공! 세션 저장 후 페이지 새로고침
                            st.session_state.user = user_row.iloc[0].to_dict()
                            st.session_state.page = "dashboard" # 대시보드로 이동 설정
                            st.rerun()
                        else:
                            st.error("아이디 또는 비밀번호가 일치하지 않습니다.")
            
            st.markdown("</div>", unsafe_allow_html=True)
            if st.button("처음 오셨나요? 회원가입하기"):
                st.session_state.auth_mode = 'signup'
                st.rerun()

# [상황 B] 로그인 성공 후
else:
    # 대시보드 전용 배경 (흰색) 및 헤더 보이기
    st.markdown("""
        <style>
        [data-testid="stAppViewContainer"] { background: #FFFFFF; }
        [data-testid="stHeader"] { visibility: visible; background: transparent; }
        </style>
    """, unsafe_allow_html=True)

    # B-1. 설문지 페이지 ("survey" 상태일 때)
    if st.session_state.page == "survey":
        # survey_step1.py 파일의 show_survey 함수 실행
        # (conn과 clean_val 함수를 넘겨줘서 거기서도 쓸 수 있게 함)
        survey_step1.show_survey(conn, clean_val)

    # B-2. 메인 대시보드 페이지
    else:
        user = st.session_state.user
        
        # 상단 네비게이션 느낌
        st.markdown(f"### 🏫 {user.get('school', '학교 미정')} | {user['name']} 선생님")
        st.title("나의 성장 대시보드")
        st.markdown("---")

        # 최신 상태 업데이트 (시트 다시 읽기)
        try:
            df = get_data()
            curr_user = df[df['id'].apply(clean_val) == clean_val(user['id'])].iloc[0]
            s1_status = str(curr_user.get('step1_status', '미실시')).strip()
            st.session_state.user['step1_status'] = s1_status # 세션 동기화
        except:
            s1_status = str(user.get('step1_status', '미실시')).strip()

        is_done = (s1_status == "완료")

        # 카드 레이아웃
        col1, col2, col3 = st.columns(3)
        
        with col1:
            # 상태에 따른 스타일 결정
            bg_color = "#D1FAE5" if is_done else "#F3F4F6" # 초록 / 회색
            border_color = "#10B981" if is_done else "#E5E7EB"
            status_text = "✅ 실시완료" if is_done else "⚪ 미실시"
            btn_text = "결과 확인" if is_done else "진단 시작하기"
            btn_key = "btn_start_s1"
            
            # HTML 카드 렌더링
            st.markdown(f"""
                <div style="background-color: {bg_color}; padding: 30px; border-radius: 20px; 
                            border: 2px solid {border_color}; text-align: center; margin-bottom: 20px;">
                    <h4 style="color: #4B5563; margin:0;">STEP 01</h4>
                    <h2 style="color: #1F2937; margin: 10px 0;">역량 진단</h2>
                    <div style="font-weight: bold; font-size: 1.2rem; color: #059669;">{status_text}</div>
                </div>
            """, unsafe_allow_html=True)
            
            # 🔥 [중요] 페이지 전환 버튼 로직
            if st.button(btn_text, key=btn_key):
                st.session_state.page = "survey"  # 페이지 상태 변경
                st.rerun()                        # 화면 즉시 새로고침

        # (추가 기능 예시)
        with col2:
             st.markdown("""
                <div style="background-color: #F3F4F6; padding: 30px; border-radius: 20px; 
                            border: 2px solid #E5E7EB; text-align: center; margin-bottom: 20px; color: #9CA3AF;">
                    <h4>STEP 02</h4><h2>연수 추천</h2><div>🔒 잠김</div>
                </div>
            """, unsafe_allow_html=True)
             st.button("준비중", disabled=True, key="btn_s2")

        st.markdown("---")
        if st.button("로그아웃"):
            st.session_state.user = None
            st.session_state.page = "dashboard"
            st.rerun()
