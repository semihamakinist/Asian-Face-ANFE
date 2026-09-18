from PIL import Image
from io import BytesIO
import hashlib
import requests
import os

# **** bunun hashes kodunu bul
# test -> get_image_hash_from_url(img_url, 1)

# Placeholder hash listesi -> "no_image" hash codes
KNOWN_PLACEHOLDER_HASHES = {
    "321ae363e068e58b22739a604765a23f1487e6ca",  # klasik
    "27fcc48c0f076407f108dfbac08110208a8f0893",  # farklı bir "boş" görsel
    "037c781eac1085059ec5cbd33baff762d049e812",  # VXxwrJ_5s, DkexDq_5s
    "c330e9d33f17e8f3b4bc84dfd28fabd740e6eaaf",
    "553a2ecd1c74bf008f29a97ceaf5981fdcaf0340",
    "e385bf097e147f917a9fef24e1735513411aa2bd",
    "f98236ff86624a0c71db2dc36b137169970f8ea4",
    "357d175d8a2211b1114bdc00ef27490fbd5c01cc",
    "24533ad73a3e1300d74590889631912033ebf323",
    "ad912f54c2c30475139c25339a7cd453f2e0e7bd" # farklı
}

def load_request_img(img_url, request_index=1):
    """
    Görseli URL'den veya lokal path'ten yükler.
    """
    try:
        if request_index == 1:
            response = requests.get(img_url, timeout=5)
            response.raise_for_status()
            return Image.open(BytesIO(response.content)).convert("RGB")
        else:
            return Image.open(img_url).convert("RGB")
    except Exception as e:
        print(f"[load_request_img] Error loading image from {img_url}: {e}")
        return None

def get_image_hash_from_url(img_url, request_index=1):
    """
    Görselin SHA1 hash'ini hesaplar.
    """
    img = load_request_img(img_url, request_index)
    if img is None:
        print(f"[get_image_hash_from_url] Failed to load image: {img_url}")
        return None
    try:
        return hashlib.sha1(img.tobytes()).hexdigest()
    except Exception as e:
        print(f"[get_image_hash_from_url] Error generating hash: {e}")
        return None

def is_placeholder_image(img_url, request_index=1):
    """
    Görselin bilinen boş placeholder olup olmadığını kontrol eder.
    """
    hash_val = get_image_hash_from_url(img_url, request_index)
    result = hash_val in KNOWN_PLACEHOLDER_HASHES if hash_val else False
    print(f"img_url: {img_url} - hash_val: {hash_val} - result: {('No_image' if result else 'Yes_image')}")
    return result

def find_placeholder_images_in_directory(directory, extensions=('.jpg', '.jpeg', '.png')):
    """
    Belirtilen dizin altında boş görselleri tespit eder.
    """
    placeholder_files = []
    for root, _, files in os.walk(directory):
        for file in files:
            if file.lower().endswith(extensions):
                full_path = os.path.join(root, file)
                if is_placeholder_image(full_path, request_index=2):
                    placeholder_files.append(full_path)
    return placeholder_files

def remove_if_empty(folder_path):
    """Klasör boşsa siler."""
    try:
        # Yalnızca dosya veya alt klasör yoksa sil
        if not any(os.scandir(folder_path)):
            os.rmdir(folder_path)
            print(f"Silindi (boş klasör): {folder_path}")
            return True
    except Exception as e:
        print(f"[remove_if_empty] Hata: {e}")
    return False