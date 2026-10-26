# 每日 AI 日報：產出流程與撰寫規範

目標：產出今天這一期 `data/digests/YYYY-MM-DD.json`，建置網站並推送到 main（GitHub Pages 會自動發布 `docs/`）。

## 步驟
1. `python3 scripts/fetch.py` → `data/candidates-今天.json`（官方部落格、HN、HF Papers、Latent Space／Import AI／TLDR 電子報）。
2. 以電子報（尤其 Latent Space AINews）為主幹挑題，再去讀官方原文或第一手來源確認細節。被擋（403）的網站改用 RSS 摘要並註明。
3. 讀 `data/digests/` 最新一期當格式範本，並讀 `learning/profile.md`（讀者設定）、`learning/state.md`（學習進度）、`learning/curriculum.json`（四週路徑）。
4. 寫 `data/digests/YYYY-MM-DD.json`，`issue` = 前一期 + 1。同一天已存在就覆寫。
5. 更新 `learning/state.md`：把今天的課加進「已完成課程」。
6. `python3 scripts/build_site.py`，確認輸出 built 行無錯誤。
7. `git add -A && git commit -m "第 N 期 YYYY-MM-DD" && git push origin main`。

## JSON 欄位
`items[]`：`id`（英文短代號，網址錨點用）、`cat`、`emoji`、`src`（來源・日期）、`title`、`what`（發生什麼）、`plain`（白話解釋）、`why`（為什麼重要）、`deep`（`[["小標","內文"],...]` 完整解析，4 到 7 段）。
`impact`（每則必填）：`{"level":"use|watch|skip","text":"對你的影響","action":"具體可做的一件事（skip 可留空）"}`。依 `learning/profile.md` 推理，推論要寫「（推測）」；與讀者無關就 skip，不硬湊；`use` 要給可立即做的具體動作與指令。
頂層 `lesson`（每期必填）：`{title, minutes, why_today, sections:[[小標,內文]], practice:[步驟], claude_prompt, example(可選), sources:[名稱]}`。
`terms[]`：`["名詞","一句話"]`，涵蓋本期出現的專有名詞，6 到 12 個。
`cat` 可用：模型發布、政策安全、資安、產業觀點、硬體、研究、工具（新增類別需同步改 `scripts/build_site.py` 的 `CATS`）。

## 讀者與風格
- 讀者：AI 軟體工程師，CV／機器人感知背景，通常不會點進原文，所以每則要自成一體且有深度。（公開 repo，不要寫真名或公司名）
- 繁體中文；每期 5 到 6 則；第一則放當天最重要的。
- 每則：`what` 講具體事實與數字、`plain` 假設第一次聽、`why` 講跟讀者有什麼關係；`deep` 要比電子報更完整（背景、細節、第三方評測、社群反應、觀察點）。
- 不放 YouTube 推薦與原文連結，標題後註明來源與日期。
- 選題偏好：模型與產品發布、AI 公司政策與做法較受喜歡；晶片與硬體部署細節每期最多 1 則；每期盡量有 1 則與電腦視覺、機器人或實用開發工具相關；開發者資安警訊重要時要放。

## 內容守則
- 只寫讀過來源的事；只看標題就明說，不下結論。
- 官方或廠商自己公布的數字要註明是官方說法；缺第三方驗證就說。
- 沒讀到的部分（例如沒看圖表、沒讀留言）要說明。
- 不編造數字、日期、連結、版本號。
- 若當天沒有足夠有價值的新聞，寧可少於 5 則，不要湊數。

## 今日一課（lesson）
- 從當天新聞延伸**一個概念或工具**，優先銜接 `curriculum.json` 中 status 為 current 的那一週；當天新聞重大且與讀者日常工具直接相關時才插隊，並在 `state.md` 註明。
- 約 800 到 1200 字：是什麼、為什麼、怎麼運作、10 分鐘小實作。`practice` 4 到 5 步；`claude_prompt` 是可直接貼給 Claude Code 的完整指令。
- 準確性：指令、參數、檔案路徑必須來自讀過的官方文件；能在環境執行的先實際跑過；沒跑過要寫「未實際執行」或「我沒有驗證」；不編造 API 與版本號。
- 課文用繁體中文，白話，假設第一次聽到。

## 選題多元化
- 同一家公司一期最多 2 則，除非有重大事件。不要整期都是同一家。
- 以 Latent Space、Import AI 當主幹，官方部落格補細節。
- 每期盡量有 1 則電腦視覺／機器人／實用開發工具相關（可看 arXiv cs.RO、cs.CV、HF Papers）。
