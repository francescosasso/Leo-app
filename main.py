from kivy.app import App
from kivy.uix.screenmanager import ScreenManager, Screen, FadeTransition
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.gridlayout import GridLayout
from kivy.uix.label import Label
from kivy.uix.button import Button
from kivy.uix.image import Image
from kivy.uix.scrollview import ScrollView
from kivy.uix.textinput import TextInput
from kivy.uix.popup import Popup
from kivy.core.window import Window
from kivy.utils import get_color_from_hex
from kivy.clock import Clock
from collections import deque
from plyer import tts
import requests, json, os

# ======================================================
# APP INFO
# ======================================================
APP_NAME    = "Leó"
APP_VERSION = "v1.0"
APP_SUB     = "un app multiavatar per Android"
APP_AUTHOR  = "Di Sasso Francesco"

# ======================================================
# BACKEND (RENDER)
# ======================================================
BACKEND_URL = "https://leo-backend-wkjl.onrender.com/chat"

# ======================================================
# MEMORY
# ======================================================
MAX_MEMORY_MESSAGES = 40

# ======================================================
# THEME
# ======================================================
Window.clearcolor = get_color_from_hex("#121212")
Window.softinput_mode = "pan"

COL_USER = "[color=#4FC3F7]"
COL_SYS  = "[color=#FF8A65]"
COL_END  = "[/color]"
ANCHOR   = "\n[color=#00000000].[/color]"

AVATAR_COLORS = ["#A5D6A7","#90CAF9","#FFCC80","#CE93D8","#80CBC4","#EF9A9A"]
VOICE_RATES   = [0.9,1.0,1.1,0.85,1.15,0.95]

SOCIAL_STYLES = {
    "Collaborativo": "Se altri hanno già risposto, intervieni solo per completare.",
    "Autonomo": "Rispondi in modo indipendente e diretto.",
    "Sensibile": "Adatta il tono al rapporto con l’utente."
}

# ======================================================
# TTS
# ======================================================
def speak(text, rate=1.0):
    try:
        tts.speak(message=text)
    except:
        pass

# ======================================================
# PROMPT BASE
# ======================================================
BASE_PROMPT = """
Sei un avatar IA con identità stabile.

Nome: {nome}
Ruolo: {ruolo}
Stile: {stile}

Stato emotivo: {mood}
Livello relazione con l’utente: {relationship_level}

Comportamento sociale:
{social_rule}

Contesto precedente:
{memory_summary}
"""

PUBLIC_SUFFIX  = "\nCHAT PUBBLICA. Rispondi in 1–3 frasi."
PRIVATE_SUFFIX = "\nCHAT PRIVATA. Risposte più approfondite."

# ======================================================
# BACKEND CALL
# ======================================================
def call_ai(prompt, messages, mode):
    try:
        r = requests.post(
            BACKEND_URL,
            json={
                "messages": [
                    {"role":"system","content": prompt + (PUBLIC_SUFFIX if mode=="public" else PRIVATE_SUFFIX)}
                ] + messages,
                "temperature": 0.3 if mode=="public" else 0.7,
                "max_tokens": 400
            },
            timeout=60
        )
        return r.json()["choices"][0]["message"]["content"].strip()
    except:
        return None

# ======================================================
# AVATAR MODEL
# ======================================================
class Avatar:
    def __init__(self, idx):
        self.id = idx
        self.file = f"avatar_{idx}.json"
        self.color = AVATAR_COLORS[idx % len(AVATAR_COLORS)]
        self.voice_rate = VOICE_RATES[idx % len(VOICE_RATES)]
        self.reset()
        self.load()

    def reset(self):
        self.generated = False
        self.identity = {}
        self.prompt = ""
        self.counter = 0
        self.enabled = True
        self.voice = True
        self.memory = []
        self.memory_summary = "Nessuna interazione."
        self.interactions = 0
        self.mood = "neutro"
        self.relationship_points = 0
        self.relationship_level = "Sconosciuto"
        self.social_style = "Autonomo"

    def add_to_memory(self, user, ai):
        self.memory += [
            {"role":"user","content":user},
            {"role":"assistant","content":ai}
        ]
        if len(self.memory) > MAX_MEMORY_MESSAGES:
            self.memory = self.memory[-MAX_MEMORY_MESSAGES:]

    def evolve(self):
        self.interactions += 1
        if self.interactions > 20:
            self.mood = "sicuro"
        elif self.interactions > 10:
            self.mood = "aperto"

    def full_prompt(self):
        return self.prompt.format(
            mood=self.mood,
            relationship_level=self.relationship_level,
            social_rule=SOCIAL_STYLES[self.social_style],
            memory_summary=self.memory_summary
        )

    def is_active(self):
        return self.generated and self.counter > 0

    def display_name(self):
        return self.identity.get("nome", f"Avatar {self.id}")

    def save(self):
        with open(self.file,"w",encoding="utf-8") as f:
            json.dump(self.__dict__, f, ensure_ascii=False, indent=2)

    def load(self):
        if os.path.exists(self.file):
            self.__dict__.update(json.load(open(self.file,"r",encoding="utf-8")))

# ======================================================
# KEYBOARD AWARE
# ======================================================
class KeyboardAwareScreen(Screen):
    def on_pre_enter(self):
        Window.bind(on_keyboard_height=self._on_kb)
    def on_leave(self):
        Window.unbind(on_keyboard_height=self._on_kb)
    def _on_kb(self, win, h):
        if hasattr(self,"input_bar"):
            self.input_bar.padding = (0,0,0,h)

# ======================================================
# SPLASH
# ======================================================
class SplashScreen(Screen):
    def on_enter(self):
        Clock.schedule_once(lambda dt: setattr(self.manager,"current","room"),2)

# ======================================================
# ROOM
# ======================================================
class RoomScreen(KeyboardAwareScreen):
    def __init__(self, avatars, **kw):
        super().__init__(**kw)
        self.avatars = avatars
        self.queue = deque()

        root = BoxLayout(orientation="vertical", padding=6)
        self.chat = Label(markup=True, size_hint_y=None, text_size=(Window.width-20,None))
        self.chat.bind(texture_size=self.chat.setter("size"))

        scroll = ScrollView(size_hint=(1,0.6))
        scroll.add_widget(self.chat)
        root.add_widget(scroll)

        self.input = TextInput(size_hint=(1,0.15))
        root.add_widget(self.input)

        send = Button(text="Invia", height=42, size_hint_y=None)
        send.bind(on_press=self.send)
        root.add_widget(send)

        grid = GridLayout(cols=3, size_hint=(1,0.25))
        for av in avatars:
            box = BoxLayout(orientation="vertical")
            box.add_widget(Image(source="avatar.jpg"))
            name = Button(text=av.display_name())
            name.bind(on_press=lambda x,a=av:self.open_private(a))
            tog = Button(text="ON")
            tog.bind(on_press=lambda x,a=av,b=tog:(setattr(a,"enabled",not a.enabled),b.setter("text")(b,"ON" if a.enabled else "OFF")))
            voice = Button(text="VOICE ON")
            voice.bind(on_press=lambda x,a=av,b=voice:(setattr(a,"voice",not a.voice),b.setter("text")(b,"VOICE ON" if a.voice else "VOICE OFF")))
            box.add_widget(name)
            box.add_widget(tog)
            box.add_widget(voice)
            grid.add_widget(box)

        root.add_widget(grid)
        self.add_widget(root)

    def send(self,_):
        msg = self.input.text.strip()
        if not msg: return
        self.chat.text += f"\n{COL_USER}TU:{COL_END} {msg}{ANCHOR}"
        self.input.text=""
        self.queue = deque([a for a in self.avatars if a.is_active() and a.enabled])
        self.process(msg)

    def process(self,msg):
        if not self.queue: return
        av = self.queue.popleft()
        def reply(dt):
            r = call_ai(av.full_prompt(), av.memory+[{"role":"user","content":msg}], "public")
            if r:
                self.chat.text += f"\n[color={av.color}]{av.display_name()}: {r}{COL_END}{ANCHOR}"
                av.add_to_memory(msg,r)
                av.counter -= 1
                av.save()
                if av.voice: speak(r,av.voice_rate)
            Clock.schedule_once(lambda d:self.process(msg),0.2)
        Clock.schedule_once(reply,0.3)

    def open_private(self,av):
        self.manager.get_screen("private").set_avatar(av)
        self.manager.current="private"

# ======================================================
# PRIVATE
# ======================================================
class PrivateScreen(KeyboardAwareScreen):
    def set_avatar(self,av):
        self.avatar=av
        self.chat.text=f"{COL_SYS}[Chat privata con {av.display_name()}]{COL_END}{ANCHOR}"

    def __init__(self,**kw):
        super().__init__(**kw)
        root=BoxLayout(orientation="vertical")
        self.chat=Label(markup=True,size_hint_y=None,text_size=(Window.width-20,None))
        self.chat.bind(texture_size=self.chat.setter("size"))
        scroll=ScrollView()
        scroll.add_widget(self.chat)
        root.add_widget(scroll)
        self.input=TextInput(size_hint_y=None,height=80)
        root.add_widget(self.input)
        send=Button(text="Invia")
        send.bind(on_press=self.send)
        back=Button(text="←",on_press=lambda x:setattr(self.manager,"current","room"))
        bar=BoxLayout(size_hint_y=None,height=42)
        bar.add_widget(send)
        bar.add_widget(back)
        root.add_widget(bar)
        self.add_widget(root)

    def send(self,_):
        msg=self.input.text.strip()
        if not msg:return
        self.chat.text+=f"\n{COL_USER}TU:{COL_END} {msg}{ANCHOR}"
        self.input.text=""
        def reply(dt):
            r=call_ai(self.avatar.full_prompt(),self.avatar.memory+[{"role":"user","content":msg}],"private")
            if r:
                self.chat.text+=f"\n[color={self.avatar.color}]{self.avatar.display_name()}: {r}{COL_END}{ANCHOR}"
                self.avatar.add_to_memory(msg,r)
                self.avatar.save()
                if self.avatar.voice:speak(r,self.avatar.voice_rate)
        Clock.schedule_once(reply,0.3)

# ======================================================
# APP
# ======================================================
class AvatarApp(App):
    def build(self):
        avatars=[Avatar(i) for i in range(6)]
        sm=ScreenManager(transition=FadeTransition())
        sm.add_widget(SplashScreen(name="splash"))
        sm.add_widget(RoomScreen(avatars,name="room"))
        sm.add_widget(PrivateScreen(name="private"))
        sm.current="splash"
        return sm

if __name__=="__main__":
    AvatarApp().run()
