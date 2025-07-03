# 安全なWebスクレイピングツール

このStreamlitアプリケーションは、Webサイトから安全にデータを取得するためのツールです。

## 🚀 機能

- **安全なスクレイピング**: 1-5秒のランダム待機時間でサーバー負荷を軽減
- **リアルタイム進捗表示**: スクレイピングの進行状況をリアルタイムで確認
- **データプレビュー**: 取得したデータをその場で確認
- **多形式ダウンロード**: Excel、CSV、テキスト形式でのダウンロード
- **CSSセレクタガイド**: 初心者向けの詳細な使用方法説明
- **エラーハンドリング**: 堅牢なエラー処理機能

## 📋 要件

- Python 3.8以上
- 必要なパッケージは`requirements.txt`に記載

## 🛠️ ローカル環境でのインストール

### 方法1: 手動インストール

1. リポジトリをクローンまたはダウンロード
```bash
git clone <repository-url>
cd web-scraping-tool
```

2. 依存関係をインストール
```bash
pip install -r requirements.txt
```

3. アプリケーションを起動
```bash
streamlit run streamlit_app.py
```

### 方法2: セットアップスクリプトを使用

1. リポジトリをクローン
```bash
git clone <repository-url>
cd web-scraping-tool
```

2. セットアップスクリプトを実行
```bash
chmod +x setup.sh
./setup.sh
```

3. アプリケーションを起動
```bash
streamlit run streamlit_app.py
```

## ☁️ Streamlit Cloudでのデプロイ

### 前提条件
- GitHubアカウント
- Streamlit Cloudアカウント（無料）

### デプロイ手順

1. **GitHubリポジトリの準備**
   ```bash
   # 新しいリポジトリを作成
   git init
   git add .
   git commit -m "Initial commit: Streamlit web scraping tool"

   # GitHubにプッシュ
   git remote add origin https://github.com/yourusername/web-scraping-tool.git
   git branch -M main
   git push -u origin main
   ```

2. **Streamlit Cloudでのデプロイ**
   - [Streamlit Cloud](https://share.streamlit.io/) にアクセス
   - GitHubアカウントでサインイン
   - "New app" をクリック
   - リポジトリを選択: `yourusername/web-scraping-tool`
   - ブランチ: `main`
   - メインファイル: `streamlit_app.py`
   - "Deploy!" をクリック

3. **デプロイ完了**
   - 数分でアプリケーションがデプロイされます
   - 自動生成されたURLでアクセス可能になります
   - 例: `https://yourusername-web-scraping-tool-streamlit-app-xyz123.streamlit.app/`

### デプロイ時の注意事項

- **requirements.txt**: 必要な依存関係がすべて記載されていることを確認
- **.streamlit/config.toml**: Streamlit Cloudに最適化された設定
- **メモリ使用量**: 大量のデータを処理する場合は注意
- **実行時間**: 長時間実行されるスクレイピングは避ける

## 📖 使用方法

### 基本的な使い方

1. **ベースURL入力**: スクレイピング対象のWebサイトのURLを入力
2. **CSSセレクタ入力**: 取得したい要素のCSSセレクタを入力
3. **ページ範囲設定**: 開始ページと終了ページを指定
4. **スクレイピング実行**: 「スクレイピング開始」ボタンをクリック

### CSSセレクタの取得方法

1. 対象サイトをブラウザで開く
2. 取得したい要素を右クリック
3. 「検証」または「要素を調査」を選択
4. 開発者ツールで要素を右クリック → Copy → Copy selector
5. 取得したセレクタを入力フィールドに貼り付け

### デフォルト設定

- **ベースURL**: `https://www.walkerplus.com/spot_list/ar0700/sg0107/`
- **CSSセレクタ**: `a.m-mainlist-item__ttl`
- **ページ範囲**: 1-5ページ
- **待機時間**: 1-5秒（ランダム）

## ⚙️ 設定オプション

### 基本設定
- **ベースURL**: スクレイピング対象のURL
- **CSSセレクタ**: 取得する要素の指定
- **ページ範囲**: 開始・終了ページの指定

### 詳細設定
- **最小待機時間**: リクエスト間の最小待機時間（1-10秒）
- **最大待機時間**: リクエスト間の最大待機時間（1-10秒）
- **タイムアウト**: リクエストのタイムアウト時間（5-30秒）

## 📊 出力データ

取得されるデータには以下の情報が含まれます：

- **page**: ページ番号
- **index**: ページ内での要素のインデックス
- **text**: 要素のテキスト内容
- **href**: リンクのhref属性（存在する場合）
- **full_url**: 完全なURL（相対URLを絶対URLに変換）
- **scraped_at**: データ取得日時

## 💾 ダウンロード形式

- **Excel (.xlsx)**: 表形式での詳細データ
- **CSV (.csv)**: 汎用的なデータ形式
- **テキスト (.txt)**: シンプルなテキスト形式

## 📁 プロジェクト構成

```
web-scraping-tool/
├── streamlit_app.py          # メインアプリケーション
├── requirements.txt          # Python依存関係
├── README.md                # このファイル
├── setup.sh                 # セットアップスクリプト（オプション）
├── .gitignore              # Git除外ファイル
└── .streamlit/
    └── config.toml         # Streamlit設定ファイル
```

## ⚠️ 重要な注意事項

### 法的・倫理的な考慮事項

1. **利用規約の確認**: 対象サイトの利用規約を必ず確認してください
2. **robots.txtの尊重**: サイトのrobots.txtファイルの内容を確認し、尊重してください
3. **適切な間隔**: サーバーに負荷をかけないよう、適切な間隔でアクセスしてください
4. **商用利用**: 商用目的での使用は、事前に対象サイトの許可を得てください

### 技術的な注意事項

1. **エラーハンドリング**: ネットワークエラーやHTTPエラーは自動的に処理されます
2. **タイムアウト**: 長時間応答がない場合は自動的にタイムアウトします
3. **文字エンコーディング**: UTF-8エンコーディングでファイルを保存します
4. **Streamlit Cloud制限**: 無料プランでは実行時間とメモリに制限があります

## 🔧 トラブルシューティング

### よくある問題

1. **データが取得できない**
   - CSSセレクタが正しいか確認
   - 対象サイトの構造が変更されていないか確認
   - ネットワーク接続を確認

2. **アクセスが拒否される**
   - User-Agentが適切に設定されているか確認
   - アクセス頻度を下げる（待機時間を増やす）
   - 対象サイトがスクレイピングを禁止していないか確認

3. **アプリケーションが起動しない**
   - Python環境を確認
   - 依存関係が正しくインストールされているか確認
   - ポートが使用されていないか確認

4. **Streamlit Cloudでのデプロイエラー**
   - requirements.txtの内容を確認
   - Python バージョンの互換性を確認
   - ログを確認してエラーの詳細を把握

### Streamlit Cloud固有の問題

1. **メモリ不足エラー**
   - 処理するページ数を減らす
   - データの処理方法を最適化する

2. **タイムアウトエラー**
   - スクレイピングの実行時間を短縮する
   - 待機時間を調整する

3. **依存関係エラー**
   - requirements.txtのバージョンを確認
   - 不要な依存関係を削除

## 🚀 パフォーマンス最適化

### ローカル環境
- 大量のデータを処理する場合は、バッチ処理を検討
- メモリ使用量を監視し、必要に応じて最適化

### Streamlit Cloud
- 無料プランの制限内で動作するよう設計
- 長時間実行を避け、適切なページ数制限を設定

## 📝 ライセンス

このプロジェクトは教育・研究目的での使用を想定しています。
商用利用の場合は、適切なライセンスを確認してください。

## 🤝 貢献

バグ報告や機能改善の提案は、GitHubのIssuesまでお願いします。

### 開発に参加する場合

1. リポジトリをフォーク
2. 機能ブランチを作成 (`git checkout -b feature/amazing-feature`)
3. 変更をコミット (`git commit -m 'Add some amazing feature'`)
4. ブランチにプッシュ (`git push origin feature/amazing-feature`)
5. プルリクエストを作成

## 📞 サポート

技術的な質問やサポートが必要な場合は、プロジェクトのドキュメントを参照するか、
コミュニティフォーラムで質問してください。

## 🔗 関連リンク

- [Streamlit Documentation](https://docs.streamlit.io/)
- [Streamlit Cloud](https://share.streamlit.io/)
- [Beautiful Soup Documentation](https://www.crummy.com/software/BeautifulSoup/bs4/doc/)
- [Requests Documentation](https://docs.python-requests.org/)
- [Pandas Documentation](https://pandas.pydata.org/docs/)

---

**免責事項**: このツールの使用によって生じた問題について、開発者は責任を負いません。
使用者の責任において、適切に使用してください。
