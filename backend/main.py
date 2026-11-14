import os
from pathlib import Path
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse, JSONResponse
from fastapi.staticfiles import StaticFiles

from models.schemas import HealthResponse
from routers import convert

app = FastAPI(
    title="업무 말투 변환기 (BizTalk) API",
    description="Upstage Solar-Pro4 기반 업무 말투 변환 서비스 API 문서",
    version="1.0.0",
)

# CORS 미들웨어 설정
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # 배포 환경에 따라 도메인 제한 가능
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# API 라우터 등록
app.include_router(convert.router, prefix="/api")


# 헬스 체크 엔드포인트
@app.get(
    "/health",
    response_model=HealthResponse,
    tags=["Health"],
    summary="서버 상태 확인",
)
async def health_check():
    return HealthResponse(status="ok")


# 프론트엔드 정적 파일 서빙
FRONTEND_DIR = Path(__file__).resolve().parent.parent / "frontend"

if FRONTEND_DIR.exists():
    app.mount("/frontend", StaticFiles(directory=str(FRONTEND_DIR)), name="frontend")
    if (FRONTEND_DIR / "css").exists():
        app.mount("/css", StaticFiles(directory=str(FRONTEND_DIR / "css")), name="css")
    if (FRONTEND_DIR / "js").exists():
        app.mount("/js", StaticFiles(directory=str(FRONTEND_DIR / "js")), name="js")


@app.get("/", include_in_schema=False)
async def serve_index():
    index_file = FRONTEND_DIR / "index.html"
    if index_file.exists():
        return FileResponse(str(index_file))
    return JSONResponse(
        content={
            "message": "업무 말투 변환기 API 서버가 정상 실행 중입니다. 프론트엔드 파일(index.html)이 준비되면 화면이 표시됩니다.",
            "docs": "/docs",
            "health": "/health",
        }
    )


if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)
