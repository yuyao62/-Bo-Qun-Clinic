# 博群診所｜看診進度

網站：https://yuyao62.github.io/-Bo-Qun-Clinic/

## 候診數字

首頁顯示目前看診號碼、等待人數及資料時間。`scripts/fetch_queue.py` 使用原站同一個匿名公開候診查詢，只保存公開候診欄位。`XXXX` 不顯示為 0 人，資料超過 15 分鐘會隱藏數字。

`.github/workflows/update-queue.yml` 在推送程式、手動執行及約每 5 分鐘排程時更新 `queue.json`。不需要額外密碼或金鑰。網頁從本儲存庫的公開 Raw 資料讀取最新 JSON，避免資料更新後仍讀到舊的 Pages 部署。頁面每 60 秒重新讀取，排程與快取都可能延遲；最新情況仍請查看原站。

保留現有 Pages 設定：**Deploy from a branch → main → /(root)**。不需改為 GitHub Actions 建置。若排程停用，可在 Actions → 更新博群診所候診資料 重新啟用或手動 Run workflow。公開儲存庫長時間無活動時 GitHub 可能停用排程。

不要只上傳 `index.html`：`queue.json`、`scripts`、`tests` 與 `.github/workflows` 都需要保留。

原站：https://wroom.vision.com.tw/MainPage/ClinicInfo.aspx?CliID=QCpjCdqyOd8V%2buKpwwfjbg==

## 門診表

醫師姓氏班表依使用者提供的 2025-02-03 Facebook 公告整理，頁面標示日期及以最新公告為準。看診時段依使用者提供的原候診頁面：早 08:30–12:00、午 14:30–18:00、晚 18:30–21:30。星期日午、晚休診。異動請致電診所確認。

電話 02-2460-1356；地址：基隆市中正區新豐街446號。

## 驗證

```sh
python -m unittest discover -s tests
python scripts/fetch_queue.py --output queue.json
```
