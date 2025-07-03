import streamlit as st
import requests
from bs4 import BeautifulSoup
import pandas as pd
import time
import chardet
import io
from openpyxl import Workbook
from openpyxl.utils.dataframe import dataframe_to_rows

def detect_encoding(response):
    """レスポンスのエンコーディングを検出"""
    # まずchardetで自動検出を試行
    detected = chardet.detect(response.content)
    detected_encoding = detected.get('encoding', 'utf-8')

    # 一般的なエンコーディングのリスト
    encodings_to_try = [
        detected_encoding,
        'utf-8',
        'shift_jis',
        'euc-jp',
        'iso-2022-jp',
        'cp932'
    ]

    # 各エンコーディングを試行
    for encoding in encodings_to_try:
        try:
            if encoding:
                response.encoding = encoding
                # デコードテストを実行
                test_text = response.text[:100]
                return encoding, detected.get('confidence', 0)
        except (UnicodeDecodeError, LookupError):
            continue

    # フォールバック
    response.encoding = 'utf-8'
    return 'utf-8', 0

def scrape_walkerplus_events(base_url, max_pages, delay_seconds):
    """WalkerPlusからイベント情報をスクレイピング"""
    all_events = []

    progress_bar = st.progress(0)
    status_text = st.empty()
    encoding_info = st.empty()

    for page in range(1, max_pages + 1):
        status_text.text(f'ページ {page}/{max_pages} を処理中...')

        # URLを構築
        if page == 1:
            url = base_url
        else:
            separator = '&' if '?' in base_url else '?'
            url = f"{base_url}{separator}p={page}"

        try:
            # リクエストを送信
            headers = {
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
            }
            response = requests.get(url, headers=headers, timeout=10)
            response.raise_for_status()

            # エンコーディングを検出・設定
            detected_encoding, confidence = detect_encoding(response)
            encoding_info.text(f'検出エンコーディング: {detected_encoding} (信頼度: {confidence:.2f})')

            # HTMLをパース
            soup = BeautifulSoup(response.text, 'html.parser')

            # イベント情報を抽出
            events = soup.find_all('div', class_='eventListItem')

            if not events:
                st.warning(f'ページ {page} でイベントが見つかりませんでした。')
                break

            for event in events:
                event_data = {}

                # タイトル
                title_elem = event.find('h3') or event.find('h2') or event.find('a')
                event_data['タイトル'] = title_elem.get_text(strip=True) if title_elem else 'タイトル不明'

                # 日時
                date_elem = event.find('time') or event.find('span', class_='date')
                if not date_elem:
                    date_elem = event.find('p', string=lambda text: text and ('月' in text or '日' in text))
                event_data['日時'] = date_elem.get_text(strip=True) if date_elem else '日時不明'

                # 場所
                venue_elem = event.find('span', class_='venue') or event.find('p', class_='venue')
                if not venue_elem:
                    venue_elem = event.find('span', string=lambda text: text and ('会場' in text or '場所' in text))
                event_data['場所'] = venue_elem.get_text(strip=True) if venue_elem else '場所不明'

                # URL
                link_elem = event.find('a')
                if link_elem and link_elem.get('href'):
                    href = link_elem.get('href')
                    if href.startswith('/'):
                        event_data['URL'] = f"https://www.walkerplus.com{href}"
                    else:
                        event_data['URL'] = href
                else:
                    event_data['URL'] = 'URL不明'

                all_events.append(event_data)

            # プログレスバーを更新
            progress_bar.progress(page / max_pages)

            # 待機時間
            if page < max_pages and delay_seconds > 0:
                time.sleep(delay_seconds)

        except requests.RequestException as e:
            st.error(f'ページ {page} の取得中にエラーが発生しました: {str(e)}')
            break
        except Exception as e:
            st.error(f'ページ {page} の処理中にエラーが発生しました: {str(e)}')
            break

    progress_bar.progress(1.0)
    status_text.text('スクレイピング完了！')

    return all_events

def create_excel_file(df):
    """DataFrameからExcelファイルを作成"""
    output = io.BytesIO()

    # Workbookを作成
    wb = Workbook()
    ws = wb.active
    ws.title = "WalkerPlusイベント"

    # DataFrameをワークシートに書き込み
    for r in dataframe_to_rows(df, index=False, header=True):
        ws.append(r)

    # 列幅を自動調整
    for column in ws.columns:
        max_length = 0
        column_letter = column[0].column_letter
        for cell in column:
            try:
                if len(str(cell.value)) > max_length:
                    max_length = len(str(cell.value))
            except:
                pass
        adjusted_width = min(max_length + 2, 50)
        ws.column_dimensions[column_letter].width = adjusted_width

    # ファイルを保存
    wb.save(output)
    output.seek(0)

    return output.getvalue()

def main():
    st.set_page_config(
        page_title="WalkerPlus イベントスクレイピング",
        page_icon="🎪",
        layout="wide"
    )

    st.title("🎪 WalkerPlus イベントスクレイピング")
    st.markdown("WalkerPlusからイベント情報を取得してCSV・Excelファイルとしてダウンロードできます。")

    # サイドバーの設定
    st.sidebar.header("⚙️ 設定")

    # URL入力
    st.sidebar.subheader("🔗 URL設定")
    base_url = st.sidebar.text_input(
        "WalkerPlus URL",
        value="https://www.walkerplus.com/event_list/today/",
        help="WalkerPlusのイベント一覧ページのURLを入力してください"
    )

    # スクレイピング設定
    st.sidebar.subheader("📊 スクレイピング設定")
    max_pages = st.sidebar.slider("取得ページ数", 1, 20, 3)
    delay_seconds = st.sidebar.slider("ページ間待機時間（秒）", 0.0, 5.0, 1.0, 0.5)

    # スクレイピング実行ボタン
    if st.sidebar.button("🚀 スクレイピング開始", type="primary"):
        if not base_url:
            st.error("URLを入力してください。")
            return

        with st.spinner("スクレイピング中..."):
            events = scrape_walkerplus_events(base_url, max_pages, delay_seconds)

        if events:
            st.success(f"✅ {len(events)}件のイベント情報を取得しました！")

            # データフレームに変換
            df = pd.DataFrame(events)

            # データ表示
            st.subheader("📋 取得したイベント情報")
            st.dataframe(df, use_container_width=True)

            # ダウンロードボタン
            st.subheader("💾 ダウンロード")

            col1, col2 = st.columns(2)

            with col1:
                # CSV ダウンロード
                csv_data = df.to_csv(index=False, encoding='utf-8-sig')
                st.download_button(
                    label="📄 CSV ダウンロード",
                    data=csv_data,
                    file_name=f"walkerplus_events_{pd.Timestamp.now().strftime('%Y%m%d_%H%M%S')}.csv",
                    mime="text/csv"
                )

            with col2:
                # Excel ダウンロード
                excel_data = create_excel_file(df)
                st.download_button(
                    label="📊 Excel ダウンロード",
                    data=excel_data,
                    file_name=f"walkerplus_events_{pd.Timestamp.now().strftime('%Y%m%d_%H%M%S')}.xlsx",
                    mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
                )

            # 統計情報
            st.subheader("📈 統計情報")
            col1, col2, col3 = st.columns(3)

            with col1:
                st.metric("取得イベント数", len(events))

            with col2:
                unique_venues = df['場所'].nunique()
                st.metric("ユニーク会場数", unique_venues)

            with col3:
                valid_urls = df[df['URL'] != 'URL不明'].shape[0]
                st.metric("有効URL数", valid_urls)

        else:
            st.error("❌ イベント情報を取得できませんでした。URLを確認してください。")

    # 使用方法
    with st.expander("📖 使用方法"):
        st.markdown("""
        ### 基本的な使い方
        1. **URL設定**: WalkerPlusのイベント一覧ページのURLを入力
        2. **設定調整**: 取得ページ数と待機時間を調整
        3. **実行**: 「スクレイピング開始」ボタンをクリック
        4. **ダウンロード**: CSV または Excel ファイルをダウンロード

        ### 注意事項
        - 適切な待機時間を設定してサーバーに負荷をかけないようにしてください
        - 大量のページを一度に取得する場合は、待機時間を長めに設定することを推奨します
        - 文字化けが発生した場合、自動的にエンコーディングを検出・修正します

        ### 出力ファイル形式
        - **CSV**: UTF-8エンコーディング（BOM付き）で出力
        - **Excel**: .xlsx形式で出力、列幅自動調整機能付き
        """)

if __name__ == "__main__":
    main()
