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
        min-height: 120px;
    }
    h1, h2, h3 { color: #5B21B6; }
    .stButton>button { background-color: #A78BFA; color: white; border-radius: 8px; width: 100%; }
    .status-alert { color: #EF4444; font-weight: bold; }
    .status-ok { color: #10B981; font-weight: bold; }
    </style>
""", unsafe_allow_html=True)

# 🔗 2. 구글 시트 연결
conn = st.connection("gsheets", type=GSheetsConnection)

# 🛠️ 데이터 클리닝 함수 (숫자/문자 일치 오류 방지)
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
if 'user' not in st.session_state: st.session_state.user = None
if 'page' not in st.session_state: st.session_state.page = "dashboard"

# --- UI 로직 ---
if st.session_state.user is None:
    # [로그인 화면]
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
                else: st.error("정보가 일치하지 않습니다.")

elif st.session_state.page == "survey":
    # 📝 4. 사전 역량 진단 페이지 (시트 업데이트 로직 포함)
    st.title("📝 사전 역량 진단")
    st.info("선생님의 현재 디지털 및 교육 역량을 진단합니다.")
    
    with st.form("survey_form"):
        q1 = st.select_slider("Q1. 수업 중 디지털 도구 활용 능력", options=["매우 미흡", "미흡", "보통", "우수", "매우 우수"])
        q2 = st.radio("Q2. 새로운 도구 도입에 대한 태도", ["매우 긍정적", "긍정적", "보통", "부담스러움"])
        q3_comment = st.text_area("Q3. 추가로 바라는 점")
        
        submit_col, cancel_col = st.columns(2)
        
        if submit_col.form_submit_button("✅ 진단 완료 및 제출"):
            try:
                # 1. 시트 데이터 다시 읽기
                df = conn.read(worksheet="users", ttl=0)
                df.columns = [c.lower().strip() for c in df.columns]
                
                # 2. 현재 로그인한 사용자의 행 찾아서 업데이트
                user_id = str(st.session_state.user['id']).strip()
                # 'id' 컬럼도 클리닝해서 비교
                idx = df[df['id'].apply(clean_val) == user_id].index
                
                if not idx.empty:
                    # 'step1_status' 컬럼을 '완료'로 변경
                    df.loc[idx, 'step1_status'] = "완료"
                    # 3. 구글 시트에 다시 쓰기 (전체 덮어쓰기 방식)
                    conn.update(worksheet="users", data=df)
                    
                    # 4. 세션 정보도 업데이트 (로그아웃 안 해도 즉시 반영되게)
                    st.session_state.user['step1_status'] = "완료"
                    
                    st.balloons()
                    st.success("데이터가 성공적으로 저장되었습니다!")
                    st.session_state.page = "dashboard"
                    st.rerun()
            except Exception as e:
                st.error(f"저장 중 오류가 발생했습니다: {e}")

        if cancel_col.form_submit_button("🏠 돌아가기"):
            st.session_state.page = "dashboard"
            st.rerun()

else:
    # 🏠 5. 메인 대시보드
    user = st.session_state.user
    with st.sidebar:
        st.title(f"🏫 {user.get('school', '학교')}")
        st.write(f"**{user['name']}** 선생님")
        if st.button("로그아웃"):
            st.session_state.user = None
            st.session_state.page = "dashboard"
            st.rerun()

    st.title(f"✨ {user['name']} 선생님, 반갑습니다!")
    
    # 상태 값 처리
    raw_s1 = user.get('step1_status')
    s1 = "미실시" if pd.isna(raw_s1) or str(raw_s1).strip() == "" or str(raw_s1).lower() == "nan" else str(raw_s1)
    s1_class = "status-alert" if s1 == "미실시" else "status-ok"

    st.subheader("📊 나의 성장 현황")
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.markdown(f'<div class="main-card"><p>1단계: 역량 진단</p><h3 class="{s1_class}">📝 {s1}</h3></div>', unsafe_allow_html=True)
        if st.button("사전 역량 진단하기" if s1 == "미실시" else "다시 진단하기"):
            st.session_state.page = "survey"
            st.rerun()
            
    with col2:
        st.markdown(f'<div class="main-card"><p>2단계: 연수 수강</p><h3>📖 {user.get("step2_status", "미완료")}</h3></div>', unsafe_allow_html=True)
        st.button("연수 목록 보기")
    
    # 3, 4단계 생략 (디자인 유지)
