import os
import logging
from dotenv import load_dotenv
from langchain_upstage import ChatUpstage
from langchain_core.messages import SystemMessage, HumanMessage
from prompts.templates import get_prompt_template

# 환경 변수 로드
load_dotenv()

logger = logging.getLogger(__name__)

# Solar-Pro4 모델 초기화
def get_llm() -> ChatUpstage:
    api_key = os.getenv("UPSTAGE_API_KEY")
    if not api_key:
        logger.error("UPSTAGE_API_KEY 환경 변수가 설정되지 않았습니다.")
        raise ValueError("UPSTAGE_API_KEY 환경 변수가 설정되지 않았습니다.")
    
    return ChatUpstage(
        model="solar-pro4",
        api_key=api_key,
        temperature=0.7,
    )


async def convert_tone(text: str, target_audience: str) -> str:
    """
    주어진 텍스트를 대상에 맞는 비즈니스 어조로 변환합니다.
    """
    system_prompt = get_prompt_template(target_audience)
    llm = get_llm()

    messages = [
        SystemMessage(content=system_prompt),
        HumanMessage(content=f"다음 내용을 변환해주세요:\n{text}"),
    ]

    try:
        response = await llm.ainvoke(messages)
        converted_text = response.content
        if isinstance(converted_text, list):
            # 일부 모델 응답이 list 형태일 경우 대비
            converted_text = "".join(str(chunk) for chunk in converted_text)
        return converted_text.strip()
    except Exception as e:
        logger.error(f"Solar-Pro4 변환 처리 중 오류 발생: {e}", exc_info=True)
        raise RuntimeError(f"말투 변환 실패: {str(e)}") from e
