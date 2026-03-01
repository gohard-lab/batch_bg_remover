import os
from pathlib import Path
from rembg import remove, new_session
from PIL import Image

def process_images(input_paths: list, output_folder: str, progress_callback=None) -> bool:
    """
    제공된 이미지 파일 목록 또는 디렉토리 내의 이미지를 처리하여 배경을 제거한다.
    UI 스레드와의 통신을 위해 progress_callback 함수를 활용한다.
    """
    output_path = Path(output_folder)
    output_path.mkdir(parents=True, exist_ok=True)

    valid_extensions = {'.jpg', '.jpeg', '.png'}
    image_files = []

    # 입력값이 폴더인지 개별 파일들의 목록인지 판별하여 처리 대상 수집
    for path_str in input_paths:
        p = Path(path_str)
        if p.is_dir():
            image_files.extend([f for f in p.iterdir() if f.suffix.lower() in valid_extensions])
        elif p.is_file() and p.suffix.lower() in valid_extensions:
            image_files.append(p)

    # 중복 제거
    image_files = list(set(image_files))
    total_files = len(image_files)

    if total_files == 0:
        return False

    session = new_session()

    for idx, img_path in enumerate(image_files, start=1):
        try:
            input_image = Image.open(img_path)
            output_image = remove(input_image, session=session)
            
            output_filename = output_path / f"{img_path.stem}_rmbg.png"
            output_image.save(output_filename)
            
            # UI 화면의 프로그레스 바를 업데이트하기 위한 무전(콜백) 발송
            if progress_callback:
                progress_callback(idx, total_files)
                
        except Exception as e:
            print(f"[Error] 파일 처리 실패 ({img_path.name}): {e}")

    return True