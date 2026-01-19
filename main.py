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
from threading import Thread
import requests, json, os, time

# ======================================================
# APP INFO
# ======================================================
APP_NAME    = "Leó"
APP_VERSION = "v1.0 UX"
APP_SUB     = "un app multiavatar per Android"
APP_AUTHOR  = "Di Sasso Francesco"

# ======================================================
# BACKEND
# ======================================================
BACKEND_URL = "https://leo-backend-wkjl.onrender.com/chat"

# ======================================================
# MEMORY SETTINGS
# ======================================================
MAX_MEMORY_MESSAGES = 40
MAX_CHAT_CHARS = 12000

# ======================================================
# THEME
# ======================================================
Window.clearcolor = get_color_from_hex("#121212")
Window.softinput_mode = "pan"

COL_USER = "[color=#4FC3F7]"
COL_SYS  = "[color=#FF8A65]"
COL_WARN = "[color=#FBC02D]"
COL_END  = "[/color]"
ANCHOR   = "\n[color=#00000000].[/color]"

AVATAR_COLORS = ["#A5D6A7","#90CAF9","#FFCC80","#CE93D8","#80CBC4","#EF9A9A"]
VOICE_RATES   = [0.9,1.0,1.1,0.85,1.15,0.95]

SOCIAL_STYLES = {
    "Collaborativo": "Se altri hanno già risposto, aggiungi solo se puoi completare o chiarire.",
    "Autonomo": "Rispondi in modo indipendente, diretto e professionale.",
    "Sensibile": "Adatta il tono in base al livello di relazione con l’utente."
}

# ======================================================
# BASE PROMPT
# ======================================================
BASE_PROMPT = """
Sei {nome}, un avatar con il ruolo di {ruolo}.
Stile comunicativo: {stile}.

Stato emotivo attuale: {mood}
Livello di relazione: {relationship_level}

Regola sociale:
{social_rule}

Memoria sintetica:
{memory_summary}

Rispondi in modo coerente con identità e contesto.
"""

# ======================================================
# TTS
# ======================================================
def speak(text, rate=1.0):
    try:
        tts.speak(message=text)
    except:
        pass

# ======================================================
# AI CALL (SYNC)
# ======================================================
def call_ai(prompt, messages, mode, retries=3):
    payload = {
        "messages": [{
            "role": "system",
            "content": prompt + (
                "\nCHAT PUBBLICA. Rispondi in modo conciso (1–3 frasi)."
                if mode == "public"
                else "\nCHAT PRIVATA. Risposte approfondite."
            )
        }] + messages,
        "temperature": 0.3 if mode == "public" else 0.7,
        "max_tokens": 120 if mode == "public" else 400
    }

    for _ in range(retries):
        try:
            r = requests.post(BACKEND_URL, json=payload, timeout=45)
            r.raise_for_status()
            data = r.json()
            return data["choices"][0]["message"]["content"].strip()
        except:
            time.sleep(2)

    return "Scusami, ho avuto un attimo di silenzio mentale…"

# ======================================================
# AI CALL (ASYNC – FIX FREEZE)
# ======================================================
def call_ai_async(prompt, messages, mode, callback):
    def worker():
        text = call_ai(prompt, messages, mode)
        Clock.schedule_once(lambda dt: callback(text), 0)
    Thread(target=worker, daemon=True).start()

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
        self.memory_summary = "Nessuna interazione significativa."
        self.interactions = 0
        self.mood = "neutro"
        self.relationship_points = 0
        self.relationship_level = "Sconosciuto"
        self.social_style = "Autonomo"

    def add_to_memory(self, u, a):
        self.memory += [
            {"role":"user","content":u},
            {"role":"assistant","content":a}
        ]
        self.memory = self.memory[-MAX_MEMORY_MESSAGES:]

    def update_relationship(self, d):
        self.relationship_points += d
        if self.relationship_points >= 60:
            self.relationship_level = "Confidente"
        elif self.relationship_points >= 30:
            self.relationship_level = "Collaboratore"
        elif self.relationship_points >= 10:
            self.relationship_level = "Conoscente"

    def evolve(self):
        self.interactions += 1
        if self.interactions > 20:
            self.mood = "sicuro"

    def full_prompt(self):
        return self.prompt.format(
            mood=self.mood,
            relationship_level=self.relationship_level,
            social_rule=SOCIAL_STYLES.get(self.social_style,""),
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
            try:
                self.__dict__.update(
                    json.load(open(self.file,"r",encoding="utf-8"))
                )
            except:
                pass

# ======================================================
# KEYBOARD AWARE
# ======================================================
class KeyboardAwareScreen(Screen):
    def on_pre_enter(self):
        Window.bind(on_keyboard_height=self._on_keyboard_height)

    def on_leave(self):
        Window.unbind(on_keyboard_height=self._on_keyboard_height)

    def _on_keyboard_height(self, window, height):
        if hasattr(self,"input_bar"):
            self.input_bar.padding = (0,0,0,height)

# ======================================================
# SPLASH SCREEN
# ======================================================
class SplashScreen(Screen):
    def __init__(self, **kw):
        super().__init__(**kw)
        root = BoxLayout(orientation="vertical", padding=40, spacing=20)
        root.add_widget(Image(source="logo.png", size_hint=(1,0.45)))
        root.add_widget(Label(text=f"[b]{APP_NAME}[/b]", markup=True, font_size="40sp"))
        root.add_widget(Label(text=APP_SUB, font_size="18sp"))
        root.add_widget(Label(text=f"{APP_VERSION}\n{APP_AUTHOR}", font_size="14sp"))
        self.add_widget(root)

    def on_enter(self):
        Clock.schedule_once(lambda dt: setattr(self.manager,"current","room"),2.5)

# ======================================================
# ROOM SCREEN (ASYNC SAFE)
# ======================================================
class RoomScreen(KeyboardAwareScreen):
    def __init__(self, avatars, **kw):
        super().__init__(**kw)
        self.avatars = avatars
        self.queue = deque()
        self.last_user_msg = ""

        root = BoxLayout(orientation="vertical", padding=6, spacing=6)

        self.chat = Label(markup=True, size_hint_y=None,
                          text_size=(Window.width-24,None))
        self.chat.bind(texture_size=self.chat.setter("size"))

        scroll = ScrollView(size_hint=(1,0.6))
        scroll.add_widget(self.chat)
        root.add_widget(scroll)

        self.input = TextInput(size_hint=(1,0.15), multiline=True)
        root.add_widget(self.input)

        send = Button(text="Invia", size_hint_y=None, height=42)
        send.bind(on_press=self.send_common)
        root.add_widget(send)

        grid = GridLayout(cols=3, size_hint=(1,0.25), spacing=6)

        for av in avatars:
            box = BoxLayout(orientation="vertical", spacing=4)
            box.add_widget(Image(source="avatar.jpg"))

            name_btn = Button(text=av.display_name(), size_hint_y=None, height=34)
            name_btn.bind(on_press=lambda x,a=av:self.open_private(a))

            toggle_btn = Button(text="ON", size_hint_y=None, height=26)
            voice_btn  = Button(text="VOICE ON", size_hint_y=None, height=26)

            toggle_btn.bind(on_press=lambda x,b=toggle_btn,a=av:self.toggle(b,a))
            voice_btn.bind(on_press=lambda x,b=voice_btn,a=av:self.toggle_voice(b,a))

            box.add_widget(name_btn)
            box.add_widget(toggle_btn)
            box.add_widget(voice_btn)
            grid.add_widget(box)

        root.add_widget(grid)
        self.add_widget(root)

    def toggle(self, btn, a):
        a.enabled = not a.enabled
        btn.text = "ON" if a.enabled else "OFF"
        a.save()

    def toggle_voice(self, btn, a):
        a.voice = not a.voice
        btn.text = "VOICE ON" if a.voice else "VOICE OFF"
        a.save()

    def send_common(self,_):
        msg = self.input.text.strip()
        if not msg: return
        self.last_user_msg = msg
        self.chat.text += f"\n{COL_USER}TU:{COL_END} {msg}{ANCHOR}"
        self.input.text = ""
        self.queue = deque([a for a in self.avatars if a.is_active() and a.enabled])
        Clock.schedule_once(self.process_next,0.1)

    def process_next(self,_):
        if not self.queue: return
        av = self.queue.popleft()
        typing = f"[color={av.color}]{av.display_name()} sta scrivendo…{COL_END}"
        self.chat.text += f"\n{typing}{ANCHOR}"

        def on_reply(text):
            self.chat.text = self.chat.text.replace(f"\n{typing}","",1)
            if text:
                self.chat.text += f"\n[color={av.color}]{av.display_name()}: {text}{COL_END}{ANCHOR}"
                av.add_to_memory(self.last_user_msg,text)
                av.update_relationship(1)
                av.evolve()
                av.counter -= 1
                av.save()
                if av.voice:
                    speak(text,av.voice_rate)

            if len(self.chat.text) > MAX_CHAT_CHARS:
                self.chat.text = self.chat.text[-8000:]

            Clock.schedule_once(self.process_next,0.15)

        call_ai_async(
            av.full_prompt(),
            av.memory + [{"role":"user","content":self.last_user_msg}],
            "public",
            on_reply
        )

    def open_private(self,av):
        self.manager.get_screen("private").set_avatar(av)
        self.manager.current = "private"

# ======================================================
# PRIVATE SCREEN (ASYNC SAFE)
# ======================================================
class PrivateScreen(KeyboardAwareScreen):
    def __init__(self, **kw):
        super().__init__(**kw)
        self.avatar = None

        root = BoxLayout(orientation="vertical", padding=6, spacing=6)

        self.chat = Label(markup=True, size_hint_y=None,
                          text_size=(Window.width-24,None))
        self.chat.bind(texture_size=self.chat.setter("size"))

        scroll = ScrollView()
        scroll.add_widget(self.chat)
        root.add_widget(scroll)

        self.input_bar = BoxLayout(orientation="vertical", size_hint_y=None)
        self.input = TextInput(size_hint_y=None, height=80)
        self.input_bar.add_widget(self.input)

        bar = BoxLayout(size_hint_y=None, height=42)

        for t,f in [
            ("Invia",self.send_private),
            ("🪪 ID",self.show_identity),
            ("Genera / Reset",self.choose_action),
            ("←",lambda x:setattr(self.manager,"current","room"))
        ]:
            b = Button(text=t)
            b.bind(on_press=f)
            bar.add_widget(b)

        self.input_bar.add_widget(bar)
        root.add_widget(self.input_bar)
        self.add_widget(root)

    def set_avatar(self,av):
        self.avatar = av
        self.chat.text = f"{COL_SYS}[Chat privata con {av.display_name()}]{COL_END}{ANCHOR}"
        for m in av.memory:
            if m["role"]=="user":
                self.chat.text += f"\n{COL_USER}TU:{COL_END} {m['content']}{ANCHOR}"
            else:
                self.chat.text += f"\n[color={av.color}]{av.display_name()}: {m['content']}{COL_END}{ANCHOR}"

    def send_private(self,_):
        msg = self.input.text.strip()
        if not msg: return
        self.chat.text += f"\n{COL_USER}TU:{COL_END} {msg}{ANCHOR}"
        self.input.text = ""

        def on_reply(text):
            if text:
                self.chat.text += f"\n[color={self.avatar.color}]{self.avatar.display_name()}: {text}{COL_END}{ANCHOR}"
                self.avatar.add_to_memory(msg,text)
                self.avatar.update_relationship(2)
                self.avatar.evolve()
                self.avatar.counter -= 1
                self.avatar.save()
                if self.avatar.voice:
                    speak(text,self.avatar.voice_rate)

        call_ai_async(
            self.avatar.full_prompt(),
            self.avatar.memory + [{"role":"user","content":msg}],
            "private",
            on_reply
        )

    def choose_action(self,_):
        box = BoxLayout(orientation="vertical",padding=12,spacing=12)
        popup = Popup(title="Azione Avatar",content=box,size_hint=(0.8,0.5))
        box.add_widget(Button(text="Genera nuovo avatar",
                              on_press=lambda x:(popup.dismiss(),self.open_generate())))
        box.add_widget(Button(text="Reset avatar",
                              on_press=lambda x:(popup.dismiss(),self.confirm_reset())))
        box.add_widget(Button(text="Annulla",
                              on_press=lambda x:popup.dismiss()))
        popup.open()

    def confirm_reset(self):
        box = BoxLayout(orientation="vertical",padding=12,spacing=12)
        popup = Popup(title="Conferma reset",content=box,size_hint=(0.7,0.4))
        box.add_widget(Label(text="Sei sicuro?"))
        box.add_widget(Button(text="SI",
                              on_press=lambda x:(popup.dismiss(),self.do_reset())))
        box.add_widget(Button(text="NO",
                              on_press=lambda x:popup.dismiss()))
        popup.open()

    def do_reset(self):
        self.avatar.reset()
        self.avatar.save()
        self.chat.text = f"{COL_SYS}[Avatar resettato]{COL_END}{ANCHOR}"

    def open_generate(self):
        layout = BoxLayout(orientation="vertical",padding=14,spacing=10)
        popup = Popup(content=layout,size_hint=(0.9,0.85))

        name = TextInput(hint_text="Nome avatar",multiline=False)
        role = TextInput(hint_text="Ruolo",multiline=True)
        style = TextInput(hint_text="Stile / Tono",multiline=True)

        layout.add_widget(name)
        layout.add_widget(role)
        layout.add_widget(style)
        layout.add_widget(Label(text="Stile sociale"))

        selected={"val":"Autonomo"}
        row=BoxLayout(size_hint_y=None,height=40,spacing=6)

        for s in SOCIAL_STYLES:
            b=Button(text=s)
            b.bind(on_press=lambda x,v=s:selected.update(val=v))
            row.add_widget(b)

        layout.add_widget(row)

        def gen(_):
            if not name.text.strip(): return
            self.avatar.identity={"nome":name.text,"ruolo":role.text,"stile":style.text}
            self.avatar.social_style=selected["val"]
            self.avatar.prompt=BASE_PROMPT.format(
                nome=name.text,
                ruolo=role.text,
                stile=style.text,
                mood="{mood}",
                relationship_level="{relationship_level}",
                social_rule="{social_rule}",
                memory_summary="{memory_summary}"
            )
            self.avatar.generated=True
            self.avatar.counter=50
            self.avatar.memory=[]
            self.avatar.memory_summary="Avatar appena generato."
            self.avatar.save()
            self.chat.text=f"{COL_SYS}[Avatar generato]{COL_END}{ANCHOR}"
            popup.dismiss()

        layout.add_widget(Button(text="GENERA",on_press=gen))
        popup.open()

    def show_identity(self,_):
        a=self.avatar
        info=f"""
Nome: {a.display_name()}
Ruolo: {a.identity.get('ruolo','')}
Stile: {a.identity.get('stile','')}
Stile sociale: {a.social_style}
Mood: {a.mood}
Relazione: {a.relationship_level} ({a.relationship_points})
Interazioni: {a.interactions}
"""
        Popup(title="Carta d'identità Avatar",
              content=Label(text=info),
              size_hint=(0.8,0.6)).open()

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
