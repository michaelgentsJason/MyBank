import os
from pathlib import Path

# 基础目录
BASE_DIR = Path(__file__).resolve().parent.parent

# 环境设置
ENV = os.getenv("ENV", "development")

# SSL证书路径
SSL = {
    "enable": ENV != "development",
    "cert_file": os.path.join(BASE_DIR, "certs", "cert.pem"),
    "key_file": os.path.join(BASE_DIR, "certs", "key.pem"),
}