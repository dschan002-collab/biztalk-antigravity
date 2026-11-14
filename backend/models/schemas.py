from enum import Enum
from pydantic import BaseModel, Field


class TargetAudience(str, Enum):
    BOSS = "boss"
    COLLEAGUE = "colleague"
    CLIENT = "client"
    TEAM = "team"


class ConvertRequest(BaseModel):
    text: str = Field(..., min_length=1, description="변환할 원문 (1자 이상)")
    target_audience: TargetAudience = Field(
        ..., description="수신 대상: boss (상사), colleague (타팀 동료), client (고객), team (팀내 동료)"
    )


class ConvertResponse(BaseModel):
    converted_text: str = Field(..., description="변환된 비즈니스 텍스트")
    target_audience: str = Field(..., description="선택된 수신 대상 코드")
    original_text: str = Field(..., description="사용자가 입력한 원문")


class HealthResponse(BaseModel):
    status: str = Field(default="ok", description="서버 상태")
