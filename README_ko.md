```markdown
🌐 **다른 언어로 읽기:** [English](README.md) | [🇰🇷 한국어 (Korean)](README_ko.md)

# AI 대량 이미지 배경 제거기 (누끼 프로그램)

API 결제나 구독 없이 평생 무료로 사용할 수 있는 오프라인 AI 배경 제거 프로그램입니다. 파이썬으로 제작되었으며, 인터넷 연결 없이도 PC 내부 자원만으로 빠르고 정교하게 배경을 지워줍니다.

## 🚀 주요 기능
* **100% 무료 및 오프라인:** 비싼 API 키가 필요 없습니다.
* **대량 일괄 변환 (Batch):** 사진 한 장은 물론, 수백 장이 들어있는 폴더 전체를 한 번에 변환합니다.
* **강력한 AI 성능:** U2Net 모델 기반의 `rembg` 라이브러리를 사용하여 머리카락 수준의 정교한 경계선을 추출합니다.
* **직관적인 UI:** 드래그 앤 드롭을 지원하는 깔끔한 그래픽 인터페이스(GUI).
* **설치 불필요 (Standalone):** 파이썬을 모르는 일반인도 바로 쓸 수 있는 단일 `.exe` 실행 파일을 제공합니다.

## 🛠️ 사용된 기술
* **언어:** Python 3.10+
* **AI 엔진:** `rembg`
* **GUI 구현:** `Tkinter` / `tkinterdnd2`
* **패키지 관리:** `uv`
* **실행 파일 빌드:** `PyInstaller`

## 📦 다운로드 및 사용법 (일반 사용자용)
코딩을 몰라도 바로 사용할 수 있습니다.
1. [Releases](../../releases) 페이지로 이동합니다.
2. 가장 최신 버전의 `BgRemover.exe` 파일을 다운로드합니다.
3. 더블 클릭하여 실행한 뒤, 원하는 사진이나 폴더를 끌어다 놓으세요.

## 💻 개발자용 실행 가이드
직접 소스 코드를 실행하거나 수정하고 싶으신 분들을 위한 가이드입니다.

# 1. 저장소 클론
```bash
git clone [https://github.com/gohard-lab/batch_bg_remover.git](https://github.com/gohard-lab/batch_bg_remover.git)
cd batch_bg_remover
```

# 2. 패키지 설치 (가장 빠른 uv 사용 권장)
```bash
uv sync
```

# 3. 프로그램 실행
```bash
uv run python src/main.py
```
# 4. EXE 실행 파일 직접 빌드하기
```bash
uv run pyinstaller --noconsole --onefile --copy-metadata pymatting src/main.py
```

* [**유튜브 영상 링크**] (https://youtu.be/HzuSu2b_5N4)

📊 데이터 수집 안내
※ 본 프로그램은 더 나은 서비스 제공과 에러 수정을 위해 익명화된 최소한의 사용 통계(기능 클릭 수 등)를 수집합니다. (개인 식별 정보는 일절 수집하지 않습니다.)

📺 관련 영상 가이드
이 프로그램의 작동 원리와 개발 과정이 궁금하시다면 유튜브 '잡학다식 개발자' 채널의 가이드 영상을 참고해 주세요.
