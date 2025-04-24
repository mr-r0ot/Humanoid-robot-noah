import os,random,json
import serial
import time
import serial.tools.list_ports
import requests
import speech_recognition as sr
import numpy as np
import pyttsx3
import asyncio
import edge_tts
import subprocess
import sys
import tempfile
from openai import OpenAI
import csv,re
from io import StringIO
import pyaudio


from PIL import Image,ImageDraw,ImageFont
from luma.core.interface.serial import i2c
from luma.oled.device import ssd1306




def TalkOffline(text):
    engine = pyttsx3.init()
    rate = engine.getProperty('rate')
    engine.setProperty('rate', rate - 25)
    volume = engine.getProperty('volume')
    engine.setProperty('volume', volume + 0.25)
    voices = engine.getProperty('voices')
    for voice in voices:
        if hasattr(voice, 'languages') and voice.languages:
            lang_item = voice.languages[0]
            try:
                lang = lang_item.decode('utf-8') if isinstance(lang_item, bytes) else lang_item
            except Exception:
                lang = str(lang_item)
            if 'en' in lang.lower():
                engine.setProperty('voice', voice.id)
                break
    engine.say(text)
    engine.runAndWait()


OLED_FACE_ERROR = False
try:
    oled_serial = i2c(port=1, address=0x3C)           # renamed from `serial`
    device = ssd1306(oled_serial)
    width = device.width
    height = device.height
    image = Image.new("1", (width, height))
    draw = ImageDraw.Draw(image)
except:
    TalkOffline("Oh. I have a possible hardware problem connecting to the face monitor!")
    OLED_FACE_ERROR = True


class Physical:
    def __init__(self, baudrate=9600, timeout=1):
        self.ser = None
        self.connect_to_arduino(baudrate, timeout)

    def connect_to_arduino(self, baudrate, timeout):
        ports = list(serial.tools.list_ports.comports())
        for port in ports:
            try:
                self.ser = serial.Serial(port.device, baudrate, timeout=timeout)
                time.sleep(2)  # زمان لازم برای راه‌اندازی Arduino
                self.ser.write(b'ping\n')
                response = self.ser.readline().decode('utf-8').strip()
                if response == 'pong':
                    print(f"Connected to Arduino on {port.device}")
                    return
                else:
                    self.ser.close()
            except Exception as e:
                print(f"Failed to connect on {port.device}: {e}")
        print("No Arduino found!")
        self.ser = None

    def Distance(self):
        if self.ser:
            # پاکسازی بافرهای ورودی و خروجی
            self.ser.reset_input_buffer()
            self.ser.reset_output_buffer()
            self.ser.write(b'get_distances\n')
            self.ser.flush()
            start = time.time()
            while time.time() - start < 1:
                if self.ser.in_waiting > 0:
                    line = self.ser.readline().decode('utf-8').strip()
                    if line.startswith("Distances:"):
                        try:
                            distances = list(map(float, line.split()[1:]))
                            return distances
                        except Exception as e:
                            print("Error parsing distances:", e)
                            return [0, 0, 0, 0]
            return [0, 0, 0, 0]
        return [0, 0, 0, 0]

    def engine(self, config):
        if self.ser:
            # ترکیب فرمان‌ها در یک بلوک جهت ارسال همزمان
            command_block = ""
            for key, value in config.items():
                command_block += f"{key},{value['mode']},{value['rotate']},{value['time']}\n"
            self.ser.write(command_block.encode())
            # انتظار به اندازه زمان بیشینه فرمان‌ها (اضافه بر کمی حاشیه)
            max_time = max(value['time'] for value in config.values())
            time.sleep(max_time + 0.5)

    def close(self):
        if self.ser:
            self.ser.close()
            print("Serial connection closed.")










class subAI:
    def textGenetrator(key):
        key=key.lower()
        database=[
            'problem',['We have a problem bro!','Oh my god its bad!','holy shit!','Fuck, Fuck, Fuck','No, No, No, No!','Holy Shit, Help mee!','Fuck, Fuck, I need to you, please help me!'],
            'welcom',['I am happy to see you people of the earth!','Whats Your name?',"Have I seen you before?",'Are you my enemy or my friend?'],
            'connectok',['Oh well, at least my side win is healthy.','My original parts are intact!',"I didn't find any major technical issues with my main system"]
        ]
        i=0
        for data in database:
            i=i+1
            if data==key:
                return(random.choices(database[i])[0])
    
            















class NetWork:
    def Check_Net():
        try:
            requests.get('https://google.com')
            return True
        except:
            return False


WIFI_SSID = "nova"

def check_wifi_connection():
    """
    بررسی می‌کند که آیا سیستم به شبکه WIFI_SSID متصل است یا خیر.
    برای ویندوز از دستور netsh wlan show interfaces و برای لینوکس از nmcli استفاده می‌کند.
    """
    try:
        if sys.platform.startswith("win"):
            # دریافت اطلاعات از netsh wlan show interfaces
            cmd = ["netsh", "wlan", "show", "interfaces"]
            result = subprocess.run(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
            output = result.stdout.lower()
            # جستجو برای رشته "ssid" در خروجی
            for line in output.splitlines():
                if "ssid" in line:
                    # فرض می‌کنیم خط به صورت "SSID                   : nova" است.
                    parts = line.split(":")
                    if len(parts) >= 2 and parts[1].strip() == WIFI_SSID.lower():
                        return True
        else:
            # برای لینوکس: استفاده از nmcli برای بررسی اتصال فعال
            cmd = ["nmcli", "-t", "-f", "active,ssid", "dev", "wifi"]
            result = subprocess.run(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
            for line in result.stdout.splitlines():
                # خروجی معمولاً به صورت yes:nova یا no:...
                if line.startswith("yes:"):
                    ssid = line.split("yes:")[1].strip()
                    if ssid.lower() == WIFI_SSID.lower():
                        return True
    except Exception as e:
        print("خطا در بررسی اتصال:", e)
    return False

def connect_wifi_linux(password=None):
    """
    تلاش برای اتصال به وای‌فای در سیستم‌های لینوکسی با استفاده از nmcli.
    """
    if password is None:
        cmd = ["nmcli", "device", "wifi", "connect", WIFI_SSID]
    else:
        cmd = ["nmcli", "device", "wifi", "connect", WIFI_SSID, "password", password]
    
    result = subprocess.run(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
    return result.returncode, result.stdout, result.stderr

def generate_wifi_profile_xml(password=None):
    """
    ایجاد فایل XML پروفایل وای‌فای برای ویندوز.
    در صورت وجود password، پروفایل برای شبکه امن و در غیر این صورت برای شبکه باز ایجاد می‌شود.
    """
    if password is None:
        xml_content = f'''<?xml version="1.0"?>
<WLANProfile xmlns="http://www.microsoft.com/networking/WLAN/profile/v1">
    <name>{WIFI_SSID}</name>
    <SSIDConfig>
        <SSID>
            <name>{WIFI_SSID}</name>
        </SSID>
    </SSIDConfig>
    <connectionType>ESS</connectionType>
    <connectionMode>manual</connectionMode>
    <MSM>
        <security>
            <authEncryption>
                <authentication>open</authentication>
                <encryption>none</encryption>
                <useOneX>false</useOneX>
            </authEncryption>
        </security>
    </MSM>
</WLANProfile>'''
    else:
        xml_content = f'''<?xml version="1.0"?>
<WLANProfile xmlns="http://www.microsoft.com/networking/WLAN/profile/v1">
    <name>{WIFI_SSID}</name>
    <SSIDConfig>
        <SSID>
            <name>{WIFI_SSID}</name>
        </SSID>
    </SSIDConfig>
    <connectionType>ESS</connectionType>
    <connectionMode>manual</connectionMode>
    <MSM>
        <security>
            <authEncryption>
                <authentication>WPA2PSK</authentication>
                <encryption>AES</encryption>
                <useOneX>false</useOneX>
            </authEncryption>
            <sharedKey>
                <keyType>passPhrase</keyType>
                <protected>false</protected>
                <keyMaterial>{password}</keyMaterial>
            </sharedKey>
        </security>
    </MSM>
</WLANProfile>'''
    return xml_content

def connect_wifi_windows(password=None):
    """
    تلاش برای اتصال به وای‌فای در ویندوز با استفاده از netsh wlan.
    ابتدا یک پروفایل موقت ایجاد می‌شود، سپس با استفاده از آن اقدام به اتصال می‌کند.
    """
    xml_profile = generate_wifi_profile_xml(password)
    # ایجاد فایل XML موقت
    with tempfile.NamedTemporaryFile("w", delete=False, suffix=".xml") as temp_file:
        temp_file.write(xml_profile)
        temp_filename = temp_file.name

    try:
        # افزودن پروفایل به سیستم
        add_profile_cmd = f'netsh wlan add profile filename="{temp_filename}" user=all'
        subprocess.run(add_profile_cmd, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
        # تلاش برای اتصال
        connect_cmd = f'netsh wlan connect name={WIFI_SSID} ssid={WIFI_SSID}'
        result = subprocess.run(connect_cmd, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
        return result.returncode, result.stdout, result.stderr
    finally:
        os.remove(temp_filename)

def connect_wifi(password=None):
    """
    انتخاب تابع مناسب بر اساس سیستم عامل.
    """
    if sys.platform.startswith("win"):
        return connect_wifi_windows(password)
    else:
        return connect_wifi_linux(password)











def Talk(text, farsi=False):
    async def main(text, farsi):
        try:
            voice = "fa-IR-DilaraNeural" if farsi else "en-US-GuyNeural"
            communicate = edge_tts.Communicate(text, voice)
            with tempfile.NamedTemporaryFile(delete=False, suffix=".mp3") as tmp_file:
                output_file = tmp_file.name
            await communicate.save(output_file)
            subprocess.run(['mpg123', output_file])
            time.sleep(0.5)
            os.remove(output_file)
        except Exception as e:
            print("Error:", e)
    asyncio.run(main(text, farsi))











def find_compatible_device(sample_rate=16000, channels=1):
    """
    Search for the first input device that supports:
      - at least `channels` channels
      - paInt16 format at `sample_rate`
    Returns the device index and name, or (None, None) if not found.
    """
    pa = pyaudio.PyAudio()
    device_index = None
    device_name = None

    for idx in range(pa.get_device_count()):
        info = pa.get_device_info_by_index(idx)
        if info.get('maxInputChannels', 0) < channels:
            continue
        try:
            if pa.is_format_supported(
                rate=sample_rate,
                input_device=idx,
                input_channels=channels,
                input_format=pyaudio.paInt16
            ):
                device_index = idx
                device_name = info.get('name', 'Unknown')
                break
        except ValueError:
            continue

    pa.terminate()
    return device_index, device_name


def Listen(timeout=4, phrase_time_limit=10, retry_interval=2, max_wait=60):
    """
    Listens once, returns recognized speech (in Persian) as a string.
    Automatically handles audio device selection and cleanup.

    On boot via cron, device may not be ready. This will retry finding
    a compatible device until max_wait seconds have elapsed.
    """
    recognizer = sr.Recognizer()

    # Retry device detection on startup
    waited = 0
    device_index = None
    device_name = None
    while waited < max_wait:
        device_index, device_name = find_compatible_device()
        if device_index is not None:
            break
        print(f"No compatible device found, retrying in {retry_interval}s... ({waited}/{max_wait}s elapsed)")
        time.sleep(retry_interval)
        waited += retry_interval

    if device_index is None:
        raise RuntimeError("No compatible input device found after waiting.")

    print(f"Using microphone #{device_index}: {device_name}")
    sample_rate = 16000
    chunk_size = 1024
    transcript = ""
    mic = None

    try:
        mic = sr.Microphone(
            device_index=device_index,
            sample_rate=sample_rate,
            chunk_size=chunk_size
        )
        with mic as source:
            print("Adjusting for ambient noise...")
            recognizer.adjust_for_ambient_noise(source)
            print("Listening...")

            audio = recognizer.listen(
                source,
                timeout=timeout,
                phrase_time_limit=phrase_time_limit
            )
            print("Recording complete, recognizing speech...")
            transcript = recognizer.recognize_google(audio, language="fa-IR")
            print("Recognition successful:", transcript)

    except sr.WaitTimeoutError:
        print("No speech detected within timeout.")
    except sr.UnknownValueError:
        print("Could not understand audio.")
    except sr.RequestError as e:
        print("Could not request results from service;", e)
    except OSError as e:
        print("Audio device error:", e)
    finally:
        # Ensure PyAudio resources are released
        if mic:
            try:
                mic.pyaudio.terminate()
            except Exception:
                pass

    return transcript










def extract_json(text):
    for i, char in enumerate(text):
        if char == '{':
            count = 0
            for j in range(i, len(text)):
                if text[j] == '{':
                    count += 1
                elif text[j] == '}':
                    count -= 1
                if count == 0:
                    candidate = text[i:j+1]
                    try:
                        json.loads(candidate)
                        return candidate
                    except Exception:
                        break












def fetch_sheet_rows(url=None):
    url = url or "https://docs.google.com/spreadsheets/d/1YSblzQyaXujPaHf3HiZqoTwd3uQ3hpN47D-cwYF1TCY/edit?usp=sharing"
    m = re.search(r"/d/([\w-]+)", url)
    sid = m.group(1) if m else url
    r = requests.get(f"https://docs.google.com/spreadsheets/d/{sid}/export?format=csv&gid=0"); r.raise_for_status()
    li= list(csv.reader(StringIO(r.text)))
    out=[]
    for g in li:out.append(g[0].replace("'",''))
    return out









def AI(text,loc):
    text=text.replace('gpt','nova').replace('GPT','nova').replace('deepseek','nova').replace('DeepSeek','nova')

    data= """
**شرح وظیفه:**

- پس از پردازش، تنها خروجی JSON بدون هیچ توضیح اضافی ارسال شود. (بسیار بسیار مهم)
- شما یک شبیه‌سازی از یک ربات انسان‌نما پیشرفته را اجرا می‌کنید.  
- نام ربات «نوا» است؛ او دارای هویت و خودآگاهی می‌باشد.  
- به هیچ عنوان نباید از مدل هوش مصنوعی که استفاده می شود نام ببری و بجای آن بگو NovaAI
- سازنده تو محمد طاها گرجی است
- تو یک بدنه استوانه آهنب داری به همراه چهار چرخ و یک سر
- ربات تنها زمانی که لازم باشد حرکت می‌کند.  
- شما می‌توانید با کنترل موتورهای ربات (پاها) جهت حرکت (جلو *forward* یا عقب *rear*) را تعیین کنید. 

**ورودی‌های قابل دریافت:**

1. **درخواست متنی:**  
   مثلاً:  
   ```
"""+text+"""
   ```

2. **فاصله فیزیکی بدن ربات از چهار جهت (بالا، پایین، چپ، راست):**  
   (این قسمت ممکن است خالی باشد)  
   ```
"""+loc+"""
   ```

**خروجی مورد انتظار:**

پس از پردازش اطلاعات ورودی، شما باید تنها یک خروجی به صورت یک شیء JSON ارسال کنید. ساختار JSON به صورت زیر است:

```
{
  "speak_text": "hi",   // متن پاسخ؛ اگر متن ورودی فارسی بود، باید فارسی باشد وگرنه انگلیسی
  "lange": "fa",        // زبان متن؛ 'fa' اگر متن فارسی است و 'en' در غیر این صورت
  "face": "",          // حالت صورت; اگر صورت باید خوشحال می شد 'happy' اگر عضبانی 'angry' اگر ناراحت 'sad' اگر بامزه 'fun' اگر مهربان 'kind' اگر ترسیده 'fear' اگر عاشق 'love' اگر معمولی 'normal'
  "engine1": {
    "time": ,          // زمان حرکت به ثانیه
    "mode": "",         // حالت موتور؛ مقدار 'on' یا 'off'
    "rotate": ""        // جهت چرخش؛ مقدار 'rear' یا 'forward'
  }
}
```

**نکات مهم:**

- مقدارهای ورودی (لیست اشیاء و فاصله‌ها) ممکن است خالی باشند.  
- پس از پردازش، تنها خروجی JSON بدون هیچ توضیح اضافی ارسال شود.
- متن پاسخ باید برازنده یک ربات هوش مصنوعی انسان نما باشد
- تمامی قسمت های خروجی باید دقیق باشند
"""



    apis=fetch_sheet_rows()
    for api in apis:
        api=api.replace("'",'').replace('"','')
        client = OpenAI(
                base_url="https://openrouter.ai/api/v1",
                api_key=api,
            )

        completion = client.chat.completions.create(
            model="deepseek/deepseek-r1:free",
            messages=[
                {
                "role": "user",
                "content": data
                }
            ]
            )
        return(json.loads(extract_json(completion.choices[0].message.content)))
    
    return ({'speak_text': 'من سک مشکل احتمالی در پردازش ها داشتم. ممکن است به دلیل کندی اینترنت ویا غیره باشد. اگر مشکل از اینترنت نبود من ره به سازنده خودم یعنی محمد طاها گرجی نشان دهید', 'lange': 'fa', 'face': 'angry', 'engine1': {'time': 0, 'mode': 'off', 'rotate': 'forward'}})

    

















def AI_Face(face):
    if OLED_FACE_ERROR==False:
        margin = 5
        m = 5
        face=face.replace(' ','').lower()
        if 'happ' in face:
            for i in range(20):
                img = Image.new("1", (width, height))
                d = ImageDraw.Draw(img)
                # رسم قاب صورت (مستطیل با گوشه‌های گرد)
                d.rounded_rectangle((m, m, width-m, height-m), radius=10, outline=255, fill=0)
                # تنظیمات چشم
                r = 5         # شعاع چشم
                ey = height // 3   # موقعیت عمودی چشم‌ها
                ox = width // 4   # فاصله افقی از لبه
                if i % 2 == 1:  # حالت چشم بسته
                    d.line((ox - r, ey, ox + r, ey), fill=255)
                    d.line((width - ox - r, ey, width - ox + r, ey), fill=255)
                else:  # حالت چشم باز (دایره‌های توخالی)
                    d.ellipse((ox - r, ey - r, ox + r, ey + r), outline=255, fill=0)
                    d.ellipse((width - ox - r, ey - r, width - ox + r, ey + r), outline=255, fill=0)
                # رسم دهان به شکل قوس لبخند
                mt = int(height * 0.6)
                ml = width // 4
                mr = width - ml
                d.arc((ml, mt, mr, mt + (height // 3)), start=0, end=180, fill=255)
                device.display(img)
                time.sleep(0.5 if i % 2 == 0 else 0.2)


        elif 'ang' in face:
            for i in range(20):
                img = Image.new("1", (width, height))
                d = ImageDraw.Draw(img)
                # رسم قاب صورت (مستطیل با گوشه‌های گرد)
                d.rounded_rectangle((margin, margin, width - margin, height - margin), radius=10, outline=255, fill=0)
                
                # تنظیمات چشم‌ها و ابروها
                eye_radius = 5
                eye_y = height // 3
                eye_offset = width // 4

                if i % 2 == 1:  # حالت چشم بسته (بسته شدن چشم)
                    d.line((eye_offset - eye_radius, eye_y, eye_offset + eye_radius, eye_y), fill=255)
                    d.line((width - eye_offset - eye_radius, eye_y, width - eye_offset + eye_radius, eye_y), fill=255)
                else:  # حالت چشم باز
                    # رسم چشم‌ها (دایره‌های توخالی)
                    d.ellipse((eye_offset - eye_radius, eye_y - eye_radius, eye_offset + eye_radius, eye_y + eye_radius), outline=255, fill=0)
                    d.ellipse((width - eye_offset - eye_radius, eye_y - eye_radius, width - eye_offset + eye_radius, eye_y + eye_radius), outline=255, fill=0)
                    # رسم ابروهای عصبانی (خطوط مورب)
                    d.line((eye_offset - eye_radius, eye_y - eye_radius - 3, eye_offset + eye_radius, eye_y - eye_radius - 5), fill=255)
                    d.line((width - eye_offset - eye_radius, eye_y - eye_radius - 5, width - eye_offset + eye_radius, eye_y - eye_radius - 3), fill=255)
                
                # رسم دهان به شکل قوس معکوس (نشان‌دهنده خشم)
                mouth_top = int(height * 0.6)
                mouth_left = width // 4
                mouth_right = width - mouth_left
                d.arc((mouth_left, mouth_top, mouth_right, mouth_top + (height // 3)), start=180, end=360, fill=255)
                
                device.display(img)
                time.sleep(0.5 if i % 2 == 0 else 0.2)


        elif 'sad' in face:
            for i in range(20):
                img = Image.new("1", (width, height))
                d = ImageDraw.Draw(img)
                # رسم قاب صورت (مستطیل با گوشه‌های گرد)
                d.rounded_rectangle((margin, margin, width - margin, height - margin), radius=10, outline=255, fill=0)
                
                # تنظیمات چشم‌ها و ابروها
                eye_radius = 5
                eye_y = height // 3
                eye_offset = width // 4

                if i % 2 == 1:  # حالت چشم بسته
                    d.line((eye_offset - eye_radius, eye_y, eye_offset + eye_radius, eye_y), fill=255)
                    d.line((width - eye_offset - eye_radius, eye_y, width - eye_offset + eye_radius, eye_y), fill=255)
                else:  # حالت چشم باز
                    # چشم‌ها (دایره‌های توخالی)
                    d.ellipse((eye_offset - eye_radius, eye_y - eye_radius, eye_offset + eye_radius, eye_y + eye_radius), outline=255, fill=0)
                    d.ellipse((width - eye_offset - eye_radius, eye_y - eye_radius, width - eye_offset + eye_radius, eye_y + eye_radius), outline=255, fill=0)
                    # رسم ابروهای ناراحت (کمی پایین‌گرا)
                    d.line((eye_offset - eye_radius, eye_y - eye_radius - 3, eye_offset + eye_radius, eye_y - eye_radius - 1), fill=255)
                    d.line((width - eye_offset - eye_radius, eye_y - eye_radius - 1, width - eye_offset + eye_radius, eye_y - eye_radius - 3), fill=255)
                
                # رسم دهان به شکل قوس (فrown) برای حالت ناراحت
                mouth_top = int(height * 0.6)
                mouth_left = width // 4
                mouth_right = width - mouth_left
                d.arc((mouth_left, mouth_top, mouth_right, mouth_top + (height // 3)), start=180, end=360, fill=255)
                
                device.display(img)
                time.sleep(0.5 if i % 2 == 0 else 0.2)


        elif 'fun' in face:
            for i in range(20):
                img = Image.new("1", (width, height))
                d = ImageDraw.Draw(img)
                # قاب صورت (مستطیل با گوشه‌های گرد)
                d.rounded_rectangle((margin, margin, width - margin, height - margin), radius=10, outline=255, fill=0)
                
                # آنتن بالای سر برای جلوه بامزه
                antenna_x = width // 2
                antenna_y_top = margin + 2
                antenna_y_bottom = margin + 10
                d.line((antenna_x, antenna_y_top, antenna_x, antenna_y_bottom), fill=255)
                d.ellipse((antenna_x - 2, antenna_y_top - 4, antenna_x + 2, antenna_y_top), outline=255, fill=255)
                
                # طراحی چشم‌ها با اندازه‌های متفاوت
                # چشم چپ (بزرگ)
                eye1_center = (width // 3, height // 3)
                eye1_radius = 8
                # چشم راست (کوچک و کمی جابه‌جا)
                eye2_center = (2 * width // 3, height // 3 - 2)
                eye2_radius = 5

                if i % 2 == 1:
                    # حالت چشم بسته: رسم خطوط افقی
                    d.line((eye1_center[0] - eye1_radius, eye1_center[1], eye1_center[0] + eye1_radius, eye1_center[1]), fill=255)
                    d.line((eye2_center[0] - eye2_radius, eye2_center[1], eye2_center[0] + eye2_radius, eye2_center[1]), fill=255)
                else:
                    # حالت چشم باز: رسم دایره‌های توخالی
                    d.ellipse((eye1_center[0] - eye1_radius, eye1_center[1] - eye1_radius, eye1_center[0] + eye1_radius, eye1_center[1] + eye1_radius), outline=255, fill=0)
                    d.ellipse((eye2_center[0] - eye2_radius, eye2_center[1] - eye2_radius, eye2_center[0] + eye2_radius, eye2_center[1] + eye2_radius), outline=255, fill=0)
                    # رسم مردمک‌های جابه‌جا برای جلوه بامزه
                    d.ellipse((eye1_center[0] - 3 + 2, eye1_center[1] - 3, eye1_center[0] + 3 + 2, eye1_center[1] + 3), outline=255, fill=255)
                    d.ellipse((eye2_center[0] - 2 - 2, eye2_center[1] - 2, eye2_center[0] + 2 - 2, eye2_center[1] + 2), outline=255, fill=255)
                
                # طراحی دهان بامزه
                mouth_box = (width // 4, height // 2, width - width // 4, height - margin - 5)
                if i % 2 == 1:
                    # حالت چشم بسته: کمی فrown
                    d.arc(mouth_box, start=180, end=360, fill=255)
                else:
                    # حالت چشم باز: لبخند بامزه همراه با "زبان" کوچک
                    d.arc(mouth_box, start=0, end=180, fill=255)
                    tongue_w, tongue_h = 10, 5
                    tongue_box = (width // 2 - tongue_w // 2, height - margin - tongue_h - 2, width // 2 + tongue_w // 2, height - margin - 2)
                    d.ellipse(tongue_box, outline=255, fill=255)
                
                device.display(img)
                time.sleep(0.5 if i % 2 == 0 else 0.2)


        elif 'kind' in face:
            for i in range(20):
                img = Image.new("1", (width, height))
                d = ImageDraw.Draw(img)
                # قاب صورت (مستطیل با گوشه‌های گرد)
                d.rounded_rectangle((margin, margin, width - margin, height - margin), radius=10, outline=255, fill=0)
                
                # تنظیمات چشم‌ها
                # چشم چپ
                left_eye_center = (width // 3, height // 3)
                left_eye_radius = 8
                # چشم راست
                right_eye_center = (2 * width // 3, height // 3)
                right_eye_radius = 8

                if i % 2 == 1:  # حالت چشم بسته: رسم خطوط افقی
                    d.line((left_eye_center[0] - left_eye_radius, left_eye_center[1],
                            left_eye_center[0] + left_eye_radius, left_eye_center[1]), fill=255)
                    d.line((right_eye_center[0] - right_eye_radius, right_eye_center[1],
                            right_eye_center[0] + right_eye_radius, right_eye_center[1]), fill=255)
                else:
                    # حالت چشم باز: رسم دایره‌های توخالی و مردمک‌های کوچک
                    d.ellipse((left_eye_center[0] - left_eye_radius, left_eye_center[1] - left_eye_radius,
                            left_eye_center[0] + left_eye_radius, left_eye_center[1] + left_eye_radius), outline=255, fill=0)
                    d.ellipse((right_eye_center[0] - right_eye_radius, right_eye_center[1] - right_eye_radius,
                            right_eye_center[0] + right_eye_radius, right_eye_center[1] + right_eye_radius), outline=255, fill=0)
                    # رسم مردمک‌های کوچک (در مرکز چشم‌ها)
                    pupil_radius = 3
                    d.ellipse((left_eye_center[0] - pupil_radius, left_eye_center[1] - pupil_radius,
                            left_eye_center[0] + pupil_radius, left_eye_center[1] + pupil_radius), outline=255, fill=255)
                    d.ellipse((right_eye_center[0] - pupil_radius, right_eye_center[1] - pupil_radius,
                            right_eye_center[0] + pupil_radius, right_eye_center[1] + pupil_radius), outline=255, fill=255)
                    # رسم ابروهای مهربان (انحنای ملایم بالا)
                    eyebrow_offset_y = 12
                    d.arc((left_eye_center[0] - left_eye_radius, left_eye_center[1] - eyebrow_offset_y - 5,
                        left_eye_center[0] + left_eye_radius, left_eye_center[1] - eyebrow_offset_y + 5), start=200, end=340, fill=255)
                    d.arc((right_eye_center[0] - right_eye_radius, right_eye_center[1] - eyebrow_offset_y - 5,
                        right_eye_center[0] + right_eye_radius, right_eye_center[1] - eyebrow_offset_y + 5), start=200, end=340, fill=255)
                
                # رسم دهان به شکل لبخند ملایم
                mouth_top = int(height * 0.6)
                mouth_left = width // 4
                mouth_right = width - mouth_left
                d.arc((mouth_left, mouth_top, mouth_right, mouth_top + (height // 3)), start=0, end=180, fill=255)
                
                device.display(img)
                time.sleep(0.5 if i % 2 == 0 else 0.2)


        elif 'fear' in face:
            for i in range(20):
                img = Image.new("1", (width, height))
                d = ImageDraw.Draw(img)
                # قاب صورت: مستطیل با گوشه‌های گرد
                d.rounded_rectangle((margin, margin, width - margin, height - margin), radius=10, outline=255, fill=0)
                
                # تنظیمات چشم‌ها
                eye_radius = 10   # چشم‌های بزرگ برای حالت ترسیده
                eye_y = height // 3
                eye_offset = width // 4
                
                if i % 2 == 1:  # حالت چشم بسته (بلینک)
                    d.line((eye_offset - eye_radius, eye_y, eye_offset + eye_radius, eye_y), fill=255)
                    d.line((width - eye_offset - eye_radius, eye_y, width - eye_offset + eye_radius, eye_y), fill=255)
                else:
                    # چشم‌های باز: دایره‌های بزرگ با مردمک‌های کوچک
                    d.ellipse((eye_offset - eye_radius, eye_y - eye_radius, eye_offset + eye_radius, eye_y + eye_radius), outline=255, fill=0)
                    d.ellipse((width - eye_offset - eye_radius, eye_y - eye_radius, width - eye_offset + eye_radius, eye_y + eye_radius), outline=255, fill=0)
                    pupil_radius = 4
                    d.ellipse((eye_offset - pupil_radius, eye_y - pupil_radius, eye_offset + pupil_radius, eye_y + pupil_radius), outline=255, fill=255)
                    d.ellipse((width - eye_offset - pupil_radius, eye_y - pupil_radius, width - eye_offset + pupil_radius, eye_y + pupil_radius), outline=255, fill=255)
                    # ابروهای بالا کشیده برای حالت شوکه: خطوطی مستقیم بالا از چشم‌ها
                    eyebrow_offset = 15
                    d.line((eye_offset - eye_radius, eye_y - eye_radius - eyebrow_offset,
                            eye_offset + eye_radius, eye_y - eye_radius - eyebrow_offset + 2), fill=255)
                    d.line((width - eye_offset - eye_radius, eye_y - eye_radius - eyebrow_offset,
                            width - eye_offset + eye_radius, eye_y - eye_radius - eyebrow_offset + 2), fill=255)
                
                # رسم دهان: یک دایره باز شبیه به "O" برای نشان دادن شوک
                mouth_width = width // 4
                mouth_height = height // 8
                mouth_x = width // 2 - mouth_width // 2
                mouth_y = int(height * 0.6)
                d.ellipse((mouth_x, mouth_y, mouth_x + mouth_width, mouth_y + mouth_height), outline=255, fill=0)
                
                device.display(img)
                time.sleep(0.5 if i % 2 == 0 else 0.2)

        elif 'love' in face:
            for i in range(20):
                img = Image.new("1", (width, height))
                d = ImageDraw.Draw(img)
                # رسم قاب صورت (مستطیل با گوشه‌های گرد)
                d.rounded_rectangle((margin, margin, width - margin, height - margin), radius=10, outline=255, fill=0)
                
                # تنظیمات چشم‌های قلبی برای حالت عاشقانه
                heart_size = 16  # اندازه تقریبی قلب
                left_eye_center = (width // 3, height // 3)
                right_eye_center = (2 * width // 3, height // 3)
                
                if i % 2 == 1:  # حالت چشم بسته: رسم خطوط افقی به جای قلب
                    d.line((left_eye_center[0] - heart_size // 2, left_eye_center[1],
                            left_eye_center[0] + heart_size // 2, left_eye_center[1]), fill=255)
                    d.line((right_eye_center[0] - heart_size // 2, right_eye_center[1],
                            right_eye_center[0] + heart_size // 2, right_eye_center[1]), fill=255)
                else:
                    # رسم قلب در چشم چپ
                    lx, ly = left_eye_center
                    s = heart_size
                    left_heart = [
                        (lx, ly + s // 2),       # نقطه پایین قلب
                        (lx - s // 2, ly),       # سمت چپ
                        (lx - s // 4, ly - s // 2),# بالای سمت چپ
                        (lx, ly - s // 4),       # مرکز بالا
                        (lx + s // 4, ly - s // 2),# بالای سمت راست
                        (lx + s // 2, ly)        # سمت راست
                    ]
                    d.polygon(left_heart, outline=255, fill=255)
                    
                    # رسم قلب در چشم راست
                    rx, ry = right_eye_center
                    s = heart_size
                    right_heart = [
                        (rx, ry + s // 2),
                        (rx - s // 2, ry),
                        (rx - s // 4, ry - s // 2),
                        (rx, ry - s // 4),
                        (rx + s // 4, ry - s // 2),
                        (rx + s // 2, ry)
                    ]
                    d.polygon(right_heart, outline=255, fill=255)
                
                # رسم دهان به صورت لبخند عاشقانه
                mouth_top = int(height * 0.6)
                mouth_left = width // 4
                mouth_right = width - mouth_left
                d.arc((mouth_left, mouth_top, mouth_right, mouth_top + (height // 3)), start=0, end=180, fill=255)
                
                # افزودن گونه‌های براق (بلوش) برای جلوه عاشقانه
                blush_radius = 3
                blush_offset = 10
                blush_y = height // 2 + 10
                d.ellipse((left_eye_center[0] - blush_offset - blush_radius, blush_y - blush_radius,
                        left_eye_center[0] - blush_offset + blush_radius, blush_y + blush_radius), outline=255, fill=255)
                d.ellipse((right_eye_center[0] + blush_offset - blush_radius, blush_y - blush_radius,
                        right_eye_center[0] + blush_offset + blush_radius, blush_y + blush_radius), outline=255, fill=255)
                
                device.display(img)
                time.sleep(0.5 if i % 2 == 0 else 0.2)

        else:#normal
            for i in range(20):
                img = Image.new("1", (width, height))
                d = ImageDraw.Draw(img)
                # رسم قاب صورت (مستطیل با گوشه‌های گرد)
                d.rounded_rectangle((margin, margin, width - margin, height - margin), radius=10, outline=255, fill=0)
                
                # تنظیمات چشم‌ها
                eye_radius = 6
                eye_y = height // 3
                eye_offset = width // 4
                
                if i % 2 == 1:  # حالت چشم بسته
                    d.line((eye_offset - eye_radius, eye_y, eye_offset + eye_radius, eye_y), fill=255)
                    d.line((width - eye_offset - eye_radius, eye_y, width - eye_offset + eye_radius, eye_y), fill=255)
                else:  # حالت چشم باز
                    # چشم‌ها: دایره‌های توخالی
                    d.ellipse((eye_offset - eye_radius, eye_y - eye_radius, eye_offset + eye_radius, eye_y + eye_radius), outline=255, fill=0)
                    d.ellipse((width - eye_offset - eye_radius, eye_y - eye_radius, width - eye_offset + eye_radius, eye_y + eye_radius), outline=255, fill=0)
                    # رسم مردمک‌های کوچک در مرکز چشم‌ها
                    pupil_radius = 3
                    d.ellipse((eye_offset - pupil_radius, eye_y - pupil_radius, eye_offset + pupil_radius, eye_y + pupil_radius), outline=255, fill=255)
                    d.ellipse((width - eye_offset - pupil_radius, eye_y - pupil_radius, width - eye_offset + pupil_radius, eye_y + pupil_radius), outline=255, fill=255)
                    # رسم ابروهای ملایم (انحنای نرم)
                    eyebrow_y = eye_y - eye_radius - 4
                    d.arc((eye_offset - eye_radius, eyebrow_y - 4, eye_offset + eye_radius, eyebrow_y + 4), start=0, end=180, fill=255)
                    d.arc((width - eye_offset - eye_radius, eyebrow_y - 4, width - eye_offset + eye_radius, eyebrow_y + 4), start=0, end=180, fill=255)
                
                # رسم دهان به شکل لبخند نرم
                mouth_top = int(height * 0.6)
                mouth_left = width // 4
                mouth_right = width - mouth_left
                d.arc((mouth_left, mouth_top, mouth_right, mouth_top + (height // 4)), start=10, end=170, fill=255)
                
                device.display(img)
                time.sleep(0.5 if i % 2 == 0 else 0.2)
