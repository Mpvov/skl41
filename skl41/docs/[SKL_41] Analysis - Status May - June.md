# [SKL_41] Analysis - Status May - June

## Purpose 
Đánh giá status của Snake Go trong 01/05 - 19/06/2026 (7 tuần) để plan cho sprint tiếp theo.

## 🌟 DATA STORYTELLING FLOW
*Tuân thủ tuyệt đối rule của PO: Xem Status tổng quan trước (Phần 1) -> Diagnostic tìm nguyên nhân sau (Phần 2) -> Đề xuất Action (Phần 3).*
*Quy tắc: Không nhìn số absolute. Tất cả các metrics (trừ Installs) đều phải quy về Cohort Weekly Trend.*

---

## Phần 1: Executive Summary (Status Layer)
*Mục đích: Trả lời nhanh gọn "Game đang Tốt lên hay Xấu đi?" dựa trên 4 trụ cột độc lập (chuẩn MECE).*

**1. Bảng KPI Dashboard (Top-line Metrics)**
- **Insight:** Đánh giá bức tranh toàn cảnh (Ví dụ: "Scale sụt giảm nhưng Chất lượng game đang đi lên").
- **Metrics:** Điền số liệu Actual và chỉ số Delta % (Week-over-Week).
- 🛡️ **Rule chống Data Masking:** Nếu US là mục tiêu chiến lược, bảng này bắt buộc chia 3 cột: `Global` | `US` | `ROW` để không bị tệp rác che lấp.

| Pillar (MECE) | Description | Key Metrics (Theo Weekly Cohort) |
| :--- | :--- | :--- |
| **Scale / Acquisition** | Game có dòng user mới không? | New Installs (D0 Users) |
| **Engagement & Retention** | Người chơi có "dính" lấy game không? | Cohort Ret (D1, D3, D7), Avg Session Time |
| **Monetization** | Hiệu quả kiếm tiền trên từng user? | Cohort LTV (D3, D7), ARPDAU |
| **Technical Stability** | Game chạy có mượt không? | ANR Rate, Crash Free Rate |

**2. Top-line Trend Charts (Theo tư duy Less is More)**
- **Insight -> Chart 1:** Đà tăng trưởng của game (Line & Bar Chart kết hợp *Total Installs* và *Total Revenue* theo tuần).
- **Insight -> Chart 2:** Chất lượng của dòng tiền và người chơi (Line Chart thể hiện *D7 Retention* và *D7 ROAS* theo tuần). 
*(Ghi chú: Thêm các vertical lines đánh dấu mốc release build/A-B test để dễ link xuống phần Diagnostic).*

---

## Phần 2: Root Cause (Diagnostic Layer)
*Mục đích: Nếu các chỉ số ở Phần 1 biến động, dùng các "key dimensions" (`Geo`, `Channel`, `Camp`) làm dao mổ để bóc tách.*

### 2.1. Diagnostic for Scale (Quy mô)
- **Insight:** Lượng user mới đổ vào game thay đổi là do dòng Organic tự nhiên hay do action bơm tiền chạy Ads? Tụt ở thị trường nào?
- **Chart:** Stacked Area Chart (New Installs).
- **Slicing Metrics:** Breakdown theo `Channel` (Organic vs Paid) và `Geo` (US vs ROW). Phải nhìn qua `CPI` để đảm bảo UA không lủng phễu.

### 2.2. Diagnostic for Engagement & Retention (Gắn kết & Giữ chân)
- **Insight:** User rời bỏ game do update tính năng dở (Changelog) hay do game quá khó/tutorial rườm rà (Core Gameplay)?
- **Chart 1 (A/B Testing Impact):** Phân tích tác động của các tính năng mới lên Retention. 
  - *⚠️ BẮT BUỘC:* Ở góc chart phải ghi rõ: `Cohort user của A/B:`, `Day diff:`, `Tổng bao nhiêu cohort:`.
- **Chart 2 (Core Gameplay Bottleneck):** 
  - Scatter Plot (Win Rate vs. Churn Rate theo Level) để phát hiện cơ chế Heart (mất tim) có gây Rage quit không.
  - Funnel Chart (Tỷ lệ qua màn Level 1-10) để check Tutorial (Tap/Zoom/Grid) có dễ hiểu không.

### 2.3. Diagnostic for Monetization (Doanh thu)
- **Insight:** Doanh thu giảm là do ép xem ads quá mức (Ad Pressure) hay do user không thèm dùng Booster (Hint/Grid)?
- **Chart 1 (Ad Pressure):** Dual-axis Line Chart (IS imp/DAU vs. D1 Retention) để tìm ngưỡng gãy retention vì quảng cáo.
- **Chart 2 (Booster Economy):** Line Chart (% Cohort User chủ động xem Reward Ads để lấy Hint) breakdown theo từng Level.
- *Check cạm bẫy:* Luôn check `IAP Conversion Rate` để đảm bảo LTV tăng không phải do lệch số bởi vài con "Cá mập" (Whale Skew).

### 2.4. Diagnostic for Technical Stability (Kỹ thuật)
- **Insight:** Nếu ANR tăng, lỗi đến từ bản update nào? Hay thiết bị nào bị dính nhiều nhất?
- **Chart:** Heatmap / Bar Chart (ANR Rate).
- **Slicing Metrics:** Breakdown theo `App Version` và `Device RAM/OS`.

---

## Phần 3: Actionable Insights (Prescriptive Layer)
*Mục đích: "Chốt sale" - Đề xuất task thực tế cho PO & Dev team trong Sprint tới.*

- **Ví dụ Insight:** "Scale giảm nhưng không đáng lo vì nguyên nhân do cắt budget UA. Tuy nhiên D1 Retention đang rớt thảm hại ở bản build v1.2 do lỗi ANR trên máy RAM 2GB."
- **Ví dụ Action:** "Dev team ưu tiên số 1 fix memory leak. Team UA chưa scale up budget cho đến khi fix xong lỗi này."
