import streamlit as st
import requests
from bs4 import BeautifulSoup
import pandas as pd
import time
import random
from urllib.parse import urljoin, urlparse
import re

def scrape_data(base_url, css_selector, num_pages, page_wait_min, page_wait_max, item_wait_min, item_wait_max):
    """WalkerPlus専用のスクレイピング関数"""
    all_data = []

    for page_num in range(1, num_pages + 1):
        # WalkerPlus用のURL生成ロジック
        if page_num == 1:
            url = base_url
        else:
            # ベースURLの末尾が.htmlで終わっている場合の処理
            if base_url.endswith('.html'):
                url = base_url.replace('.html', f'{page_num}.html')
            else:
                url = f"{base_url.rstrip('/')}/{page_num}.html"

        st.write(f"📄 ページ {page_num}: {url}")

        try:
            response = requests.get(url)
            response.raise_for_status()
            soup = BeautifulSoup(response.content, 'html.parser')

            # CSSセレクタでアイテムを取得
            items = soup.select(css_selector)

            if not items:
                st.warning(f"ページ {page_num} でアイテムが見つかりませんでした")
                continue

            st.write(f"✅ {len(items)} 件のアイテムを発見")

            # 各アイテムを処理
            for i, item in enumerate(items, 1):
                try:
                    # テキストとリンクを取得
                    text = item.get_text(strip=True)
                    link = item.get('href', '')

                    # 相対URLを絶対URLに変換
                    if link and not link.startswith('http'):
                        link = urljoin(url, link)

                    all_data.append({
                        'ページ': page_num,
                        'アイテム番号': i,
                        'テキスト': text,
                        'リンク': link
                    })

                    # アイテム間待機時間
                    if i < len(items):  # 最後のアイテム以外
                        wait_time = random.uniform(item_wait_min, item_wait_max)
                        time.sleep(wait_time)

                except Exception as e:
                    st.error(f"アイテム {i} の処理中にエラー: {str(e)}")
                    continue

            # ページ間待機時間
            if page_num < num_pages:
                wait_time = random.uniform(page_wait_min, page_wait_max)
                st.write(f"⏳ {wait_time:.1f}秒待機中...")
                time.sleep(wait_time)

        except requests.RequestException as e:
            st.error(f"ページ {page_num} の取得中にエラー: {str(e)}")
            continue
        except Exception as e:
            st.error(f"ページ {page_num} の処理中にエラー: {str(e)}")
            continue

    return all_data

def main():
    st.title("🚶 WalkerPlus スクレイピングツール")
    st.write("WalkerPlus専用のシンプルなスクレイピングツールです")

    # サイドバー設定
    st.sidebar.header("⚙️ 設定")

    # ベースURL
    base_url = st.sidebar.text_input(
        "ベースURL",
        value="https://www.walkerplus.com/event_list/today/ar0313/",
        help="スクレイピング対象のベースURL"
    )

    # CSSセレクタ
    css_selector = st.sidebar.text_input(
        "CSSセレクタ",
        value="a.m-mainlist-item__ttl",
        help="取得したい要素のCSSセレクタ"
    )

    # ページ数
    num_pages = st.sidebar.number_input(
        "ページ数",
        min_value=1,
        max_value=50,
        value=3,
        help="スクレイピングするページ数"
    )

    # ページ間待機時間
    st.sidebar.subheader("⏱️ ページ間待機時間（秒）")
    page_wait_min = st.sidebar.number_input(
        "最小",
        min_value=0.1,
        max_value=10.0,
        value=1.0,
        step=0.1,
        key="page_wait_min"
    )
    page_wait_max = st.sidebar.number_input(
        "最大",
        min_value=0.1,
        max_value=10.0,
        value=3.0,
        step=0.1,
        key="page_wait_max"
    )

    # アイテム間待機時間
    st.sidebar.subheader("⏱️ アイテム間待機時間（秒）")
    item_wait_min = st.sidebar.number_input(
        "最小",
        min_value=0.0,
        max_value=5.0,
        value=0.2,
        step=0.1,
        key="item_wait_min"
    )
    item_wait_max = st.sidebar.number_input(
        "最大",
        min_value=0.0,
        max_value=5.0,
        value=0.5,
        step=0.1,
        key="item_wait_max"
    )

    # 設定確認
    if page_wait_min > page_wait_max:
        st.sidebar.error("ページ間待機時間: 最小値が最大値より大きいです")
        return

    if item_wait_min > item_wait_max:
        st.sidebar.error("アイテム間待機時間: 最小値が最大値より大きいです")
        return

    # 現在の設定を表示
    st.subheader("📋 現在の設定")
    col1, col2 = st.columns(2)

    with col1:
        st.write(f"**ベースURL:** {base_url}")
        st.write(f"**CSSセレクタ:** `{css_selector}`")
        st.write(f"**ページ数:** {num_pages}")

    with col2:
        st.write(f"**ページ間待機:** {page_wait_min}-{page_wait_max}秒")
        st.write(f"**アイテム間待機:** {item_wait_min}-{item_wait_max}秒")

    # スクレイピング実行
    if st.button("🚀 スクレイピング開始", type="primary"):
        if not base_url:
            st.error("ベースURLを入力してください")
            return

        if not css_selector:
            st.error("CSSセレクタを入力してください")
            return

        # プログレスバー
        progress_bar = st.progress(0)
        status_text = st.empty()

        start_time = time.time()

        try:
            # スクレイピング実行
            data = scrape_data(
                base_url, css_selector, num_pages,
                page_wait_min, page_wait_max,
                item_wait_min, item_wait_max
            )

            progress_bar.progress(100)
            end_time = time.time()

            if data:
                st.success(f"✅ スクレイピング完了！ {len(data)} 件のデータを取得しました")
                st.write(f"⏱️ 実行時間: {end_time - start_time:.1f}秒")

                # データフレーム作成
                df = pd.DataFrame(data)

                # 結果表示
                st.subheader("📊 取得データ")
                st.dataframe(df, use_container_width=True)

                # 統計情報
                st.subheader("📈 統計情報")
                col1, col2, col3 = st.columns(3)

                with col1:
                    st.metric("総アイテム数", len(df))

                with col2:
                    st.metric("処理ページ数", df['ページ'].nunique())

                with col3:
                    avg_items = len(df) / df['ページ'].nunique()
                    st.metric("平均アイテム数/ページ", f"{avg_items:.1f}")

                # CSVダウンロード
                csv = df.to_csv(index=False, encoding='utf-8-sig')
                st.download_button(
                    label="📥 CSVダウンロード",
                    data=csv,
                    file_name=f"walkerplus_data_{int(time.time())}.csv",
                    mime="text/csv"
                )

            else:
                st.warning("データが取得できませんでした")

        except Exception as e:
            st.error(f"エラーが発生しました: {str(e)}")

        finally:
            progress_bar.empty()
            status_text.empty()

if __name__ == "__main__":
    main()
