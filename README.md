# LayerLab

**音源を自分のPCで分離し、試聴・ミックス・書き出しできるローカルアプリです。**

**日本語** | [English](README.en.md) | [詳細ガイド](README.ja.md) | [操作マニュアル](MANUAL.ja.md)

[![CI](https://github.com/bassmicrobe/LayerLab/actions/workflows/ci.yml/badge.svg?branch=main)](https://github.com/bassmicrobe/LayerLab/actions/workflows/ci.yml)

## 概要

[StemDeck](https://github.com/stemdeckapp/stemdeck) をベースにした非公式 fork です。MP3 / WAV / FLAC / M4A、利用する権利を持つ YouTube・SoundCloud 音源を、自分のマシン上で stem に分離します。分離サービスへの音源アップロード、アカウント登録、サブスクリプションは不要です。

> **非公式 fork test build**
>
> 元プロジェクトは [StemDeck（stemdeckapp/stemdeck）](https://github.com/stemdeckapp/stemdeck) です。LayerLab は Apache License 2.0 に基づく非公式変更版であり、元プロジェクトの公式リリースではありません。提携・承認・推奨関係はありません。アプリ名とこの fork のリポジトリ名を `LayerLab` に変更しています。元の StemDeck 自体を改名したものではありません。

この fork では品質プリセット、float32 / Rust 後処理、モデル常駐ワーカー、キューと進捗表示、コード / MIDI 解析、独自 UI、ローカルデスクトップ配布を追加・改良しています。詳細は [日本語ガイドの変更点](README.ja.md#この-fork-で加えた主な変更) と Git 履歴を参照してください。

- ボーカル、ドラム、ベース、ギター、ピアノ、その他へ分離。使用モデルにより 4stem または 6stem になります。
- `Standard` / `High` / `Max` / `Ultra` の品質プリセットと、CPU / Apple GPU（MPS）/ NVIDIA CUDA の選択。
- 複数曲のキュー処理。抽出中でも完成した別の曲を試聴・書き出しできます。
- 同じ曲を設定違いで抽出する複数プロファイル。書き出し名と ZIP 内の設定情報で識別できます。
- 波形、ミュート・ソロ・音量調整、ループ、各 stem・ミックスの書き出し。
- 任意のノイズ除去、微小音ゲート、ベース欠け補正、位相・残差補正。
- BPM・拍グリッド・キー解析、コード進行の MIDI / CSV 出力。MIDI は推定結果であり、正確な採譜や原曲の全ノート再現を保証しません。
- 全体進捗、経過時間、実測履歴と処理段階に基づく残り時間の推定、画面内ログ。
- モデル常駐ワーカーと Rust WAV/PCM 処理による再ロード・後処理の負荷削減。

音質・速度・並列処理数は音源、品質設定、PC の CPU / GPU / メモリに依存します。欠損やクリッピングで失われた原音を完全に復元する機能ではありません。

現行の実装・検証済み手順は [`main` ブランチ](https://github.com/bassmicrobe/LayerLab/tree/main) を対象とします。配布アプリは [Releases](https://github.com/bassmicrobe/LayerLab/releases) から取得できます。

## 技術スタック

- Python 3.11〜3.13（推奨 3.13）/ [uv](https://docs.astral.sh/uv/)
- FastAPI / uvicorn
- Demucs 4.0.1 / PyTorch 2.14.1 / Torchaudio 2.11.0 / SoundFile
- librosa / beat-this / music21 / pyloudnorm
- yt-dlp / FFmpeg（開発時は `imageio-ffmpeg` を fallback に利用）
- フロントエンド: HTML / CSS / 素の JavaScript（バンドルなし）
- デスクトップ: Tauri 2 / Rust
- 検証: ruff / pytest / Node の `node --test`

## セットアップ

### デスクトップ版（macOS）

[GitHub Releases](https://github.com/bassmicrobe/LayerLab/releases) に**実際に添付されているファイルのみ**が公開済みです。非公式版は Pre-release として公開します。同じコミットに対して CI・依存関係のセキュリティ検査・配布物検証が成功した場合にだけ公開します。検査成功も脆弱性が一切ないことの保証ではありません。

| ファイル | 用途 |
| --- | --- |
| `LayerLab-macOS-arm64.dmg` | macOS 14 以降の Apple Silicon Mac 向けアプリ。通常はこちらを使用します。Python ランタイムを同梱します。 |
| `LayerLab-runtime-macOS-arm64.tar.zst` | Python・バックエンド等の実行環境。単体では Mac アプリとして起動できません。 |
| `SHA256SUMS-macOS-arm64.txt` | ダウンロードしたファイルの整合性確認用です。 |

macOS 版は DMG を開き、アプリを Applications へインストールして起動します。初回は同梱ランタイムを検証・展開し、FFmpeg / ffprobe を取得します。AI モデルは必要になったときに取得します。初回セットアップにはインターネット接続と数 GB 以上の空き容量が必要です。

公式モデルは読込ごとにチェックサムを確認し、`weights_only=True` と限定的な許可リストで読み込みます。危険な旧版や無制限 pickle 読込へのフォールバックは行いません。

Developer ID 署名・Apple 公証を実施していないビルドは、その旨を Release 本文に明記します。ad-hoc 署名は正式な配布署名ではありません。安全な現行 PyTorch の wheel がない Intel Mac は非対応です。Windows は今回の配布検証・公開対象外です。

### ローカル Web 版

Git、uv、対応する Python（3.11〜3.13）が必要です。Python 3.13 を推奨し、macOS 用 CI も 3.13 で検証します。開発・ビルド手順の詳細は [日本語ガイド](README.ja.md) にあります。

```sh
git clone https://github.com/bassmicrobe/LayerLab.git
cd LayerLab
git switch main
./run.sh setup
./run.sh start
```

ブラウザで `http://127.0.0.1:8765/` を開きます。停止は `./run.sh stop` です。デスクトップ版も同じマシン上のローカルバックエンドで動作します。

### 開発・検証

```sh
uv sync --frozen --all-extras
uv run ruff check app tests
uv run ruff format --check app tests
uv run pytest -q
node --test tests/*.test.mjs
bash scripts/check-distribution-notices.sh
```

CI は [GitHub Actions](https://github.com/bassmicrobe/LayerLab/actions/workflows/ci.yml) で確認できます。

## 使い方

日常操作は [操作マニュアル](MANUAL.ja.md) を参照してください。

このアプリは認証のない単一ユーザー向けです。`127.0.0.1` で利用し、そのままインターネットへ公開しないでください。Host / Origin 検証や容量制限は、ログイン・利用者間のデータ分離の代わりにはなりません。信頼できない学習済みモデルや、書き換えられたモデルキャッシュを読み込まないでください。

音源、生成 stem、モデル等のキャッシュはローカルに保存します。URL 音源取得、初回モデル取得、フォント、更新確認には外部への通信が発生します。「完全に通信しないアプリ」ではありません。

生成音源は標準で**処理完了から 24 時間**の保存期間があり、永久保存ではありません。必要な成果物は書き出してください。`STEMDECK_JOB_TTL_SECONDS` で保存期間を変更できます。

## 構成

```text
app/          FastAPI バックエンド（API・パイプライン）
static/       ローカル Web UI（HTML / CSS / JS）
desktop/      Tauri v2 デスクトップシェル（Rust）
scripts/      配布・ベンチマーク用スクリプト
tests/        pytest / Node テスト
packaging/    ライセンス表記と配布物生成
imgs/         スクリーンショットとブランド素材
benchmarks/   品質比較用の評価セット置き場
```

## ドキュメント

- [詳細な日本語ガイド](README.ja.md) — 変更点、ビルド、署名、容量、環境変数、ライセンス詳細
- [操作マニュアル](MANUAL.ja.md) — 日常操作
- [英語版 README](README.en.md) — 上流の技術説明と謝辞
- [セキュリティ方針](SECURITY.md)
- [監査記録](AUDIT.ja.md)
- [採用 OSS とモデル条件](OSS_COMPONENTS.md)
- [コントリビューション案内](CONTRIBUTING.md)

## ライセンス

LayerLab / StemDeck 由来コードは **Apache License 2.0** です。条件を守ればコードの改変・再配布・商用利用が可能ですが、モデル・音源・商標まで同じ許諾になるわけではありません。

- [LICENSE](LICENSE) と [NOTICE](NOTICE) を保持し、元プロジェクトへの帰属・変更点・非公式版であることを明記します。Apache-2.0 は商標権を自動許諾しません。
- 第三者ソフトウェアは各ライセンスに従います。実配布環境から生成する [一覧](packaging/generated/macos-arm64/THIRD_PARTY_NOTICES.md)、[全文](packaging/generated/macos-arm64/THIRD_PARTY_LICENSES.txt)、[JSON インベントリ](packaging/generated/macos-arm64/THIRD_PARTY_INVENTORY.json) を同梱します。配布時のファイル名は `THIRD_PARTY_NOTICES.txt`、`THIRD_PARTY_LICENSES.txt`、`THIRD_PARTY_INVENTORY.json` です。
- Demucs 本体コードは MIT ですが、標準の学習済み重みは別条件です。上流の開発者回答では個人・研究用途と説明されています。初回ダウンロードにしても商用利用権は追加されません。
- FFmpeg は実際のビルド構成に応じた条件が適用されます。現行の macOS 取得先は GPL-3.0-or-later 版であり、アプリ独自コードの Apache-2.0 と混同しないでください。
- 利用する音源の著作権・取得元の規約は利用者が別途確認してください。

詳細は [日本語ガイドのライセンス説明](README.ja.md#商用利用有償配布について)、[採用 OSS とモデル条件](OSS_COMPONENTS.md) を参照してください。法的助言や商用利用の一律保証ではありません。
