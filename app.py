import streamlit as st
from gtts import gTTS
import base64
import io
import time

# 웹페이지 설정
st.set_page_config(page_title="아빠표 받아쓰기", page_icon="✏️")

# --- 함수 정의 ---
@st.cache_data(show_spinner=False)
def generate_audio_bytes(text):
    mp3_fp = io.BytesIO()
    # 목소리 안정성을 위해 기본 여성 톤 유지
    tts = gTTS(text=", " + text, lang='ko')
    tts.write_to_fp(mp3_fp)
    return mp3_fp.getvalue()

def play_audio(audio_bytes):
    b64 = base64.b64encode(audio_bytes).decode()
    # 밀리초 단위까지 정밀한 ID 생성
    unique_id = str(time.time()).replace('.', '')
    
    # 브라우저가 매번 '완전히 새로운 객체'로 인식하도록 랜덤성을 부여한 HTML
    html_code = f"""
    <div id="wrapper_{unique_id}" style="display:none;">
        <audio autoplay="true">
            <source src="data:audio/mp3;base64,{b64}" type="audio/mp3">
        </audio>
    </div>
    """
    # [개선] 별도의 컨테이너를 만들어 이전 오디오 엘리먼트를 확실히 밀어냅니다.
    st.components.v1.html(html_code, height=0)

# --- 세션 상태 초기화 ---
if 'step' not in st.session_state:
    st.session_state.step = 'SETUP'
if 'quiz_list' not in st.session_state:
    st.session_state.quiz_list = []
if 'current_idx' not in st.session_state:
    st.session_state.current_idx = 0
if 'last_played_idx' not in st.session_state:
    st.session_state.last_played_idx = -1

# --- 1단계: 문제 입력 화면 (SETUP) ---
if st.session_state.step == 'SETUP':
    st.title("✏️ 2학년 1반 전유하 받아쓰기 준비")
    st.write("공부할 문장들을 입력해 주세요.")
    
    input_text = st.text_area("문장 입력 (엔터로 구분)", 
                             placeholder="예:\n날씨가 맑아요.\n공책을 샀어요.",
                             height=200)
    
    if st.button("시험 시작하기 🚀"):
        lines = [line.strip() for line in input_text.split('\n') if line.strip()]
        if len(lines) > 0:
            st.session_state.quiz_list = lines
            st.session_state.current_idx = 0
            st.session_state.last_played_idx = -1
            st.session_state.step = 'EXAM'
            st.rerun()
        else:
            st.warning("최소 한 문장 이상 입력해 주세요!")

# --- 2단계: 시험 진행 화면 (EXAM) ---
elif st.session_state.step == 'EXAM':
    idx = st.session_state.current_idx
    total = len(st.session_state.quiz_list)
    current_sentence = st.session_state.quiz_list[idx]
    
    # 음성 데이터 준비
    audio_data = generate_audio_bytes(current_sentence)
    
    # [자동 재생] 인덱스가 바뀌면 무조건 재생
    if st.session_state.last_played_idx != idx:
        play_audio(audio_data)
        st.session_state.last_played_idx = idx

    st.title(f"✍️ 제 {idx + 1}번 문제")
    st.progress((idx + 1) / total)
    st.write("문장을 잘 듣고 종이에 적어보세요.")
    
    # 다시 들려주기
    if st.button("🔊 다시 들려주기"):
        play_audio(audio_data)
    
    st.divider()
    
    # --- [수정] 이전/다음 버튼 배치 ---
    col1, col2 = st.columns(2)
    
    with col1:
        # 1번 문제가 아닐 때만 '이전 문제' 버튼 표시
        if idx > 0:
            if st.button("⬅️ 이전 문제로"):
                st.session_state.current_idx -= 1
                # 인덱스가 줄어들면 다시 재생되도록 last_played_idx 초기화
                st.session_state.last_played_idx = -1 
                st.rerun()
    
    with col2:
        if idx < total - 1:
            if st.button("다음 문제로 ➡️"):
                st.session_state.current_idx += 1
                st.rerun()
        else:
            if st.button("시험 종료 및 결과 확인 🏁"):
                st.session_state.step = 'RESULT'
                st.rerun()

# --- 3단계: 결과 확인 화면 (RESULT) ---
elif st.session_state.step == 'RESULT':
    st.title("🎉 시험 끝! 정답을 확인해요")
    for i, q in enumerate(st.session_state.quiz_list):
        st.info(f"**{i+1}번:** {q}")
    
    if st.button("새로운 시험 준비하기 🔄"):
        st.session_state.step = 'SETUP'
        st.session_state.quiz_list = []
        st.session_state.last_played_idx = -1
        st.rerun()