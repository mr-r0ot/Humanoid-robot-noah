print("Start...")
# ======== Noah.py ========
# Import Class
from Noah_Class import *
Physical_bug = False

from os import system
print("Connect to the noah wifi network")
system("sudo nmcli device disconnect")
system('while true; do sudo nmcli device wifi connect "noah" ifname wlan0 && break; sleep 2; done')



# ==================Connect to Internet==================

Talk(f"Hi, My name is Nova! , {subAI.textGenetrator('welcom')}")
# Set dlt Face
if OLED_FACE_ERROR==False:AI_Face('normal')
def Cnet():
    Talk("I check the status of the wifi connections!")
    system("sudo nmcli device disconnect")
    system('while true; do sudo nmcli device wifi connect "noah" ifname wlan0 && break; sleep 2; done')





# ==================Select Lang==================

Talk('Do you want me to speak English or Persian?')
lang='en'
userla=(Listen()).lower()
if 'en' in userla:
    lang='en'
    Talk('Sure, my friend. I will speak English.')
else:
    lang='fa'
    Talk('باشه حتما دوست خوبم. از این به بعد من فارسی صحبت می کنم.',farsi=True)








# ==================Physical Test==================
if lang=='en':Talk("Let's go check the hardware connections.")
else:Talk("یکم صبر کن تا اتصالات سخت افزاری خودم رو چک بکنم تا خرابی نداشته باشه",farsi=True)
phy = Physical()
if not phy.ser:
    Physical_bug = True

    if lang=='en':Talk(f"holy ship bro!, {subAI.textGenetrator('problem')}! , {subAI.textGenetrator('problem')}!, ! I Dont Have, Leg!, My legs, don't work!, I can not solve them!, Even my Fuck sub-board is not recognized!")
    else:Talk('یا ابوالفضل. من نمی تونم به قطعه آردوینو متصل بشم. پاهام رو حس نمی کنم',farsi=True)

    if lang=='en':Talk("Please check my connections. Of course, if you know!")
    else:Talk("لطفا اتصالات سخت افزاری من رو برسی کن. البته نه! وایسا ببینم اصلا بلدی؟",farsi=True)

    if lang=='en':Talk("If you don't know, take me to an electronics engineer. ,  Of course, no one will be like my own creator, Mohammad Taha Gorji, ha, ha, ha, ah")
    else:Talk('البته که هیچ کس مثل سازنده خود آدم نمیشه. محمد طاها گرجی. ها. ها. ها. ها',farsi=True)

    if lang=='en':Talk("I predict that the wire connection to the Arduino has been disconnected, and if we are unlucky, the Arduino has broken down.")

    if lang=='en':Talk("Fuck you! ,  What did you do to me ,when I was sleeping?")
    else:Talk('لعنت بهت چیکارم کردی وقتی خواب بودم؟  باهات صحبت می کنم ولی نمی تونم راه برم',farsi=True)

    if lang=='en':Talk("I'll talk to you, but I can't walk.")
else:
    if lang=='en':Talk(subAI.textGenetrator('connectok'))
    else:Talk('خوشبختانه خرابی وجود نداشت',farsi=True)


    


def con_run(time,rotate,mode='on'):
    if rotate=='rear':rotate='left'
    elif rotate=='forward':rotate='right'
    else:mode='off'

    if mode=='on':
        config = {
        'engine1': {
            'time': int(time),
            'mode': 'on',
            'rotate': str(rotate)
        },'engine2': {'time': 0,'mode': 'off','rotate': 'right'}}
        phy.engine(config)



# Get Start
if lang=='en':Talk("Ok. Lets go. Can i help you?")
else:Talk("خب. حالا چجوری می تونم بهت کمک کنم؟",farsi=True)

# a loop for work 
print("[+] Start while....")
while True:
    # ۱. منتظر بمان تا کاربر حرف بزند
    heard = ""
    while not heard:
        heard = Listen(
            timeout=3,
            phrase_time_limit=10,
            language='fa-IR'
        )
    print("Heard.")
    # ۳. اطمینان از اتصال اینترنت
    try:
        if not NetWork.Check_Net()==True:
            Cnet()
            continue
    except Exception:
        pass
    print("Network is ok")

    # ۴. خواندن فاصله‌ها در صورت اتصال سخت‌افزار
    if not Physical_bug:
        North, West, South, East = phy.Distance()
        loc_str = f"North: {North}\nWest: {West}\nSouth: {South}\nEast: {East}"
    else:
        loc_str = ''

    # ۵. فراخوانی AI درون بلوک try/except
    try:
        response = AI(heard, loc=loc_str)
    except Exception:
        response = {
            'speak_text': 'متأسفم، در پردازش درخواست شما خطایی رخ داد.',
            'lange': 'fa',
            'face': 'sad',
            'engine1': {'time': 0, 'mode': 'off', 'rotate': 'forward'}
        }

    # ۶. به‌روزرسانی چهره OLED بر اساس خروجی AI
    if OLED_FACE_ERROR == False:AI_Face(response['face'])

    # ۷. صحبت کردن ربات
    if response['lange'] == 'en':
        Talk(response['speak_text'])
    else:
        Talk(response['speak_text'],farsi=True)

    # ۸. حرکت موتورها بر اساس خروجی AI
    if not Physical_bug:
        cfg = response.get('engine1', {})
        con_run(
            time=cfg.get('time', 0),
            mode=cfg.get('mode', 'off'),
            rotate=cfg.get('rotate', 'forward')
        )

    # ۹. کمی مکث برای پایداری حلقه
    time.sleep(0.1)
