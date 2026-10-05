# ai-in-english-feed

《AI in English》播客的自托管 RSS（含 Apple Podcasts 所需的 itunes:author 字段）。

- RSS: https://guanlan1469.github.io/ai-in-english-feed/feed.xml
- 音频托管在原 feed（muse.ai），国内可直连。
- 每天新的一期由助手更新此文件。
- 每次推送都会由 GitHub Action 运行 `scripts/validate_feed.py` 检查 feed（本地也可直接运行 `python3 scripts/validate_feed.py`）。
