from app.cli import main

import zipfile
import json



if __name__ == "__main__":
    main()
    # model_path = './model/fold_3.keras'  

    # with zipfile.ZipFile(model_path, 'r') as zip_ref:
    #     # Đọc file cấu hình định dạng json bên trong file mã nguồn
    #     config_bytes = zip_ref.read('config.json')
    #     config_data = json.loads(config_bytes.decode('utf-8'))
        
    #     # Lấy thông tin phiên bản
    #     keras_version = config_data.get('keras_version')
    #     backend = config_data.get('backend') # Keras 3 thường lưu cả backend (tensorflow, jax, torch)

    # print(f"File được lưu bằng Keras phiên bản: {keras_version}")
    # if backend:
    #     print(f"Backend sử dụng: {backend}")

