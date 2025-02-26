from fastapi import FastAPI
from api.v1 import auth, users, accounts, transactions

app = FastAPI(title="MyBank API", version="1.0.0")

# 注册路由
app.include_router(auth.router, prefix="/api/v1/auth", tags=["认证"])
app.include_router(users.router, prefix="/api/v1/users", tags=["用户"])
app.include_router(accounts.router, prefix="/api/v1/accounts", tags=["账户"])
app.include_router(transactions.router, prefix="/api/v1/transactions", tags=["交易"])

@app.get("/")
async def root():
    return {"message": "Welcome to MyBank API"}