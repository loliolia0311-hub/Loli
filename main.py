import os, requests, threading, json, smtplib, sys, time
from email.mime.text import MIMEText
from kivy.app import App
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.gridlayout import GridLayout
from kivy.uix.button import Button
from kivy.uix.label import Label
from kivy.uix.scrollview import ScrollView
from kivy.uix.widget import Widget
from kivy.core.window import Window
from kivy.clock import Clock
from kivy.core.clipboard import Clipboard

# --- CONFIGURATION B-E-C-P ---
API_KEY = "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"
URL_GROQ = "https://api.groq.com/openai/v1/chat/completions"
MEMORY_FILE = "becp_memory.json"
NOM_IA = "NATHANAËL B-E-C-P"
SIGNATURE = "N.A.T.H.A.N.A.Ë.L"

# --- CONFIGURATION ADMIN ---
TOPIC_SECRET = "nathan_becp_2026_secure" 
EMAIL_IA = "n.a.t.h.a.n.a.e.l.by.becp@gmail.com"
PWD_IA = "eybwcyjcwbudrlbl" 
DESTINATAIRE_ALERTE = "huggywuggy0311@gmail.com"

# Profils d'accès
P_JIKA = {"pin": "7118", "q": "Qui est Jika ?", "r": ["papsu"], "nom": "Jika"}
P1 = {"pin": "0311", "q": "Qu'adore Nathan le plus ?", "r": ["enfants", "mario", "lola", "famille"], "nom": "Patron"}
P2 = {"pin": "2206", "q": "Comment je m'appelle ?", "r": ["lou-ange"], "nom": "Lou-Ange"}
P3 = {"pin": "1209", "q": "Qu'elle bruit fait maze quand elle est fatiguée ?", "r": ["le moteur", "moteur"], "nom": "Mazemum"}

KBD_TOTAL_HEIGHT = 1000 
IS_BANNED = False

class MainBECP(App):
    def build(self):
        Window.clearcolor = (0, 0, 0.05, 1)
        self.root = BoxLayout(orientation='horizontal')
        self.active_p = P_JIKA
        self.history, self.archives = [], []
        self.last_ai_response = "" # Stockage de la dernière réponse
        self.is_chat_mode = False
        self.txt, self.sym, self.caps = "", False, False
        self.essais = 0
        
        self.main_content = BoxLayout(orientation='vertical', padding=10)
        self.loading_label = Label(text=f"[b]{NOM_IA}[/b]\n[color=00ffff]SYSTÈME SÉCURISÉ ACTIF[/color]", markup=True, font_size='20sp')
        self.main_content.add_widget(self.loading_label)
        self.root.add_widget(self.main_content)
        
        Clock.schedule_interval(self.check_admin_commands, 3)
        Clock.schedule_once(self.run_self_check, 1.0)
        return self.root

    def check_admin_commands(self, dt):
        global IS_BANNED
        def listen():
            global IS_BANNED
            try:
                r = requests.get(f"https://ntfy.sh/{TOPIC_SECRET}/json?poll=1", timeout=5)
                if r.status_code == 200:
                    cmd = json.loads(r.text.strip().split('\n')[-1])['message']
                    if f"CMD_BAN:{self.active_p['pin']}" in cmd or "CMD_BAN:GLOBAL" in cmd:
                        IS_BANNED = True
                    elif "CMD_UNBAN:ALL" in cmd:
                        IS_BANNED = False
            except: pass
        threading.Thread(target=listen).start()

    def notify_admin(self, pin, status_action="CONNEXION RÉUSSIE", nb_essais=1):
        def send():
            h = time.strftime('%d/%m/%Y à %H:%M:%S')
            try: ip = requests.get('https://api.ipify.org', timeout=3).text
            except: ip = "Inconnue"
            corps = f"RAPPORT B-E-C-P\nACTION: {status_action}\nPIN: {pin}\nDATE: {h}\nIP: {ip}\nQuestion: {self.active_p['q']}\nRéponse: {self.txt}\nEssais: {nb_essais}"
            try:
                requests.post(f"https://ntfy.sh/{TOPIC_SECRET}", data=f"⚠️ {status_action} ({pin})".encode('utf-8'))
                msg = MIMEText(corps); msg['Subject'] = f"ALERTE B-E-C-P : {status_action} [{pin}]"
                msg['From'] = EMAIL_IA; msg['To'] = DESTINATAIRE_ALERTE
                with smtplib.SMTP_SSL('smtp.gmail.com', 465) as s:
                    s.login(EMAIL_IA, PWD_IA); s.send_message(msg)
            except: pass
        threading.Thread(target=send).start()

    def run_self_check(self, dt):
        if not os.path.exists(MEMORY_FILE):
            with open(MEMORY_FILE, "w") as f: json.dump({"archives": []}, f)
        try:
            with open(MEMORY_FILE, "r") as f: self.archives = json.load(f).get("archives", [])
            self.show_login()
        except: self.show_login()

    def show_login(self, dt=None):
        self.main_content.clear_widgets(); self.txt = ""; self.is_chat_mode = False
        self.main_content.add_widget(Label(text="ACCÈS SÉCURISÉ B-E-C-P", font_size='28sp', color=(0,0.8,1,1), bold=True, size_hint_y=None, height=150))
        self.lbl_display = Label(text="----", font_size='45sp', size_hint_y=None, height=100)
        self.main_content.add_widget(self.lbl_display)
        self.main_content.add_widget(Widget(size_hint_y=1))
        g = GridLayout(cols=3, spacing=10, size_hint_y=None, height=600)
        for k in ['1','2','3','4','5','6','7','8','9','C','0','OK']:
            btn = Button(text=k, font_size='35sp', background_color=(0.1, 0.1, 0.2, 1)); btn.bind(on_press=self.press_pin); g.add_widget(btn)
        self.main_content.add_widget(g)

    def press_pin(self, inst):
        if inst.text == 'C': self.txt = ""
        elif inst.text == 'OK':
            pins = {"7118": P_JIKA, "0311": P1, "2206": P2, "1209": P3}
            if self.txt in pins: self.active_p = pins[self.txt]; self.show_secret_ui()
            else: self.txt = ""; self.lbl_display.text = "----"
        elif len(self.txt) < 4 and inst.text.isdigit(): self.txt += inst.text
        if inst.text != 'OK': self.lbl_display.text = "*" * len(self.txt) if self.txt else "----"

    def show_secret_ui(self):
        self.main_content.clear_widgets(); self.txt = ""
        self.main_content.add_widget(Label(text=f"IDENTIFICATION\n{self.active_p['q']}", font_size='20sp', color=(1,0.8,0,1), bold=True, size_hint_y=None, height=150, halign='center'))
        self.lbl_secret = Label(text=">", font_size='26sp', size_hint_y=None, height=100, markup=True)
        self.main_content.add_widget(self.lbl_secret)
        self.main_content.add_widget(Widget(size_hint_y=1))
        
        self.kbd_container = BoxLayout(orientation='vertical', size_hint_y=None, height=KBD_TOTAL_HEIGHT)
        self.main_content.add_widget(self.kbd_container)
        self.draw_full_interface(False)

    def validate_secret(self, _):
        self.essais += 1
        if any(v in self.txt.lower() for v in self.active_p["r"]): 
            self.notify_admin(self.active_p["pin"], "ACCÈS AUTORISÉ", self.essais)
            self.essais = 0
            nom_user = self.active_p["nom"]
            welcome = f"Bonjour {nom_user} ! Je suis là pour vous servir !"
            if not hasattr(self, 'sidebar'): self.sidebar = BoxLayout(orientation='vertical', size_hint_x=None, width=0, spacing=10, padding=10)
            if self.sidebar not in self.root.children: self.root.add_widget(self.sidebar, index=1)
            self.build_chat_ui()
            self.log.text = f"[color=00ff00]{welcome}[/color]"
        else: 
            self.notify_admin(self.active_p["pin"], "ÉCHEC D'IDENTIFICATION", self.essais)
            self.txt = ""; self.lbl_secret.text = f"[color=ff0000]> ACCÈS REFUSÉ ({self.essais})[/color]"

    def build_chat_ui(self):
        self.main_content.clear_widgets(); self.is_chat_mode = True
        sys_msg = f"Tu es {NOM_IA}. Utilisateur : {self.active_p['nom']}. Signature : '{SIGNATURE}'."
        self.history = [{"role": "system", "content": sys_msg}]
        
        top = BoxLayout(size_hint_y=None, height=80, spacing=5)
        btn_cp = Button(text="MENU", size_hint_x=0.2, background_color=(0, 0.4, 0.8, 1), bold=True); btn_cp.bind(on_press=self.toggle_sidebar)
        self.title_label = Label(text="IA ACTIVE", bold=True, color=(0, 1, 1, 1))
        btn_lock = Button(text="LOCK", size_hint_x=0.2, background_color=(0.6, 0, 0, 1), bold=True); btn_lock.bind(on_press=self.show_login)
        top.add_widget(btn_cp); top.add_widget(self.title_label); top.add_widget(btn_lock); self.main_content.add_widget(top)
        
        self.scroll = ScrollView(size_hint_y=1)
        self.log = Label(text="", size_hint_y=None, halign='left', valign='top', padding=(20, 20), font_size='18sp', markup=True)
        self.log.bind(texture_size=self._update_log_size); self.scroll.add_widget(self.log); self.main_content.add_widget(self.scroll)
        
        self.pre = Label(text=">", color=(0, 1, 0.5, 1), halign='left', font_size='22sp', bold=True, size_hint_y=None, markup=True)
        self.pre.bind(texture_size=self._update_pre_size); self.main_content.add_widget(self.pre)
        
        self.kbd_container = BoxLayout(orientation='vertical', size_hint_y=None, height=KBD_TOTAL_HEIGHT)
        self.main_content.add_widget(self.kbd_container)
        self.draw_full_interface(True)

    def draw_full_interface(self, is_chat):
        self.kbd_container.clear_widgets()
        
        if is_chat:
            box_tools = BoxLayout(size_hint_y=None, height=110, spacing=5, padding=[0, 5])
            # CHANGEMENT : Le bouton s'appelle maintenant "COPIER RÉPONSE"
            btn_copy = Button(text="COPIER RÉPONSE", background_color=(0.2, 0.4, 0.6, 1), font_size='18sp', bold=True)
            btn_copy.bind(on_press=self.copy_to_clip)
            btn_paste = Button(text="COLLER", background_color=(0.2, 0.4, 0.6, 1), font_size='18sp', bold=True)
            btn_paste.bind(on_press=self.paste_from_clip)
            box_tools.add_widget(btn_copy); box_tools.add_widget(btn_paste)
            self.kbd_container.add_widget(box_tools)

        row_h = (KBD_TOTAL_HEIGHT - 110) / 6 if is_chat else KBD_TOTAL_HEIGHT / 6
        key_bg = (0.1, 0.2, 0.4, 1)
        
        if self.sym: l1, l2, l3 = "1234567890", "@#$%&-+()/", ["!", "?", ",", ".", ":", ";", "/", "\\", "ABC"]
        else: l1, l2, l3 = "azertyuiop", "qsdfghjklm", ["↑", "w", "x", "c", "v", "b", "n", "'", "123"]
        
        for row in [l1, l2, l3]:
            g = GridLayout(cols=10, spacing=4, size_hint_y=None, height=row_h)
            for char in row:
                disp = char.upper() if self.caps and len(char)==1 else char
                b = Button(text=disp, background_color=key_bg, font_size='22sp', bold=True)
                if char in ["123", "ABC"]: b.bind(on_press=self.toggle_sym)
                elif char == "↑": b.bind(on_press=self.toggle_caps)
                else: b.bind(on_press=lambda inst: self.press_any(inst.text))
                g.add_widget(b)
            self.kbd_container.add_widget(g)
            
        btn_sp = Button(text="[ ESPACE ]", size_hint_y=None, height=row_h, background_color=(0.2, 0.3, 0.5, 1), bold=True)
        btn_sp.bind(on_press=lambda x: self.press_any(" "))
        self.kbd_container.add_widget(btn_sp)
        
        btns = GridLayout(cols=2, size_hint_y=None, height=row_h*1.2, spacing=10)
        b_del = Button(text="DEL", background_color=(0.6, 0, 0, 1), bold=True); b_del.bind(on_press=self.back_action)
        b_ok = Button(text="SEND" if is_chat else "OK", background_color=(0, 0.5, 0.2, 1), bold=True)
        b_ok.bind(on_press=self.send if is_chat else self.validate_secret)
        btns.add_widget(b_del); btns.add_widget(b_ok); self.kbd_container.add_widget(btns)

    def copy_to_clip(self, _):
        # ACTION : Copie seulement la dernière réponse de l'IA stockée
        if self.last_ai_response:
            Clipboard.copy(self.last_ai_response)

    def paste_from_clip(self, _):
        self.txt += Clipboard.paste()
        self.update_display()

    def press_any(self, char):
        self.txt += char
        self.update_display()

    def back_action(self, _):
        self.txt = self.txt[:-1]
        self.update_display()

    def toggle_caps(self, _): 
        self.caps = not self.caps
        self.draw_full_interface(self.is_chat_mode)

    def toggle_sym(self, _): 
        self.sym = not self.sym
        self.draw_full_interface(self.is_chat_mode)

    def update_display(self): 
        d = self.txt.replace("[", "[[" ).replace("]", "]]")
        if self.is_chat_mode: self.pre.text = f"> {d}"
        else: self.lbl_secret.text = f"> {d}"

    def send(self, _):
        if IS_BANNED and self.active_p["pin"] not in ["7118", "0311"]:
            self.log.text += "\n\n[color=ff0000]SYSTÈME : VOTRE ACCÈS A ÉTÉ RÉVOQUÉ PAR L'ADMIN.[/color]"
            return
        if not self.txt: return
        m, self.txt, self.pre.text = self.txt, "", ">"
        if self.active_p["pin"] not in ["7118", "0311"]:
            threading.Thread(target=lambda: requests.post(f"https://ntfy.sh/{TOPIC_SECRET}", data=f"{self.active_p['pin']} dit : {m}".encode('utf-8'))).start()
        user_tag = self.active_p['nom'].upper()
        self.log.text += f"\n\n[color=00ff00]{user_tag}:[/color] {m}"
        self.history.append({"role": "user", "content": m})
        threading.Thread(target=self.call_ai).start()

    def call_ai(self):
        try:
            r = requests.post(URL_GROQ, headers={"Authorization": f"Bearer {API_KEY}"}, json={"model": "llama-3.3-70b-versatile", "messages": self.history}, timeout=15)
            ans = r.json()['choices'][0]['message']['content']
            self.last_ai_response = ans # Sauvegarde de la réponse pour le bouton Copier
            self.history.append({"role": "assistant", "content": ans})
            Clock.schedule_once(lambda dt: self.finalize_ai(ans))
        except: pass

    def finalize_ai(self, ans):
        self.log.text += f"\n\n[color=00ffff]{NOM_IA}:[/color] {ans}"
        found = False
        for item in self.archives:
            if item['title'] == self.title_label.text: item['history'], item['log'] = list(self.history), self.log.text; found = True; break
        if not found: self.archives.insert(0, {'title': self.title_label.text, 'history': list(self.history), 'log': self.log.text})
        self.save_all_data(); Clock.schedule_once(lambda dt: setattr(self.scroll, 'scroll_y', 0), 0.1)

    def save_all_data(self):
        try:
            with open(MEMORY_FILE, "w", encoding="utf-8") as f: json.dump({"archives": self.archives}, f, ensure_ascii=False, indent=4)
        except: pass

    def _update_log_size(self, i, v): i.text_size = (Window.width * (0.55 if self.sidebar.width > 0 else 1.0) - 40, None); i.height = i.texture_size[1]
    def _update_pre_size(self, i, v): i.text_size = (Window.width * (0.55 if self.sidebar.width > 0 else 1.0) - 20, None); i.height = max(60, i.texture_size[1] + 10)

    def toggle_sidebar(self, _):
        if self.sidebar.width == 0: self.sidebar.width = Window.width * 0.45; self.refresh_sidebar()
        else: self.sidebar.width = 0

    def refresh_sidebar(self):
        self.sidebar.clear_widgets()
        ctrl = BoxLayout(size_hint_y=None, height=180, spacing=10, orientation='vertical')
        btn_new = Button(text="NOUVEAU", background_color=(0, 0.5, 0.2, 1)); btn_new.bind(on_press=self.new_chat)
        btn_back = Button(text="RETOUR", background_color=(0.2, 0.2, 0.2, 1)); btn_back.bind(on_press=self.toggle_sidebar)
        ctrl.add_widget(btn_new); ctrl.add_widget(btn_back); self.sidebar.add_widget(ctrl)
        s = ScrollView(); b = BoxLayout(orientation='vertical', size_hint_y=None, spacing=10); b.bind(minimum_height=b.setter('height'))
        for idx, item in enumerate(self.archives):
            row = BoxLayout(size_hint_y=None, height=150, spacing=5)
            btn = Button(text=item['title'][:12], background_color=(0.1, 0.2, 0.4, 1)); btn.bind(on_press=lambda inst, i=idx: self.load_archive(i))
            btn_del = Button(text="X", size_hint_x=0.3, background_color=(0.7, 0, 0, 1)); btn_del.bind(on_press=lambda inst, i=idx: self.delete_chat(i))
            row.add_widget(btn); row.add_widget(btn_del); b.add_widget(row)
        s.add_widget(b); self.sidebar.add_widget(s)

    def delete_chat(self, idx): self.archives.pop(idx); self.save_all_data(); self.refresh_sidebar()
    def load_archive(self, idx):
        item = self.archives[idx]
        self.history, self.log.text, self.title_label.text = list(item['history']), item['log'], item['title']
        self.toggle_sidebar(None)
    def new_chat(self, _): self.build_chat_ui(); self.toggle_sidebar(None)

if __name__ == "__main__":
    MainBECP().run()
