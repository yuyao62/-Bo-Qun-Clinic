# 博群診所｜看診進度

提供給客人查看的獨立網站。正式診所名稱為「博群診所」。顯示原站的目前看診號碼、等待人數、原站最後更新及本站擷取時間，附電話、地址、導航與原始候診查詢連結。

## 上傳 GitHub（一次設定）

1. 建立新的公開 repository，建議命名 `Bo-Qun-Clinic`，預設分支使用 `main`。
2. 解壓縮本套件，將內容放在 repository 根目錄。請確定 `.github/workflows/pages.yml` 也有上傳，勿只傳 ZIP 或 `index.html`。
3. 開啟 **Settings → Pages → Build and deployment → Source**，選 **GitHub Actions**。
4. 開啟 **Actions → 更新候診數字並部署網站 → Run workflow**。第一次部署成功後，Pages 設定頁會提供網站網址。
5. 此後排程約每 5 分鐘擷取數字並重新部署。網頁每 60 秒讀取發布的 JSON；「重新讀取」只重讀最近發布的資料，不會直接執行擷取排程。

若帳號為 `yuyao62` 且 repository 為 `Bo-Qun-Clinic`，成功啟用後預期網址為 `https://yuyao62.github.io/Bo-Qun-Clinic/`。套件提供不代表此網址已上線。

GitHub Actions 排程會延遲或跳過，不能保證每 5 分鐘準時。公開 repository 連續 60 天無活動可能自動停用排程，請在 Actions 檢查並重新啟用。需要更即時的資訊請使用頁面的原站連結。

## 資料方式

來源：使用者提供的 https://wroom.vision.com.tw/MainPage/ClinicInfo.aspx?CliID=QCpjCdqyOd8V%2buKpwwfjbg==

來源頁面由 JavaScript 載入數字。Python 先讀取該頁確認「博群診所」，再呼叫同頁使用的匿名公開候診查詢（GetWaitInfo），只保留候診欄位。不需密碼、金鑰或病患資料。不使用頁面其他功能的授權值。

- 原站 `RTime` 對應「門診序／目前看診號碼」，`WRecs` 對應「等待人數」，不相減推算。
- 原站 `RTime=XXXX` 時，依原站行為清空數字，顯示「—」，不把 `WRecs=0` 當成現況。
- 原站資料或擷取時間超過 15 分鐘即隱藏數字，提醒使用者到原站確認。
- 查詢失敗或來源欄位變動時，發布無資料狀態，不捏造數字；原站最後更新與本站擷取時間分別顯示。
- 初始 `queue.json` 是製作套件時的真實擷取快照，並非持續更新服務。必須完成上述 Actions 設定。

診所地址：基隆市中正區新豐街446號；電話：02-2460-1356。
地址電話參考：基隆市中正區衛生所醫療資源 https://www.klchb.klcg.gov.tw/tw/klchbkljj/1093.html

## 本機檢查

僅需 Python 3.12，沒有第三方套件。

```sh
python -m unittest discover -s tests
python scripts/fetch_queue.py --output dist/queue.json
python -m http.server 8000 --directory dist
```

網站內容在 `dist/index.html`，不是藥局原本的 `index.html`。兩個網站請使用不同 repository。

GitHub 官方說明：
- https://docs.github.com/en/pages/getting-started-with-github-pages/using-custom-workflows-with-github-pages
- https://docs.github.com/en/actions/reference/workflows-and-actions/events-that-trigger-workflows#schedule
