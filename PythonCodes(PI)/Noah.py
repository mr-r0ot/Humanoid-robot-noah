# ======== Noah.py ========
# Import Class
from Noah_Class import *
Physical_bug = False

from os import system
TalkOffline("Connect to the noah wifi network")
system("sudo nmcli device disconnect")
system('while true; do sudo nmcli device wifi connect "noah" ifname wlan0 && break; sleep 2; done')


# ==================Connect to Internet==================

TalkOffline(f"Hi, My name is Nova! , {subAI.textGenetrator('welcom')}")
# Set dlt Face
if OLED_FACE_ERROR == False:
    AI_Face('normal')

def Cnet():
    TalkOffline("I check the status of the wifi connections!")
    system("sudo nmcli device disconnect")
    system('while true; do sudo nmcli device wifi connect "noah" ifname wlan0 && break; sleep 2; done')

    

# ==================Select Lang==================
Talk('Do you want me to speak English or Persian?')
lang = 'en'
userla = (Listen()).lower()
if 'en' in userla:
    lang = 'en'
    Talk('Sure, my friend. I will speak English.')
else:
    lang = 'fa'
    Talk('باشه حتما دوست خوبم. از این به بعد من فارسی صحبت می کنم.', farsi=True)

# ==================Physical Test==================
if lang == 'en':
    Talk("Let's go check the hardware connections.")
else:
    Talk("یکم صبر کن تا اتصالات سخت افزاری خودم رو چک بکنم تا خرابی نداشته باشه", farsi=True)
phy = Physical()
if not phy.ser:
    Physical_bug = True

    if lang == 'en':
        Talk(f"holy ship bro!, {subAI.textGenetrator('problem')}! , {subAI.textGenetrator('problem')}!, ! I Dont Have, Leg!, My legs, don't work!, I can not solve them!, Even my Fuck sub-board is not recognized!")
    else:
        Talk('یا ابوالفضل. من نمی تونم به قطعه آردوینو متصل بشم. پاهام رو حس نمی کنم', farsi=True)

    if lang == 'en':
        Talk("Please check my connections. Of course, if you know!")
    else:
        Talk("لطفا اتصالات سخت افزاری من رو برسی کن. البته نه! وایسا ببینم اصلا بلدی؟", farsi=True)

    if lang == 'en':
        Talk("If you don't know, take me to an electronics engineer. ,  Of course, no one will be like my own creator, Mohammad Taha Gorji, ha, ha, ha, ah")
    else:
        Talk('البته که هیچ کس مثل سازنده خود آدم نمیشه. محمد طاها گرجی. ها. ها. ها. ها', farsi=True)

    if lang == 'en':
        Talk("I predict that the wire connection to the Arduino has been disconnected, and if we are unlucky, the Arduino has broken down.")

    if lang == 'en':
        Talk("Fuck you! ,  What did you do to me ,when I was sleeping?")
    else:
        Talk('لعنت بهت چیکارم کردی وقتی خواب بودم؟  باهات صحبت می کنم ولی نمی تونم راه برم', farsi=True)

    if lang == 'en':
        Talk("I'll talk to you, but I can't walk.")
else:
    if lang == 'en':
        Talk(subAI.textGenetrator('connectok'))
    else:
        Talk('خوشبختانه خرابی وجود نداشت', farsi=True)

# Get Start
if lang == 'en':
    Talk("Ok. Lets go. Can i help you?")
else:
    Talk("خب. حالا چجوری می تونم بهت کمک کنم؟", farsi=True)
print('start while')
# a loop for work 
while True:
    # Start Listen to user speak
    heard = Listen()
    if heard:  # IF heard
        if NetWork.Check_Net() == True:
            if Physical_bug == False:
                North, West, South, East = phy.Distance()  # Get Map
                response = AI(heard, loc=f"""
North : {North}
West  : {West}
South : {South}
East  : {East}""")
            else:
                response = AI(heard, loc='')  # Send to LLM

            # ==============================USE FROM INFO==================================
            # Set Face
            if OLED_FACE_ERROR == False:
                AI_Face(response['face'])
            print(response)

            # Speak
            if response['lange'] == 'en':
                Talk(response['speak_text'])
            else:
                Talk(response['speak_text'], farsi=True)

            # Run
            config = {}
            if Physical_bug == False:
                config = {
                    'engine1': {
                        'time': response['engine1']['time'],
                        'mode': response['engine1']['mode'],
                        'rotate': response['engine1']['rotate']
                    },
                    'engine2': {
                        'time': response['engine2']['time'],
                        'mode': response['engine2']['mode'],
                        'rotate': response['engine2']['rotate']
                    }
                }
                phy.engine(config)
        else:
            Cnet()

phy.close()
