# Wuwa AI Vietnamese Translator

**Wuwa AI Vietnamese Translator** là một ứng dụng phi lợi nhuận do người hâm mộ phát triển, nhằm dịch lời thoại và lời dẫn truyện từ game *Wuthering Waves* từ tiếng Anh sang tiếng Việt. Ứng dụng kết hợp công nghệ OCR (Nhận diện ký tự quang học) và AI sinh ngôn ngữ tiên tiến để mang đến bản dịch mượt mà và chính xác, giúp nâng cao trải nghiệm chơi game của bạn.


## 🎮 Tính năng

1. **Chụp và Dịch**: Chụp nhanh văn bản tiếng Anh trên màn hình và dịch bằng AI.
2. **Dịch lại**: Tinh chỉnh bản dịch (không tốn lượt sử dụng Google OCR).
3. **Nhập tay**: Xem hoặc chỉnh sửa văn bản tiếng Anh được nhận dạng trước khi dịch.
4. **Công cụ OCR**:
    - EasyOCR (mặc định, offline, hoàn toàn miễn phí – chậm hơn và độ chính xác *hơi* thấp hơn).
    - Google Vision OCR (online, độ chính xác cao hơn, cần API key – vui lòng **đọc kỹ** phần ghi chú bên dưới nếu muốn dùng).
5. **Nhật ký lịch sử**: Hiển thị/ẩn lịch sử bản dịch.
6. **Xuất lịch sử**: Xuất nhật ký dịch ra file `.txt` (có thể dùng để tóm tắt cốt truyện bằng ChatGPT).
7. **Tùy chỉnh đại từ nhân xưng tiếng Việt (Beta)**: Tự động thay đổi đại từ phù hợp khi nhân vật nói với Rover.
8. **Prompt tùy chỉnh**: Tùy biến cách AI dịch bằng hướng dẫn riêng.
![guidance](https://github.com/user-attachments/assets/d7c0ddee-6a53-4ddd-b496-07e226da6379)


## 🧩 Yêu cầu hệ thống

- Hệ điều hành Windows  
- Kết nối Internet ổn định  
- [Groq API Key](https://console.groq.com/keys) — để dịch bằng AI (**Miễn phí**)  
- [Google Cloud Vision API Key](https://cloud.google.com/vision/docs/setup) — tuỳ chọn, để tăng độ chính xác OCR (**Cần đọc kỹ để sử dụng miễn phí**)  
   - Yêu cầu thẻ credit/ debit để kích hoạt  
   - Xem ghi chú bên dưới để tránh bị tính phí

### 📌 Ghi chú về Google Vision API:

- Google cung cấp **3 tháng miễn phí** cho tài khoản mới.
- Sau đó, bạn có **1.000 lượt OCR miễn phí mỗi tháng**.
- Vượt quá hạn mức này, mỗi 1.000 lượt tiếp theo có giá khoảng **1,50 USD**.
- Bạn **sẽ không bị tính phí** nếu không vượt giới hạn miễn phí.
- **Mẹo sử dụng**: Với nhu cầu đọc cốt truyện, hạn mức 1.000 lượt mỗi tháng là đủ.
- Nếu cần thêm, bạn có thể dùng một tài khoản Google khác để lấy thêm API key và tận dụng lượt miễn phí mới.

> 💡 Mẹo: Nếu chỉ cần chỉnh lại bản dịch, hãy dùng nút **Re-translate** thay vì **Translate $** lại để tiết kiệm lượt OCR.


## 🛠️ Hướng dẫn sử dụng

1. **Tải về và cài đặt**
   - Truy cập [Releases Page](https://github.com/dothuan-git/wuwa-vi-ai-translator/releases) để tải phiên bản mới nhất.
   - Nhấn chuột phải vào `GioHuAI_Setup.exe` và chọn **"Run as administrator"**.
   - Có thể chọn tạo lối tắt ngoài desktop để mở nhanh hơn.

2. **Thiết lập ban đầu (Quan trọng)**
   - Mở ứng dụng.
   - Nhấn nút `Config` ở góc dưới bên phải cửa sổ chính.
   - Điền các thông tin:
     - **Google Vision API key** (không bắt buộc nhưng khuyến nghị dùng để cải thiện độ chính xác).
     - **Groq API key** (bắt buộc để dịch bằng AI).
     - Prompt tùy chỉnh nếu muốn.
     - Tên và giới tính của Rover (để cá nhân hoá đại từ).

   > Tham khảo [hướng dẫn này](https://github.com/dothuan-git/wuwa-vi-ai-translator/blob/main/doc/api-setup-guide-en.md) để biết cách lấy API key.

3. **Bắt đầu dịch**
   - Di chuyển khung xanh trong suốt sao cho bao phủ văn bản tiếng Anh trong game.
   - Nhấn **"Translate $"** để chụp và dịch.
   - Sử dụng **"Re-translate"** để dịch lại bản dịch hiện tại.

