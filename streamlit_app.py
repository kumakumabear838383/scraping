import streamlit as st
import requests
from bs4 import BeautifulSoup
import pandas as pd
import time
import random
from urllib.parse import urljoin, urlparse
import io
from datetime import datetime

# Page configuration
st.set_page_config(
    page_title="安全なWebスクレイピングツール",
    page_icon="🕷️",
    layout="wide"
)

# Custom CSS
st.markdown("""
<style>
.main-header {
    font-size: 2.5rem;
    color: #1f77b4;
    text-align: center;
    margin-bottom: 2rem;
}
.section-header {
    font-size: 1.5rem;
    color: #ff7f0e;
    margin-top: 2rem;
    margin-bottom: 1rem;
}
.info-box {
    background-color: #f0f2f6;
    padding: 1rem;
    border-radius: 0.5rem;
    border-left: 4px solid #1f77b4;
    margin: 1rem 0;
}
.warning-box {
    background-color: #fff3cd;
    padding: 1rem;
    border-radius: 0.5rem;
    border-left: 4px solid #ffc107;
    margin: 1rem 0;
}
.success-box {
    background-color: #d4edda;
    padding: 1rem;
    border-radius: 0.5rem;
    border-left: 4px solid #28a745;
    margin: 1rem 0;
}
</style>
""", unsafe_allow_html=True)

# Title
st.markdown('<h1 class="main-header">🕷️ 安全なWebスクレイピングツール</h1>', unsafe_allow_html=True)

# Warning message
st.markdown("""
<div class="warning-box">
<strong>⚠️ 重要な注意事項</strong><br>
このツールを使用する前に、対象サイトの利用規約とrobots.txtを必ず確認してください。
適切な間隔でのアクセスを心がけ、サーバーに負荷をかけないよう注意してください。
</div>
""", unsafe_allow_html=True)

# Sidebar for settings
st.sidebar.markdown('<h2 class="section-header">⚙️ 設定</h2>', unsafe_allow_html=True)

# Input fields
base_url = st.sidebar.text_input(
    "ベースURL",
    value="https://www.walkerplus.com/spot_list/ar0700/sg0107/",
    help="スクレイピング対象のベースURLを入力してください"
)

css_selector = st.sidebar.text_input(
    "CSSセレクタ",
    value="a.m-mainlist-item__ttl",
    help="取得したい要素のCSSセレクタを入力してください"
)

# Page range
col1, col2 = st.sidebar.columns(2)
with col1:
    start_page = st.number_input("開始ページ", min_value=1, value=1)
with col2:
    end_page = st.number_input("終了ページ", min_value=1, value=5)

# Advanced settings
st.sidebar.markdown("### 詳細設定")
min_delay = st.sidebar.slider("最小待機時間（秒）", 1, 10, 1)
max_delay = st.sidebar.slider("最大待機時間（秒）", 1, 10, 5)
timeout = st.sidebar.slider("タイムアウト（秒）", 5, 30, 10)

# CSS Selector Guide
st.markdown('<h2 class="section-header">📖 CSSセレクタの取得方法</h2>', unsafe_allow_html=True)

with st.expander("CSSセレクタの取得手順", expanded=False):
    st.markdown("""
    ### 手順：
    1. **対象サイトを開く** - ブラウザで対象のWebページを開きます
    2. **要素を右クリック** - 取得したいテキストやリンクを右クリックします
    3. **検証を選択** - コンテキストメニューから「検証」または「要素を調査」を選択
    4. **要素をコピー** - 開発者ツールで要素を右クリック → Copy → Copy selector
    5. **セレクタを貼り付け** - 上記の入力フィールドに貼り付けます

    ### よく使用されるセレクタの例：
    - `a` - すべてのリンク
    - `.class-name` - 特定のクラスを持つ要素
    - `#id-name` - 特定のIDを持つ要素
    - `h1, h2, h3` - 見出し要素
    - `p` - 段落要素
    - `div.container a` - containerクラス内のリンク
    """)

# Function to scrape data
def scrape_data(base_url, css_selector, start_page, end_page, min_delay, max_delay, timeout):
    """
    Webスクレイピングを実行する関数
    """
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
    }

    results = []
    progress_bar = st.progress(0)
    status_text = st.empty()

    total_pages = end_page - start_page + 1

    for page_num in range(start_page, end_page + 1):
        try:
            # Construct URL
            if '{}' in base_url:
                url = base_url.format(page_num)
            elif base_url.endswith('/'):
                url = f"{base_url}?page={page_num}"
            else:
                url = f"{base_url}&page={page_num}"

            status_text.text(f"ページ {page_num} を処理中... URL: {url}")

            # Make request
            response = requests.get(url, headers=headers, timeout=timeout)
            response.raise_for_status()

            # Parse HTML
            soup = BeautifulSoup(response.content, 'html.parser')
            elements = soup.select(css_selector)

            # Extract data
            page_results = []
            for i, element in enumerate(elements):
                data = {
                    'page': page_num,
                    'index': i + 1,
                    'text': element.get_text(strip=True),
                    'href': element.get('href', ''),
                    'full_url': urljoin(url, element.get('href', '')) if element.get('href') else '',
                    'scraped_at': datetime.now().strftime('%Y-%m-%d %H:%M:%S')
                }
                page_results.append(data)

            results.extend(page_results)

            # Update progress
            progress = (page_num - start_page + 1) / total_pages
            progress_bar.progress(progress)

            status_text.text(f"ページ {page_num} 完了 - {len(page_results)} 件のデータを取得")

            # Random delay
            if page_num < end_page:  # Don't delay after the last page
                delay = random.uniform(min_delay, max_delay)
                time.sleep(delay)

        except requests.exceptions.RequestException as e:
            st.error(f"ページ {page_num} でエラーが発生しました: {str(e)}")
            continue
        except Exception as e:
            st.error(f"予期しないエラーが発生しました (ページ {page_num}): {str(e)}")
            continue

    progress_bar.progress(1.0)
    status_text.text(f"スクレイピング完了! 合計 {len(results)} 件のデータを取得しました。")

    return results

# Main content area
st.markdown('<h2 class="section-header">🚀 スクレイピング実行</h2>', unsafe_allow_html=True)

# Validation
if st.button("🕷️ スクレイピング開始", type="primary", use_container_width=True):
    if not base_url:
        st.error("ベースURLを入力してください。")
    elif not css_selector:
        st.error("CSSセレクタを入力してください。")
    elif start_page > end_page:
        st.error("開始ページは終了ページ以下である必要があります。")
    else:
        with st.spinner("スクレイピングを実行中..."):
            results = scrape_data(base_url, css_selector, start_page, end_page, min_delay, max_delay, timeout)

        if results:
            st.success(f"✅ スクレイピング完了! {len(results)} 件のデータを取得しました。")

            # Store results in session state
            st.session_state.scraping_results = results
            st.session_state.scraping_timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')

# Display results if available
if 'scraping_results' in st.session_state and st.session_state.scraping_results:
    st.markdown('<h2 class="section-header">📊 取得データ</h2>', unsafe_allow_html=True)

    results = st.session_state.scraping_results
    df = pd.DataFrame(results)

    # Data preview
    st.markdown("### データプレビュー")
    st.dataframe(df, use_container_width=True)

    # Statistics
    col1, col2, col3, col4 = st.columns(4)
    with col1:
        st.metric("総データ数", len(results))
    with col2:
        st.metric("ページ数", df['page'].nunique())
    with col3:
        st.metric("リンク数", df[df['href'] != ''].shape[0])
    with col4:
        st.metric("テキストのみ", df[df['href'] == ''].shape[0])

    # Download section
    st.markdown('<h2 class="section-header">💾 ダウンロード</h2>', unsafe_allow_html=True)

    timestamp = st.session_state.scraping_timestamp

    col1, col2, col3 = st.columns(3)

    with col1:
        # Excel download
        excel_buffer = io.BytesIO()
        df.to_excel(excel_buffer, index=False, engine='openpyxl')
        excel_buffer.seek(0)

        st.download_button(
            label="📊 Excelファイルをダウンロード",
            data=excel_buffer.getvalue(),
            file_name=f"scraping_results_{timestamp}.xlsx",
            mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
            use_container_width=True
        )

    with col2:
        # CSV download
        csv_buffer = io.StringIO()
        df.to_csv(csv_buffer, index=False, encoding='utf-8-sig')

        st.download_button(
            label="📄 CSVファイルをダウンロード",
            data=csv_buffer.getvalue(),
            file_name=f"scraping_results_{timestamp}.csv",
            mime="text/csv",
            use_container_width=True
        )

    with col3:
        # Text download
        text_content = "\n".join([f"{item['text']} - {item['full_url']}" for item in results if item['text']])

        st.download_button(
            label="📝 テキストファイルをダウンロード",
            data=text_content,
            file_name=f"scraping_results_{timestamp}.txt",
            mime="text/plain",
            use_container_width=True
        )

# Footer
st.markdown("---")
st.markdown("""
<div class="info-box">
<strong>💡 使用上の注意</strong><br>
• このツールは教育・研究目的での使用を想定しています<br>
• 商用利用の場合は、対象サイトの利用規約を必ず確認してください<br>
• 過度なアクセスはサーバーに負荷をかける可能性があります<br>
• robots.txtファイルの内容を尊重してください
</div>
""", unsafe_allow_html=True)
