import streamlit as st
from PIL import Image, ImageDraw, ImageFont
import os

# 1. ページ設定
st.set_page_config(
    page_title="マイキャラ日記アプリ",
    page_icon="✍️",
    layout="wide", # 横幅いっぱい
    initial_sidebar_state="expanded" # サイドバーを最初から開く
)

st.markdown("""
<style>
/* カスタムスタイル */
body {
    background-color: #f7f3e8; /* 温かみのあるパステル */
}
.stApp {
    background-color: transparent;
}
.main .block-container {
    padding-top: 2rem;
}
/* 生成されたキャラエリア */
#generated-char-section {
    background-color: #ffffff;
    border-radius: 15px;
    padding: 20px;
    box-shadow: 0 4px 10px rgba(0,0,0,0.05);
}
/* 日記入力エリア */
#diary-input-section {
    background-color: transparent;
    padding: 20px;
}
/* メッセージエリア */
#message-display-section {
    background-color: transparent;
    padding: 20px;
}
#message-display-section p {
    color: #888;
}
.character-label {
    text-align: center;
    color: #444;
    font-weight: bold;
    margin-top: 5px;
}
.stage-label {
    background-color: #fff;
    color: #333;
    font-size: 0.9em;
    padding: 2px 10px;
    border-radius: 10px;
    position: absolute;
    top: -12px;
    left: 20px;
    box-shadow: 0 2px 5px rgba(0,0,0,0.05);
    z-index: 10;
}
.stRadio > div {
    gap: 0.5rem;
}
</style>
""", unsafe_allow_html=True)

# 2. 初期化 (セッション状態)
if 'page_stage' not in st.session_state:
    st.session_state.page_stage = 1 # 1:キャラ生成, 2:日記
if 'generated_character_data' not in st.session_state:
    st.session_state.generated_character_data = None # 生成されたキャラ画像
if 'last_message' not in st.session_state:
    st.session_state.last_message = None # AIからのメッセージ
if 'selected_style_index' not in st.session_state:
    st.session_state.selected_style_index = 5 # デフォルトのスタイル6
if 'diary_input_text' not in st.session_state:
    st.session_state.diary_input_text = ""
if 'current_partner_data' not in st.session_state:
    st.session_state.current_partner_data = {} # 生成に使った設定

# タイトル
st.markdown("<h1 style='text-align: center; color: #444;'>✨ マイキャラ日記アプリ ✨</h1>", unsafe_allow_html=True)
st.markdown("<p style='text-align: center; color: #888;'>あなたのAIパートナー</p>", unsafe_allow_html=True)
st.write("---")

# ダミー画像生成関数 (本番用はImagenなどに置き換えてください)
def generate_character_image_dummy(style_name):
    # PILを使ってスタイル名とダミーのキャラを描画
    width, height = 500, 500
    image = Image.new('RGB', (width, height), color=(255, 255, 255))
    draw = ImageDraw.Draw(image)
    
    # 枠を描画
    draw.rectangle([(10, 10), (width-10, height-10)], outline=(220, 220, 220), width=2)
    
    # スタイル名
    font_size = 30
    # フォントが見つからない場合はデフォルト
    font_path = "Arial.ttf" if os.path.exists("Arial.ttf") else "/usr/share/fonts/truetype/liberation/LiberationSans-Regular.ttf"
    try:
        if os.path.exists(font_path):
            font = ImageFont.truetype(font_path, font_size)
        else:
            font = ImageFont.load_default()
    except Exception:
        font = ImageFont.load_default()

    text_w, text_h = draw.textsize(style_name, font=font)
    draw.text(((width - text_w) / 2, 20), style_name, fill=(68, 68, 68), font=font)
    
    # ダミーの顔を描画 (非常にシンプル)
    draw.ellipse([(150, 100), (350, 400)], outline=(100, 100, 100), width=3) # 顔
    draw.ellipse([(200, 180), (230, 230)], fill=(50, 100, 200)) # 目L
    draw.ellipse([(270, 180), (300, 230)], fill=(50, 100, 200)) # 目R
    draw.arc([(220, 250), (280, 320)], start=30, end=150, fill=(100, 100, 100), width=2) # 口

    # ダミーの「Imagen 3」ラベル
    model_text = "(生成モデル: Imagen 3)"
    font_small_size = 18
    try:
        if os.path.exists(font_path):
            font_small = ImageFont.truetype(font_path, font_small_size)
        else:
            font_small = ImageFont.load_default()
    except Exception:
        font_small = ImageFont.load_default()
    text_w_sm, text_h_sm = draw.textsize(model_text, font=font_small)
    draw.text(((width - text_w_sm) / 2, height - 30), model_text, fill=(150, 150, 150), font=font_small)

    return image

# ダミーAIメッセージ生成関数
def generate_ai_message(diary_text, reply_style, partner_data):
    if not diary_text: return "..."
    
    # 非常にシンプルなメッセージ生成
    partner_name = f"{partner_data.get('hair_color')}の{partner_data.get('hair')}"
    if reply_style == "優しく寄り添う":
        return f"きょうは {diary_text[:10]}... いろいろあったんだね。{partner_name}のわたしが、いつもあなたのそばにいるよ。おはなししてくれて、ありがとう。"
    elif reply_style == "全力で褒める":
        return f"わあ！きょうも{diary_text[:10]}... をがんばったんだね！すごすぎるよ！{partner_name}のわたしは、あなたのことがだいすきだよ！"
    elif reply_style == "客観的にアドバイス":
        return f"きょうの出来事{diary_text[:10]}... について、どう思った？{partner_name}として、あしたはこうしてみるのもいいかもしれないよ。"
    return "..."

# ==========================================
# レイアウトとロジック
# ==========================================
col1, col2 = st.columns([1, 1], gap="medium") # キャラ生成/表示エリアと日記/メッセージエリア

# --- 左カラム: キャラ生成と表示 ---
with col1:
    st.markdown('<div id="generated-char-section">', unsafe_allow_html=True)
    st.markdown('<div class="stage-label">1. あなたのAIパートナー (キャラクター生成完了)</div>', unsafe_allow_html=True)
    
    if st.session_state.page_stage == 1:
        # **ステージ1: キャラ生成**
        st.subheader("👤 キャラクターを作成")
        
        # フォーム
        with st.form(key="char_gen_form"):
            hair_colors = ["ピンク", "シルバー", "黒", "茶", "金", "青", "緑"]
            hair_color = st.selectbox("髪の色", hair_colors)
            
            hair_styles = ["ロングストレート", "ショートボブ", "ツインテール", "ポニーテール"]
            hair_style = st.selectbox("髪型", hair_styles)
            
            eye_colors = ["ブルー", "グリーン", "ブラウン", "パープル", "イエロー"]
            eye_color = st.selectbox("目の色", eye_colors)
            
            outfits = [
                "スタイル 6: ゴシックロリータ (黒/クリーム)",
                "スタイル 1: カジュアルパーカ (グレー/ピンク)",
                "スタイル 2: 制服 (ブレザー/ネイビー)",
                "スタイル 3: ワンピース (花柄/白)",
                "スタイル 4: アートスタイル (ペイント/カラフル)",
                "スタイル 5: サイバーパンク (ネオン/黒)"
            ]
            
            # スタイルの選択をドロップダウンに
            selected_outfit = st.selectbox("服装のスタイル", outfits, index=st.session_state.selected_style_index)
            
            # 決定ボタン
            submit_button = st.form_submit_button(label="決定")

        if submit_button:
            # 生成を実行
            with st.spinner("AIパートナーを生成しています..."):
                style_full_name = selected_outfit
                
                # 画像生成を実行 (ダミー)
                img = generate_character_image_dummy(style_full_name)
                
                # セッションを更新
                st.session_state.generated_character_data = img
                st.session_state.page_stage = 2 # ステージ2に切り替え
                st.session_state.last_message = None # メッセージをリセット
                st.session_state.diary_input_text = "" # 入力をリセット
                st.session_state.current_partner_data = {
                    "hair_color": hair_color,
                    "hair": hair_style,
                    "eye_color": eye_color,
                    "outfit": selected_outfit
                }
                st.experimental_rerun() # リロードして更新

    elif st.session_state.page_stage == 2 and st.session_state.generated_character_data:
        # **ステージ2: キャラ表示**
        st.markdown(f"**現在の設定:** {st.session_state.current_partner_data.get('hair_color')} / {st.session_state.current_partner_data.get('hair')} / {st.session_state.current_partner_data.get('eye_color')} / {st.session_state.current_partner_data.get('outfit')}")
        
        # 画像を表示
        st.image(st.session_state.generated_character_data, use_column_width=True)
        st.markdown(f'<div class="character-label">{st.session_state.current_partner_data.get("outfit")}</div>', unsafe_allow_html=True)
        
        # 作り直しボタン
        if st.button("作り直す", key="recreate_btn"):
            st.session_state.page_stage = 1
            st.session_state.generated_character_data = None
            st.experimental_rerun()
            
    st.markdown('</div>', unsafe_allow_html=True)

# --- 右カラム: メッセージ表示と日記入力 ---
with col2:
    if st.session_state.page_stage == 2:
        # **ステージ2: 日記とメッセージ**

        # メッセージ表示エリア
        st.markdown('<div id="message-display-section">', unsafe_allow_html=True)
        st.markdown('<div class="stage-label">2. パートナーからのメッセージ</div>', unsafe_allow_html=True)
        st.markdown("### ✍️ パートナーからのメッセージ")
        
        if st.session_state.last_message:
            st.chat_message("assistant").write(st.session_state.last_message)
        else:
            st.chat_message("assistant").write("...")
        st.markdown('</div>', unsafe_allow_html=True)

        # 日記入力エリア
        st.markdown('<div id="diary-input-section">', unsafe_allow_html=True)
        
        # 返答スタイルの選択
        st.markdown("<p style='color: #888;'>今日のキャラの返答スタイルを選んでね：</p>", unsafe_allow_html=True)
        reply_style = st.radio(
            "返答スタイル",
            ["優しく寄り添う", "全力で褒める", "客観的にアドバイス"],
            horizontal=True,
            label_visibility="collapsed"
        )
        
        # 日記テキスト入力
        diary_text = st.text_area("今日の出来事を入力してください", value=st.session_state.diary_input_text, height=150, placeholder="今日はステキな一日でした...")
        st.session_state.diary_input_text = diary_text # 入力を保持

        # 送信ボタン
        if st.button("日記を送信", key="send_diary_btn"):
            if not diary_text:
                st.warning("日記が空欄だよ！何か書いてみてね。")
            else:
                with st.spinner("AIパートナーが返信を考えています..."):
                    # AIメッセージを生成 (ダミー)
                    ai_msg = generate_ai_message(diary_text, reply_style, st.session_state.current_partner_data)
                    
                    # セッションを更新
                    st.session_state.last_message = ai_msg
                    st.session_state.diary_input_text = "" # 送信後は入力をクリア
                    st.experimental_rerun() # リロードして更新
                    
        st.markdown('</div>', unsafe_allow_html=True)

    else:
        # まだキャラがいない時
        st.markdown('<div id="message-display-section" style="opacity: 0.5;">', unsafe_allow_html=True)
        st.markdown('<div class="stage-label">2. パートナーからのメッセージ (日記入力待ち)</div>', unsafe_allow_html=True)
        st.markdown("### ✍️ パートナーからのメッセージ")
        st.markdown("<p>まずは左側でキャラクターを生成してください...</p>", unsafe_allow_html=True)
        st.markdown('</div>', unsafe_allow_html=True)
