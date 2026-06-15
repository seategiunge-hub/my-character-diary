import streamlit as st
import google.generativeai as genai
from PIL import Image
import io

# 1. ページ設定（画面を横いっぱいに広く使う設定）
st.set_page_config(
    page_title="マイキャラ日記アプリ",
    page_icon="✍️",
    layout="wide"
)

# APIキーの接続チェックとエラー対策
if "GEMINI_API_KEY" in st.secrets and st.secrets["GEMINI_API_KEY"] != "":
    try:
        genai.configure(api_key=st.secrets["GEMINI_API_KEY"])
    except Exception as e:
        st.error(f"APIキーの設定エラー: {e}")
else:
    st.error("【設定エラー】StreamlitのSecretsに 'GEMINI_API_KEY' が登録されていません。")

# タイトル
st.markdown("<h1 style='text-align: center; color: #444;'>✨ マイキャラ日記アプリ ✨</h1>", unsafe_allow_html=True)
st.write("---")

# セッション状態の初期化
if 'page_stage' not in st.session_state:
    st.session_state.page_stage = 1  # 1:キャラ作成, 2:日記画面
if 'char_image' not in st.session_state:
    st.session_state.char_image = None
if 'last_message' not in st.session_state:
    st.session_state.last_message = None
if 'current_partner_data' not in st.session_state:
    st.session_state.current_partner_data = {}

# 服装スタイル20種類の一覧（詳細な説明付き）
style_details = {
    "1. カジュアルパーカー": "シンプルでダボっとしたストリート系の可愛いスウェットパーカー姿",
    "2. 王道トラッド制服": "ブレザーにチェックスカート（またはスラックス）を合わせたお洒落な学生服姿",
    "3. クラシックロリータ": "フリルとレースが上品な、クラシカルで華やかなドレス姿",
    "4. サイバーパンクネオン": "ネオンに光るラインが入った、未来的でサイバーなハイテクジャケット姿",
    "5. 癒やし系ニット": "萌え袖気味のゆったりとした、温かみのあるオーバーサイズニットセーター姿",
    "6. ゴシックドレス": "黒を基調とした、退廃的で美しい薔薇があしらわれたゴシックドレス姿",
    "7. スタイリッシュスーツ": "細身で仕立ての良い、クールで知的なビジネススーツ姿",
    "8. モダンファンタジー軽装": "RPGの冒険者を思わせる、レザーの軽鎧とマントを羽織った旅人姿",
    "9. レトロモダン和服": "着物に現代風のブーツや小物を合わせた、お洒落な大正ロマン風の和装姿",
    "10. 夏色サマードレス": "爽やかな麦わら帽子に、風になびく白いノースリーブのワンピース姿",
    "11. ミリタリージャケット": "ミリタリー調の、ワッペンがついたクールでカッコいい迷彩アウター姿",
    "12. モード系モノトーン": "洗練された、黒と白の幾何学的なデザインのアシンメトリーな私服姿",
    "13. スポーティアクティブ": "キャップを被り、動きやすいトラックジャケットを着た活発なスタイル",
    "14. おやすみルームウェア": "モコモコした素材の、パステルカラーのパジャマを着たリラックス姿",
    "15. テクノ近未来ウェア": "白とシルバーを基調にした、宇宙
