import streamlit as st
import requests
from bs4 import BeautifulSoup
import pandas as pd
import time
import random
from urllib.parse import urljoin, urlparse
import re

def scrape_data(base_url, max_pages=5, delay_range=(1, 3)):
    """
    WalkerPlusのスポット情報をスクレイピングする関数

    Args:
        base_url (str): ベースURL
        max_pages (int): 最大ページ数
        delay_range (tuple): 待機時間の範囲（秒）

    Returns:
        list: スクレイピングしたデータのリスト
    """
    all_data = []

    # セッションを作成してUser-Agentを設定
    session = requests.Session()
    session.headers.update({
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
    })

    for page_num in range(1, max_pages + 1):
        try:
            # URL生成ロジック（修正版）
            if page_num == 1:
                url = base_url.rstrip('/')  # 1ページ目は番号なし
            else:
                # ベースURLから末尾の/を除去して、ページ番号.htmlを追加
                clean_base_url = base_url.rstrip('/')
                url = f"{clean_base_url}/{page_num}.html"

            st.write(f"📄 ページ {page_num} を処理中: {url}")

            # リクエスト送信
            response = session.get(url, timeout=10)
            response.raise_for_status()

            # BeautifulSoupでHTMLを解析
            soup = BeautifulSoup(response.content, 'html.parser')

            # スポット情報を抽出（WalkerPlusの構造に基づく）
            spots = soup.find_all('div', class_='spot-item') or soup.find_all('li', class_='spot-list-item')

            if not spots:
                # 別の構造を試す
                spots = soup.find_all('div', class_='item') or soup.find_all('article')

            if not spots:
                st.warning(f"ページ {page_num} でスポット情報が見つかりませんでした")
                continue

            page_data = []
            for spot in spots:
                try:
                    # タイトル抽出
                    title_elem = (spot.find('h3') or 
                                spot.find('h2') or 
                                spot.find('a', class_='title') or
                                spot.find('div', class_='title'))
                    title = title_elem.get_text(strip=True) if title_elem else "タイトル不明"

                    # リンク抽出
                    link_elem = spot.find('a')
                    link = urljoin(url, link_elem['href']) if link_elem and link_elem.get('href') else ""

                    # 住所抽出
                    address_elem = (spot.find('div', class_='address') or 
                                  spot.find('span', class_='address') or
                                  spot.find('p', class_='address'))
                    address = address_elem.get_text(strip=True) if address_elem else ""

                    # 説明抽出
                    desc_elem = (spot.find('div', class_='description') or 
                               spot.find('p', class_='description') or
                               spot.find('div', class_='text'))
                    description = desc_elem.get_text(strip=True) if desc_elem else ""

                    # カテゴリ抽出
                    category_elem = (spot.find('span', class_='category') or 
                                   spot.find('div', class_='category'))
                    category = category_elem.get_text(strip=True) if category_elem else ""

                    data = {
                        'タイトル': title,
                        'リンク': link,
                        '住所': address,
                        '説明': description,
                        'カテゴリ': category,
                        'ページ': page_num,
                        'URL': url
                    }
                    page_data.append(data)

                except Exception as e:
                    st.warning(f"スポット情報の抽出でエラー: {e}")
                    continue

            all_data.extend(page_data)
            st.success(f"✅ ページ {page_num}: {len(page_data)} 件のデータを取得")

            # 次のページへの待機時間
            if page_num < max_pages:
                wait_time = random.uniform(delay_range[0], delay_range[1])
                st.info(f"⏳ {wait_time:.1f}秒待機中...")
                time.sleep(wait_time)

        except requests.exceptions.RequestException as e:
            st.error(f"❌ ページ {page_num} でリクエストエラー: {e}")
            continue
        except Exception as e:
            st.error(f"❌ ページ {page_num} で予期しないエラー: {e}")
            continue

    return all_data

def preview_page_structure(url):
    """
    ページ構造をプレビューする関数
    """
    try:
        session = requests.Session()
        session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
        })

        response = session.get(url, timeout=10)
        response.raise_for_status()

        soup = BeautifulSoup(response.content, 'html.parser')

        # 可能なスポット要素を探す
        possible_elements = [
            ('div.spot-item', soup.find_all('div', class_='spot-item')),
            ('li.spot-list-item', soup.find_all('li', class_='spot-list-item')),
            ('div.item', soup.find_all('div', class_='item')),
            ('article', soup.find_all('article')),
        ]

        st.write("### 🔍 ページ構造分析")
        for selector, elements in possible_elements:
            if elements:
                st.write(f"**{selector}**: {len(elements)} 個の要素が見つかりました")

                # 最初の要素の構造を表示
                if elements:
                    first_element = elements[0]
                    st.write("最初の要素の構造:")
                    st.code(str(first_element)[:500] + "..." if len(str(first_element)) > 500 else str(first_element))
                    break
        else:
            st.warning("スポット要素が見つかりませんでした")

    except Exception as e:
        st.error(f"プレビューエラー: {e}")

def main():
    st.title("🏢 WalkerPlus スポット情報スクレイピングツール")
    st.markdown("---")

    # サイドバーで設定
    st.sidebar.header("⚙️ 設定")

    # デフォルトURLを新しいサンプルに更新
    default_url = "https://www.walkerplus.com/spot_list/ar0623/sg0051/"
    base_url = st.sidebar.text_input(
        "ベースURL", 
        value=default_url,
        help="WalkerPlusのスポット一覧ページのURL"
    )

    max_pages = st.sidebar.slider("最大ページ数", 1, 20, 5)

    delay_min = st.sidebar.slider("最小待機時間（秒）", 0.5, 5.0, 1.0, 0.5)
    delay_max = st.sidebar.slider("最大待機時間（秒）", 1.0, 10.0, 3.0, 0.5)

    # メインエリア
    col1, col2 = st.columns([2, 1])

    with col1:
        if st.button("🚀 スクレイピング開始", type="primary"):
            if not base_url:
                st.error("ベースURLを入力してください")
                return

            with st.spinner("スクレイピング実行中..."):
                data = scrape_data(base_url, max_pages, (delay_min, delay_max))

            if data:
                st.success(f"🎉 合計 {len(data)} 件のデータを取得しました！")

                # データフレーム作成
                df = pd.DataFrame(data)

                # データ表示
                st.subheader("📊 取得データ")
                st.dataframe(df, use_container_width=True)

                # 統計情報
                st.subheader("📈 統計情報")
                col1, col2, col3 = st.columns(3)
                with col1:
                    st.metric("総データ数", len(df))
                with col2:
                    st.metric("処理ページ数", df['ページ'].nunique())
                with col3:
                    st.metric("平均データ/ページ", f"{len(df)/df['ページ'].nunique():.1f}")

                # CSVダウンロード
                csv = df.to_csv(index=False, encoding='utf-8-sig')
                st.download_button(
                    label="📥 CSVダウンロード",
                    data=csv,
                    file_name=f"walkerplus_spots_{pd.Timestamp.now().strftime('%Y%m%d_%H%M%S')}.csv",
                    mime="text/csv"
                )

            else:
                st.error("❌ データを取得できませんでした")

    with col2:
        if st.button("🔍 ページ構造プレビュー"):
            if base_url:
                preview_page_structure(base_url)
            else:
                st.error("ベースURLを入力してください")

    # 使用方法
    with st.expander("📖 使用方法"):
        st.markdown("""
        ### 🎯 このツールの使い方

        1. **ベースURL**: WalkerPlusのスポット一覧ページのURLを入力
           - 例: `https://www.walkerplus.com/spot_list/ar0623/sg0051/`

        2. **最大ページ数**: スクレイピングするページ数を設定

        3. **待機時間**: リクエスト間の待機時間を設定（サーバー負荷軽減）

        4. **プレビュー**: ページ構造を事前確認

        5. **実行**: スクレイピングを開始

        ### ⚠️ 注意事項
        - 利用規約を遵守してください
        - 過度なアクセスは避けてください
        - 取得したデータの利用は自己責任で行ってください

        ### 🔧 URL構造について
        - 1ページ目: ベースURL（番号なし）
        - 2ページ目以降: ベースURL + ページ番号.html
        """)

if __name__ == "__main__":
    main()
