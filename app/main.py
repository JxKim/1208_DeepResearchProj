from fastapi import FastAPI
from app.config.config import get_setting
from app.routers import router
from fastapi.middleware.cors import CORSMiddleware



app = FastAPI()

@app.get("/health", tags=["系统"])
async def health_check() -> dict[str, str]:
    """返回服务健康状态，用于本地调试、容器探针和部署检查。"""

    return {"status": "ok"}

# CORS —— 允许本地前端页面跨域调用
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


app.include_router(router=router, prefix=get_setting().api_prefix)
