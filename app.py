import streamlit as st
import gspread
from oauth2client.service_account import ServiceAccountCredentials
import pandas as pd
from datetime import datetime

# 1. 페이지 설정
st.set_page_config(page_title="재고 관리 시스템", layout="wide")
st.title("📊 실시간 재고/데이터 관리 앱")

# 2. 구글 시트 연결 설정 (Secrets 사용)
# 캐시를 사용하여 API 호출을 줄입니다.
@st.cache_resource
def init_connection():
    scope = ["https://spreadsheets.google.com/feeds", "https://www.googleapis.com/auth/drive"]
    creds = ServiceAccountCredentials.from_json_keyfile_dict(st.secrets["gcp_service_account"], scope)
    client = gspread.authorize(creds)
    return client

try:
    client = init_connection()
    # 여기에 구글 시트 이름을 정확히 적어주세요!
    SPREADSHEET_NAME = "경영진보고" 
    sh = client.open(SPREADSHEET_NAME)
    worksheet = sh.sheet1 # 첫 번째 시트 사용
except Exception as e:
    st.error(f"구글 시트 연결 오류: {e}")
    st.stop()

# 3. 데이터 읽기 함수
def load_data():
    data = worksheet.get_all_records()
    return pd.DataFrame(data)

# 4. 앱 레이아웃 (탭 구성)
tab1, tab2, tab3 = st.tabs(["📝 기록하기", "📋 조회하기", "🔍 검색하기"])

# --- 탭 1: 데이터 쓰기 (입력) ---
with tab1:
    st.header("데이터 입력")
    with st.form("entry_form"):
        col1, col2 = st.columns(2)
        with col1:
            name = st.text_input("품목명/이름")
        with col2:
            amount = st.number_input("수량/금액", min_value=0)
        
        category = st.selectbox("카테고리", ["입고", "출고", "기타"])
        note = st.text_area("비고")
        
        submitted = st.form_submit_button("저장하기")
        
        if submitted:
            if not name:
                st.warning("품목명을 입력해주세요.")
            else:
                timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                # 구글 시트에 행 추가
                worksheet.append_row([timestamp, name, amount, category, note])
                st.success("저장되었습니다!")
                # 데이터 갱신을 위해 캐시 삭제
                st.cache_data.clear()

# --- 탭 2: 데이터 조회 (읽기) ---
with tab2:
    st.header("전체 데이터 조회")
    if st.button("새로고침"):
        st.cache_data.clear()
        
    df = load_data()
    if not df.empty:
        st.dataframe(df, use_container_width=True)
    else:
        st.info("데이터가 없습니다.")

# --- 탭 3: 데이터 검색 ---
with tab3:
    st.header("데이터 검색")
    search_term = st.text_input("검색어 입력 (품목명)")
    
    if search_term:
        df = load_data()
        # 품목명에 검색어가 포함된 행만 필터링
        result = df[df["품목명/이름"].astype(str).str.contains(search_term, case=False)]
        
        if not result.empty:
            st.success(f"{len(result)}건이 검색되었습니다.")
            st.dataframe(result, use_container_width=True)
        else:
            st.warning("검색 결과가 없습니다.")
