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

KV = '''
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
        right_action_items: [["information", lambda x: app.show_about()]]

    GridLayout:
        cols: 1
        padding: [5, 5]
        spacing: 5

        Image:
            id: servo_image
            source: ""
            size_hint: None, None
            size: 1050, 800
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
            text: "digite um comando para o Servo"
            halign: "center"
            theme_text_color: "Secondary"
            color: (1,1,1,1)
            
        MDLabel:
            id: servo_text_space1
            text: "_______________________________________"
            halign: "center"
            theme_text_color: "Secondary"
            color: (1,1,1,1)

    MDTextField:
        id: task_input
        hint_text: "Digite um comando para o servo"
        mode: "rectangle"
        size_hint_x: 0.9
        pos_hint: {'center_x': 0.5}

    BoxLayout:  # Buttons container
        orientation: 'vertical'  # Arrange buttons vertically
        size_hint_y: 0.3
        pos_hint: {'center_x': 0.5}
        spacing: 20 
        
        MDLabel:
            id: servo_text_space2
            text: "_______________________________________"
            halign: "center"
            theme_text_color: "Secondary"
            color: (1,1,1,1)
        
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
            width: 200 #Example width
            pos_hint: {'center_x': 0.5} 

        MDRaisedButton:
            text: "Recompensa"
            on_release: app.feed_servo()
            size_hint_x: None
            width: 200
            pos_hint: {'center_x': 0.5}
            
        MDLabel:
            id: servo_selection
            text: "Selecione um servo"
            halign: "center"
            theme_text_color: "Secondary"
            color: (1,1,1,1)
            
    ScrollView:
        size_hint_x: 0.5
        size_hint_y: 0.2
        max_height: "500dp"
        MDList:
            id: servos_list
'''

class ServoApp(MDApp):
    dialog = None
    servos_dir = "servos"
    servos_data_dir = "servos_data"
    current_servo = None
    audio = None

    def build(self):
        return Builder.load_string(KV)

    def on_start(self):
        self.load_servos()
        self.load_audio()

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

    def load_servo_data(self, filename):
        servo_data_path = os.path.join(self.servos_data_dir, f"{filename}.json")
        if not os.path.exists(servo_data_path):
            servo_data = {"name": filename, "power": 0, "code": 0, "tasks": []}
            with open(servo_data_path, "w") as file:
                json.dump(servo_data, file)
        else:
            with open(servo_data_path, "r") as file:
                servo_data = json.load(file)
            if "tasks" not in servo_data: 
                servo_data["tasks"] = [] 
            with open(servo_data_path, "w") as file:
                json.dump(servo_data, file)
                self.update_ui(servo_data)
            if "power" not in servo_data:
                servo_data["power"] = 0

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
        
    def feed_servo(self):

        if self.current_servo is None:
        
            return
        
        servo_data_path = os.path.join(self.servos_data_dir, f"{self.current_servo}.json")
        
        with open(servo_data_path, "r") as file:
        
            servo_data = json.load(file)
        
        if servo_data["code"] == 0:
        
            self.dialog = MDDialog(
        
            title="Código Não Definido",
        
            text="Defina um código para o servo antes de alimentá-lo.",
        
            buttons=[MDRaisedButton (text="OK",
        
            on_release=lambda x:
        
                self.dialog.dismiss())]
        
            )
            self.dialog.open()

            return
        servo_data["power"] += servo_data["code"]
        
        with open(servo_data_path, "w") as file:
        
            json.dump(servo_data, file)
        
            self.update_ui(servo_data)
            
    def add_servo_code(self):
        if self.current_servo is None:
            return

        servo_data_path = os.path.join(self.servos_data_dir, f"{self.current_servo}.json")

        with open(servo_data_path, "r") as file:
            servo_data = json.load(file)

        if servo_data["code"] != 0:
            self.dialog = MDDialog(
                title="Código já definido",
                text=f"O código deste servo já foi definido como {servo_data['code']}.",
                buttons=[MDRaisedButton(text="OK", on_release=lambda x: self.dialog.dismiss())]
            )
            self.dialog.open()
            return

        self.dialog = MDDialog(
            title="Definir Código do Servo",
            type="custom",
            content_cls=MDTextField(hint_text="Digite o código do servo"),
            buttons=[
                MDRaisedButton(text="Salvar", on_release=lambda x: self.save_servo_code()),
                MDRaisedButton(text="Cancelar", on_release=lambda x: self.dialog.dismiss())
            ]
        )
        self.dialog.open()

    def save_servo_code(self):
        if self.current_servo is None:
            return

        new_code = self.dialog.content_cls.text
        if not new_code.isdigit():
            return

        new_code = int(new_code)
        servo_data_path = os.path.join(self.servos_data_dir, f"{self.current_servo}.json")

        with open(servo_data_path, "r") as file:
            servo_data = json.load(file)

        servo_data["code"] = new_code

        with open(servo_data_path, "w") as file:
            json.dump(servo_data, file)

        self.dialog.dismiss()
        
    def show_about(self):
        if not self.dialog:
            self.dialog = MDDialog(
                title="Sobre",
                text='''Nome do App: Servo Manager
\nVersão: 2.0
\nDesenvolvedor: Loki Nefarius, inspirado pelo
\nTecnomago (Caotize-se)
\nDescrição: controle o poder dos servos astrais com \neste aplicativo tecnomágico! O Servo Manager \npermite que você gerencie e recompense seus servos de \nforma intuitiva e eficaz.
\nComo funciona: Cada servo astral possui um código \nnumérico único. Ao completar tarefas com sucesso, \nvocê recompensa o servo com esse código, como uma \ncriptomoeda especial que o fortalece e o motiva. \nImagine que seus servos são movidos a essa "droga" \nde recompensa, sempre dispostos a realizar suas \nordens em troca de mais poder e prazer.
\nQuer saber mais sobre a filosofia por trás do aplicativo? Visite: https://caotize.se/
''',
                buttons=[MDRaisedButton(text="OK", on_release=lambda x: self.dialog.dismiss())]
            )
        self.dialog.open()
        
    def load_audio(self):
        self.audio = SoundLoader.load("alpha.wav") 
        
    def play_audio(self):
        if self.audio:
            self.audio.play()
        else:
            print("Áudio não encontrado.")

if __name__ == '__main__':
    ServoApp().run()