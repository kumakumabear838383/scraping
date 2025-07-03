import streamlit as st
import requests
import pandas as pd
from datetime import datetime
import time

# BeautifulSoupのインポート（エラーハンドリング付き）
try:
    from bs4 import BeautifulSoup
    BS4_AVAILABLE = True
    st.success("✅ BeautifulSoup successfully imported")
except ImportError as e:
    st.error(f"❌ BeautifulSoup import failed: {e}")
    st.error("Please check requirements.txt and ensure beautifulsoup4 is installed")
    BS4_AVAILABLE = False
    # フォールバック: 基本的なHTMLパースのみ
    BeautifulSoup = None

# アプリケーションの設定
st.set_page_config(
    page_title="Web Scraping Tool",
    page_icon="🔍",
    layout="wide"
)

def safe_request(url, timeout=10):
    """安全なHTTPリクエスト"""
    try:
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
        }
        response = requests.get(url, headers=headers, timeout=timeout)
        response.raise_for_status()
        return response
    except requests.exceptions.RequestException as e:
        st.error(f"Request failed: {e}")
        return None

def parse_html_content(html_content):
    """HTMLコンテンツの解析"""
    if not BS4_AVAILABLE:
        st.warning("BeautifulSoup not available. Using basic text extraction.")
        return {"title": "N/A", "text": html_content[:500] + "..."}

    try:
        soup = BeautifulSoup(html_content, 'html.parser')

        # タイトルの取得
        title = soup.find('title')
        title_text = title.get_text().strip() if title else "No title found"

        # メインコンテンツの取得
        # 一般的なコンテンツタグを優先順位で検索
        content_selectors = [
            'main', 'article', '.content', '#content', 
            '.main-content', '.post-content', 'body'
        ]

        main_content = ""
        for selector in content_selectors:
            content_elem = soup.select_one(selector)
            if content_elem:
                main_content = content_elem.get_text(strip=True)
                break

        if not main_content:
            main_content = soup.get_text(strip=True)

        return {
            "title": title_text,
            "text": main_content[:1000] + "..." if len(main_content) > 1000 else main_content,
            "links": len(soup.find_all('a')),
            "images": len(soup.find_all('img'))
        }

    except Exception as e:
        st.error(f"HTML parsing failed: {e}")
        return {"title": "Parse Error", "text": "Failed to parse HTML content"}

# メインアプリケーション
def main():
    st.title("🔍 Web Scraping Tool")
    st.markdown("---")

    # BeautifulSoupの状態表示
    if BS4_AVAILABLE:
        st.success("🟢 BeautifulSoup is ready")
    else:
        st.error("🔴 BeautifulSoup is not available")
        st.info("The app will work with limited functionality")

    # URL入力
    url = st.text_input(
        "Enter URL to scrape:",
        placeholder="https://example.com",
        help="Enter a valid URL to extract content"
    )

    if st.button("🚀 Scrape Content", type="primary"):
        if not url:
            st.warning("Please enter a URL")
            return

        if not url.startswith(('http://', 'https://')):
            st.error("Please enter a valid URL starting with http:// or https://")
            return

        with st.spinner("Fetching content..."):
            # HTTPリクエスト
            response = safe_request(url)

            if response is None:
                return

            # コンテンツの解析
            parsed_content = parse_html_content(response.text)

            # 結果の表示
            st.success("✅ Content successfully scraped!")

            col1, col2 = st.columns([2, 1])

            with col1:
                st.subheader("📄 Page Content")
                st.write(f"**Title:** {parsed_content['title']}")
                st.text_area("Content Preview:", parsed_content['text'], height=300)

            with col2:
                st.subheader("📊 Page Statistics")
                if BS4_AVAILABLE:
                    st.metric("Links Found", parsed_content.get('links', 'N/A'))
                    st.metric("Images Found", parsed_content.get('images', 'N/A'))
                st.metric("Content Length", len(parsed_content['text']))
                st.metric("Response Status", response.status_code)

            # ダウンロード機能
            st.subheader("💾 Download Results")

            # CSVデータの準備
            df = pd.DataFrame([{
                'URL': url,
                'Title': parsed_content['title'],
                'Content_Preview': parsed_content['text'][:200],
                'Scraped_At': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
                'Status_Code': response.status_code
            }])

            csv_data = df.to_csv(index=False)

            st.download_button(
                label="📥 Download as CSV",
                data=csv_data,
                file_name=f"scraped_content_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv",
                mime="text/csv"
            )

# サイドバー情報
with st.sidebar:
    st.header("ℹ️ Information")
    st.info("""
    This tool allows you to scrape web content safely.

    **Features:**
    - Safe HTTP requests
    - HTML content parsing
    - Content extraction
    - CSV export

    **Requirements:**
    - Valid URL
    - Internet connection
    - BeautifulSoup4 library
    """)

    st.header("🔧 Debug Info")
    st.write(f"BeautifulSoup Available: {BS4_AVAILABLE}")
    st.write(f"Streamlit Version: {st.__version__}")

if __name__ == "__main__":
    main()
