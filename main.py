import os
import json
from kivy.lang import Builder
from kivymd.app import MDApp
from kivymd.uix.button import MDRaisedButton
from kivymd.uix.dialog import MDDialog
from kivymd.uix.textfield import MDTextField
from kivymd.uix.list import MDList, OneLineListItem
from kivymd.uix.label import MDLabel
from kivy.uix.image import Image
from kivy.uix.scrollview import ScrollView
from kivy.core.audio import SoundLoader
from kivy.uix.screenmanager import ScreenManager, Screen

import afirm_screen             # Importa o módulo afirm_screen
from afirm_screen import AfirmScreen  # Importa a tela secundária

KV = '''
ScreenManager:
    ServoScreen:
        name: "servo_manager"
    AfirmScreen:
        name: "afirm_screen"

<ServoScreen>:
    BoxLayout:
        orientation: 'vertical'
        canvas.before:
            Color:
                rgba: 0, 0, 0, 1
            Rectangle:
                pos: self.pos
                size: self.size

        MDTopAppBar:
            title: "Servo Manager"
            left_action_items: [["image", lambda x: app.open_afirm_screen()]]  # Botão para abrir a tela secundária
            right_action_items: [["information", lambda x: app.show_about()]]

        GridLayout:
            cols: 1
            padding: [2, 2]
            spacing: 2

            Image:
                id: servo_image
                source: ""
                size_hint: None, None
                size: 1050, 700
                pos_hint: {'center_x': 0.5}

            MDLabel:
                id: servo_name
                text: "Nome do Servo:"
                halign: "center"
                theme_text_color: "Secondary"
                color: (1,1,1,1)

            MDLabel:
                id: servo_coins
                text: "Power: 0"
                halign: "center"
                theme_text_color: "Secondary"
                color: (1,1,1,1)

            MDLabel:
                id: servo_info
                text: "Digite um comando para o Servo"
                halign: "center"
                theme_text_color: "Secondary"
                color: (1,1,1,1)

        MDTextField:
            id: task_input
            hint_text: "Digite um comando para o servo"
            mode: "rectangle"
            size_hint_x: 0.9
            pos_hint: {'center_x': 0.5}

        BoxLayout:
            orientation: 'vertical'
            size_hint_y: 0.5
            pos_hint: {'center_x': 0.5}
            spacing: 15 

            MDRaisedButton:
                text: "Enviar Intento"
                on_release: app.send_task()
                size_hint_x: None
                width: 200
                pos_hint: {'center_x': 0.5}

            MDRaisedButton:
                text: "Adicionar Código do Servo"
                on_release: app.add_servo_code()
                size_hint_x: None  
                width: 200
                pos_hint: {'center_x': 0.5} 

            MDRaisedButton:
                text: "Recompensa"
                on_release: app.feed_servo()
                size_hint_x: None
                width: 200
                pos_hint: {'center_x': 0.5}

        ScrollView:
            size_hint_x: 0.5
            size_hint_y: 0.2
            max_height: "500dp"
            MDList:
                id: servos_list
'''

class ServoScreen(Screen):
    pass

class AfirmScreen(afirm_screen.AfirmScreen):  # Herda da tela secundária
    pass

class ServoApp(MDApp):
    dialog = None
    servos_dir = "servos"
    servos_data_dir = "servos_data"
    current_servo = None
    code_input = None

    def build(self):
        self.binaural = SoundLoader.load("binaural.mp3")  # Carrega o som binaural
        sm = ScreenManager()
        sm.add_widget(ServoScreen(name="servo_manager"))
        sm.add_widget(AfirmScreen(name="afirm_screen"))
        # Carrega a interface definida no KV
        root = Builder.load_string(KV)
        # Para manter a compatibilidade com o acesso aos ids, atribuímos os ids do ServoScreen à raiz.
        root.ids = root.get_screen("servo_manager").ids
        return root

    def on_start(self):
        self.load_servos()

    def load_servos(self):
        servos_list = self.root.ids.servos_list
        servos_list.clear_widgets()
        os.makedirs(self.servos_dir, exist_ok=True)
        os.makedirs(self.servos_data_dir, exist_ok=True)
        servo_files = [f for f in os.listdir(self.servos_dir) if f.lower().endswith(('.png', '.jpg', '.jpeg'))]
        
        if not servo_files:
            servos_list.add_widget(MDLabel(text="Nenhum servo encontrado.", halign="center"))
        
        for file in servo_files:
            item = OneLineListItem(text=file, on_release=lambda x, f=file: self.view_servo(f))
            item.text_color = (1, 1, 1, 1)
            item.theme_text_color = "Custom"
            servos_list.add_widget(item)

    def view_servo(self, filename):
        full_path = os.path.join(self.servos_dir, filename)
        self.root.ids.servo_image.source = full_path
        self.root.ids.servo_name.text = filename
        self.current_servo = filename
        self.load_servo_data(filename)
        if self.binaural:
            self.binaural.loop = True
            self.binaural.play()

    def open_afirm_screen(self):
        self.root.current = "afirm_screen"  # Muda para a tela secundária
        if self.binaural:
            self.binaural.loop = True
            self.binaural.stop()

    def load_servo_data(self, filename):
        servo_data_path = os.path.join(self.servos_data_dir, f"{filename}.json")
        if not os.path.exists(servo_data_path):
            servo_data = {"name": filename, "power": 0, "code": 0, "tasks": []}
            with open(servo_data_path, "w") as file:
                json.dump(servo_data, file)
        else:
            with open(servo_data_path, "r") as file:
                servo_data = json.load(file)
            self.update_ui(servo_data)

    def update_ui(self, servo_data):
        self.root.ids.servo_coins.text = f"Power: {servo_data['power']}"

    def send_task(self):
        if self.current_servo is None:
            return
        task = self.root.ids.task_input.text.strip()
        if not task:
            return
        servo_data_path = os.path.join(self.servos_data_dir, f"{self.current_servo}.json")
        with open(servo_data_path, "r") as file:
            servo_data = json.load(file)
        servo_data["tasks"].append(task)
        with open(servo_data_path, "w") as file:
            json.dump(servo_data, file)
        self.root.ids.task_input.text = ""

    def show_about(self):
        about_dialog = MDDialog(
            title="Sobre",
            text='''Nome do App: Servo Manager
Versão: 1.1.1
Desenvolvedor: Loki Nefarius
Descrição: Controle e fortaleça seus servos astrais.''',
            buttons=[MDRaisedButton(text="OK", on_release=lambda x: about_dialog.dismiss())]
        )
        about_dialog.open()

if __name__ == '__main__':
    ServoApp().run()
