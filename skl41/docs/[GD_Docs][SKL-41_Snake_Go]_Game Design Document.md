# \[GD\_Docs\]\[SKL\-41\_Snake\_Go\]\_Game Design Document

# 🔹 Tổng Quan về Snake Escape

---



- **Tên game**: Snake Escape

- **Thể loại** : Puzzle, casual, hypercasual

- **Platform**: iOS, Android





# **GAME MECHANIC**

### **OVERVIEW**

**Theme**: Snake

**Control**: Tap lên các con rắn để di chuyển chúng ra khỏi board

**Mechanic**: 

- Con rắn có thể di chuyển ra khỏi board nếu đường đi **không bị chặn bởi bất kỳ con rắn nào khác**\.

    - Con rắn di chuyển theo hướng nhìn của đầu rắn

    - Nếu cùng 1 lúc có nhiều con rắn có available move cùng di chuyển thì chúng có thể cắt nhau

- Nếu đường đi bị chặn, con rắn sẽ **quay lại vị trí ban đầu** và hiển thị **animation bị choáng**\.

- Mỗi lần một con rắn bị choáng sẽ **trừ 1 tim,** nếu tap lại vào con rắn đang bị choáng mà **vẫn không thể di chuyển**, thì **không trừ thêm tim**\.


**Win \| Lose Condition: **

- Win: Di chuyển toàn bộ rắn ra khỏi board

- Lose: Hết tim \(heart\)



### **CORELOOP**

### BOOSTERS

#### **Grid**

- Sử dụng Free dạng Toggle ON\|OFF

    - Khi ở trạng thái **ON**, tại đầu mỗi con rắn của tất cả rắn trên màn sẽ hiển thị **một đường kẻ định hướng**, follow theo hướng nhìn của con rắn\.

    - Khi ở trạng thái **ON, **nếu 1 con rắn di chuyển được xác nhận ra khỏi board thì grid sẽ chuyển sang trạng thái **OFF**

    - Khi ở trạng thái **ON, **nếu rắn đang bị choáng thì đường kẻ của hướng đi của con rắn đó sẽ có màu đỏ


#### **Hint**

- Mỗi lần sử dụng cần **xem 1 Reward Ad**\.

- Sau khi kích hoạt thì sẽ ẩn button booster **Hint**

- Bình thường, **button booster Hint** sẽ **không hiển thị** trên màn chơi cho đến khi đạt điều kiện trigger

    - Điều kiện trigger:

        - Sau khi **hoàn tất đưa 1 con rắn ra khỏi board**, nếu** 10 giây tiếp theo không có thao tác nào khác**\.

        - Sau khi **di chuyển rắn không thành công **bị **trừ 1 tim \(heart\)**, nếu **10 giây tiếp theo không có thao tác nào khác**\.

- Visual: Chọn 1 con rắn có available move

    - Chọn **1 con rắn có available move** và **highlight hướng di chuyển** của nó bằng **màu xanh neon**\.

    - Highlight **viền của con rắn** bằng **màu xanh neon**, kèm hiệu ứng **breathing** \(nhấp nháy nhẹ\)\.

- Sau khi kích hoạt booster, đợi tới khi hành động tiếp theo xảy ra để kích hoạt trigger

- Trong lúc đang kích hoạt booster vẫn có thể move các con rắn khác



# **UI/UX**

### Animation/Transition **Reference**

#### Loading Screen

- Screen loading Skylink Studio

- Screen loading đầu game:

    - Logo game xuất hiện lần lượt: Snake \-\> Go

    - Dạng anim: Scale to \(10\-20%\) \-\> Scale nhỏ 10\-20% \-\> Về trạng thái ban đầu 

    - Thanh tiến trình loading fill xanh cho đến khi đầy thanh

- Screen loading gameplay:

    - Logo game xuất hiện lần lượt: Snake \-\> Go

    - Dạng anim: Scale to \(10\-20%\) \-\> Scale nhỏ 10\-20% \-\> Về trạng thái ban đầu 

    - Thanh tiến trình thay bằng chữ Loading\.\.\.


#### FTUE Tap

- Start Level 1

- Hiển thị text "Tap to move" nằm phía trên hình bàn tay có anim đang tap liên tục vào con rắn chính giữa level

- Trong lúc hiển thị nếu tap vào bất kì con rắn nào để move hoặc di chuyển màn hình thì tắt text và anim bàn tay

\[2\.mp4\]

#### FTUE Zoom

- Start level 6

- Hiển thị text "Pinch to zoom" nằm phía trên 2 hình bàn tay trái và phải đang chỉ ngón tay vào màn chơi

- Sau khi trigger được hành động zoom của User thì tắt text và anim 2 bàn tay

\[4\.mp4\]

#### FTUE Grid

- Start level 10

- Hiển thị text "Tap to view Grid" nằm phía trên hình bàn tay có anim đang tap liên tục vào button Grid

- Text và anim sẽ xuất hiện liên tục cho đến khi Button Grid được tap và kích hoạt Grid thì text và anim sẽ biến mất

\[6\.mp4\]

#### Tap Button

- Khi tap vào, button sẽ scale nhỏ lại \(10\-20% \- thông số có thể điều chỉnh\), tâm ở center

- Khi thả ra:

    - Nếu tay còn trên vùng button: button scale về lại trạng thái ban đầu \-\> process tính năng của button

    - Nếu tay kéo ra khỏi vùng button: button scale về lại trạng thái ban đầu \-\> không có process gì diễn ra

\[Button\-Click\-1\.mp4\]

\[Button\-Click\-2\.mp4\]

#### Show Popup

- Popup xuất hiện, BG có dark overlay 80%

- Animation: Xuất hiện fullscreen \(có overlay\) \-\> popup Scale to \(5%: Điểm X\) \-\> popup Scale nhỏ \(5%: Điểm Y\) \-\> về trạng thái ban đầu

\*Lưu ý: tất cả các số % đều có thể điều chỉnh được

\[Show\-popup\.mp4\]

#### AD Break

\[7\.mp4\]

#### Hard \| Super Hard Level

- Khi vào level, camera sẽ ở vị trí zoom out 50% và banner level Hard \| Super Hard ở giữa màn hình theo chiều dọc

- Khi kích hoạt, camera sẽ zoom màn hình về vị trí default 100%

- Trong lúc Zoom In, banner level Hard \| Super Hard sẽ liên tục nhấp nháy và biến mất khi camera ở vị trí default

\[5\.mp4\]

\[8\.mp4\]

#### Win Confetti

- Sau khi con rắn cuối cùng được move khỏi màn hình, delay 0,5s và bắn confetti lên cùng với dòng text khen thưởng

\[3\.mp4\]

#### Remove Ads Popup \| Remove Ads Icon

\[9\.mp4\]

\[icon\.mp4\]



#### Scroll Level Map \| Slide Tab

- Level hiện tại được neo lại, khi kéo dạng drag để xem level khác nhưng thả tay ra sẽ chạy về level hiện tại

- Vuốt tay qua bên phải hoặc tap vào Icon Daily Challenge để chuyển sang tab Daily Challenge \(chưa có Daily Challenge nên chưa cần làm\)

\[video19\.mp4\]

#### Model Snake

- Dạng Idle con rắn nhìn qua lại và nhắm mở mắt, thêm anim thè lưỡi\. Đảm bảo random kích hoạt anim tự nhiên, các con rắn cùng lắc đầu không cùng 1 thời điểm

\[video20\.mp4\]

- **Khi tap vào rắn:**

    - Phần đầu vừa di chuyển vừa uốn lượn nhẹ\.

    - Tạo gợn sóng nước nhẹ để lại ở sau khi rắn di chuyển


\[Water\_fx\.mp4\]

- Con rắn bị choáng có 2 mắt hình xoáy đang xoay, có 3 ngôi sao quay trên đầu rắn, đầu rắn lắc xoay theo hình tròn và highlight viền con rắn bằng màu đỏ nhấp nháy breathing

\[video20\.mp4\]



### Flow Game

### Asset List




# **Game Engagement \(incoming\)**

- Visual

- Animation

- VFX

- SFX: 

- Camera

- Haptic

# **Monetization \(incoming\)**

- IAA

- IAP

# **Notification \(incoming\)**

# **Tracking \(incoming\)**



