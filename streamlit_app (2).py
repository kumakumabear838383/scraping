import streamlit as st
import requests
from bs4 import BeautifulSoup
import pandas as pd
import time
import random
from urllib.parse import urljoin, urlparse
import re

def scrape_data(url, css_selector="a.m-mainlist-item__ttl"):
    """
    指定されたURLからデータをスクレイピングする

    Args:
        url (str): スクレイピング対象のURL
        css_selector (str): 使用するCSSセレクタ

    Returns:
        tuple: (データのリスト, ページが存在するかのフラグ)
    """
    try:
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
        }

        response = requests.get(url, headers=headers, timeout=10)

        # 404エラーや他のHTTPエラーをチェック
        if response.status_code == 404:
            return [], False

        response.raise_for_status()

        soup = BeautifulSoup(response.content, 'html.parser')

        # 指定されたCSSセレクタで要素を検索
        elements = soup.select(css_selector)

        # 要素が見つからない場合は空ページと判定
        if not elements:
            return [], False

        data = []
        for element in elements:
            # テキストとリンクを取得
            text = element.get_text(strip=True)
            link = element.get('href', '')

            # 相対URLを絶対URLに変換
            if link and not link.startswith('http'):
                link = urljoin(url, link)

            if text:  # テキストが空でない場合のみ追加
                data.append({
                    'タイトル': text,
                    'URL': link,
                    'ソースページ': url
                })

        return data, True

    except requests.exceptions.RequestException as e:
        st.error(f"リクエストエラー: {e}")
        return [], False
    except Exception as e:
        st.error(f"スクレイピングエラー: {e}")
        return [], False

def generate_walkerplus_url(base_url, page_num):
    """
    WalkerPlusのURL構造に対応したページURLを生成する

    WalkerPlusのURL構造:
    - 1ページ目: https://walker.plus/example/ (番号なし)
    - 2ページ目: https://walker.plus/example/2.html
    - 3ページ目: https://walker.plus/example/3.html

    Args:
        base_url (str): ベースURL
        page_num (int): ページ番号

    Returns:
        str: 生成されたページURL
    """
    try:
        if page_num == 1:
            # 1ページ目はベースURLをそのまま使用
            return base_url

        # ベースURLの末尾処理
        if base_url.endswith('/'):
            base_url = base_url.rstrip('/')

        # 2ページ目以降: ベースURL + ページ番号.html
        page_url = f"{base_url}/{page_num}.html"

        return page_url

    except Exception as e:
        st.error(f"WalkerPlus URL生成エラー: {e}")
        return base_url

def main():
    st.title("🔍 WalkerPlus専用 Webスクレイピングツール")
    st.markdown("---")

    # サイドバーの設定
    st.sidebar.header("⚙️ 設定")

    # URL入力
    url = st.sidebar.text_input(
        "📝 スクレイピング対象URL",
        placeholder="https://walker.plus/example/",
        help="WalkerPlusのスクレイピング対象URLを入力してください（末尾は/で終わることを推奨）"
    )

    # CSSセレクタ入力（要件1: 復活）
    css_selector = st.sidebar.text_input(
        "🎯 CSSセレクタ",
        value="a.m-mainlist-item__ttl",
        help="抽出したい要素のCSSセレクタを指定してください。WalkerPlusのデフォルト: a.m-mainlist-item__ttl"
    )

    # ページ数選択（要件2: number_inputに変更、上限なし）
    max_pages = st.sidebar.number_input(
        "📄 スクレイピングページ数",
        min_value=1,
        value=5,
        step=1,
        help="スクレイピングするページ数を指定してください（上限なし）"
    )

    # 待機時間設定
    wait_time = st.sidebar.slider(
        "⏱️ ページ間待機時間（秒）",
        min_value=1,
        max_value=10,
        value=3,
        help="各ページのスクレイピング間隔を設定してください（WalkerPlusサーバーへの負荷軽減）"
    )

    st.sidebar.markdown("---")

    # WalkerPlus URL構造の説明
    with st.sidebar.expander("🌐 WalkerPlus URL構造"):
        st.markdown("""
        **WalkerPlusのページネーション:**
        - 1ページ目: `https://walker.plus/example/`
        - 2ページ目: `https://walker.plus/example/2.html`
        - 3ページ目: `https://walker.plus/example/3.html`

        このツールは上記の構造に最適化されています。
        """)

    # プレビュー機能（維持）
    if url and st.sidebar.button("👀 プレビュー（1ページ目のみ）"):
        with st.spinner("プレビューを取得中..."):
            preview_data, page_exists = scrape_data(url, css_selector)

            if not page_exists:
                st.error("❌ ページが存在しないか、指定されたCSSセレクタで要素が見つかりませんでした。")
                st.info("💡 URLやCSSセレクタを確認してください。")
            elif preview_data:
                st.success(f"✅ {len(preview_data)}件のデータが見つかりました！")

                # プレビューデータを表示
                st.subheader("📋 プレビューデータ")
                preview_df = pd.DataFrame(preview_data)
                st.dataframe(preview_df, use_container_width=True)

                # 使用したCSSセレクタを表示
                st.info(f"🎯 使用したCSSセレクタ: `{css_selector}`")
            else:
                st.warning("⚠️ 指定されたCSSセレクタでデータが見つかりませんでした。セレクタを確認してください。")

    st.sidebar.markdown("---")

    # メインのスクレイピング実行
    if url and st.sidebar.button("🚀 スクレイピング開始", type="primary"):
        if not css_selector.strip():
            st.error("❌ CSSセレクタを入力してください。")
            return

        # 結果を格納するリスト
        all_data = []

        # プログレスバーとステータス表示
        progress_bar = st.progress(0)
        status_text = st.empty()
        results_container = st.empty()

        # 自動終了フラグ（要件3: 自動終了機能）
        auto_terminated = False
        actual_pages_scraped = 0

        try:
            for page in range(1, max_pages + 1):
                # WalkerPlus専用のページURLを生成
                page_url = generate_walkerplus_url(url, page)

                status_text.text(f"📄 ページ {page}/{max_pages} を処理中... ({page_url})")

                # データをスクレイピング（要件4: css_selectorパラメータ使用）
                page_data, page_exists = scrape_data(page_url, css_selector)

                # ページが存在しない場合は自動終了（要件3: 自動終了機能）
                if not page_exists:
                    auto_terminated = True
                    actual_pages_scraped = page - 1
                    break

                # データを追加
                if page_data:
                    all_data.extend(page_data)
                    actual_pages_scraped = page

                # プログレスバーを更新
                progress_bar.progress(page / max_pages)

                # 中間結果を表示
                if all_data:
                    with results_container.container():
                        st.subheader(f"📊 現在の結果 ({len(all_data)}件)")
                        temp_df = pd.DataFrame(all_data)
                        st.dataframe(temp_df.tail(10), use_container_width=True)

                # 最後のページでない場合は待機（ランダム待機時間維持）
                if page < max_pages:
                    wait_seconds = random.uniform(wait_time, wait_time + 2)
                    time.sleep(wait_seconds)

            # 完了メッセージ
            progress_bar.progress(1.0)

            # 要件3: 自動終了時のメッセージ表示
            if auto_terminated:
                status_text.success(f"✅ 自動終了: 指定ページ数({max_pages})に達する前に終了しました（実際: {actual_pages_scraped}ページ）")
                st.info(f"ℹ️ ページ {actual_pages_scraped + 1} が存在しないか、データが見つからなかったため自動で終了しました。")
            else:
                status_text.success(f"✅ スクレイピング完了! {max_pages}ページを処理しました。")

            # 最終結果の表示
            if all_data:
                st.subheader(f"📈 最終結果 ({len(all_data)}件)")

                # データフレームを作成
                df = pd.DataFrame(all_data)

                # 結果を表示
                st.dataframe(df, use_container_width=True)

                # 統計情報
                col1, col2, col3 = st.columns(3)
                with col1:
                    st.metric("📊 総データ数", len(all_data))
                with col2:
                    st.metric("📄 処理ページ数", actual_pages_scraped)
                with col3:
                    unique_urls = df['URL'].nunique() if 'URL' in df.columns else 0
                    st.metric("🔗 ユニークURL数", unique_urls)

                # CSVダウンロード（維持）
                csv = df.to_csv(index=False, encoding='utf-8-sig')
                st.download_button(
                    label="📥 CSVファイルをダウンロード",
                    data=csv,
                    file_name=f"walkerplus_scraped_data_{int(time.time())}.csv",
                    mime="text/csv"
                )

                # 使用した設定情報を表示
                st.subheader("⚙️ 使用した設定")
                settings_df = pd.DataFrame({
                    '設定項目': ['ベースURL', 'CSSセレクタ', '指定ページ数', '実際の処理ページ数', '待機時間', 'URL構造'],
                    '値': [url, css_selector, max_pages, actual_pages_scraped, f"{wait_time}秒", 'WalkerPlus専用']
                })
                st.table(settings_df)

                # 生成されたURLの確認
                st.subheader("🔗 生成されたURL一覧")
                url_list = []
                for i in range(1, actual_pages_scraped + 1):
                    generated_url = generate_walkerplus_url(url, i)
                    url_list.append({
                        'ページ': i,
                        '生成URL': generated_url
                    })

                if url_list:
                    url_df = pd.DataFrame(url_list)
                    st.dataframe(url_df, use_container_width=True)

            else:
                st.warning("⚠️ データが取得できませんでした。URLやCSSセレクタを確認してください。")

        except Exception as e:
            st.error(f"❌ エラーが発生しました: {e}")
            status_text.error("❌ スクレイピングが中断されました")

    # 使用方法の説明（要件5: UI改善）
    with st.expander("📖 使用方法"):
        st.markdown("""
        ### 🔧 基本的な使い方
        1. **URL入力**: WalkerPlusのスクレイピング対象URLを入力
        2. **CSSセレクタ指定**: 抽出したい要素のCSSセレクタを入力
        3. **ページ数設定**: スクレイピングするページ数を指定（上限なし）
        4. **プレビュー**: まず「プレビュー」で1ページ目の結果を確認
        5. **実行**: 「スクレイピング開始」でデータ収集を開始

        ### 🎯 WalkerPlus用CSSセレクタの例
        - `a.m-mainlist-item__ttl` - WalkerPlusのタイトルリンク（デフォルト）
        - `a.m-mainlist-item__link` - メインリストのリンク
        - `.m-mainlist-item__ttl` - タイトル要素
        - `.m-mainlist-item` - リストアイテム全体

        ### 🌐 WalkerPlus URL構造対応
        このツールはWalkerPlusの特殊なURL構造に最適化されています：

        **URL生成パターン:**
        - **1ページ目**: `https://walker.plus/example/` （番号なし）
        - **2ページ目**: `https://walker.plus/example/2.html`
        - **3ページ目**: `https://walker.plus/example/3.html`
        - **4ページ目**: `https://walker.plus/example/4.html`

        **入力例:**
        - ベースURL: `https://walker.plus/tochigi/gourmet/`
        - 生成される2ページ目: `https://walker.plus/tochigi/gourmet/2.html`

        ### 🔄 自動終了機能
        - 指定したページ数より実際のページが少ない場合、自動で終了
        - 404エラーや空ページを検出して停止
        - 無駄なリクエストを防ぎ、効率的にスクレイピング
        - 「指定ページ数に達する前に終了しました」というメッセージを表示

        ### 🛡️ 安全機能
        - **ランダム待機時間**: 設定時間+0〜2秒のランダム間隔でアクセス
        - **User-Agent設定**: ブラウザからのアクセスを模擬
        - **エラーハンドリング**: 各種エラーに対する適切な処理
        - **タイムアウト設定**: 10秒でリクエストタイムアウト

        ### ⚠️ 注意事項
        - WalkerPlusの利用規約を遵守してください
        - 過度なアクセスは避けてください
        - robots.txtを確認してください
        - サーバーに負荷をかけないよう適切な間隔を設定してください
        - このツールはWalkerPlus専用に最適化されています
        """)

if __name__ == "__main__":
    main()
