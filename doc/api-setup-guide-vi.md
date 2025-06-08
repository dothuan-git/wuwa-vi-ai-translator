# 🔑 Hướng Dẫn Thiết Lập API Key

Để kích hoạt tính năng nhận diện văn bản chính xác và dịch AI chất lượng cao trong **Wuwa AI Vietnamese Translator**, bạn cần có **hai API key** sau:

- ✅ **Groq API Key** — dùng cho dịch thuật bằng GenAI
- ✅ **Google Vision API Key** — dùng để nhận diện văn bản (OCR)


## 1. Groq API Key (dịch bằng LLaMA 3)

Đây là key **bắt buộc** để sử dụng tính năng dịch bằng AI.

### 🛠️ Các bước lấy Groq API Key:

1. Truy cập [https://console.groq.com/keys](https://console.groq.com/keys)  
   ![image](https://github.com/user-attachments/assets/124cf025-2c83-4fbc-932e-77469a505714)

2. Đăng nhập hoặc tạo tài khoản miễn phí trên Groq  
   ![image](https://github.com/user-attachments/assets/c8b4c76a-2298-4270-a7de-6e958338d8fd)

3. Nhấn **Create API Key** — bạn có thể đặt tên tùy ý  
   ![image](https://github.com/user-attachments/assets/3b0bba33-9831-4675-a0ff-00e7a5b02a9e)

4. Sao chép API key vừa tạo  
   ![image](https://github.com/user-attachments/assets/45d720f5-048f-40c0-955a-bd69957f506f)


## 2. Google Vision API Key (OCR) — có thể bỏ qua nếu không sử dụng

Key này **không bắt buộc** nhưng **rất khuyến khích** nếu bạn muốn tăng độ chính xác khi nhận diện văn bản trong game.  
- Video hướng dẫn: https://youtu.be/zF27tW5bEMY

### 🛠️ Các bước lấy Google Vision API Key:

1. Truy cập [Google Cloud Console](https://console.cloud.google.com/) và đăng nhập bằng tài khoản Gmail  
   ![image](https://github.com/user-attachments/assets/90594469-021f-4b49-9766-5c489adcb10f)

2. Nhấn chọn dự án (Project) ở góc trên, rồi tạo **New Project** – tên đặt tùy ý  
   ![image](https://github.com/user-attachments/assets/f1297e3e-a411-4f41-bc25-5bdfbca9f6b6)

3. Sau khi tạo, vào mục **APIs & Services**  
   ![image](https://github.com/user-attachments/assets/f99bc319-c4d0-475b-a74a-6ef8bebf7ca3)

4. Tìm kiếm `Vision API` và nhấn **Enable**  
   ![image](https://github.com/user-attachments/assets/3f83bef4-26f9-42c5-879e-0eb31815bb6c)

5. Vào **APIs & Services > Credentials** ở menu bên trái  
   ![image](https://github.com/user-attachments/assets/a1410936-1ad7-43a3-848f-4b50100f4c55)

6. Nhấn **Create Credentials > API Key**  
   ![image](https://github.com/user-attachments/assets/19469fc9-c0aa-47d4-9dee-8b2931cd34e7)

7. Một cửa sổ hiện ra, sao chép API key của bạn  
   ![image](https://github.com/user-attachments/assets/194659ec-5232-4ad7-9f6f-6a993f5736e6)

8. ✅ **Kích hoạt thanh toán (Billing)** cho dự án:
   - Mỗi tháng được miễn phí **1.000 yêu cầu OCR**.
   - Vượt quá sẽ tính phí khoảng **1,50 USD mỗi 1.000 yêu cầu**.
   - Bạn **sẽ không bị tính phí** nếu không vượt giới hạn miễn phí.  
   ![image](https://github.com/user-attachments/assets/ba5fca06-e6ab-4361-83a2-d2863bcd7418)

9. Tạo tài khoản thanh toán và thêm thẻ tín dụng hoặc thẻ ghi nợ.  
   ![image](https://github.com/user-attachments/assets/f071ad6a-88ca-46bd-847f-7de3bcb4329d)


### 🔽 Nhập API Key vào ứng dụng:

- Mở ứng dụng và nhấn nút **`Config`**
- Dán API key vào ô **GOOGLE VISION API_KEY**


## 💾 Bước Cuối: Lưu Cấu Hình

Sau khi nhập cả hai key API:
- Nhấn nút **Save** trong cửa sổ cài đặt.


## 🧩 Khắc phục sự cố

Nếu bạn gặp lỗi (ví dụ lỗi trong cửa sổ dòng lệnh):

- Kiểm tra lại xem API key có hợp lệ và đã được dán đúng chưa.
- Đảm bảo có kết nối Internet.
- Nếu sử dụng Google Vision, hãy chắc chắn rằng **Billing đã được bật**.


Chúc bạn có trải nghiệm dịch mượt mà và chất lượng với **Wuwa AI Translator** 🇻🇳✨
