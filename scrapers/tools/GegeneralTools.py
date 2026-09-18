from tools.SeleniumTools import wait_load_main_webpage

from tools.ImageTools import is_placeholder_image

from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

from urllib.parse import urlparse
from datetime import datetime

import requests
import pymongo
import random
import time
import base64
import shutil
import string
import re
import os

import sys
sys.getfilesystemencoding()

IMAGE_EXISTS_ERROR = -1
IMAGE_NOT_FOUND = 0
IMAGE_FOUND = 1


def setFamousName(famous_name=None, punctuation_digits=(string.punctuation + string.digits)):
    if famous_name is not None:
        clear_text_str = [
            "actor", "actress", "reporter", "screenwriter", "screen_writer", "assistantdirector", "assistant_director",
            "cinematographer", "Director", "musicalactress", "musical_actress", "director", "fx", "comedian", "Secret",
            "Sissonne", "Wednesday_Campanella",  "lawyer",  "MeloMance", "Laboum", "BIFF",  "Hoya", "Jarujaru", "NUEST",
            "GOT", "GOT7",  "Got7",  "EPEX", "BA", "producer", "writer", "screen", "assistant","Defconn", "TWICE", "PO",
            "disambiguation", "BeeShuffle", "Bee_Shuffle", "ShimofuriMyojo", "Shimofuri_Myojo", "Boyfriend", "BIKOON",
            "WednesdayCampanella", "Wednesday_Campanella",  "Myname", "My_Name", "bequixxt", "be_quixxt", "AB6IX", "PD",
            "GoldenChild", "Golden_Child", "announcer", "Fromis9", "Gugudan","UKISS", "MILK", "EXILE", "Chidori", "KNK",
            "CLC", "child", "INFINITE", "X1", "cellist", "GIDLE", "BTS", "HALO","B1A4", "Girl'sDay",
            "Exile", "WJSN", "IzOne", "Iz_One","ABIX", "ACE", "Lalande", "Hellovenus", "FruitPunch", "Fruit_Punch",
            "mangaka", "HighTop", "Victon", "DIA", "Yasei_Bakudan", "Yasei Bakudan", "Pritti", "DKZ", "Margaret_Natsuki",
            "Margaret Natsuki", "Jewelry", "Mogurider"
        ]

        famous_name = famous_name.replace('\n', '').translate(str.maketrans('', '', punctuation_digits))
        famous_name = (famous_name
                       .replace("_-_", "_")
                       .replace("-_", "_")
                       .replace("_-", "_")
                       .replace(" ", "_")
                       .replace("%E2%80%93", "-")
                       .replace("–", " ")
                       .replace("_–_", "_"))

        for clear_text in clear_text_str:
            famous_name = famous_name.replace(clear_text, "")

        if famous_name.endswith('__'):
            famous_name = famous_name[:-2]
        elif famous_name.endswith('_-'):
            famous_name = famous_name[:-2]
        elif famous_name.endswith('-_'):
            famous_name = famous_name[:-2]
        elif famous_name.endswith('-_-'):
            famous_name = famous_name[:-3]
        elif famous_name.endswith('_-_'):
            famous_name = famous_name[:-3]
        elif famous_name.endswith('_'):
            famous_name = famous_name[:-1]
        return famous_name
    else:
        print(f"Litfen oluşturulacak klasö ismini belirtin!")
        return ""

def setGender(gender):
    try:
        if ("Actresses" in gender) or ("actresses" in gender):
            return "F"
        elif ("Actors" in gender) or ("actors" in gender):
            return "M"
        else:
            return "None"
    except:
        return "None"



def setBase64(driver, xpath):
    return driver.execute_script("""
        //var xpath = '//*[@id="mw-content-text"]/div[2]/div/a/img';
        var xpath = '{xpath}';
        // XPath ifadesine göre öğeyi seç
        var img = document.evaluate(
          xpath,                 // XPath ifadesi
          document,              // Bağlam düğümü (genellikle 'document')
          null,                  // Namespace çözücü (genellikle 'null')
          XPathResult.FIRST_ORDERED_NODE_TYPE, // Döndürülecek sonuç türü
          null                   // Sonuç nesnesi (genellikle 'null')
        ).singleNodeValue;
        var canvas = document.createElement('canvas');
        canvas.width = img.naturalWidth;
        canvas.height = img.naturalHeight;
        var ctx = canvas.getContext('2d');
        ctx.drawImage(img, 0, 0);
        return canvas.toDataURL('image/jpeg').split(',')[1];
    """.format(xpath=xpath))

def setBase64_fast(driver, xpath):
    """
    XPath ile bulunan görselin gerçekten yüklenmiş olmasını kontrol eder.
    Yüklü değilse None döner.
    Base64 çıktısı data:image/... öneki olmadan döner.
    """
    try:
        script = """
        const xpath = arguments[0];

        const img = document.evaluate(
            xpath,
            document,
            null,
            XPathResult.FIRST_ORDERED_NODE_TYPE,
            null
        ).singleNodeValue;

        if (!img) {
            return {ok: false, reason: "img_not_found", data: null};
        }

        // Görsel gerçekten yüklenmiş mi?
        if (!img.complete || !img.naturalWidth || !img.naturalHeight) {
            return {ok: false, reason: "img_not_loaded", data: null};
        }

        const canvas = document.createElement('canvas');
        canvas.width = img.naturalWidth;
        canvas.height = img.naturalHeight;

        const ctx = canvas.getContext('2d');
        ctx.drawImage(img, 0, 0);

        const dataUrl = canvas.toDataURL('image/jpeg', 0.95);

        if (!dataUrl || !dataUrl.startsWith("data:image/")) {
            return {ok: false, reason: "invalid_dataurl", data: null};
        }

        return {
            ok: true,
            reason: "success",
            data: dataUrl.split(',')[1],
            width: img.naturalWidth,
            height: img.naturalHeight
        };
        """
        result = driver.execute_script(script, xpath)

        if not result or not result.get("ok"):
            print(f"setBase64_error: {result}")
            return None

        return result.get("data")
    except Exception as ex:
        print(f"setBase64_exception: {ex}")
        return None

def is_valid_base64(data):
    if not data or not isinstance(data, str):
        return False
    try:
        base64.b64decode(data, validate=True)
        return True
    except Exception:
        return False

def save_src_image(base64_data, save_img_path):
    # Base64 verisini decode et ve kaydet
    try:
        base64_string = base64.b64decode(base64_data, validate=True)
        # base64_string = re.sub(r"^data:image/\w+;base64,", "", base64_string)
        # print(f"base64_string: {base64_string}")
        with open(save_img_path, "wb") as f:
            f.write(base64_string)
            print("Image_Saved: {img_path}\n**************".format(img_path=save_img_path))
        f.close()
    except base64.binascii.Error as ex:
        print(f"save_src_image: {ex}")

def save_src_image_fast(base64_data, save_img_path):
    """
    Base64 verisini decode edip dosyaya yazar.
    Başarılıysa True döner.
    """
    try:
        if not is_valid_base64(base64_data):
            return False

        base64_string = base64.b64decode(base64_data, validate=True)

        # Çok küçük çıktı genelde bozuk capture işaretidir
        if len(base64_string) < 1024:
            print(f"save_src_image_warning: very_small_file -> {save_img_path}")
            return False

        with open(save_img_path, "wb") as f:
            f.write(base64_string)

        print(f"Image_Saved_Base64: {save_img_path}\n**************")
        return True

    except Exception as ex:
        print(f"save_src_image_error: {ex}")
        return False

def build_folder_name(folder_name: str):
    if not folder_name:
        return None

    set_folder_name = (
        folder_name
        .replace('\n', '')
        .replace("%28", "(")
        .replace("%29", ")")
        .replace("%27", "'")
        .replace("%26", "&")
        .replace("%21", "!")
        .replace("%3F", "?")
        .replace("%2C", ",")
        .replace("½", " ")
        .replace("%E2%80%93", "-")
        .replace("–", " ")
        .replace("_–_", " ")
        .replace("_~_", " ")
        .replace("_-_", " ")
        .replace(" - ", " ")
        .replace(" ~ ", " ")
        .replace("-_", " ")
        .replace("_-", " ")
        .replace("___", " ")
        .replace("__", " ")
        .replace("    ", " ")
        .replace("   ", " ")
        .replace("  ", " ")
        )
    if set_folder_name[-1] == " ":
        set_folder_name = set_folder_name[:-1]
    return set_folder_name

def set_img_name(img_url):
    try:
        if not img_url:
            print(f"Boş URL: {img_url}")
            return None

        # Dosya adı çıkar
        parsed = urlparse(img_url)
        img_filename = os.path.basename(parsed.path)

        if not img_filename:
            return None

        str_punctuation_digits = (
            string.punctuation
            .replace('.', '')
            .replace('_', '')
            .replace('-', '')
        )

        tmp_img_name = build_folder_name(img_filename)
        img_filename = (
            build_folder_name(
                tmp_img_name
                .translate(
                    str.maketrans('', '', str_punctuation_digits)
                )
            )
            .replace(" ", "_")
            .replace("___", "_")
        )

        return img_filename
    except Exception as ex:
        print(f"set_img_name_error: {ex}")
        return None

def set_save_folder(main_path="dataset", movie_name=None, folder_name=None):
    # Klasör yolunu olustur
    if folder_name:
        return os.path.join(main_path, movie_name, folder_name)
    return os.path.join(main_path, movie_name)

def exists_in_image(img_url, main_path="dataset", movi_name=None, folder_name=None):
    try:
        img_filename = set_img_name(img_url)
        if img_filename is None:
            return IMAGE_EXISTS_ERROR

        check_dir = set_save_folder(main_path, movi_name, folder_name)
        file_path = os.path.join(check_dir, img_filename)
        return IMAGE_FOUND if os.path.exists(file_path) else IMAGE_NOT_FOUND
        #     return 1
        # else: return 0
    except Exception as ex:
        print(f"exists_in_image_error: {ex}")
        return IMAGE_EXISTS_ERROR

def save_response_content(response, file_path):
    """
    requests ile gelen içeriği dosyaya yazar.
    Başarılıysa True döner.
    """
    try:
        content_type = response.headers.get("Content-Type", "").lower()

        # resim değilse yazma
        if "image" not in content_type:
            print(f"save_response_content_warning: not_image_content -> {content_type}")
            return False

        content = response.content
        if not content or len(content) < 1024:
            print(f"save_response_content_warning: very_small_response -> {file_path}")
            return False

        with open(file_path, "wb") as f:
            f.write(content)

        print(f"Image_Saved_URL: {file_path}\n**************")
        return True
    except Exception as ex:
        print(f"save_response_content_error: {ex}")
        return False

def wait_load_img(driver, img_xpath, timeout=5):
    WebDriverWait(driver, timeout).until(
        lambda d: d.execute_script(
            """
            const img = document.evaluate(arguments[0], document, null,
            XPathResult.FIRST_ORDERED_NODE_TYPE, null).singleNodeValue;
            return img && img.complete && img.naturalWidth > 0 && img.naturalHeight > 0;
            """, img_xpath)
    )


# === XPath ile Görseli Base64 Formatına Çek ===
def extract_base64_from_xpath(web_driver, xpath):
    return web_driver.execute_script("""
        var img = document.evaluate(`{xpath}`, document, null, XPathResult.FIRST_ORDERED_NODE_TYPE, null).singleNodeValue;

        var canvas = document.createElement('canvas');
        canvas.width = img.naturalWidth;
        canvas.height = img.naturalHeight;
        var ctx = canvas.getContext('2d');
        ctx.drawImage(img, 0, 0);
        return canvas.toDataURL('image/jpeg').split(',')[1];
    """.format(xpath=xpath))

# === HTTP veya Base64 (403 hatasi ile) ile Görsel Kaydet ===
def save_image_smart(
    img_url,
    headers,
    main_path,
    movie_name,
    folder_name=None,
    *,
    session: requests.Session,
    timeout=(10, 30),
    base64_fetcher=None,   # lambda: extract_base64_from_xpath(driver, img_xpath)
):
    img_name = set_img_name(img_url)
    if img_name is None:
        return False

    folder_path = set_save_folder(main_path, movie_name, folder_name)
    os.makedirs(folder_path, exist_ok=True)

    save_img_path = os.path.join(folder_path, img_name)
    try:
        # res = requests.get(
        #     img_url,
        #     headers={"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64)"},
        #     timeout=timeout
        # )
        # if res.status_code == 200:
        #     with open(save_img_path, "wb") as img_f:
        #         img_f.write(res.content)
        #     return os.path.getsize(save_img_path) > 0

        r = session.get(img_url, headers=headers, timeout=timeout)
        if r.status_code == 200:
            with open(save_img_path, "wb") as f:
                f.write(r.content)
            return os.path.getsize(save_img_path) > 0

        # SADECE 403 ise base64'e düş
        if r.status_code == 403 and base64_fetcher:
            b64 = base64_fetcher()
            if b64:
                img_data = base64.b64decode(b64, validate=True)
                with open(save_img_path, "wb") as f:
                    f.write(img_data)
                return os.path.getsize(save_img_path) > 0

        print(f"⚠️ Görsel indirilemedi. status={r.status_code} url={img_url}")
        return False

    except Exception as e:
        print(f"❌ Görsel kaydedilemedi: {e}")
        return False

def saveSRCImage_faster(
    img_url,
    movie_name=None,
    header=None,
    main_path="dataset",
    folder_name=None,
    driver=None,
    img_xpath=None,
    wait_before_base64=False,
    wait_timeout=5,
):
    """
    Önce normal URL ile indirmeyi dener.
    URL başarısız olursa base64 fallback kullanır.
    Bu sıralama siyah/bozuk canvas sorununu azaltır.
    """
    try:
        img_filename = set_img_name(img_url)
        if img_filename is None:
            return False

        save_dir = set_save_folder(main_path, movie_name, folder_name)
        os.makedirs(save_dir, exist_ok=True)

        file_path = os.path.join(save_dir, img_filename)

        # dosya zaten varsa tekrar indirme
        if os.path.exists(file_path):
            print(f"Exists: {file_path}")
            return True

        if wait_before_base64 and driver and img_xpath:
            try:
                wait_load_img(driver, img_xpath, timeout=wait_timeout)
            except Exception:
                pass

        # 1) Önce normal base64 ile fallback olarak resmi indir
        base64_data = setBase64_fast(driver, img_xpath)
        # base64_data = extract_base64_from_xpath(driver, img_xpath)
        print_msj = f"**************\nbase64_data_case: {(base64_data is not None)}"
        if base64_data is not None and is_valid_base64(base64_data):
            print(f"{print_msj} - Fallback_Base64: {file_path}")
            if save_src_image_fast(base64_data, file_path):
                return True

        # 2) Eger base64 başarısızsa daha sonra URL ile indirmeyi dene
        try:
            # session = requests.Session()  # main'de 1 kere oluştur, hep kullan
            # r = session.get(img_url, headers=header, timeout=10)
            response = requests.get(img_url, headers=header, timeout=15)
            if response.status_code == 200:
                if save_response_content(response, file_path):
                    return True
            else:
                print(f"requests_status_code: {response.status_code} -> {img_url}")

        except Exception as req_ex:
            print(f"requests_get_error: {img_url} -> {req_ex}")

        print(f"{print_msj} - Not_Save: {file_path}")
        return False

    except Exception as ex:
        print(f"Image_Save_Error: {img_url} -> {ex}")
        return False

def saveSRCImage_fast(
    img_url,
    movi_name=None,
    header=None,
    main_path="dataset",
    folder_name=None,
    base64_data=None
):
    try:
        # set img_name
        img_filename = set_img_name(img_url)
        if img_filename is None:
            return

        # print(f"base64_data_1: {base64_data}")
        print_msj = f"**************\nbase64_data_case: {(base64_data is not None)}"
        save_dir = set_save_folder(main_path, movi_name, folder_name)

        os.makedirs(save_dir, exist_ok=True)
        file_path = os.path.join(save_dir, img_filename)
        # 🔥 EN KRİTİK OPTİMİZASYON
        if os.path.exists(file_path):
            # zaten varsa tekrar indirme
            print(f"{print_msj} - Exists: {file_path}")
            return
        # Base64 varsa onu kullan (daha hızlı)
        if base64_data is not None and is_valid_base64(base64_data) :
            print(f"{print_msj} - Download: {file_path}")
            try:
                save_src_image(base64_data, file_path)
                return
            except Exception:
                pass

        # Normal download
        response = requests.get(img_url, headers=header, timeout=10)
        if response.status_code == 200:
            with open(file_path, "wb") as f:
                f.write(response.content)
            f.close()
            return
        print(f"{print_msj} - Not_Save: {file_path}")
    except Exception as ex:
        print(f"Image_Save_Error: {img_url} -> {ex}")

def saveSRCImage(img_url, movi_name=None, folder_name=None, header=None, main_path=None, base64_data=None):
    # time.sleep(random.randint(1, 3))
    print(f"base64_data_case: {(base64_data is not None)}")
    try:
        if folder_name is None:
            save_folder_path = os.path.join(main_path, movi_name)
        else:
            save_folder_path = os.path.join(main_path, movi_name, folder_name)
        print("{0} - {1}".format(os.path.exists(save_folder_path), save_folder_path))
        if not os.path.exists(save_folder_path):
            os.makedirs(save_folder_path)
        # str_punctuation_digits = string.punctuation.replace('.', '').replace('_', '').replace('-', '') + string.digits
        str_punctuation_digits = (
                string.punctuation
                .replace('.', '')
                .replace('_', '')
                .replace('-', '')
        )

        image_name = img_url.split('/')[-1]
        tmp_img_name = build_folder_name(image_name)
        if tmp_img_name:
            image_name = (
                tmp_img_name.replace(' ', '_')
                .translate(str.maketrans('', '', str_punctuation_digits))
            )

        save_img_path = os.path.join(save_folder_path, f"{image_name}").replace("/", "\\")
        image_data = requests.get(img_url, headers=header)

        if image_data.status_code == 200:
            with open(save_img_path, 'wb') as f:
                f.write(image_data.content)
            f.close()
        elif image_data.status_code == 403:
            try:
                save_src_image(base64_data, save_img_path)
            except:
                print("error saving base64 image ")
        del image_data
    except Exception as ex:
        print(f"ex: {ex}")
def saveLinkList(a_xPath, file_name="asianwiki_player_movie_links.txt"):
    [saveLink(href.get_attribute('href'), file_name)
     for href in a_xPath
     if (ifCondition(href.get_attribute('href'), condition_type=0))]


def ifCondition(condition_link, condition_type=0):
    if condition_type == 0:  # movie
        return (("php" not in condition_link)
                and ("title" not in condition_link)
                and ("asianwiki.com/Category:" not in condition_link)
                and ("asianwiki.com" in condition_link)
                and ("Awards" not in condition_link)
                and ("Prize" not in condition_link)
                and ("Film_Festival" not in condition_link)
                and ("th)_" not in condition_link)
                and ("Mika_Nakashima:_" not in condition_link)
                and ("Yui:_" not in condition_link)
                and ('_Entertainment' not in condition_link)
                and ('_Pictures' not in condition_link)
                and ('Plot_Synopsis' not in condition_link)
                and ('disambiguation' not in condition_link)
                and('_University' not in condition_link)
                )
    return True


def get_relative_xpath(driver, element, container):
    script = """
    function getRelativeXPath(elt, container) {
      var path = "";
      // Döngü: elt, container elementine ulaşana kadar
      while (elt && elt !== container) {
        var index = 1;
        // Önceki kardeşleri say (aynı tag adını kullanan)
        var sibling = elt.previousSibling;
        while (sibling) {
          if (sibling.nodeType === 1 && sibling.tagName === elt.tagName) {
            index++;
          }
          sibling = sibling.previousSibling;
        }
        var tagName = elt.tagName.toLowerCase();
        // Bu elementin segmentini oluştur
        var segment = "/" + tagName + "[" + index + "]";
        // Her seferinde segmenti en başa ekle
        path = segment + path;
        elt = elt.parentNode;
      }
      return path;
    }
    return getRelativeXPath(arguments[0], arguments[1]);
    """
    relative_xpath = driver.execute_script(script, element, container)
    return '//*[@id="mw-content-text"]{relative_xpath}'.format(relative_xpath=relative_xpath)


def get_element_xpath(driver, element):
    script = """
    function getElementXPath(elt) {
        var path = "";
        for (; elt && elt.nodeType === 1; elt = elt.parentNode) {
            var index = 1;
            for (var sibling = elt.previousSibling; sibling; sibling = sibling.previousSibling) {
                if (sibling.nodeType === 1 && sibling.tagName === elt.tagName) {
                    index++;
                }
            }
            var tagName = elt.tagName.toLowerCase();
            var segment = "/" + tagName + "[" + index + "]";
            path = segment + path;
        }
        return path;
    }
    return getElementXPath(arguments[0]);
    """
    return driver.execute_script(script, element)

# all_list = ['The Bait Part 2',
#              'Jang Keun-Suk',
#              'https://asianwiki.com/Jang_Keun-Suk',
#              'The Bait-Pt2-Jang Keun-Suk.jpg',
#              'https://asianwiki.com/images/0/06/The_Bait-Pt2-Jang_Keun-Suk.jpg',
#              setBase64(drive, '//*[@id="mw-content-text"]/table[2]/tbody[1]/tr[2]/td[1]/a[1]/img[1]') # base64_data
#              ]


def collectLinksList(movie_name, a_tags, img_scrs, driver, container):
    # print(f"403_xpath: {xpath} - save_img_path: {save_img_path}")
    return [
        [
            movie_name,
            # tag[0].text.strip(),
            # tag[0].get_attribute("href").strip(),
            # tag[1].get_attribute('alt').strip(),
            # tag[1].get_attribute('src')
            # # setBase64(driver, get_relative_xpath(driver, tag[1], container))
            # # setBase64(driver, get_element_xpath(driver, tag[1]))
            (tag[0].text or "").strip(),
            (tag[0].get_attribute("href") or "").strip(),
            (tag[1].get_attribute('alt') or "").strip(),
            (tag[1].get_attribute('src') or "").strip(),
        ]
        for tag in zip(a_tags, img_scrs)
        # if (ifCondition(tag[0].get_attribute("href").strip(), condition_type=0))
        if ifCondition((tag[0].get_attribute("href") or "").strip(), condition_type=0)
    ]


def saveLink(link, file_name):
    if file_name is not None:
    # if file_name != None:
        try:
            with open(os.path.join("dataset", file_name), 'a', encoding="utf-8", errors="ignore") as f:
                f.write(f'{link}\n')
            f.close()
        except Exception as ex:
            print(f"saveLink_Error: {ex}")
    else:
        print(f"Kaydedilecek dosya adı boş olamaz. Lütfen dosya ismini giriniz!")


def readFile(file_path):
    try:
        datas = []
        with open(file_path, 'r', encoding="utf-8", errors="ignore") as f:
            datas = f.read().split('\n')
            del(datas[-1])  # kaldir
        f.close()
        return datas
    except Exception as ex:
        print(f"readFile_Error: {ex}")
        return []


def checkFolder(create_folder_path=None):
    if not os.path.exists(create_folder_path):
        os.makedirs(create_folder_path)


def copyFolder(src=None, dest=None, gender_main_path=r'dataset\asianwiki\gender\male'):
    if (src is not None) and (dest is not None):
        checkFolder(create_folder_path=os.path.join(gender_main_path))
        try:
            destination = shutil.copytree(src, dest)
            return destination
        except Exception as ex:
            return False
    else:
        print(f"Litfen kopyalancak dosyaların yolunu belirtin!")
    return False

def sleep_if_needed(min_s: float, max_s: float):
    if max_s <= 0:
        return
    if min_s < 0:
        min_s = 0
    if max_s < min_s:
        t_temp = max_s
        max_s = min_s
        min_s = t_temp
    time.sleep(random.uniform(min_s, max_s))

def normalize_url(url: str) -> str:
    if not url:
        return ""
    return url.strip()

def punctuation_person() -> str:
    return (string.punctuation
            .replace('_', '')
            .replace('-', '')
            +
            string.digits
            )

def build_person_folder_name(personel_name: str) -> str:
    if "(" in personel_name:
        personel_name = personel_name.split("(")[0]
    elif "%28" in personel_name:
        personel_name = personel_name.split("%28")[0]

    if personel_name.endswith(" ") or personel_name.endswith("_") or personel_name.endswith("-"):
        personel_name = personel_name[:-1]

    tmp_personel_name = build_folder_name(personel_name)
    if tmp_personel_name: person_folder_name = tmp_personel_name.replace(' ', '_')
    else: person_folder_name = personel_name

    return setFamousName(
        famous_name=person_folder_name,
        punctuation_digits=punctuation_person()
    )

def safe_old_urls(value):
    if isinstance(value, list):
        return [normalize_url(v) for v in value if v]
    if isinstance(value, str) and value.strip():
        return [normalize_url(value)]
    return []

def load_xpaths(driver, timeout: int=10,
                tag_type=By.XPATH,
                tag_value="/html/body/div[2]/article/h1"):
    try:
        return WebDriverWait(driver, timeout).until(
            EC.presence_of_element_located((tag_type, tag_value))
            )
    except Exception as ex:
        print(
            f"load_xpaths_Error: {tag_type} -> {tag_value}"
            f"\nError_Code: {ex}"
        )
        return None


def load_profile_data(driver, target_url: str):
    driver.get(target_url)
    personel_name = (
        load_xpaths(
            driver,
            timeout=5,
            tag_type=By.XPATH,
            tag_value='/html/body/div[2]/article/h1'
        )
        .text.strip()
    )
    person_img_xpath = '//*[@id="mw-content-text"]/div/div/a/img'
    img_element = load_xpaths(
        driver,
        timeout=5,
        tag_type=By.XPATH,
        tag_value=person_img_xpath
    )
    img_scr = img_element.get_attribute("src")
    img_scr = img_scr.strip() if (img_scr and "No_image_available" not in img_scr) else "No_image_available"

    try:
        gender_txt = (
            load_xpaths(
                driver,
                timeout=5,
                tag_type=By.XPATH,
                tag_value='//*[@id="mw-normal-catlinks"]/ul/li[1]/a'
            )
            .text.strip()
        )
        gender = setGender(gender_txt)
    except Exception:
        gender = "None"

    return {
        "personel_name_raw": personel_name,
        "person_folder_name": build_person_folder_name(personel_name),
        "img_scr": img_scr,
        "gender": gender,
        "person_img_xpath": person_img_xpath
    }

def load_profile_data_fast_old(driver, target_url: str,
                           wind: int, restart_every: int,
                           driver_path: str, headless: bool,
                           ):
    driver = wait_load_main_webpage(
        driver,
        target_url,
        wind,
        restart_every,
        driver_path,
        headless,
        by_tag_type=By.XPATH,
        by_tag_name="/html/body/div[2]/article/h1"
    )
    if driver is None:
        raise RuntimeError("Driver yüklenemedi")

    personel_name = driver.find_element(By.XPATH, '/html/body/div[2]/article/h1').text.strip()

    person_img_xpath = '//*[@id="mw-content-text"]/div/div/a/img'
    img_element = load_xpaths(
            driver,
            timeout=5,
            tag_type=By.XPATH,
            tag_value=person_img_xpath
        )

    if img_element is None:
        img_scr = "No_image_available"
    else:
        img_scr = img_element.get_attribute("src")
    img_scr = img_scr.strip() if (img_scr and "No_image_available" not in img_scr) else "No_image_available"

    try:
        gender_txt = (
            load_xpaths(
                driver,
                timeout=5,
                tag_type=By.XPATH,
                tag_value='//*[@id="mw-normal-catlinks"]/ul/li[1]/a'
            )
            .text.strip()
        )
        gender = setGender(gender_txt)
    except Exception:
        gender = "None"
    return_data = {
        "personel_name_raw": personel_name,
        "person_folder_name": build_person_folder_name(personel_name),
        "img_scr": img_scr,
        "gender": gender,
        "person_img_xpath": person_img_xpath
    }
    return driver, return_data


# tools/GegeneralTools.py
def load_profile_data_fast(driver, target_url: str,
                           wind: int, restart_every: int,
                           driver_path: str, headless: bool):
    driver = wait_load_main_webpage(
        driver,
        target_url,
        wind,
        restart_every,
        driver_path,
        headless,
        by_tag_type=By.XPATH,
        by_tag_name="/html/body/div[2]/article/h1"
    )
    if driver is None:
        raise RuntimeError("Driver yüklenemedi")

    # Doğrudan element aramak yerine bekleme fonksiyonunu kullanın
    h1_elem = load_xpaths(driver, timeout=10, tag_type=By.XPATH, tag_value='/html/body/div[2]/article/h1')
    if h1_elem is None:
        # Sayfa başlığı bulunamazsa alternatif olarak URL'den isim üret veya hata fırlat
        raise RuntimeError(f"Sayfa başlığı yüklenemedi (Bot engeli veya bozuk sayfa): {target_url}")

    personel_name = h1_elem.text.strip()
    person_img_xpath = '//*[@id="mw-content-text"]/div/div/a/img'

    img_element = load_xpaths(driver, timeout=5, tag_type=By.XPATH, tag_value=person_img_xpath)
    img_scr = img_element.get_attribute("src").strip() if img_element else "No_image_available"
    if "No_image_available" in img_scr:
        img_scr = "No_image_available"

    try:
        gender_elem = load_xpaths(driver, timeout=3, tag_type=By.XPATH,
                                  tag_value='//*[@id="mw-normal-catlinks"]/ul/li[1]/a')
        gender_txt = gender_elem.text.strip() if gender_elem else ""
        gender = setGender(gender_txt)
    except Exception:
        gender = "None"

    return driver, {
        "personel_name_raw": personel_name,
        "person_folder_name": build_person_folder_name(personel_name),
        "img_scr": img_scr,
        "gender": gender,
        "person_img_xpath": person_img_xpath
    }

# ----------------- MyDramaList Yapilandirmalari ----------------- #
def build_person_record_from_blob(person_url: str, blob: dict, safe_folder_name_fn):
    details = blob.get("details") or {}
    display_name = (blob.get("display_name") or "").strip()
    img_scr = (blob.get("img_scr") or "").strip()

    first_name = details.get("FirstName", "Unknown").replace(" ", "-")
    family_name = details.get("FamilyName", "Unknown").replace(" ", "-")

    gender = (details.get("Gender", "") or "").lower()
    nationality = details.get("Nationality", "") or ""
    born = details.get("Born", "") or ""

    folder_name = safe_folder_name_fn(
        first_name=first_name,
        family_name=family_name,
        display_name=display_name
    )

    person = {
        "born": born,
        "display_name": display_name,
        "family_name": family_name,
        "first_name": first_name,
        "folder_name": folder_name,
        "gender": gender,
        "img_scr": img_scr,
        "nationality": nationality,
        "person_name": display_name,  # senin mantığınla aynı: ekrandaki isim
        "url": person_url
    }
    return person


def extract_profile_blob_fast_v3(driver):
    js = r"""
    const qx = (xp) =>
      document.evaluate(xp, document, null, XPathResult.FIRST_ORDERED_NODE_TYPE, null).singleNodeValue;

    const qxs = (xp) =>
      document.evaluate(xp, document, null, XPathResult.ORDERED_NODE_SNAPSHOT_TYPE, null);

    // 1) Display name
    const nameEl = qx("//*[@id='content']/div/div[2]/div/div[2]/div/div[1]/div[1]/h1");
    const display_name = nameEl ? nameEl.textContent.trim() : "";
    if (display_name === ""){
        nameEl = qx("//*[@id='content']/div/div[2]/div/div[1]/div[1]/div[3]/div/div[2]/div/h1");
        display_name = nameEl ? nameEl.textContent.trim() : "";
    }

    // 2) Details
    const details = {};
    const detSnap = qxs("//*[@id='content']/div/div[2]/div/div[2]/div/div/div[2]/ul/li");
    for (let i = 0; i < detSnap.snapshotLength; i++) {
      const li = detSnap.snapshotItem(i);
      if (!li) continue;

      const b = li.querySelector("b");
      if (!b) continue;

      const rawKey = (b.textContent || "").trim();
      const key = rawKey.replace(":", "").replaceAll(" ", "").trim();
      if (!key) continue;

      const liText = (li.textContent || "").trim();
      const val = liText.replace(rawKey, "").trim();
      if (val) details[key] = val;
    }

    // 3) Image URL
    const imgEl = qx("//*[@id='content']/div/div[2]/div/div[2]/div/div[1]/div[2]/img");
    let img_scr = "";
    if (imgEl) {
      img_scr = imgEl.getAttribute("src") || imgEl.getAttribute("data-src") || imgEl.src || "";
      // imgEl.setAttribute("crossorigin", "anonymous"); // sadece canvas/base64 için gerekirse aç
    }

    // 4) Movie/Drama list (senin movie_xpath)
    const movie_urls = [];

    const addHref = (href) => {
      if (!href) return;
      href = href.trim();
      if (!href) return;
      movie_urls.push(href.endsWith("/cast") ? href : (href + "/cast"));
    };

    const movSnap = qxs("//*[@id='content']/div/div[2]/div/div[1]/div[1]/div[5]/table/tbody/tr/td[2]/b/a");
    const snapFast = qxs("//*[@id='content']/div/div[2]/div/div[1]/div[1]/div[5]//table//tbody//tr//td[2]//b//a");
    for (let i = 0; i < snapFast.snapshotLength; i++) {
      const a = snapFast.snapshotItem(i);
      if (!a) continue;
      addHref(a.href || "");
    }

    return { display_name, details, img_scr, movie_urls };
    """
    return driver.execute_script(js)

def extract_people_db_fast_v3(driver, col_players_db):
    # //*[@id='content']/div/div[2]/div/div[1]/div/div[3]/ul[5]/li[1]/div[2]/a/b
    js = r"""
    const root = document.evaluate(
        "//*[@id='content']/div/div[2]/div/div[1]/div/div[3]",
        document, null, XPathResult.FIRST_ORDERED_NODE_TYPE, null
    ).singleNodeValue;
    if (!root) return [];

    const rows = root.querySelectorAll("ul li");
    const out = [];

    for (const li of rows) {
        const a = li.querySelector(":scope > div:nth-child(2) a");
        const img = li.querySelector(":scope > div:nth-child(1) img");

        if (!a) continue;

        const href = a.href || "";
        const name = (a.textContent || "").trim();

        let img_url = "";
        if (img) {
            img_url =
                img.getAttribute("data-src") ||
                img.getAttribute("src") ||
                img.src || "";
        }

        out.push({ href, name, img: img_url });
    }
    return out;
    """

    items = driver.execute_script(js)  # 🔥 TEK selenium çağrısı

    people = []
    now = datetime.now()

    for it in items:
        href = (it.get("href") or "").strip()
        name = (it.get("name") or "").strip()
        img_url = (it.get("img") or "").strip()

        if not (href.startswith("https://mydramalist.com/people/") and name):
            continue

        # Mevcut placeholder kontrolünü AYNEN kullanıyorsun
        if is_placeholder_image(img_url, 1):
            print(f"No Image Available: {href} - {img_url}")
            col_players_db.update_one(
                {"url": href},
                {"$setOnInsert": {
                    "person_name": name,
                    "url": href,
                    "case": False,
                    "updated_at": now,
                    "created_at": now
                }},
                upsert=True
            )
            continue

        people.append({"person_name": name, "url": href})

    return people

def safe_folder_name(first_name: str, family_name: str, display_name: str, fallback="Unknown") -> str:
    first = (first_name or "").strip()
    family = (family_name or "").strip()
    disp = (display_name or "").strip()

    # 1) aday üret
    candidate = f"{family}_{first}".strip()

    # 2) boş/çöp ise display_name'e düş
    if candidate in ("", "Unknown_Unknown", "-_-", "_", "__"):
        candidate = disp.replace(" ", "_") if disp else fallback

    # 3) Unicode harfleri (Thai vb.) istemiyorsan bunu aktif bırak.
    #    Sadece [A-Za-z0-9_-] kalsın:
    candidate = re.sub(r"[^A-Za-z0-9_-]+", "", candidate)

    # 4) çoklu '_' ve '-' toparla
    candidate = re.sub(r"_-+", "-", candidate)  # "_-" -> "-"
    candidate = re.sub(r"-+_", "-", candidate)  # "-_" -> "-"
    candidate = re.sub(r"_+", "_", candidate)
    candidate = re.sub(r"-+", "-", candidate)

    # 5) baş/son '_' veya '-' kırp
    candidate = candidate.strip("_-")

    # 6) yine boş kaldıysa fallback
    if not candidate:
        candidate = re.sub(r"[^A-Za-z0-9_-]+", "_", disp) if disp else fallback
        candidate = re.sub(r"_+", "_", candidate)
        candidate = re.sub(r"-+", "-", candidate)
        candidate = candidate.strip("_-") or fallback

    return candidate

def get_dbperson(profile_infos: list, db_players: pymongo.collection.Collection) -> list:
    # Bu profiller daha önce işlenmiş mi? (resimli veya resimsiz fark etmez)
    urls = [p["url"] for p in profile_infos if
            (p.get("url") or "").startswith("https://mydramalist.com/people/")]

    return [
        list(set(urls)),
        list(set(
            [
                doc["url"] for doc in db_players.find(
                {"url": {"$in": urls}},
                      {"url": 1, "_id": 0}
                )
            ]
        ))
    ]

# all_list = ['The Bait Part 2',
#              'Jang Keun-Suk',
#              'https://asianwiki.com/Jang_Keun-Suk',
#              'The Bait-Pt2-Jang Keun-Suk.jpg',
#              'https://asianwiki.com/images/0/06/The_Bait-Pt2-Jang_Keun-Suk.jpg',
#              setBase64(drive, '//*[@id="mw-content-text"]/table[2]/tbody[1]/tr[2]/td[1]/a[1]/img[1]') # base64_data
#              ]