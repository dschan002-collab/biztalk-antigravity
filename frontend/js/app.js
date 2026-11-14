/**
 * 업무 말투 변환기 (BizTalk) — Application Logic
 */

document.addEventListener("DOMContentLoaded", () => {
  // DOM Elements
  const targetButtons = document.querySelectorAll(".target-btn");
  const inputText = document.getElementById("inputText");
  const outputText = document.getElementById("outputText");
  const charCount = document.getElementById("charCount");
  const convertBtn = document.getElementById("convertBtn");
  const copyBtn = document.getElementById("copyBtn");
  const copyBtnText = document.getElementById("copyBtnText");
  const spinner = document.getElementById("spinner");
  const loadingOverlay = document.getElementById("loadingOverlay");
  const targetBadge = document.getElementById("targetBadge");
  const toastMsg = document.getElementById("toastMsg");

  // State
  let currentTarget = "boss";
  const targetLabels = {
    boss: "상사 / 임원",
    colleague: "타팀 동료",
    client: "고객 / 외부",
    team: "팀 내 동료",
  };

  // API Base URL (동일 origin 또는 로컬 FastAPI 기본 포트)
  const isLocalStatic = window.location.protocol === "file:";
  const API_BASE = isLocalStatic ? "http://127.0.0.1:8000" : "";

  // 1. 수신 대상 선택 이벤트
  targetButtons.forEach((btn) => {
    btn.addEventListener("click", () => {
      targetButtons.forEach((b) => {
        b.classList.remove("active");
        b.setAttribute("aria-checked", "false");
      });

      btn.classList.add("active");
      btn.setAttribute("aria-checked", "true");
      currentTarget = btn.dataset.target;
      targetBadge.textContent = targetLabels[currentTarget] || "상사 / 임원";
    });
  });

  // 2. 글자 수 카운터
  inputText.addEventListener("input", () => {
    const len = inputText.value.length;
    charCount.textContent = `${len}자`;
  });

  // 3. 로딩 상태 제어 함수
  const setLoading = (isLoading) => {
    convertBtn.disabled = isLoading;
    if (isLoading) {
      spinner.classList.remove("hidden");
      loadingOverlay.classList.remove("hidden");
    } else {
      spinner.classList.add("hidden");
      loadingOverlay.classList.add("hidden");
    }
  };

  // 4. 말투 변환 API 호출 함수
  const handleConvert = async () => {
    const text = inputText.value.trim();

    if (!text) {
      alert("변환할 원문을 입력해 주세요.");
      inputText.focus();
      return;
    }

    if (!currentTarget) {
      alert("메시지를 수신할 대상을 선택해 주세요.");
      return;
    }

    setLoading(true);

    try {
      const response = await fetch(`${API_BASE}/api/convert`, {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
        },
        body: JSON.stringify({
          text: text,
          target_audience: currentTarget,
        }),
      });

      if (!response.ok) {
        const errorData = await response.json().catch(() => ({}));
        const detail = errorData.detail || "변환 서버에서 오류가 발생했습니다.";
        throw new Error(detail);
      }

      const data = await response.json();
      outputText.value = data.converted_text || "";
      copyBtn.disabled = !outputText.value;

      // 성공 시 출력 영역으로 부드럽게 시선 유도
      outputText.scrollIntoView({ behavior: "smooth", block: "nearest" });
    } catch (error) {
      console.error("변환 요청 실패:", error);
      alert(`말투 변환에 실패했습니다: ${error.message}`);
    } finally {
      setLoading(false);
    }
  };

  convertBtn.addEventListener("click", handleConvert);

  // 5. 단축키 (Ctrl + Enter 또는 Cmd + Enter) 지원
  inputText.addEventListener("keydown", (e) => {
    if ((e.ctrlKey || e.metaKey) && e.key === "Enter") {
      e.preventDefault();
      handleConvert();
    }
  });

  // 6. 결과 복사 기능
  copyBtn.addEventListener("click", async () => {
    const textToCopy = outputText.value;
    if (!textToCopy) return;

    try {
      if (navigator.clipboard && window.isSecureContext) {
        await navigator.clipboard.writeText(textToCopy);
      } else {
        // Fallback for non-secure contexts
        outputText.select();
        document.execCommand("copy");
      }

      // 복사 완료 피드백
      copyBtnText.textContent = "복사 완료!";
      toastMsg.classList.remove("hidden");

      setTimeout(() => {
        copyBtnText.textContent = "복사하기";
        toastMsg.classList.add("hidden");
      }, 2000);
    } catch (err) {
      console.error("클립보드 복사 실패:", err);
      alert("클립보드 복사에 실패했습니다. 직접 복사해 주세요.");
    }
  });
});
