Hướng dẫn chạy website

## Chạy trên Windows

Mở PowerShell hoặc Command Prompt tại thư mục gốc của dự án và chạy:
```powershell
cd web
python -m venv .venv
.\.venv\Scripts\activate
python -m pip install --upgrade pip
python -m pip install -r requirements.txt
```

## Cài đặt trên macOS/Linux
Mở Terminal tại thư mục gốc dự án, sau đó chạy:

```bash
cd web
python3 -m venv .venv
source .venv/bin/activate
python -m pip install --upgrade pip
python -m pip install -r requirements.txt
```

## Mở website
Khi đã set up đầy đủ các thư viện cần thiết, để chạy website sử dụng lệnh sau:
```bash
python main.py
```

