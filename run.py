import uvicorn
from api.main import app
from config.setting import SSL

if __name__ == "__main__":
    if SSL["enable"]:
        # Production Environment use HTTPS
        uvicorn.run(
            "api.main:app",
            host="0.0.0.0",
            port=443,
            ssl_keyfile=SSL["key_file"],
            ssl_certfile=SSL["cert_file"]
        )
    else:
        # 开发环境使用HTTP
        uvicorn.run(
            "api.main:app",
            host="0.0.0.0",
            port=8000,
            reload=True
        )