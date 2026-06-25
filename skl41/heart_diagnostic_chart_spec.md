# 🫀 Heart Mechanism Diagnostic — Chart Design Spec

## Hypothesis
> Cơ chế Heart (Lives) ở Build 1.1.0 làm nghẽn luồng chơi → giảm session/retries → giảm IS Impression → giảm Ad Revenue & LTV7.
> RW Impression tăng (do user xem ads hồi tim) nhưng không đủ bù đắp IS bị mất.

## Data Sources

| File | Build | Rows | Key Columns |
|------|-------|------|-------------|
| `level_1_0_11.csv` | Cũ (1.0.11) — KHÔNG có Heart | 810 levels | `is_imp`, `rw_imp`, `cum_avg_is_imp`, `cum_avg_rw_imp`, `ad_is_revenue`, `ad_rw_revenue`, `funnel_rate`, `playing_user`, `level_fail_rate`, `rw_*_imp` breakdown |
| `level_1_1_0.csv` | Mới (1.1.0) — CÓ Heart | 679 levels | Cùng cấu trúc, có thêm `rw_heart_imp` |
| `heart.csv` | Mới (1.1.0) — Chi tiết hết tim | 430 levels | `total_out_of_lives_users`, `out_of_lives_dropped`, `out_of_lives_passed_sameday`, `out_of_lives_passed_later`, `rw_heart_imp`, `rw_home_heart_imp` |

## Constraints
- **Level range hiển thị:** 1–80 (sau level 80, sample size < 50 users, không đủ ý nghĩa thống kê)
- **Library:** Matplotlib + Seaborn (theo rule của user)
- **Boss levels cần highlight:** Level 25, 40, 44 (spike hết tim + fail rate cao nhất)

---

## PHẦN A: Narrative Story Charts (6 charts riêng lẻ)

Mỗi chart kể một phần của câu chuyện, xem theo thứ tự từ 1→6.

---

### Chart A1: Funnel Comparison — "User rớt ở đâu?"

| Thuộc tính | Giá trị |
|-----------|---------|
| **Loại chart** | Dual-line plot |
| **Trục X** | Level (1–80) |
| **Trục Y** | `funnel_rate` (0–1.0) |
| **Series** | Line 1: Build Cũ (1.0.11) — màu xanh dương, Line 2: Build Mới (1.1.0) — màu cam |
| **Annotations** | Vertical dashed lines tại Level 25, 40, 44 với label "Boss Level" |
| **Insight mong đợi** | Funnel Build Mới rớt mạnh hơn tại các boss levels. Gap giữa 2 đường ngày càng rộng sau Level 20 |
| **Title** | "Level Funnel Rate: Build 1.0.11 vs 1.1.0" |
| **Subtitle** | "Cohort D7 | Excl. VN, IN | Level 1–80" |

---

### Chart A2: IS Impression Gap — "Mất bao nhiêu IS?"

| Thuộc tính | Giá trị |
|-----------|---------|
| **Loại chart** | Dual-line plot + Shaded area (fill_between) |
| **Trục X** | Level (1–80) |
| **Trục Y** | `cum_avg_is_imp` (Cumulative Average IS Impressions per user) |
| **Series** | Line 1: Build Cũ — xanh dương, Line 2: Build Mới — cam |
| **Shaded area** | Vùng giữa 2 đường tô màu đỏ nhạt = "IS bị mất" |
| **Annotations** | Arrow annotation tại Level 80 ghi delta: "Δ = X imp/user" |
| **Insight mong đợi** | Build Cũ tích lũy IS nhanh hơn nhiều. Gap bắt đầu rõ từ Level 15–16 (IS placement đầu tiên) và ngày càng doãng ra |
| **Title** | "Cumulative Avg IS Impressions per User" |
| **Note** | Đây là chart quan trọng nhất — trực tiếp chứng minh IS bị giảm |

---

### Chart A3: RW Impression Breakdown — "RW tăng nhờ cái gì?"

| Thuộc tính | Giá trị |
|-----------|---------|
| **Loại chart** | Stacked bar chart (Build Mới only) |
| **Trục X** | Level (1–80, có thể nhóm thành bins nếu quá dày: 1-5, 6-10, 11-15, ...) |
| **Trục Y** | Số lượt RW Impression |
| **Stack layers** | `rw_star_imp` (vàng), `rw_coin_imp` (xám), `rw_heart_imp` (đỏ), `rw_hint_booster_imp` (xanh lá), `rw_eraser_booster_imp` (tím), `rw_wand_booster_imp` (xanh dương), `rw_grid_booster_imp` (cam) |
| **Highlight** | `rw_heart_imp` dùng màu đỏ nổi bật nhất |
| **Insight mong đợi** | Phần lớn RW tăng thêm ở Build Mới đến từ `rw_heart_imp` (user xem ads để hồi tim). Các loại RW khác gần như không đổi |
| **Title** | "RW Impression Breakdown by Type (Build 1.1.0)" |
| **Note** | Nếu bar quá dày, nhóm levels thành bins 5 levels/group |

---

### Chart A4: Heart Behavior Waterfall — "Hết tim rồi làm gì?"

| Thuộc tính | Giá trị |
|-----------|---------|
| **Loại chart** | Stacked bar chart (từ heart.csv) |
| **Trục X** | Level (1–80) |
| **Trục Y** | Số users |
| **Stack layers** | `out_of_lives_dropped` (đỏ đậm — "Bỏ cuộc"), `out_of_lives_passed_sameday` (xanh lá — "Qua ngay"), `out_of_lives_passed_later` (xanh dương — "Quay lại sau") |
| **Secondary axis (optional)** | Line plot: `out_of_lives_rate` = `total_out_of_lives_users / playing_users` (tỷ lệ %) |
| **Annotations** | Highlight Level 25 (78 users), Level 40 (59 users), Level 44 (106 users) — đây là 3 "killing fields" |
| **Insight mong đợi** | Tại boss levels, số user hết tim spike cực mạnh. Phần lớn bị `dropped` (đỏ) = bỏ game luôn, không chịu xem ads hay quay lại |
| **Title** | "Out-of-Lives Behavior by Level (Build 1.1.0)" |
| **Subtitle** | "Stacked: Dropped (Red) | Passed Same Day (Green) | Returned Later (Blue)" |

---

### Chart A5: Revenue Delta — "Tiền mất bao nhiêu?"

| Thuộc tính | Giá trị |
|-----------|---------|
| **Loại chart** | Grouped bar chart (2 nhóm cạnh nhau) |
| **Trục X** | Level (1–80, nhóm thành bins 5 levels nếu cần) |
| **Trục Y** | Revenue ($) |
| **Groups** | Nhóm 1: `ad_is_revenue` (Build Cũ vs Build Mới), Nhóm 2: `ad_rw_revenue` (Build Cũ vs Build Mới) |
| **Color scheme** | IS Cũ: xanh đậm, IS Mới: xanh nhạt, RW Cũ: cam đậm, RW Mới: cam nhạt |
| **Insight mong đợi** | IS Revenue Build Mới thấp hơn đáng kể (đặc biệt từ Level 15 trở đi). RW Revenue Build Mới cao hơn một chút nhưng không đủ bù |
| **Title** | "Ad Revenue Comparison: IS vs RW by Level" |
| **Alternative** | Có thể vẽ `cumulative sum` thay vì per-level nếu muốn thấy tổng tích lũy |

---

### Chart A6: Net Revenue Impact — "Tổng kết: Lời hay Lỗ?"

| Thuộc tính | Giá trị |
|-----------|---------|
| **Loại chart** | Horizontal waterfall chart (hoặc simple bar chart) |
| **Data** | Tổng hợp Level 1–80: `Total IS Revenue Lost` = Σ(IS_old - IS_new), `Total RW Revenue Gained` = Σ(RW_new - RW_old), `Net Impact` = Lost - Gained |
| **Bars** | Bar 1: "IS Revenue Lost" (đỏ, giá trị âm), Bar 2: "RW Revenue Gained" (xanh lá, giá trị dương), Bar 3: "Net Impact" (đen/đỏ tùy dương/âm) |
| **Annotations** | Ghi giá trị cụ thể trên mỗi bar |
| **Insight mong đợi** | Net Impact là số âm lớn → Chứng minh rằng cơ chế Heart đang gây thiệt hại ròng về revenue |
| **Title** | "Net Ad Revenue Impact: Heart Mechanism (L1–80)" |
| **Subtitle** | "IS Lost vs RW Gained = Net Change" |

---

## PHẦN B: Dashboard Grid (1 figure tổng hợp 2x3)

Tất cả 6 subplots trên gộp vào 1 figure lớn `figsize=(24, 14)`.

| Vị trí | Subplot | Dữ liệu |
|--------|---------|----------|
| **(1,1)** | Funnel Old vs New | = Chart A1 (compact version) |
| **(1,2)** | Cum Avg IS Imp Old vs New | = Chart A2 (compact, không shaded area) |
| **(1,3)** | Cum Avg RW Imp Old vs New | Dual-line `cum_avg_rw_imp` cho cả 2 build |
| **(2,1)** | Heart Behavior Stacked | = Chart A4 (compact version) |
| **(2,2)** | IS + RW Revenue per Level | = Chart A5 (compact version) |
| **(2,3)** | Net Revenue Delta bar | = Chart A6 |

**Dashboard Title:** `"Heart Mechanism Diagnostic Dashboard — Build 1.0.11 vs 1.1.0"`

**Dashboard Footer:** `"Cohort: first_open 2026-05-23 to 2026-05-31 | D7 | Excl. VN, IN | App Version: 1.0.11 (Old) vs 1.1.0 (New)"`

---

## PHẦN C: Bonus Charts (Nếu cần đào sâu thêm)

### Chart C1: RW Heart Conversion Funnel
| Thuộc tính | Giá trị |
|-----------|---------|
| **Loại chart** | Funnel / Horizontal bar |
| **Data** | `total_out_of_lives_users` → `rw_heart_imp` (xem ads hồi tim) + `rw_home_heart_imp` (xem ads hồi tim ở home) → `out_of_lives_passed_sameday` (qua được màn) |
| **Insight** | Tỷ lệ chuyển đổi từ "hết tim" → "xem ads" → "qua màn" là bao nhiêu? Nếu thấp = cơ chế Heart không monetize hiệu quả |

### Chart C2: Fail Rate Spike Correlation
| Thuộc tính | Giá trị |
|-----------|---------|
| **Loại chart** | Dual-axis: Bar (`level_fail_rate` Build Mới) + Line (`out_of_lives_dropped / playing_users`) |
| **Insight** | Kiểm tra tương quan: Level nào fail rate cao thì out_of_lives_dropped cũng cao? Nếu correlation mạnh → Heart mechanism khuếch đại tác động tiêu cực của level khó |

### Chart C3: Session Killer — Drop Rate at Boss Levels
| Thuộc tính | Giá trị |
|-----------|---------|
| **Loại chart** | Grouped bar chart, chỉ focus 3 boss levels (25, 40, 44) |
| **Data** | Mỗi boss level: `total users`, `out_of_lives`, `dropped`, `passed_sameday`, `win_dropped`, `lose_dropped` |
| **Insight** | Deep-dive 3 level nguy hiểm nhất. Tại L44: 106/379 users (28%) hết tim, trong đó 63 users (59%) bỏ cuộc luôn |

### Chart C4: Per-Level IS Impression Delta
| Thuộc tính | Giá trị |
|-----------|---------|
| **Loại chart** | Bar chart (positive/negative) |
| **Trục X** | Level (1–80) |
| **Trục Y** | `is_imp_new - is_imp_old` (delta) |
| **Color** | Xanh nếu dương (Build Mới hơn), Đỏ nếu âm (Build Mới kém hơn) |
| **Insight** | Nhìn rõ từng level nào mất IS nhiều nhất. Kỳ vọng: Level 15–16 trở đi toàn đỏ |

### Chart C5: Avg IS Impression per User per Level (Normalized)
| Thuộc tính | Giá trị |
|-----------|---------|
| **Loại chart** | Dual-line |
| **Trục X** | Level (1–80) |
| **Trục Y** | `is_imp / playing_user` (IS per user per level) |
| **Series** | Build Cũ vs Build Mới |
| **Insight** | Normalized theo số user để loại bỏ ảnh hưởng của funnel drop khác nhau. Nếu IS/user vẫn thấp hơn → Không phải do ít user hơn, mà là mỗi user xem ít IS hơn |

### Chart C6: Total RW vs IS Volume Trade-off (Scatter)
| Thuộc tính | Giá trị |
|-----------|---------|
| **Loại chart** | Scatter plot |
| **Trục X** | `rw_imp` (per level) |
| **Trục Y** | `is_imp` (per level) |
| **Points** | Mỗi điểm = 1 level, size = `playing_user`, color = Build (Cũ/Mới) |
| **Insight** | Xem có phải RW và IS trade-off lẫn nhau không (inverse correlation) ở Build Mới |

---

## PHẦN D: Drop Behavior Analysis (Giai đoạn Churn/Drop)

Để trả lời trực tiếp câu hỏi: "Cơ chế Tim có làm drop user nhiều hơn bản cũ không? Và rụng ở đâu?", ta định nghĩa 3 Stage:
- **Early Stage:** Level 1–14 (Chưa có quảng cáo IS).
- **Hard Level Stage:** Bất kỳ level nào thuộc bản 1.1.0 có `avg_attempts > 2.5` hoặc `funnel_rate < 0.5`.
- **Standard Stage:** Các level còn lại.

### Chart D1: Stage-by-Stage Drop Rate Comparison
| Thuộc tính | Giá trị |
|-----------|---------|
| **Loại chart** | Grouped bar chart |
| **Trục X** | 3 Stages (Early, Hard, Standard) |
| **Trục Y** | Tỷ lệ Drop Rate của toàn bộ Stage (`Total Drops / Users entering stage`) |
| **Series** | Build Cũ (Xanh) vs Build Mới (Cam) |
| **Insight mong đợi** | Nhìn rõ "Cụm" nào đang mất nhiều user hơn (đặc biệt là Early Stage). |

### Chart D2: Hard Level Frustration
| Thuộc tính | Giá trị |
|-----------|---------|
| **Loại chart** | Stacked bar chart (chỉ focus vào các Hard Level của Build Mới) |
| **Trục X** | Các level thỏa mãn điều kiện Hard |
| **Trục Y** | Số lượng user drop ở Build Mới |
| **Stack layers** | Thua bình thường (Xám), Mất tim nản nghỉ - `lost_heart_not_out_dropped` (Vàng), Cạn máu nghỉ - `out_of_lives_churned` (Đỏ) |
| **Insight mong đợi** | Giải phẫu tâm lý drop: Bao nhiêu % nghỉ vì cạn sạch máu, bao nhiêu % nghỉ vì mới mẻ 1-2 tim đã ức chế. |

### Chart D3: Cumulative Drop Funnel
| Thuộc tính | Giá trị |
|-----------|---------|
| **Loại chart** | Dual-line plot + Area fill |
| **Trục X** | Level (1–80) |
| **Trục Y** | % Cộng dồn số user đã drop (Tính trên số user tại L1) |
| **Series** | Build Cũ (Xanh) vs Build Mới (Cam). Vùng nằm giữa 2 đường được tô màu đỏ (nếu Mới rớt nhiều hơn) hoặc xanh. |
| **Insight mong đợi** | Trực quan hóa "Lost Volume" (Tổng lượng máu chảy ròng) xuyên suốt cả hành trình. |

### Chart D4: Per-Level Drop Rate Delta Overlay
| Thuộc tính | Giá trị |
|-----------|---------|
| **Loại chart** | Bar chart (positive/negative) + Background Highlights |
| **Trục X** | Level (1–80) |
| **Trục Y** | `Drop Rate Var - Drop Rate Base` |
| **Overlay** | Tô nền xám nhạt (L1-14), Tô nền đỏ mờ dọc theo các Hard Level. |
| **Insight mong đợi** | Quét mắt nhanh: Các cọc đỏ chót vót (Var rớt nhiều hơn) có nằm lọt thỏm trong các vùng nhạy cảm (Early/Hard) hay không. |

### Chart D5: Drop Causality Decomposition (Bằng Chứng Nhân Quả)
| Thuộc tính | Giá trị |
|-----------|---------|
| **Loại chart** | Stacked Bar Chart so sánh 2 cột (Base vs Var) đặt cạnh nhau tại 1 Stage (ví dụ: Hard Levels). |
| **Cột Base (Bản Cũ)** | 1 khối màu Xám: `Base Lose Drop Rate` (`lose_dropped / playing_users`). |
| **Cột Var (Bản Mới)** | Xếp chồng 3 khối: <br>1. Khối Xám (Normal Drop): `(Total Lose Drop - Heart Drop - Out of Lives Drop) / playing_users` <br>2. Khối Vàng (Heart Frustration Drop): `lost_heart_not_out_dropped / playing_users` <br>3. Khối Đỏ (Out of Lives Drop): `out_of_lives_churned / playing_users`. |
| **Insight mong đợi** | Khối màu Xám của bản Mới và bản Cũ có độ cao xấp xỉ nhau, chứng tỏ tỷ lệ drop tự nhiên không đổi. Toàn bộ phần nhô lên cao hơn của bản Mới được đóng góp 100% từ phần Vàng và Đỏ. **$\Rightarrow$ Trực tiếp chứng minh sự dôi ra của Drop Rate là do cơ chế Tim gây ra.** |

---

## Decision Log

| # | Decision | Alternatives | Reason |
|---|----------|-------------|--------|
| 1 | Giới hạn Level 1–80 | Level 1–50 / Level 1–100 | < 50 users không đủ ý nghĩa thống kê, 80 là ranh giới hợp lý |
| 2 | Dùng Matplotlib + Seaborn | Plotly / D3.js | Theo rule user bắt buộc dùng matplotlib/seaborn |
| 3 | Vẽ cả 2 format (Narrative + Dashboard) | Chỉ 1 format | User yêu cầu cả 2 |
| 4 | Boss levels = 25, 40, 44 | Tất cả levels | 3 levels này có spike hết tim lớn nhất (78, 59, 106 users) |
| 5 | Định nghĩa Hard Level | Chỉ xem 3 Boss Level (25,40,44) | Dùng `avg_attempts > 2.5` HOẶC `funnel_rate < 0.5` để cover đủ các nút thắt cổ chai |
| 6 | Combine Stage & Delta | Chỉ dùng Line / Bar | Mix Stage (dễ báo cáo chốt số) và Delta (thấy dòng chảy rụng từng level) |
| 7 | Thêm D5 (Causality) | Sửa D1/D3 | Thêm mới D5 để làm bằng chứng tuyệt đối mà không bỏ đi flow nhìn tổng quan của D1/D3 |

---

## Implementation Priority

| Priority | Charts | Effort |
|----------|--------|--------|
| 🔴 P0 (Must-have) | A1, A2, A4, A6, D1, D3, D5 | Core narrative — Funnel, IS Gap, Heart Behavior, Net Impact, Stage Drop, Cum. Drop, Causality Proof |
| 🟡 P1 (Should-have) | A3, A5, Dashboard B, D2, D4 | Revenue breakdown, Dashboard tổng hợp, Hard Level Stack, Per-Level Delta Overlay |
| 🟢 P2 (Nice-to-have) | C1–C6 | Deep-dive cho Q&A session |
