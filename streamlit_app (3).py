import streamlit as st
import requests
from bs4 import BeautifulSoup
import pandas as pd
import time
import random
from urllib.parse import urljoin, urlparse
import re

def scrape_data(url, max_pages, delay_range, item_delay_range, css_selectors, auto_stop_enabled, auto_stop_threshold):
    """
    指定されたURLからデータをスクレイピングする

    Args:
        url: スクレイピング対象のURL
        max_pages: 最大ページ数
        delay_range: ページ間の待機時間範囲 (min, max)
        item_delay_range: アイテム間の待機時間範囲 (min, max)
        css_selectors: CSSセレクタの辞書
        auto_stop_enabled: 自動終了機能の有効/無効
        auto_stop_threshold: 自動終了の閾値
    """
    all_data = []
    base_url = f"{urlparse(url).scheme}://{urlparse(url).netloc}"

    # プログレス表示用のコンテナ
    progress_container = st.container()

    for page in range(1, max_pages + 1):
        with progress_container:
            st.write(f"📄 ページ {page}/{max_pages} を処理中...")

        try:
            # ページのHTMLを取得
            response = requests.get(url, timeout=10)
            response.raise_for_status()
            soup = BeautifulSoup(response.content, 'html.parser')

            # アイテムを取得
            items = soup.select(css_selectors['item'])

            if not items:
                st.warning(f"ページ {page} でアイテムが見つかりませんでした。")
                break

            page_data = []

            # 各アイテムを処理
            for i, item in enumerate(items, 1):
                try:
                    # データを抽出
                    title = item.select_one(css_selectors['title'])
                    title_text = title.get_text(strip=True) if title else "タイトルなし"

                    link = item.select_one(css_selectors['link'])
                    link_url = ""
                    if link:
                        href = link.get('href')
                        if href:
                            link_url = urljoin(base_url, href)

                    # その他の情報を抽出
                    other_info = {}
                    for key, selector in css_selectors.items():
                        if key not in ['item', 'title', 'link', 'next_page']:
                            element = item.select_one(selector)
                            if element:
                                other_info[key] = element.get_text(strip=True)

                    # データを追加
                    item_data = {
                        'ページ': page,
                        'アイテム番号': i,
                        'タイトル': title_text,
                        'リンク': link_url,
                        **other_info
                    }
                    page_data.append(item_data)

                    # アイテム間の待機時間
                    if i < len(items):  # 最後のアイテムでは待機しない
                        item_delay = random.uniform(item_delay_range[0], item_delay_range[1])
                        with progress_container:
                            st.write(f"⏳ アイテム処理待機中... {item_delay:.1f}秒")
                        time.sleep(item_delay)

                except Exception as e:
                    st.warning(f"アイテム {i} の処理中にエラーが発生しました: {str(e)}")
                    continue

            all_data.extend(page_data)

            with progress_container:
                st.write(f"✅ ページ {page} 完了: {len(page_data)} 件のデータを取得")

            # 自動終了機能のチェック
            if auto_stop_enabled and len(page_data) < auto_stop_threshold:
                st.info(f"自動終了: ページ {page} で取得データが {auto_stop_threshold} 件未満のため終了しました。")
                break

            # 次のページのURLを取得
            if page < max_pages:
                next_link = soup.select_one(css_selectors['next_page'])
                if next_link:
                    next_href = next_link.get('href')
                    if next_href:
                        url = urljoin(base_url, next_href)
                    else:
                        st.warning(f"ページ {page} で次のページのリンクが見つかりませんでした。")
                        break
                else:
                    st.warning(f"ページ {page} で次のページのセレクタが見つかりませんでした。")
                    break

                # ページ間の待機時間
                page_delay = random.uniform(delay_range[0], delay_range[1])
                with progress_container:
                    st.write(f"⏳ ページ間待機中... {page_delay:.1f}秒")
                time.sleep(page_delay)

        except requests.RequestException as e:
            st.error(f"ページ {page} の取得中にエラーが発生しました: {str(e)}")
            break
        except Exception as e:
            st.error(f"ページ {page} の処理中に予期しないエラーが発生しました: {str(e)}")
            break

    return all_data

def main():
    st.set_page_config(
        page_title="Webスクレイピングツール",
        page_icon="🕷️",
        layout="wide"
    )

    st.title("🕷️ Webスクレイピングツール")
    st.markdown("---")

    # サイドバーの設定
    with st.sidebar:
        st.header("⚙️ 設定")

        # 基本設定
        st.subheader("🌐 基本設定")
        url = st.text_input(
            "スクレイピング対象URL",
            placeholder="https://example.com",
            help="スクレイピングを開始するページのURLを入力してください"
        )

        max_pages = st.number_input(
            "最大ページ数",
            min_value=1,
            max_value=100,
            value=5,
            help="スクレイピングする最大ページ数を設定してください"
        )

        # サーバー負荷軽減設定
        st.subheader("🛡️ サーバー負荷軽減設定")
        st.markdown("*サーバーへの負荷を軽減するための待機時間設定*")

        # ページ間待機時間
        st.markdown("**ページ間待機時間**")
        col1, col2 = st.columns(2)
        with col1:
            min_delay = st.number_input(
                "最小待機時間（秒）",
                min_value=0.1,
                max_value=10.0,
                value=1.0,
                step=0.1,
                key="page_min_delay",
                help="ページ間の最小待機時間"
            )
        with col2:
            max_delay = st.number_input(
                "最大待機時間（秒）",
                min_value=0.1,
                max_value=10.0,
                value=3.0,
                step=0.1,
                key="page_max_delay",
                help="ページ間の最大待機時間"
            )

        # アイテム間待機時間
        st.markdown("**アイテム間待機時間**")
        col3, col4 = st.columns(2)
        with col3:
            min_item_delay = st.number_input(
                "最小待機時間（秒）",
                min_value=0.0,
                max_value=5.0,
                value=0.2,
                step=0.1,
                key="item_min_delay",
                help="アイテム間の最小待機時間"
            )
        with col4:
            max_item_delay = st.number_input(
                "最大待機時間（秒）",
                min_value=0.0,
                max_value=5.0,
                value=0.5,
                step=0.1,
                key="item_max_delay",
                help="アイテム間の最大待機時間"
            )

        # 待機時間の妥当性チェック
        if min_delay > max_delay:
            st.error("⚠️ ページ間待機時間: 最小値が最大値を上回っています")
        if min_item_delay > max_item_delay:
            st.error("⚠️ アイテム間待機時間: 最小値が最大値を上回っています")

        # 自動終了設定
        st.subheader("🔄 自動終了設定")
        auto_stop_enabled = st.checkbox(
            "自動終了機能を有効にする",
            value=True,
            help="取得データが少ないページで自動的に終了します"
        )

        auto_stop_threshold = st.number_input(
            "自動終了の閾値",
            min_value=1,
            max_value=50,
            value=5,
            disabled=not auto_stop_enabled,
            help="この数値未満のデータしか取得できない場合に終了します"
        )

    # メインコンテンツ
    col1, col2 = st.columns([1, 1])

    with col1:
        st.subheader("🎯 CSSセレクタ設定")

        # 必須セレクタ
        st.markdown("**必須セレクタ**")
        item_selector = st.text_input(
            "アイテムセレクタ",
            placeholder=".item, .product, .post",
            help="各アイテム（商品、記事など）を囲む要素のCSSセレクタ"
        )

        title_selector = st.text_input(
            "タイトルセレクタ",
            placeholder="h2, .title, .name",
            help="タイトルを含む要素のCSSセレクタ"
        )

        link_selector = st.text_input(
            "リンクセレクタ",
            placeholder="a, .link",
            help="詳細ページへのリンクを含む要素のCSSセレクタ"
        )

        next_page_selector = st.text_input(
            "次ページセレクタ",
            placeholder=".next, .pagination a[rel='next']",
            help="次のページへのリンクを含む要素のCSSセレクタ"
        )

        # 追加セレクタ
        st.markdown("**追加セレクタ（オプション）**")
        additional_selectors = {}

        num_additional = st.number_input(
            "追加セレクタ数",
            min_value=0,
            max_value=10,
            value=0,
            help="価格、評価、説明文など、追加で取得したい情報の数"
        )

        for i in range(num_additional):
            col_name, col_selector = st.columns([1, 2])
            with col_name:
                field_name = st.text_input(
                    f"フィールド名 {i+1}",
                    placeholder="価格, 評価, 説明",
                    key=f"field_name_{i}"
                )
            with col_selector:
                field_selector = st.text_input(
                    f"セレクタ {i+1}",
                    placeholder=".price, .rating, .description",
                    key=f"field_selector_{i}"
                )

            if field_name and field_selector:
                additional_selectors[field_name] = field_selector

    with col2:
        st.subheader("📊 プレビュー・実行")

        # 設定の確認
        if url and item_selector and title_selector and link_selector and next_page_selector:
            st.success("✅ 必須項目がすべて入力されています")

            # 設定サマリー
            with st.expander("設定サマリー", expanded=True):
                st.write(f"**URL:** {url}")
                st.write(f"**最大ページ数:** {max_pages}")
                st.write(f"**ページ間待機:** {min_delay}〜{max_delay}秒")
                st.write(f"**アイテム間待機:** {min_item_delay}〜{max_item_delay}秒")
                st.write(f"**自動終了:** {'有効' if auto_stop_enabled else '無効'}")
                if auto_stop_enabled:
                    st.write(f"**終了閾値:** {auto_stop_threshold}件")
                st.write(f"**追加フィールド:** {len(additional_selectors)}個")

            # スクレイピング実行ボタン
            if st.button("🚀 スクレイピング開始", type="primary", use_container_width=True):
                # CSSセレクタをまとめる
                css_selectors = {
                    'item': item_selector,
                    'title': title_selector,
                    'link': link_selector,
                    'next_page': next_page_selector,
                    **additional_selectors
                }

                # 待機時間の範囲
                delay_range = (min_delay, max_delay)
                item_delay_range = (min_item_delay, max_item_delay)

                # スクレイピング実行
                with st.spinner("スクレイピング中..."):
                    try:
                        data = scrape_data(
                            url, 
                            max_pages, 
                            delay_range, 
                            item_delay_range,
                            css_selectors, 
                            auto_stop_enabled, 
                            auto_stop_threshold
                        )

                        if data:
                            st.success(f"✅ スクレイピング完了！ {len(data)} 件のデータを取得しました。")

                            # データフレームに変換
                            df = pd.DataFrame(data)

                            # 結果の表示
                            st.subheader("📋 取得データ")
                            st.dataframe(df, use_container_width=True)

                            # CSVダウンロード
                            csv = df.to_csv(index=False, encoding='utf-8-sig')
                            st.download_button(
                                label="📥 CSVファイルをダウンロード",
                                data=csv,
                                file_name=f"scraped_data_{int(time.time())}.csv",
                                mime="text/csv",
                                use_container_width=True
                            )

                            # 統計情報
                            with st.expander("📈 統計情報"):
                                st.write(f"**総データ数:** {len(data)}")
                                st.write(f"**処理ページ数:** {df['ページ'].nunique()}")
                                st.write(f"**平均アイテム数/ページ:** {len(data) / df['ページ'].nunique():.1f}")

                                # ページ別データ数
                                page_counts = df['ページ'].value_counts().sort_index()
                                st.write("**ページ別データ数:**")
                                st.bar_chart(page_counts)

                        else:
                            st.warning("⚠️ データが取得できませんでした。CSSセレクタを確認してください。")

                    except Exception as e:
                        st.error(f"❌ エラーが発生しました: {str(e)}")

        else:
            st.warning("⚠️ 必須項目を入力してください")
            missing_items = []
            if not url:
                missing_items.append("URL")
            if not item_selector:
                missing_items.append("アイテムセレクタ")
            if not title_selector:
                missing_items.append("タイトルセレクタ")
            if not link_selector:
                missing_items.append("リンクセレクタ")
            if not next_page_selector:
                missing_items.append("次ページセレクタ")

            st.write(f"**未入力項目:** {', '.join(missing_items)}")

    # フッター
    st.markdown("---")
    st.markdown(
        """
        <div style='text-align: center; color: #666;'>
            <p>🕷️ Webスクレイピングツール | 
            サーバー負荷を考慮した安全なスクレイピングを心がけましょう</p>
        </div>
        """,
        unsafe_allow_html=True
    )

if __name__ == "__main__":
    main()
