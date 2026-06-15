import streamlit as st
import google.generativeai as genai

# Gemini APIの設定
if "GEMINI_API_KEY" in st.secrets:
    genai.configure(api_key=st.secrets["GEMINI_API_KEY"])
else:
    st.error("GitHubのSecretsに GEMINI_API_KEY が設定されていません。")

# 画面設定
st.set_page_config(
    page_title="キャラ日記アプリ",
    page_icon="✍️",
    layout="centered"
)

st.title("✨ マイキャラ日記アプリ ✨")

# キャラ作成状態
if "char_created" not in st.session_state:
    st.session_state.char_created = False

# キャラ作成
if not st.session_state.char_created:
    st.subheader("👤 キャラクターを作ろう")
    gender = st.radio("性別", ["女性型", "男性型", "中性的"])
    hair = st.selectbox("髪型", ["ショート", "ロング", "ボブ", "ツーブロック"])
    eyes = st.selectbox("目の形", ["たれ目", "つり目", "ぱっちり", "切れ長"])
    clothes = st.selectbox("服の種類", [f"スタイル {i}" for i in range(1, 21)])

    if st.button("このキャラクターで決定！"):
        st.session_state.character = {
            "gender": gender, "hair": hair, "eyes": eyes, "clothes": clothes
        }
        st.session_state.char_created = True
        st.rerun()

# 日記画面
else:
    char = st.session_state.character
    st.success(f"現在のパートナー: {char['gender']} / {char['hair']} / {char['eyes']} / {char['clothes']}")

    if st.button("キャラクターを作り直す"):
        st.session_state.char_created = False
        st.rerun()

    st.divider()
    st.subheader("✍️ 今日の日記")
    diary_text = st.text_area("今日、どんなことがあった？キャラに話しかけてみよう。")

    if st.button("日記を送信する"):
        if not diary_text:
            st.warning("日記が空欄だよ！")
        else:
            with st.spinner("キャラクターが返信を考えています..."):
                try:
                    prompt = f"""
                    あなたはユーザー専属のAIパートナーです。
                    【あなたの設定】性別: {char['gender']}, 髪型: {char['hair']}, 目の形: {char['eyes']}, 服装: {char['clothes']}
                    ユーザーの日記に対して、優しく共感しながら150文字程度で返答してください。
                    【今日の日記】\n{diary_text}
                    """
                    model = genai.GenerativeModel('gemini-1.5-flash')
                    response = model.generate_content(prompt)
                    st.chat_message("assistant").write(response.text)
                except Exception as e:
                    st.error(f"エラーが発生しました: {e}")
