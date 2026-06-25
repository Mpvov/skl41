# Bản Thiết Kế Hệ Thống Biểu Đồ So Sánh Level Funnel

Tài liệu này tổng hợp toàn bộ quyết định thiết kế biểu đồ trực quan hóa dữ liệu từ `sample.csv` nhằm phục vụ việc đánh giá hiệu năng giữa 2 phiên bản ứng dụng (VD: Build A vs Build B).

## 1. Tóm tắt mục tiêu (Understanding Summary)
*   **Mục đích:** Xây dựng bộ biểu đồ chuyên sâu để so sánh hành vi người chơi, độ khó, và hiệu quả kiếm tiền giữa các phiên bản build dọc theo chiều dài các level.
*   **Người dùng mục tiêu:** Product Managers, Game Designers, Data Analysts.
*   **Khó khăn chính:** Hàng trăm level với dữ liệu thưa dần ở cuối phễu.
*   **Non-goals:** Đây là tài liệu thiết kế (Specification), chưa đi vào chi tiết source code vẽ biểu đồ.

## 2. Giả định & Rủi ro (Assumptions & Risks)
*   **Công cụ vẽ:** Sử dụng `Matplotlib` / `Seaborn` trong Python theo tiêu chuẩn.
*   **Chuẩn bị Dữ liệu:** Dữ liệu đã có thêm nhãn/cột phân loại phiên bản (ví dụ: `build_version`) để làm Dimension phân nhóm.
*   **Rủi ro:** Các level cao (VD: > 100) có rất ít user (chỉ vài user), khiến cho tỷ lệ % như Pass Rate hoặc Win Duration dao động nhiễu. **Cách giải quyết:** Áp dụng Rolling Average (Trung bình trượt) hoặc làm mờ dải tín nhiệm (Confidence Interval).

## 3. Nhật ký Quyết định (Decision Log)

| Quyết định | Phương án thay thế đã xét | Lý do lựa chọn |
| :--- | :--- | :--- |
| **Cách tổ chức tổng thể** | Dense Heatmap, Scatter Clustering | Chọn **Story-Driven Sequential Notebook** vì nó giúp tạo ra một luồng kể chuyện logic từ tổng quan (Funnel) đến chi tiết (Difficulty) và kinh tế (Monetization), phù hợp nhất cho Stakeholders. |
| **So sánh Funnel Drop** | So sánh 2 line Funnel Rate tuyệt đối | Vẽ thêm **Drop-off Delta (Bar Chart)** để làm nổi bật ngay lập tức level nào đang gây thất thoát người chơi nhiều nhất ở bản build mới. |
| **So sánh Win Duration** | Chỉ lấy số trung bình (Mean) | Dùng **Dải Ruy-băng (Ribbon chart) p50 đến p90** để tránh bị outlier (user treo máy) làm sai lệch nhận định về thời gian chơi. |
| **Tracking Resource** | Line chart thông thường | Dùng **Overlapping Area Chart** giữa Source (nhận) và Sink (tiêu) để dễ dàng nhìn ra sự lạm phát (khoảng trống lồi lên) hoặc khan hiếm (khoảng trống lõm xuống) của tài nguyên. |

## 4. Chi tiết Thiết kế Biểu đồ (Final Design)

### Phần 1: Funnel & Churn (Sức khỏe người chơi)
1. **Cumulative Funnel Rate:** Line chart kép thể hiện % sống sót của tập người chơi theo level.
2. **Level-specific Drop-off Delta:** Bar chart thể hiện sự chênh lệch (Build B - Build A) về tỷ lệ rơi rụng ở từng level.
3. **Level Continue Rate Trend:** Line chart (có rolling average) thể hiện độ "cuốn" của game, tỷ lệ user chơi tiếp ngay lập tức sau khi thắng.

### Phần 2: Difficulty & Engagement (Độ khó & Trải nghiệm)
1. **1st Attempt Win Rate Delta:** Diverging Bar chart (Đỏ/Xanh) phát hiện ngay level nào bị làm khó lén khiến user không thể qua ngay lần đầu.
2. **Fail Rate & Attempts:** Dual-Axis Line chart đo lường sự kiên nhẫn. Fail rate cao nhưng Attempts cao = Trải nghiệm vượt khó tốt.
3. **Average Progress upon Failure:** Line chart đánh giá mức độ tiến triển khi thua (tiến gần đến đích hay thua ngay từ đầu).
4. **Win Duration Spectrum:** Ribbon chart (p50-p90) kiểm tra xem thời gian qua màn có bị kéo dài lê thê không.

### Phần 3: Monetization & Resource Economy (Dòng tiền & Tài nguyên)
1. **ARPU & Ad ARPU Curve:** Line chart kép kiểm tra đỉnh doanh thu.
2. **Cumulative Impressions (RW & IS):** Line/Step chart với 2 mảng màu để xem Build nào tích lũy được vòng đời quảng cáo tốt hơn.
3. **Resource Source vs Sink Balance:** Area chart kiểm soát cung-cầu của Hint, Wand, Eraser, Grid.
4. **T1 vs T2 Ad Quality Mix:** 100% Stacked Bar chart theo dõi tỷ trọng người dùng xem quảng cáo có giá trị cao (Tier 1) so với Tier 2.
