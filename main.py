from kivy.app import App
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.image import Image
from kivy.uix.textinput import TextInput
from kivy.uix.button import Button
from kivy.uix.label import Label
from kivy.core.window import Window
from kivy.utils import platform
from kivy.clock import Clock
import qrcode
import os
from kivy.graphics import Color, Rectangle, RoundedRectangle

# Set window size for PC testing to resemble a phone
if platform not in ('android', 'ios'):
    Window.size = (400, 700)

class QRCodeApp(App):
    def build(self):
        self.title = "Dhanvanth's QR Code"
        self.icon = 'icon.png'
        
        # Main layout with minimalistic design
        root = BoxLayout(orientation='vertical', padding=30, spacing=20)
        
        # Canvas for background color
        with root.canvas.before:
            Color(0.95, 0.96, 0.98, 1)  # Soft off-white/grey background
            self.rect = Rectangle(size=root.size, pos=root.pos)
        root.bind(size=self._update_rect, pos=self._update_rect)

        # Title Label
        title_label = Label(
            text="QR Generator",
            font_size='28sp',
            bold=True,
            color=(0.2, 0.2, 0.2, 1),
            size_hint_y=None,
            height=60
        )
        root.add_widget(title_label)
        
        # Text Input
        self.text_input = TextInput(
            hint_text="Enter text or URL here...",
            multiline=False,
            size_hint_y=None,
            height=50,
            background_normal='',
            background_active='',
            background_color=(1, 1, 1, 1),
            foreground_color=(0.2, 0.2, 0.2, 1),
            padding=(15, 15)
        )
        # Add simple styling to input
        self.text_input.background_color = (1, 1, 1, 0)
        self.text_input.canvas.before.add(Color(0.9, 0.9, 0.9, 1))
        self.text_input.canvas.before.add(RoundedRectangle(pos=self.text_input.pos, size=self.text_input.size, radius=[10]))
        self.text_input.bind(pos=self._update_input_canvas, size=self._update_input_canvas)
        
        root.add_widget(self.text_input)

        # Generate Button
        gen_btn = Button(
            text="Generate QR Code",
            size_hint_y=None,
            height=50,
            background_normal='',
            background_color=(0.4, 0.6, 0.8, 1), # Soft blue
            color=(1, 1, 1, 1),
            bold=True
        )
        gen_btn.bind(on_press=self.generate_qr)
        root.add_widget(gen_btn)

        # Space for QR Code
        self.qr_image = Image(
            size_hint=(1, 1),
            allow_stretch=True
        )
        root.add_widget(self.qr_image)

        # Save Button
        save_btn = Button(
            text="Save to Gallery",
            size_hint_y=None,
            height=50,
            background_normal='',
            background_color=(0.4, 0.8, 0.6, 1), # Soft green
            color=(1, 1, 1, 1),
            bold=True
        )
        save_btn.bind(on_press=self.save_qr)
        root.add_widget(save_btn)

        # Status Label (for messages)
        self.status_label = Label(
            text="",
            size_hint_y=None,
            height=30,
            color=(0.4, 0.4, 0.4, 1),
            font_size='14sp'
        )
        root.add_widget(self.status_label)

        # Request Permissions on Android
        if platform == 'android':
            from android.permissions import request_permissions, Permission
            request_permissions([Permission.WRITE_EXTERNAL_STORAGE, Permission.READ_EXTERNAL_STORAGE])

        return root

    def _update_rect(self, instance, value):
        self.rect.pos = instance.pos
        self.rect.size = instance.size

    def _update_input_canvas(self, instance, value):
        instance.canvas.before.clear()
        with instance.canvas.before:
            Color(1, 1, 1, 1)
            RoundedRectangle(pos=instance.pos, size=instance.size, radius=[10])
            Color(0.8, 0.8, 0.8, 1) # Border
            # Simple border trick or just leave as is. kept simple.

    def generate_qr(self, instance):
        data = self.text_input.text.strip()
        if not data:
            self.status_label.text = "Please enter some text first!"
            return

        try:
            # Generate QR Code
            qr = qrcode.QRCode(
                version=1,
                error_correction=qrcode.constants.ERROR_CORRECT_L,
                box_size=10,
                border=4,
            )
            qr.add_data(data)
            qr.make(fit=True)

            img = qr.make_image(fill_color="black", back_color="white")
            
            # Save to temporary file
            self.temp_img_path = "temp_qr.png"
            img.save(self.temp_img_path)
            
            # Update Image Widget
            self.qr_image.source = self.temp_img_path
            self.qr_image.reload()
            self.status_label.text = "QR Code Generated!"
        except Exception as e:
            self.status_label.text = f"Error: {str(e)}"

    def save_qr(self, instance):
        if not hasattr(self, 'temp_img_path') or not os.path.exists(self.temp_img_path):
            self.status_label.text = "Generate a QR code first!"
            return

        try:
            if platform == 'android':
                from android.storage import primary_external_storage_path
                from shutil import copyfile
                
                # Define path: usually /storage/emulated/0/DCIM/ or Pictures
                dir_path = os.path.join(primary_external_storage_path(), 'DCIM', 'DhanvanthQRCode')
                if not os.path.exists(dir_path):
                    os.makedirs(dir_path)
                
                filename = f"QR_{len(os.listdir(dir_path)) + 1}.png"
                dest_path = os.path.join(dir_path, filename)
                
                copyfile(self.temp_img_path, dest_path)
                self.status_label.text = f"Saved to {dest_path}"
                
                # Optionally scan media so it shows up in Gallery immediately
                # (Requires jnius usually, keeping it simple for now)
            else:
                # Desktop Save
                import shutil
                dest_path = os.path.join(os.getcwd(), f"Saved_QR_{len(os.listdir(os.getcwd()))}.png")
                shutil.copy(self.temp_img_path, dest_path)
                self.status_label.text = f"Saved to {os.path.basename(dest_path)}"
                
        except Exception as e:
            self.status_label.text = f"Save failed: {str(e)}"

if __name__ == '__main__':
    QRCodeApp().run()
