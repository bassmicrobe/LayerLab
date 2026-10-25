# LayerLab

**日本語** | [English](README.en.md) | [詳細な日本語ガイド](README.ja.md) | [操作マニュアル](MANUAL.ja.md)

[![CI](https://github.com/bassmicrobe/stemdeck/actions/workflows/ci.yml/badge.svg?branch=feat%2Fhigh-quality-separation)](https://github.com/bassmicrobe/stemdeck/actions/workflows/ci.yml)

音源を自分のPCで分離し、試聴・ミックス・書き出しできるローカルアプリです。MP3 / WAV / FLAC / M4A、利用する権利を持つYouTube・SoundCloud音源に対応します。分離サービスへの音源アップロード、アカウント登録、サブスクリプションは不要です。

> **非公式 fork test build / unofficial fork test build**
>
> 元プロジェクトは [StemDeck（stemdeckapp/stemdeck）](https://github.com/stemdeckapp/stemdeck) です。LayerLabはApache License 2.0に基づく非公式変更版であり、元プロジェクトの公式リリースではありません。元プロジェクトとの提携・承認・推奨関係はありません。

## ダウンロードと公開状況

[このforkのGitHub Releases](https://github.com/bassmicrobe/stemdeck/releases) に**実際に添付されているファイルのみ**が公開済みです。開発ブランチ、ビルド用スクリプト、過去のローカルDMGは、新版の公開・検証完了を意味しません。非公式版はPre-releaseとして公開します。

| ファイル | 用途 |
| --- | --- |
| `LayerLab-macOS-arm64.dmg` | Apple Silicon Mac向けアプリ。通常はこちらを使用します。Pythonランタイムを同梱します。 |
| `LayerLab-runtime-macOS-arm64.tar.zst` | Python・バックエンド等の実行環境。単体ではMacアプリとして起動できません。 |
| `SHA256SUMS-macOS-arm64.txt` | ダウンロードしたファイルの整合性確認用です。 |

macOS版はDMGを開き、アプリをApplicationsへインストールして起動します。初回は同梱ランタイムを検証・展開し、FFmpeg/ffprobeを取得します。AIモデルは必要になったときに取得します。初回セットアップにはインターネット接続と数GB以上の空き容量が必要です。

**現在の公開条件:** 同じコミットに対してCI・依存関係のセキュリティ検査・配布物検証が成功した場合にだけ公開します。PyTorchの互換性固定に伴う既知の問題が残っており、「テスト版」という表示だけで安全性を保証するものではありません。[監査記録](AUDIT.ja.md) と [セキュリティ方針](SECURITY.md) を確認してください。

Developer ID署名・Apple公証を実施していないビルドは、その旨をRelease本文に明記します。ad-hoc署名は正式な配布署名ではありません。Intel Mac / Windows向けスクリプトもありますが、各版の公開・検証状況はReleaseごとに確認してください。

## 主な機能

- ボーカル、ドラム、ベース、ギター、ピアノ、その他へ分離。使用モデルにより4stemまたは6stemになります。
- `Standard` / `High` / `Max` / `Ultra`の品質プリセットと、CPU / Apple GPU（MPS）/ NVIDIA CUDAの選択。
- 複数曲のキュー処理。抽出中でも完成した別の曲を試聴・書き出しできます。
- 同じ曲を設定違いで抽出する複数プロファイル。書き出し名とZIP内の設定情報で識別できます。
- 波形、ミュート・ソロ・音量調整、ループ、各stem・ミックスの書き出し。
- 任意のノイズ除去、微小音ゲート、ベース欠け補正、位相・残差補正。
- BPM・拍グリッド・キー解析、コード進行のMIDI / CSV出力。MIDIは推定結果であり、正確な採譜や原曲の全ノート再現を保証しません。
- 全体進捗、経過時間、実測履歴と処理段階に基づく残り時間の推定、画面内ログ。
- モデル常駐ワーカーとRust WAV/PCM処理による再ロード・後処理の負荷削減。

音質・速度・並列処理数は音源、品質設定、PCのCPU/GPU/メモリに依存します。欠損やクリッピングで失われた原音を完全に復元する機能ではありません。

## ローカルWeb版の起動

Git、uv、対応するPython（3.10～3.13）が必要です。新規環境はPython 3.13を推奨し、今回のmacOS用CIも3.13で検証します。3.10向け互換依存には追加の既知の脆弱性が残るため、配布対象として検証していません。開発・ビルド手順の詳細は[日本語ガイド](README.ja.md)にあります。

```sh
git clone https://github.com/bassmicrobe/stemdeck.git
cd stemdeck
git switch feat/high-quality-separation
./run.sh setup
./run.sh start
```

ブラウザで `http://127.0.0.1:8765/` を開きます。停止は `./run.sh stop` です。デスクトップ版も同じマシン上のローカルバックエンドで動作します。

## 保存・プライバシー・安全性

音源、生成stem、モデル等のキャッシュはローカルに保存します。URL音源取得、初回モデル取得、フォント、更新確認には外部への通信が発生します。「完全に通信しないアプリ」ではありません。

生成音源は標準で**処理完了から24時間**の保存期間があり、永久保存ではありません。必要な成果物は書き出してください。`STEMDECK_JOB_TTL_SECONDS`で保存期間を変更できます。

このアプリは認証のない単一ユーザー向けです。`127.0.0.1`で利用し、そのままインターネットへ公開しないでください。Host/Origin検証や容量制限はログイン・利用者間のデータ分離の代わりにはなりません。信頼できない学習済みモデルや、書き換えられたモデルキャッシュを読み込まないでください。

## ライセンス

LayerLab / StemDeck由来コードは **Apache License 2.0** です。条件を守ればコードの改変・再配布・商用利用が可能ですが、モデル・音源・商標まで同じ許諾になるわけではありません。

- [LICENSE](LICENSE) と [NOTICE](NOTICE) を保持し、元プロジェクトへの帰属・変更点・非公式版であることを明記します。Apache-2.0は商標権を自動許諾しません。
- 第三者ソフトウェアは各ライセンスに従います。実配布環境から生成する [一覧](packaging/generated/macos-arm64/THIRD_PARTY_NOTICES.md)、[全文](packaging/generated/macos-arm64/THIRD_PARTY_LICENSES.txt)、[JSONインベントリ](packaging/generated/macos-arm64/THIRD_PARTY_INVENTORY.json) を同梱します。配布時のファイル名は`THIRD_PARTY_NOTICES.txt`、`THIRD_PARTY_LICENSES.txt`、`THIRD_PARTY_INVENTORY.json`です。
- Demucs本体コードはMITですが、標準の学習済み重みは別条件です。上流の開発者回答では個人・研究用途と説明されています。初回ダウンロードにしても商用利用権は追加されません。
- FFmpegは実際のビルド構成に応じた条件が適用されます。現行のmacOS取得先はGPL-3.0-or-later版であり、アプリ独自コードのApache-2.0と混同しないでください。
- 利用する音源の著作権・取得元の規約は利用者が別途確認してください。

詳細は[日本語ガイドのライセンス説明](README.ja.md#商用利用有償配布について)、[採用OSSとモデル条件](OSS_COMPONENTS.md)を参照してください。法的助言や商用利用の一律保証ではありません。

## 開発・検証

```sh
uv sync --frozen --all-extras
uv run ruff check app tests
uv run ruff format --check app tests
uv run pytest -q
node --test tests/*.test.mjs
bash scripts/check-distribution-notices.sh
```

CIは[このforkのGitHub Actions](https://github.com/bassmicrobe/stemdeck/actions/workflows/ci.yml)で確認できます。上流のCIバッジや別コミットの成功結果は、このforkのRelease検証結果として扱いません。未解決の依存脆弱性を無視して公開する運用にはしていません。

元の英語READMEの技術説明と謝辞は[英語版](README.en.md)に保持しています。このforkでの追加・変更点、ビルド・署名・容量・環境変数の詳細は[日本語ガイド](README.ja.md)、日常操作は[マニュアル](MANUAL.ja.md)を参照してください。
