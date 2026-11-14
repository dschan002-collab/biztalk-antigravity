from fastapi import APIRouter, HTTPException, status
from models.schemas import ConvertRequest, ConvertResponse
from services.tone_converter import convert_tone

router = APIRouter(tags=["Tone Conversion"])


@router.post(
    "/convert",
    response_model=ConvertResponse,
    status_code=status.HTTP_200_OK,
    summary="업무 말투 변환 API",
    description="입력된 원문을 지정된 수신 대상(상사, 타팀 동료, 고객, 팀내 동료)에 맞는 비즈니스 말투로 변환합니다.",
)
async def convert_text(request: ConvertRequest) -> ConvertResponse:
    try:
        converted = await convert_tone(
            text=request.text,
            target_audience=request.target_audience.value,
        )
        return ConvertResponse(
            converted_text=converted,
            target_audience=request.target_audience.value,
            original_text=request.text,
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="LLM API 호출 중 오류가 발생했습니다.",
        ) from e
