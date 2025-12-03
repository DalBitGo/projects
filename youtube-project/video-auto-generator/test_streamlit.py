"""
Streamlit 기본 동작 테스트
"""
import streamlit as st

st.set_page_config(
    page_title="Test App",
    page_icon="🎬",
    layout="wide"
)

st.title("🎬 Streamlit 테스트")

# 파일 업로드 테스트
uploaded_file = st.file_uploader(
    "테스트 파일 업로드",
    type=['mp4', 'mov'],
    help="비디오 파일을 업로드하세요"
)

if uploaded_file:
    st.success(f"✓ 파일 업로드 성공: {uploaded_file.name}")
    st.info(f"크기: {uploaded_file.size / 1024 / 1024:.2f} MB")

# 설정 패널 테스트
with st.sidebar:
    st.header("⚙️ 설정")
    top_n = st.slider("Top N", 1, 10, 5)
    style = st.selectbox("스타일", ["Modern", "Neon", "Minimal"])

    st.write(f"선택: Top {top_n}, {style}")

# 3단 레이아웃 테스트
col1, col2, col3 = st.columns(3)

with col1:
    st.subheader("입력")
    st.write("파일 업로드 영역")

with col2:
    st.subheader("미리보기")
    st.write("프리뷰 영역")

with col3:
    st.subheader("출력")
    st.write("결과 영역")

# 진행률 테스트
if st.button("진행률 테스트"):
    import time

    progress_bar = st.progress(0)
    status_text = st.empty()

    for i in range(100):
        progress_bar.progress(i + 1)
        status_text.text(f"처리 중... {i+1}%")
        time.sleep(0.01)

    st.success("✅ 완료!")

st.write("---")
st.info("✅ Streamlit 기본 기능 정상 동작")
