import streamlit as st
import pandas as pd

def show_survey(conn, clean_val):
    # 1. 페이지 제목 및 안내
    st.title("📝 1단계: 사전 역량 진단")
    st.markdown("---")
    st.info("선생님의 현재 디지털 교육 역량을 진단합니다. 응답하신 내용은 연수 추천의 기초 자료로 활용됩니다.")

    # 2. 설문 문항 구성
    with st.form("survey_form"):
        st.subheader("📊 역량 자가진단")
        
        q1 = st.select_slider(
            "Q1. 디지털 도구(CBT, 에듀테크 등)를 수업에 활용하는 능력이 어느 정도라고 생각하시나요?",
            options=["매우 미흡", "미흡", "보통", "우수", "매우 우수"],
            value="보통"
        )
        
        q2 = st.radio(
            "Q2. 새로운 디지털 기술을 수업에 도입하는 것에 대해 어떻게 느끼시나요?",
            ["매우 긍정적", "긍정적", "보통", "부담스러움", "매우 부담스러움"]
        )

        st.divider()
        
        st.subheader("💡 희망 사항")
        q3_interest = st.multiselect(
            "Q3. 관심 있는 연수 분야를 모두 선택해 주세요.",
            ["AI 보조교사 활용", "디지털 콘텐츠 제작", "데이터 기반 학생 상담", "코딩 및 SW 교육"]
        )
        
        q4_comment = st.text_area("Q4. 플랫폼에 바라는 점이나 기타 의견을 자유롭게 적어주세요.")

        # 3. 버튼 레이아웃
        col1, col2 = st.columns(2)
        
        with col1:
            submit_btn = st.form_submit_button("✅ 진단 완료 및 제출")
        with col2:
            cancel_btn = st.form_submit_button("🏠 취소하고 돌아가기")

        # 4. 저장 로직
        if submit_btn:
            try:
                with st.spinner('데이터를 안전하게 저장하고 있습니다...'):
                    # 1. 시트 전체 데이터 읽기
                    df = conn.read(worksheet="users", ttl=0)
                    df.columns = [c.lower().strip() for c in df.columns]
                    
                    # 2. 현재 사용자 찾기 (ID 비교)
                    user_id = str(st.session_state.user['id']).strip()
                    # clean_val 함수를 이용해 정확한 행 인덱스 매칭
                    idx = df[df['id'].apply(clean_val) == user_id].index
                    
                    if not idx.empty:
                        # 3. 데이터 업데이트 (step1_status를 '완료'로 변경)
                        df.loc[idx, 'step1_status'] = "완료"
                        
                        # (선택사항) 설문 상세 결과도 다른 시트에 저장하고 싶다면 여기에 로직 추가 가능
                        
                        # 4. 구글 시트 업데이트 반영
                        conn.update(worksheet="users", data=df)
                        
                        # 5. 세션 상태 업데이트 (대시보드 즉시 반영용)
                        st.session_state.user['step1_status'] = "완료"
                        
                        st.balloons()
                        st.success("진단이 완료되었습니다! 잠시 후 대시보드로 이동합니다.")
                        
                        # 6. 대시보드로 페이지 전환
                        st.session_state.page = "dashboard"
                        st.rerun()
                    else:
                        st.error("사용자 정보를 찾을 수 없습니다. 다시 로그인해 주세요.")
            
            except Exception as e:
                st.error(f"저장 중 오류가 발생했습니다: {e}")

        if cancel_btn:
            st.session_state.page = "dashboard"
            st.rerun()