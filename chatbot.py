import streamlit as st
import openai
import os
from dotenv import load_dotenv
import gpts_prompt
import sqlite3
from datetime import datetime, date

load_dotenv()

# --- OpenAI API KEY ---
openai.api_key = os.getenv("OPENAI_API_KEY")

# --- DB 초기화 및 유틸 함수 ---
def init_db():
    conn = sqlite3.connect("chat_records.db")
    c = conn.cursor()
    c.execute("CREATE TABLE IF NOT EXISTS records (ts TEXT, symptom TEXT, memo TEXT)")
    conn.commit()
    conn.close()

def migrate_db():
    conn = sqlite3.connect("chat_records.db")
    c = conn.cursor()
    c.execute("PRAGMA table_info(records)")
    columns = [row[1] for row in c.fetchall()]
    if "memo" not in columns:
        c.execute("ALTER TABLE records ADD COLUMN memo TEXT")
        conn.commit()
    conn.close()

def save_history(symptom: str, memo: str = ""):
    conn = sqlite3.connect("chat_records.db")
    c = conn.cursor()
    ts = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    c.execute("INSERT INTO records (ts, symptom, memo) VALUES (?, ?, ?)", (ts, symptom, memo))
    conn.commit()
    conn.close()
    st.success("기록이 저장되었습니다!")

def load_history(today_only=False):
    conn = sqlite3.connect("chat_records.db")
    c = conn.cursor()
    if today_only:
        today = date.today().strftime("%Y-%m-%d")
        c.execute("SELECT ts, symptom, memo FROM records WHERE ts LIKE ?", (f"{today}%",))
    else:
        c.execute("SELECT ts, symptom, memo FROM records ORDER BY ts DESC")
    rows = c.fetchall()
    conn.close()
    return rows

init_db()
migrate_db()

# --- 커스텀 CSS (배경사진, 카드, 버튼, 입력창, 애니메이션 등) ---
st.markdown('''
    <style>
    html, body, [class*="css"]  {
        font-family: 'Pretendard', 'Noto Sans KR', sans-serif;
        background: url('https://images.unsplash.com/photo-1506744038136-46273834b3fb?auto=format&fit=crop&w=1500&q=80') no-repeat center center fixed;
        background-size: cover;
        min-height: 100vh;
    }
    .main {
        background: rgba(255,255,255,0.85) !important;
        border-radius: 24px;
        box-shadow: 0 8px 32px #0002;
        padding: 2em 1.5em 2em 1.5em;
        margin: 2em auto 2em auto;
        max-width: 800px;
    }
    .stButton > button {
        background: linear-gradient(90deg, #ffb347 0%, #ffcc33 100%);
        color: #222;
        font-weight: bold;
        border-radius: 12px;
        padding: 0.7em 2.5em;
        font-size: 1.15em;
        box-shadow: 0 4px 16px #ffb34744, 0 1.5px 0 #fff8 inset;
        border: none;
        transition: 0.2s;
        margin: 0.5em 0 0.5em 0;
        letter-spacing: 0.5px;
        animation: popbtn 0.7s cubic-bezier(.68,-0.55,.27,1.55);
    }
    .stButton > button:hover {
        background: linear-gradient(90deg, #ffcc33 0%, #ffb347 100%);
        color: #d35400;
        box-shadow: 0 8px 32px #ffb34788;
        transform: scale(1.04);
    }
    @keyframes popbtn {
        0% { transform: scale(0.9); }
        80% { transform: scale(1.08); }
        100% { transform: scale(1); }
    }
    .chat-card {
        background: rgba(255,255,255,0.97);
        border-radius: 20px;
        box-shadow: 0 4px 24px #0001, 0 1.5px 0 #fff8 inset;
        padding: 1.3em 1.2em 1.1em 1.2em;
        margin-bottom: 1.3em;
        border: 2px solid #ffe0b2;
        text-align: left;
        animation: fadein 0.7s;
    }
    .emergency-card {
        background: #fff7e6;
        border-radius: 18px;
        box-shadow: 0 4px 16px #ffb34733;
        padding: 1.1em 1.2em 0.8em 1.2em;
        margin-bottom: 1.2em;
        border: 2.5px solid #ffb347;
        animation: fadein 0.7s;
    }
    @keyframes fadein {
        0% { opacity: 0; transform: translateY(20px); }
        100% { opacity: 1; transform: translateY(0); }
    }
    .stTextInput > div > input, .stTextArea textarea {
        background: #fffbe7;
        border: 2px solid #ffe082;
        border-radius: 10px;
        font-size: 1.08em;
        padding: 0.7em 1em;
        margin-bottom: 0.5em;
        box-shadow: 0 2px 8px #ffb34722;
        transition: border 0.2s;
    }
    .stTextInput > div > input:focus, .stTextArea textarea:focus {
        border: 2.5px solid #ffb347;
        outline: none;
    }
    .header-logo {
        display: flex; justify-content: center; align-items: center; margin-bottom: 2em;
        background: rgba(255,255,255,0.85); border-radius: 18px; box-shadow: 0 2px 12px #ffb34733;
        padding: 1.2em 1.5em 1.2em 1.5em;
        max-width: 600px; margin-left:auto; margin-right:auto;
    }
    .header-logo img {
        height: 70px; margin-right: 1.2em; filter: drop-shadow(0 2px 8px #ffb34788);
    }
    .header-logo h1 {
        font-size: 2.5em; font-weight: 900; color: #ff8800; letter-spacing: -1px; text-shadow: 0 2px 8px #fff8;
        margin-bottom: 0;
    }
    .sidebar-menu { margin-top: 2em; }
    .sidebar-menu a { display: block; margin-bottom: 1em; color: #ff8800; font-weight: bold; text-decoration: none; }
    .sidebar-menu a:hover { color: #d35400; }
    .save-ui-card {
        background: rgba(255,255,255,0.98);
        border: 2.5px solid #ffcc80;
        border-radius: 18px;
        box-shadow: 0 4px 24px #ffb34722;
        padding: 2em 1.5em 1.5em 1.5em;
        margin: 2em auto 1.5em auto;
        max-width: 520px;
        text-align: center;
        animation: fadein 0.7s;
    }
    .stRadio > div { justify-content: center !important; }
    .stTextInput, .stTextArea { margin-left:auto; margin-right:auto; max-width: 400px; }
    </style>
''', unsafe_allow_html=True)

# --- 헤더 로고 ---
st.markdown(
    '''<div class="header-logo">
        <img src="https://cdn-icons-png.flaticon.com/512/616/616408.png" alt="logo" />
        <h1>VetQuick Buddy</h1>
    </div>''', unsafe_allow_html=True
)

# --- 사이드바 메뉴 ---
menu = st.sidebar.radio("메뉴", ["챗 상담", "오늘 기록 보기", "이전 상담 내역", "설정"])

# 세션 상태 기본값 초기화
if 'messages' not in st.session_state:
    st.session_state['messages'] = [
        {"role": "system", "content": gpts_prompt.SYSTMEM_PROMPT}
    ]

if menu == "챗 상담":
    # 질문 입력 영역 (반응형 컬럼)
    def send_message():
        user_input = st.session_state['user_input']
        if user_input.strip():
            st.session_state['symptom'] = user_input
            st.session_state['messages'].append({"role": "user", "content": user_input})
            try:
                response = openai.chat.completions.create(
                    model="gpt-4o",
                    messages=st.session_state['messages'],
                    max_tokens=1024,
                    temperature=0.7
                )
                bot_reply = response.choices[0].message.content
                st.session_state['messages'].append({"role": "assistant", "content": bot_reply})
                st.rerun()
            except Exception as e:
                st.error(f"API 호출 오류: {e}")

    col1, col2 = st.columns([5,1])
    with col1:
        user_input = st.text_input(
            "어떤 증상이세요?",
            key="user_input",
            on_change=send_message
        )
    with col2:
        send = st.button("전송", use_container_width=True)
        if send:
            send_message()

    # 증상 세션 상태 저장
    if 'symptom' not in st.session_state:
        st.session_state['symptom'] = ''
    if 'step' not in st.session_state:
        st.session_state['step'] = 'chat'
    if send and user_input.strip():
        st.session_state['symptom'] = user_input
        st.session_state['messages'].append({"role": "user", "content": user_input})
        try:
            response = openai.chat.completions.create(
                model="gpt-4o",
                messages=st.session_state['messages'],
                max_tokens=1024,
                temperature=0.7
            )
            bot_reply = response.choices[0].message.content
            st.session_state['messages'].append({"role": "assistant", "content": bot_reply})
            st.rerun()
        except Exception as e:
            st.error(f"API 호출 오류: {e}")

    def render_result(content, last_result_idx, causes=None, emergency_action=None, urgency_icon='✅'):
        if 'save_done' in st.session_state:
            del st.session_state['save_done']
        st.markdown(f'''
            <div style="background:#FFF8E1; border:1px solid #FFE082; border-radius:10px; padding:20px; margin:20px auto; max-width:700px; display:flex; flex-direction:column; gap:10px;">
                <div style="font-weight:bold; font-size:1.1em; display:flex; align-items:center; gap:0.5em;">
                    <span style="font-size:1.3em;">{urgency_icon}</span> 집에서 경과 관찰해도 괜찮아요
                </div>
                <div>
                    <ol style="margin:0 0 0 1.2em; padding:0;">
                        {''.join([f'<li>{c}</li>' for c in (causes or ['원인1', '원인2', '원인3'])])}
                    </ol>
                </div>
                <div style="background:#FFFDE7; border-radius:7px; padding:0.8em 1em; border:1px solid #FFE082;">
                    <b>응급 조치 카드:</b><br>{emergency_action or '응급 시 바로 동물병원에 연락하세요.'}
                </div>
            </div>
        ''', unsafe_allow_html=True)
        # --- 저장 카드 UI ---
        save_choice = st.radio("저장하시겠습니까?", ["예", "아니요"], key=f"save_choice_{last_result_idx}", horizontal=True)
        if st.button("저장", key=f"save_choice_btn_{last_result_idx}", use_container_width=True):
            if save_choice == "예":
                st.session_state[f"save_choice_confirmed_{last_result_idx}"] = True
            elif save_choice == "아니요":
                # 관련 세션 상태 모두 삭제
                for k in [f'save_mode_{last_result_idx}',f'save_memo_{last_result_idx}',f'save_choice_{last_result_idx}',f'save_symptom_input_{last_result_idx}',f'save_choice_confirmed_{last_result_idx}']:
                    if k in st.session_state:
                        del st.session_state[k]
                st.session_state['step'] = 'chat'
                st.info("저장이 취소되었습니다. 챗봇을 계속 이용하실 수 있습니다.")
                st.rerun()
                return
        # 예를 선택하고 저장 버튼을 눌렀을 때만 다음 단계 노출
        if st.session_state.get(f"save_choice_confirmed_{last_result_idx}"):
            st.markdown("<div style='text-align:center;font-weight:600;color:#ff8800; margin-bottom:0.7em;'>저장 방법을 선택하세요</div>", unsafe_allow_html=True)
            save_mode = st.radio(
                label="",
                options=["증상 입력", "간단 메모 추가"],
                key=f"save_mode_{last_result_idx}",
                horizontal=True,
                help="상담 기록을 직접 입력하거나, 메모를 추가해 저장할 수 있습니다."
            )
            st.markdown("<div style='height:0.5em'></div>", unsafe_allow_html=True)
            if save_mode == "증상 입력":
                st.markdown('<div style="color:#ff8800; font-weight:500; text-align:center; margin-bottom:0.5em;">저장할 증상을 입력해 주세요.</div>', unsafe_allow_html=True)
                symptom_input = st.text_input("증상 입력", key=f"save_symptom_input_{last_result_idx}")
                if st.button("📝 증상 저장", key=f"symptom_save_btn_{last_result_idx}", use_container_width=True):
                    save_history(symptom_input)
                    st.success(f"증상 '{symptom_input}' 이(가) 저장되었습니다!", icon="✅")
                    st.session_state['save_done'] = True
                    for k in [f'save_mode_{last_result_idx}',f'save_memo_{last_result_idx}',f'save_choice_{last_result_idx}',f'save_symptom_input_{last_result_idx}',f'save_choice_confirmed_{last_result_idx}']:
                        if k in st.session_state:
                            del st.session_state[k]
                    st.session_state['step'] = 'chat'
                    st.rerun()
            elif save_mode == "간단 메모 추가":
                st.markdown('<div style="color:#ff8800; font-weight:500; text-align:center; margin-bottom:0.5em;">메모를 입력해 주세요.</div>', unsafe_allow_html=True)
                memo = st.text_area("메모 입력", key=f"save_memo_{last_result_idx}", height=90)
                if st.button("💾 메모 저장", key=f"memo_save_btn_{last_result_idx}", use_container_width=True):
                    save_history(st.session_state.get('symptom',''), memo)
                    st.success(f"메모가 저장되었습니다!", icon="✅")
                    st.session_state['save_done'] = True
                    for k in [f'save_mode_{last_result_idx}',f'save_memo_{last_result_idx}',f'save_choice_{last_result_idx}',f'save_symptom_input_{last_result_idx}',f'save_choice_confirmed_{last_result_idx}']:
                        if k in st.session_state:
                            del st.session_state[k]
                    st.session_state['step'] = 'chat'
                    st.rerun()
        # 아무것도 선택하지 않은 상태에서는 다음 단계 노출 X

    # --- 대화 내용 출력 및 Save 버튼 노출 제어 ---
    result_ready = False
    last_result_idx = None
    for idx, msg in enumerate(st.session_state['messages']):
        if msg['role'] == 'system':
            continue
        if msg['role'] == 'user':
            st.markdown(f'<div class="chat-card"><b>🙋‍♂️ 나:</b> {msg["content"]}</div>', unsafe_allow_html=True)
        else:
            if any(x in msg['content'] for x in ['고위험', '중간', '낮음', '즉시', '병원', '탈수', '응급']):
                render_result(
                    msg['content'],
                    idx,
                    causes=['감기', '스트레스', '소화불량'],
                    emergency_action='증상이 악화되면 즉시 병원 방문!'
                )
                result_ready = True
                last_result_idx = idx
            elif 'tel:' in msg['content']:
                render_result(
                    msg['content'] + '<br><a class="phone-btn" href="tel:+821012345678">24시 동물병원 전화걸기</a>',
                    idx,
                    causes=['감기', '스트레스', '소화불량'],
                    emergency_action='증상이 악화되면 즉시 병원 방문!'
                )
                result_ready = True
                last_result_idx = idx
            else:
                st.markdown(f'<div class="chat-card"><b>🤖 챗봇:</b> {msg["content"]}</div>', unsafe_allow_html=True)

elif menu == "오늘 기록 보기":
    st.header("오늘 기록 보기")
    records = load_history(today_only=True)
    if records:
        for ts, symptom, memo in records:
            if memo:
                st.write(f"- {ts}  {symptom}\n메모: {memo}")
            else:
                st.write(f"- {ts}  {symptom}")
    else:
        st.info("오늘 기록이 없습니다.")

elif menu == "이전 상담 내역":
    st.header("이전 상담 내역")
    records = load_history(today_only=False)
    if records:
        for ts, symptom, memo in records:
            if memo:
                st.write(f"- {ts}  {symptom}\n메모: {memo}")
            else:
                st.write(f"- {ts}  {symptom}")
    else:
        st.info("상담 내역이 없습니다.")

elif menu == "설정":
    st.header("설정")
    st.write("설정 기능은 준비 중입니다.")
