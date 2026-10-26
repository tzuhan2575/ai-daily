# 每週回顧（週日 08:00 台灣時間）

目標：產出 `weekly/YYYY-Www.json`（ISO 週，例如 2026-W44），更新學習路徑，建置並推送。

## 步驟
1. 讀本週（週一到週日）所有 `data/digests/*.json`，讀 `learning/profile.md`、`learning/state.md`、`learning/curriculum.json`。
2. 寫 `weekly/YYYY-Www.json`：
   `{"week":"2026-W44","range":"10/26–11/1","summary":["本週脈絡 3 到 5 點"],"actions":[{"title":"做什麼","why":"為什麼","how":"怎麼做（具體指令或步驟）"}],"covered":["本週上過的課"]}`
   `actions` 3 到 5 件，來自本週各則的 `impact`（use／watch）與課程，必須具體可執行，沒有就少寫，不湊數。
3. 更新 `learning/curriculum.json`：本週主題改 `done`、下週改 `current`（四週結束後依讀者興趣再排下一輪四週）；更新 `learning/state.md`。
4. `python3 scripts/build_site.py`，`git add -A`、commit、push 到 main。

## 守則
- 只根據本週已發布內容整理，不編造。
- 繁體中文，白話。
