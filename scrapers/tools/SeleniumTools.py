import undetected_chromedriver as uc

from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as ec
from selenium.webdriver.common.by import By

from selenium.common.exceptions import TimeoutException
from selenium.common.exceptions import WebDriverException

from webdriver_manager.chrome import ChromeDriverManager

import time
import os
from pathlib import Path

def find_cached_chromedriver_old():
    base_dir = Path.home() / ".wdm" / "drivers" / "chromedriver" / "win64"

    if not base_dir.exists():
        return None

    drivers = list(base_dir.rglob("chromedriver.exe"))

    if not drivers:
        return None

    # En son değiştirileni al
    latest_driver = max(
        drivers,
        key=lambda p: p.stat().st_mtime
    )

    return str(latest_driver)

def find_cached_chromedriver():
    base_dir = Path.home() / ".wdm" / "drivers" / "chromedriver" / "win64"
    if not base_dir.exists():
        return None

    # Güncel sürümü manager üzerinden oku
    manager = ChromeDriverManager()
    chrome_version = manager.driver.get_browser_version_from_os()
    if not chrome_version:
        return None

    chrome_major = chrome_version.split(".")[0]  # Örn: '153'

    # Sadece o ana sürüme ait klasördeki sürücüleri bul
    matched_drivers = list(base_dir.glob(f"*{chrome_major}*/**/chromedriver.exe"))
    print(f"{chrome_version}-{chrome_major}-{matched_drivers}")
    if matched_drivers:
        return str(max(matched_drivers, key=lambda p: p.stat().st_mtime))

    return None

def get_or_download_chromedriver() -> str:
    """
    Sistemdeki kurulu Chrome sürümünü kontrol eder.
    - Önbellekte eşleşen güncel ChromeDriver varsa doğrudan yolunu döner.
    - Önbellekte yoksa veya sürüm eskiyse ChromeDriverManager ile indirip güncel yolu döner.
    """
    base_dir = Path.home() / ".wdm" / "drivers" / "chromedriver" / "win64"

    try:
        manager = ChromeDriverManager()
        chrome_version = manager.driver.get_browser_version_from_os()

        if chrome_version and base_dir.exists():
            chrome_major = chrome_version.split(".")[0]  # Örn: '153'
            matched_drivers = list(base_dir.glob(f"*{chrome_major}*/**/chromedriver.exe"))

            if matched_drivers:
                # Eşleşen güncel sürücülerden en son değiştirileni al
                latest_driver = max(matched_drivers, key=lambda p: p.stat().st_mtime)
                return str(latest_driver)
    except Exception as ex:
        print(f"[Uyarı] Önbellek kontrolünde hata: {ex}")

    # Önbellekte bulunamadıysa veya sürüm uyuşmuyorsa otomatik indir
    print("[Info] Güncel ChromeDriver indiriliyor...")
    return ChromeDriverManager().install()

def close_driver(driver):
    try:
        if driver:
            driver.quit()
    except Exception:
        pass

def setupOption(driver_index=1):
    if driver_index == 1:
        options = webdriver.ChromeOptions()
    else:
        options = webdriver.FirefoxOptions()
    options.headless = False  # open browser
    # options.headless = True  # not open browser
    # options.add_experimental_option("excludeSwitches", ["enable-logging", "enable-automation"])

    options.add_experimental_option("excludeSwitches", ["enable-automation"])
    options.add_experimental_option("useAutomationExtension", False)

    options.add_argument(
        "user-agent=Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/62.0.3202.62 Safari/537.36")

    options.add_argument("start-maximized") # Tarayıcıyı tam ekran aç
    options.add_argument("disable-infobars")
    options.add_argument("--disable-extensions")

    return options

def setupDriver(driver_index=1):
    #print("driver_index:{driver_index}".format(driver_index=driver_index))
    if driver_index == 1:
        # service = Service(executable_path=r'win\chromedriver-win64\chromedriver.exe')
        connect_driver = webdriver.Chrome(
            # service=service,
            service=webdriver.ChromeService(),
            options=setupOption(driver_index=driver_index))
    else:
        # service = Service(executable_path=r'win\operadriver_win64-122\operadriver.exe')
        connect_driver = webdriver.Firefox(
            service=webdriver.FirefoxService(),
            options=setupOption(driver_index=driver_index)
        )
    # elif driver_index == 2:
    #     service = Service(executable_path=r'win\operadriver_win64-122\operadriver.exe')
    #     connect_driver = webdriver.Opera(
    #         service=service,
    #         options=setupOption())
    # wait = WebDriverWait(connect_driver, 10)
    # element = WebDriverWait(connect_driver, 15).until(ec.presence_of_element_located((By.ID, "mw-content-text")))
    # connect_driver.minimize_window()  # clicking "-" button on browser

    return connect_driver

# === Driver Ayarları ===
def setup_driver_old(drive_path=None, headless=False):
    options = webdriver.ChromeOptions()
    # False # browser ı ac, True # browser ı kapa
    if headless:
        # Ekransız mod
        # dinamik sayfalarda kullanılmaz
        options.add_argument("--headless=new")
        options.add_argument("--window-size=1920,1080")  # KRİTİK
        options.add_argument("--disable-gpu")  # Windows için stabilite
        options.add_argument("--disable-webgl")
        options.add_argument("--disable-software-rasterizer")
    else:
        # 1. YÖNTEM (HİLE): Pencereyi ekran sınırlarının çok dışına it
        # Bu sayede ekranda "popup" gibi açıldığını görmezsin.
        options.add_argument("--window-position=-10000,0")
        options.add_argument("--window-size=1920,1080")  # headful’da da sabitle

    # 'normal'	(Varsayılan) Sayfa tamamen yüklendiğinde (document.readyState == "complete"). Yani tüm JS, resimler, iframe’ler vs. dahil.
    # 'eager'	Sayfa DOMContentLoaded olduğunda devam eder (document.readyState == "interactive"). Yani HTML ve DOM hazır, ama resim, stil, JS henüz yükleniyor olabilir.
    # 'none'	Sayfa yüklemesi beklenmeden hemen devam eder. Çok tehlikeli, kontrol sende.
    options.page_load_strategy = 'normal'
    # options.page_load_strategy = 'eager'
    # options.add_argument("--ignore_local_proxy")
    options.add_argument("--ignore-certificate-errors")  # bazı ağlarda işe yarar (opsiyonel)
    options.add_argument("--disable-background-networking")
    options.add_argument("--disable-notifications")
    options.add_argument("--disable-sync")
    options.add_argument("--disable-extensions")
    options.add_argument("--no-first-run")
    options.add_argument("--no-default-browser-check")
    options.add_argument("--disable-dev-shm-usage")
    options.add_argument("--no-sandbox")
    options.add_argument("--log-level=3")  # log azaltır
    options.add_argument("--disable-logging")
    options.add_argument("--disable-blink-features=AutomationControlled")

    # options.add_experimental_option("excludeSwitches", ["enable-logging"])
    options.add_experimental_option("excludeSwitches", ["enable-automation", "enable-logging"])
    options.add_experimental_option("useAutomationExtension", False)
    # prefs = {"profile.managed_default_content_settings.images": 2}
    # options.add_experimental_option("prefs", prefs)
    service = Service(drive_path)

    driver = webdriver.Chrome(service=service, options=options)

    # Ayrıca runtime'da da ayarla:
    driver.set_page_load_timeout(60)
    driver.set_script_timeout(60)
    # driver.minimize_window()

    return driver

def setup_driver_test1(drive_path=None, headless=False):
    options = webdriver.ChromeOptions()

    # Otomasyon bayraklarını ve blink özelliklerini kapat
    options.add_argument("--disable-blink-features=AutomationControlled")
    options.add_experimental_option("excludeSwitches", ["enable-automation", "enable-logging"])
    options.add_experimental_option("useAutomationExtension", False)

    # Modern ve güncel User-Agent
    options.add_argument(
        "user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36")

    if headless:
        options.add_argument("--headless=new")
        options.add_argument("--window-size=1920,1080")
        options.add_argument("--disable-gpu")
    else:
        # Ekranın dışına itmek yerine pencereyi normalize edin (Cloudflare boyutu kontrol eder)
        options.add_argument("--window-size=1280,800")
        options.add_argument("--start-maximized")

    options.page_load_strategy = 'eager'
    options.add_argument("--no-sandbox")
    options.add_argument("--disable-dev-shm-usage")
    options.add_argument("--disable-notifications")
    options.add_argument("--disable-extensions")

    service = Service(drive_path) if drive_path else webdriver.ChromeService()
    driver = webdriver.Chrome(service=service, options=options)

    # navigator.webdriver bayrağını sil
    driver.execute_cdp_cmd(
        "Page.addScriptToEvaluateOnNewDocument",
        {
            "source": """
                Object.defineProperty(navigator, 'webdriver', {
                    get: () => undefined
                });
                Object.defineProperty(navigator, 'plugins', {
                    get: () => [1, 2, 3, 4, 5]
                });
                Object.defineProperty(navigator, 'languages', {
                    get: () => ['en-US', 'en']
                });
            """
        }
    )

    driver.set_page_load_timeout(30)
    driver.set_script_timeout(30)
    return driver


def setup_driver(drive_path=None, headless=False):
    options = uc.ChromeOptions()

    if headless:
        options.add_argument("--headless=new")
        # Cloudflare tespiti için pencere boyutunu standart tutun
        options.add_argument("--window-size=1366,768")
    else:
        options.add_argument("--window-position=-10000,0")
        options.add_argument("--window-size=1920,1080")  # headful’da da sabitle
        # Ekranın dışına itmek yerine pencereyi normalize edin (Cloudflare boyutu kontrol eder)
        # options.add_argument("--window-size=1280,800")
        options.add_argument("--start-maximized")


    options.add_argument("--no-sandbox")
    options.add_argument("--disable-dev-shm-usage")

    # setup_driver içine eklenebilir:
    profile_path = os.path.join(os.getcwd(), "selenium_profile")
    options.add_argument(f"--user-data-dir={profile_path}")
    # # Bu sekilde drive nesnesi olusturuldugunda
    # # "Sorry, you have been blocked" hatasi alindi
    # service = Service(drive_path)
    # driver = webdriver.Chrome(service=service, options=options)

    # undetected-chromedriver driver_executable_path parametresi alır
    driver = uc.Chrome(options=options, driver_executable_path=drive_path)

    driver.set_page_load_timeout(45)
    return driver

def force_close_driver_windows_old(driver):
    """
    Windows: SADECE bu driver'ın chromedriver PID'ini (ve çocuklarını) öldürür.
    Kullanıcının açtığı chrome.exe süreçlerine dokunmaz.
    """
    if driver is None:
        return

    # Önce nazik kapatmayı dene
    try:
        driver.quit()
        return
    except Exception as e:
        print(f"⚠️ driver.quit() başarısız, PID ile kapatılacak: {e}")

    # chromedriver PID yakala
    pid = None
    try:
        svc = getattr(driver, "service", None)
        proc = getattr(svc, "process", None) if svc else None
        pid = getattr(proc, "pid", None) if proc else None
    except Exception:
        pid = None

    if pid:
        # /T => child process tree (chromedriver’ın açtığı chrome) kapanır
        print(f"taskkill /F /T /PID {pid} >NUL 2>NUL")
        os.system(f"taskkill /F /T /PID {pid} >NUL 2>NUL")
    else:
        # PID yoksa son çare: sadece chromedriver.exe öldür (yine manual chrome’a dokunmaz)
        print("taskkill /F /IM chromedriver.exe >NUL 2>NUL")
        os.system("taskkill /F /IM chromedriver.exe >NUL 2>NUL")
    print("finished force_close_driver_windows")
    #time.sleep(0.5)


def close_driver_old(driver):
    try:
        if driver:
            driver.quit()
    except Exception as quit_error:
        print(f"⚠️ driver.quit() sırasında hata: {quit_error}")
        force_close_driver_windows(driver)


def wait_load_main_webpage_old(con_driver,
                           url,
                           counter: int,
                           restart_every: int,
                           driver_path: str,
                           headless: bool,
                           by_tag_type=By.CLASS_NAME,
                           by_tag_name="box-body"):
    try:
        con_driver = maybe_restart_driver(con_driver, counter, restart_every, driver_path, headless)
        print(f"🌐 Page loading: {url}")
        print("wait_load_main_webpage buradayım")
        con_driver.get(url)
        try:
            WebDriverWait(con_driver, 10).until(
                ec.presence_of_element_located((by_tag_type, by_tag_name))
            )
        except Exception as e:
            print(f"❌❌ Load Page Error: {e} \n ❌❌target_url: {url}")
            return None
        return con_driver
    except Exception as e:
        print(f"❌❌ wait_load_main_webpage_Error: {e} \n ❌❌target_url: {url}")
        return None

def wait_load_main_webpage_test1(con_driver,
                           url,
                           counter: int,
                           restart_every: int,
                           driver_path: str,
                           headless: bool,
                           by_tag_type=By.CLASS_NAME,
                           by_tag_name="box-body"):
    try:
        con_driver = maybe_restart_driver(con_driver, counter, restart_every, driver_path, headless)
        print(f"🌐 Page loading: {url}")
        con_driver.get(url)

        WebDriverWait(con_driver, 10).until(
            ec.presence_of_element_located((by_tag_type, by_tag_name))
        )
        return con_driver
    except Exception as e:
        print(f"❌❌ Load Page Error: {e} \n❌❌ target_url: {url}")
        # Driver kilitlenmiş olabileceği için bir sonraki istekte baştan açılmasını sağla
        close_driver(con_driver)
        return None

def force_close_driver_windows(driver):
    """
    Windows: Driver'a ait chromedriver ve chrome.exe süreçlerini PID üzerinden zorla sonlandırır.
    """
    if driver is None:
        return

    # 1) PID bilgilerini quit çağrısından ÖNCE yakala
    pids_to_kill = set()

    # undetected-chromedriver için browser PID
    browser_pid = getattr(driver, "browser_pid", None)
    if browser_pid:
        pids_to_kill.add(browser_pid)

    # Standart chromedriver service PID
    try:
        svc = getattr(driver, "service", None)
        proc = getattr(svc, "process", None) if svc else None
        if proc and proc.pid:
            pids_to_kill.add(proc.pid)
    except Exception:
        pass

    # 2) Nazik kapatmayı dene
    try:
        driver.quit()
    except Exception as e:
        print(f"⚠️ driver.quit() sırasında hata: {e}")

    # 3) Kalan veya kilitlenen süreçleri PID ağacıyla (/T) öldür
    for pid in pids_to_kill:
        try:
            os.system(f"taskkill /F /T /PID {pid} >NUL 2>NUL")
        except Exception:
            pass

    # 4) Windows port/soket temizliği için kritik bekleme
    time.sleep(1.5)


def kill_processes_by_pids(pids: set):
    """
    Verilen PID değerlerini ve onların alt süreçlerini (/T) Windows üzerinde zorla sonlandırır.
    """
    for pid in pids:
        if pid:
            try:
                # /F: Zorla kapat, /T: Alt süreçleriyle (child processes) birlikte kapat
                os.system(f"taskkill /F /T /PID {pid} >NUL 2>NUL")
            except Exception as e:
                print(f"⚠️ PID {pid} kapatılırken hata: {e}")
    # Windows'un soketleri ve portları serbest bırakması için kısa bekleme
    time.sleep(1.0)


def close_driver(driver):
    """
    Önce PID'leri güvenceye alır, nazikçe quit() dener;
    başarısız olursa yakalanan PID'ler üzerinden zorla kapatır.
    """
    if driver is None:
        return

    # 1. PID'leri henüz nesne sağlamken en başta yakala
    pids_to_kill = set()

    # undetected-chromedriver için Chrome ana process PID'i
    browser_pid = getattr(driver, "browser_pid", None)
    if browser_pid:
        pids_to_kill.add(browser_pid)

    # Standart ChromeDriver service PID'i
    try:
        svc = getattr(driver, "service", None)
        proc = getattr(svc, "process", None) if svc else None
        if proc and proc.pid:
            pids_to_kill.add(proc.pid)
    except Exception:
        pass

    # 2. Nazikçe kapatmayı dene
    try:
        driver.quit()
    except Exception as ex:
        print(f"⚠️ Standart driver.quit() başarısız oldu ({ex}), zorla sonlandırılıyor...")
        # 3. quit() çökerse veya kilitlenirse en başta alınan PID'leri temizle
        kill_processes_by_pids(pids_to_kill)

def new_driver(driver_path: str, headless: bool):
    # print(f"driver_path: {driver_path}")
    return setup_driver(drive_path=driver_path, headless=headless)

def maybe_restart_driver(driver, counter: int, restart_every: int, driver_path: str, headless: bool):
    if driver is None:
        print(f"[Info] Selenium ile Browser açılıyor.\n#{'*'*35}#{'*'*35}#")
        return new_driver(driver_path, headless)

    if restart_every > 0 and counter > 0 and counter % restart_every == 0:
        print(f"[Info] Selenium ile Browser restart ediliyor.\n#{'*'*35}#{'*'*35}#")
        close_driver(driver)
        driver = None
        # Portların ve geçici dosyaların tamamen boşalması için kısa bekleme
        time.sleep(2)
        return new_driver(driver_path, headless)

    return driver

def wait_load_main_webpage(con_driver,
                           url,
                           counter: int,
                           restart_every: int,
                           driver_path: str,
                           headless: bool,
                           by_tag_type=By.ID,
                           by_tag_name="mw-content-text"):
    import random
    try:
        con_driver = maybe_restart_driver(con_driver, counter, restart_every, driver_path, headless)
        con_driver.get(url)

        # Cloudflare "Just a moment..." veya "Blocked" durumunu bekleme
        # time.sleep(1.5)
        time.sleep(random.randint(1, 3))
        timeout_counter = random.randint(5, 15)
        # Sayfa içeriğinin gelmesini bekle
        WebDriverWait(con_driver, timeout_counter).until(
            ec.presence_of_element_located((by_tag_type, by_tag_name))
        )
        return con_driver
    except Exception as e:
        # Eğer yine de blok ekranı gelirse tespit et
        if con_driver and "blocked" in con_driver.page_source.lower():
            print(f"⚠️ [BLOCKED] Cloudflare engeline takıldı: {url}")
        else:
            print(f"❌ Load Error ({url}): {e}")
        return con_driver

# === Güvenli GET (timeout olursa driver reset + retry) ===
def safe_get(url, setup_driver_fn, headless=False, driver=None, retries=2, page_load_timeout=60):
    """
    driver.get() kilitlenirse:
    - driver'ı kapatır (PID kill)
    - yeni driver açar
    - aynı URL'i tekrar dener
    Dönüş: (driver, ok_bool)
    """
    for attempt in range(1, retries + 1):
        if driver is None:
            driver = setup_driver_fn(headless=headless)

        try:
            # driver.set_page_load_timeout(page_load_timeout)
            # driver.set_script_timeout(page_load_timeout)
            driver.get(url)
            element = WebDriverWait(driver, 5).until(
                ec.presence_of_element_located((By.CLASS_NAME, "box-body")))
            return driver, True

        except Exception as e:
            msg = str(e)
            is_local_timeout = ("HTTPConnectionPool(host='localhost'" in msg and "Read timed out" in msg) \
                               or isinstance(e, (TimeoutException, WebDriverException))

            print(f"⚠️ safe_get hata (deneme {attempt}/{retries}): {e}")

            # Bu noktada driver büyük ihtimalle “yarı-kilitli”
            if is_local_timeout:
                # 🔥 DRIVER KİLİTLENDİ → ÖLDÜR
                print("🧨 Driver kilitlendi, kapatılıyor.")
                force_close_driver_windows(driver)
                driver = None
            else:
                # 🟡 Sayfa/element sorunu → driver sağlıklı
                print("🟡 Sayfa geçici sorun, driver korunuyor.")

            # küçük backoff
            time.sleep(0.5 * attempt)

    return driver, False