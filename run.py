import os
# 在导入任何其他模块之前设置环境变量
os.environ["ENV"] = "production"

import uvicorn
from api.main import app
from config.setting import SSL
import os

# 显式打印环境和SSL配置，帮助调试
print(f"Current ENV: {os.getenv('ENV', 'Not set')}")
print(f"SSL enabled: {SSL['enable']}")

if __name__ == "__main__":
    if SSL["enable"]:
        print("Starting in HTTPS mode...")
        uvicorn.run(
            "api.main:app",
            host="0.0.0.0",
            port=8443,  # 使用8443避免需要管理员权限
            ssl_keyfile=SSL["key_file"],
            ssl_certfile=SSL["cert_file"],
            reload=False  # 禁用热重载
        )
    else:
        print("Starting in HTTP mode...")
        uvicorn.run(
            "api.main:app",
            host="0.0.0.0",
            port=8000,
            reload=True
        )