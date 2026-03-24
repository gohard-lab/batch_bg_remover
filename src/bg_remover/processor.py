import os
from pathlib import Path
from rembg import remove, new_session
from PIL import Image

def process_images(input_paths: list, output_folder: str, progress_callback=None) -> bool:
    """
    Process a list of image files or directories to remove backgrounds.
    Uses progress_callback to communicate with the UI thread.
    """
    output_path = Path(output_folder)
    output_path.mkdir(parents=True, exist_ok=True)

    valid_extensions = {'.jpg', '.jpeg', '.png'}
    image_files = []

    # Collect target files
    for path_str in input_paths:
        p = Path(path_str)
        if p.is_dir():
            image_files.extend([f for f in p.iterdir() if f.suffix.lower() in valid_extensions])
        elif p.is_file() and p.suffix.lower() in valid_extensions:
            image_files.append(p)

    # Remove duplicates
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
            
            if progress_callback:
                progress_callback(idx, total_files)
                
        except Exception as e:
            print(f"[Error] Failed to process ({img_path.name}): {e}")

    return True