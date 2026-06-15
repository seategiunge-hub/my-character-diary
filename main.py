import streamlit as st
import google.generativeai as genai

# 画面設定（必ず最初に行う）
st.set_page_config(
    page_title="マイキャラ日記アプリ",
    page_icon="✍️",
    layout="centered"
)

# Gemini APIの接続チェック
if "GEMINI_API_KEY" in st.secrets and st.secrets["GEMINI_API_KEY"] != "":
    try:
        genai.configure(api_key=st.secrets["GEMINI_API_KEY"])
    except Exception as e:
        st.error(f"APIキーの設定エラー: {e}")
else:
    st.error("【設定エラー】StreamlitのSecretsに 'GEMINI_API_KEY' が登録されていません。")

st.title("✨ マイキャラ日記アプリ ✨")

# セッション状態の初期化
if "char_created" not in st.session_state:
    st.session_state.char_created = False
if "char_image_url" not in st.session_state:
    st.session_state.char_image_url = None

# ==========================================
# 1. キャラクター作成画面
# ==========================================
if not st.session_state.char_created:

    st.subheader("👤 キャラクターを作ろう")

    gender = st.radio("性別・タイプ", ["女性型", "男性型", "中性的"])
    
    # 髪型20種類
    hair_styles = [
        "ショートボブ", "ロングストレート", "ツインテール", "ポニーテール", "ツープロック",
        "ウルフカット", "マッシュ", "ベリーショート", "ミディアムウェーブ", "ハーフアップ",
        "お団子ヘア", "三つ編み", "姫カット", "アシンメトリー", "パーマスタイル",
        "センター分け", "ボブカット", "サイドポニー", "ギブソンタック", "リーゼント風ショート"
    ]
    hair = st.selectbox("髪型 (全20種)", hair_styles)
    
    # 髪色10種類
    hair_colors = ["黒髪", "茶髪", "金髪", "銀髪", "白髪", "ピンク髪", "青髪", "緑髪", "紫髪", "赤髪"]
    hair_color = st.selectbox("髪色 (全10種)", hair_colors)
    
    eyes = st.selectbox("目の形", ["たれ目", "つり目", "ぱっちりジト目", "切れ長・クール"])
    clothes = st.selectbox("服の種類", [f"スタイル {i}" for i in range(1, 21)])

    if st.button("このキャラクターで決定！"):
        with st.spinner("キャラクターイラストを生成中..."):
            try:
                st.session_state.character = {
                    "gender": gender,
                    "hair": hair,
                    "hair_color": hair_color,
                    "eyes": eyes,
                    "clothes": clothes
                }
                
                # アニメ風キャラクターの画像生成プロンプト
                image_prompt = f"Cute anime style character icon, {gender}, {hair_color} {hair}, {eyes} eyes, wearing {clothes}, high quality, standard professional anime illustration, solo, looking at viewer, detailed."
                
                # Imagenモデルを使って画像生成
                img_model = genai.GenerativeModel("imagen-3.0-generate-002")
                result = img_model.generate_images(
                    prompt=image_prompt,
                    number_of_images=1,
                    aspect_ratio="1:1"
                )
                
                # 生成された画像をセッションに保存
                if result.generated_images:
                    st.session_state.char_image_url = result.generated_images[0].image
                
                st.session_state.char_created = True
                st.rerun()
                
            except Exception as e:
                st.error(f"画像生成中にエラーが発生しました（キャラクター作成は続行します）: {e}")
                st.session_state.char_created = True
                st.rerun()

# ==========================================
# 2. 日記画面（メイン画面）
# ==========================================
else:
    char = st.session_state.character

    # キャラクター情報の表示
    st.success(
        f"現在のパートナー: {char['gender']} / {char['hair_color']}{char['hair']} / {char['eyes']} / {char['clothes']}"
    )

    # 生成されたキャラクター画像の表示
    if st.session_state.char_image_url:
        st.image(st.session_state.char_image_url, caption="あなたのAIパートナー", width=250)

    if st.button("キャラクターを作り直す"):
        st.session_state.char_created = False
        st.session_state.char_image_url = None
        st.rerun()

    st.divider()

    st.subheader("✍️ 今日の日記")
    
    # 3つの返答スタイルから選択機能
    reply_style = st.radio(
        "今日のキャラの返答スタイルを選んでね：",
        ["優しく寄り添う（共感・癒やし）", "全力で褒める（肯定・モチベUP）", "客観的にアドバイス（冷静・前向き）"]
    )

    diary_text = st.text_area("今日、どんなことがあった？キャラに話しかけてみよう。")

    if st.button("日記を送信する"):
        if not diary_text.strip():
            st.warning("日記が空欄だよ！何か書いてみてね。")
        else:
            with st.spinner("キャラクターが返信を考えています..."):
                try:
                    # AIへの指示書（プロンプト）
                    prompt = f"""
                    あなたはユーザー専属のAIパートナーです。
                    
                    【あなたの外見設定】
                    性別タイプ: {char['gender']}
                    髪型・髪色: {char['hair_color']}の{char['hair']}
                    目の形: {char['eyes']}
                    服装: {char['clothes']}
                    
                    【今回の返答ルール】
                    あなたはユーザーに対して、指定された以下のスタイルで150文字程度で返答してください。
                    指定スタイル: 【{reply_style}】
                    
                    【今日の日記】
                    {diary_text}
                    """
                    
                    # テキスト生成モデルを呼び出し
                    model = genai.GenerativeModel('gemini-1.5-flash')
                    response = model.generate_content(prompt)
                    
                    # 返答を表示
                    if response and response.text:
                        st.write("---")
                        st.chat_message("assistant").write(response.text)
                    else:
                        st.error("AIからの返答をうまく受信できませんでした。もう一度送信してください。")
                        
                except Exception as e:
                    st.error(f"エラーが発生しました。日記の文章を少し変えるか、もう一度お試しください。エラー詳細: {e}")
