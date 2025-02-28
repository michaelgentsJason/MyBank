from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from api.v1 import auth, users, accounts, transactions
from api.v1 import blockchain
from api.v1 import message

app = FastAPI(title="MyBank API", version="1.0.0")

# Add CORS Middelware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["https://Mybankdomain.com", "https://app.Mybankdomain.com"],
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "DELETE"],
    allow_headers=["Authorization", "Content-Type"],
)

# 注册路由
app.include_router(auth.router, prefix="/api/v1/auth", tags=["认证"])
app.include_router(users.router, prefix="/api/v1/users", tags=["用户"])
app.include_router(accounts.router, prefix="/api/v1/accounts", tags=["账户"])
app.include_router(transactions.router, prefix="/api/v1/transactions", tags=["交易"])
app.include_router(blockchain.router, prefix="/api/v1/blockchain", tags=["区块链"])
app.include_router(message.router, prefix="/api/v1/message", tags=["安全消息"])

@app.get("/")
async def root():
    return {"message": "Welcome to MyBank API"}