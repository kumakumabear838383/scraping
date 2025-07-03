import streamlit as st
import requests
from bs4 import BeautifulSoup
import pandas as pd
from datetime import datetime
import re
import time

def try_decode_content(content):
    """
    シンプルな文字コード処理
    UTF-8 -> Shift_JIS -> EUC-JP の順で試行
    """
    encodings = ['utf-8', 'shift_jis', 'euc-jp']

    for encoding in encodings:
        try:
            return content.decode(encoding)
        except (UnicodeDecodeError, AttributeError):
            continue

    # すべて失敗した場合はエラーを無視してデコード
    try:
        return content.decode('utf-8', errors='ignore')
    except:
        return str(content)

def get_page_content(url):
    """
    ページコンテンツを取得
    """
    try:
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
        }

        response = requests.get(url, headers=headers, timeout=10)
        response.raise_for_status()

        # シンプルな文字コード処理
        if isinstance(response.content, bytes):
            html_content = try_decode_content(response.content)
        else:
            html_content = response.content

        return html_content

    except requests.exceptions.RequestException as e:
        st.error(f"ページの取得に失敗しました: {str(e)}")
        return None
    except Exception as e:
        st.error(f"予期しないエラーが発生しました: {str(e)}")
        return None

def extract_event_info(soup):
    """
    イベント情報を抽出
    """
    events = []

    try:
        # WalkerPlusの一般的なイベント要素を検索
        event_selectors = [
            '.item',
            '.event-item',
            '.list-item',
            'article',
            '.content-item'
        ]

        event_elements = []
        for selector in event_selectors:
            elements = soup.select(selector)
            if elements:
                event_elements = elements
                break

        if not event_elements:
            # フォールバック: より広範囲な検索
            event_elements = soup.find_all(['div', 'article'], class_=re.compile(r'(item|event|list)', re.I))

        for element in event_elements[:50]:  # 最大50件に制限
            try:
                # タイトル抽出
                title_selectors = ['h2', 'h3', 'h4', '.title', '.name', 'a']
                title = None

                for selector in title_selectors:
                    title_elem = element.select_one(selector)
                    if title_elem and title_elem.get_text(strip=True):
                        title = title_elem.get_text(strip=True)
                        break

                if not title:
                    continue

                # 日付抽出
                date_text = ""
                date_selectors = ['.date', '.time', '.period', '.schedule']
                for selector in date_selectors:
                    date_elem = element.select_one(selector)
                    if date_elem:
                        date_text = date_elem.get_text(strip=True)
                        break

                # 場所抽出
                location = ""
                location_selectors = ['.place', '.location', '.venue', '.address']
                for selector in location_selectors:
                    location_elem = element.select_one(selector)
                    if location_elem:
                        location = location_elem.get_text(strip=True)
                        break

                # URL抽出
                url = ""
                link_elem = element.select_one('a')
                if link_elem and link_elem.get('href'):
                    href = link_elem.get('href')
                    if href.startswith('http'):
                        url = href
                    elif href.startswith('/'):
                        url = f"https://www.walkerplus.com{href}"

                # 説明抽出
                description = ""
                desc_selectors = ['.description', '.summary', '.text', 'p']
                for selector in desc_selectors:
                    desc_elem = element.select_one(selector)
                    if desc_elem:
                        desc_text = desc_elem.get_text(strip=True)
                        if len(desc_text) > 20:  # 十分な長さの説明のみ
                            description = desc_text[:200]  # 200文字に制限
                            break

                events.append({
                    'タイトル': title,
                    '日付': date_text,
                    '場所': location,
                    'URL': url,
                    '説明': description
                })

            except Exception as e:
                # 個別のイベント処理エラーは無視して続行
                continue

    except Exception as e:
        st.error(f"イベント情報の抽出中にエラーが発生しました: {str(e)}")

    return events

def main():
    st.set_page_config(
        page_title="WalkerPlus イベント情報取得",
        page_icon="🎉",
        layout="wide"
    )

    st.title("🎉 WalkerPlus イベント情報取得ツール")
    st.markdown("---")

    # URL入力
    st.subheader("📝 URL入力")
    url = st.text_input(
        "WalkerPlusのイベントページURLを入力してください",
        placeholder="https://www.walkerplus.com/..."
    )

    # 実行ボタン
    if st.button("🔍 イベント情報を取得", type="primary"):
        if not url:
            st.warning("URLを入力してください。")
            return

        if "walkerplus.com" not in url:
            st.warning("WalkerPlusのURLを入力してください。")
            return

        # プログレスバー表示
        progress_bar = st.progress(0)
        status_text = st.empty()

        try:
            # ページ取得
            status_text.text("ページを取得中...")
            progress_bar.progress(25)

            html_content = get_page_content(url)
            if not html_content:
                return

            # HTML解析
            status_text.text("HTMLを解析中...")
            progress_bar.progress(50)

            soup = BeautifulSoup(html_content, 'html.parser')

            # イベント情報抽出
            status_text.text("イベント情報を抽出中...")
            progress_bar.progress(75)

            events = extract_event_info(soup)

            progress_bar.progress(100)
            status_text.text("完了!")

            time.sleep(0.5)
            progress_bar.empty()
            status_text.empty()

            if not events:
                st.warning("イベント情報が見つかりませんでした。URLを確認してください。")
                return

            # 結果表示
            st.success(f"✅ {len(events)}件のイベント情報を取得しました！")

            # データフレーム作成
            df = pd.DataFrame(events)

            # 結果表示
            st.subheader("📊 取得結果")
            st.dataframe(df, use_container_width=True)

            # Excel出力
            st.subheader("💾 ファイル出力")

            # Excelファイル作成
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"walkerplus_events_{timestamp}.xlsx"

            try:
                df.to_excel(filename, index=False, engine='openpyxl')

                # ダウンロードボタン
                with open(filename, 'rb') as f:
                    st.download_button(
                        label="📥 Excelファイルをダウンロード",
                        data=f.read(),
                        file_name=filename,
                        mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
                    )

                st.success("Excelファイルが作成されました！")

            except Exception as e:
                st.error(f"Excelファイルの作成に失敗しました: {str(e)}")

        except Exception as e:
            st.error(f"処理中にエラーが発生しました: {str(e)}")
            progress_bar.empty()
            status_text.empty()

    # 使用方法
    with st.expander("📖 使用方法"):
        st.markdown("""
        ### 使用手順
        1. **URL入力**: WalkerPlusのイベント一覧ページのURLを入力
        2. **取得実行**: 「イベント情報を取得」ボタンをクリック
        3. **結果確認**: 取得されたイベント情報を確認
        4. **ファイル出力**: 必要に応じてExcelファイルをダウンロード

        ### 対応URL例
        - `https://www.walkerplus.com/event_list/today/`
        - `https://www.walkerplus.com/event_list/ar0313/`
        - その他のWalkerPlusイベントページ

        ### 注意事項
        - 取得できる情報はページの構造によって異なります
        - 大量のデータ取得時は時間がかかる場合があります
        - 文字化けが発生した場合は、基本的な文字コード処理で対応します
        """)

if __name__ == "__main__":
    main()
