from kivy.app import App
from kivy.lang import Builder
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.floatlayout import FloatLayout
from kivy.uix.anchorlayout import AnchorLayout
from kivy.uix.image import Image
from kivy.uix.textinput import TextInput
from kivy.uix.button import Button
from kivy.uix.label import Label
from kivy.uix.widget import Widget
from kivy.core.window import Window
from kivy.utils import get_color_from_hex
from kivy.graphics import Color, Ellipse, Rectangle, Line, RoundedRectangle
from kivy.clock import Clock
from kivy.animation import Animation
from kivy.metrics import dp
from kivy.properties import ListProperty, StringProperty, NumericProperty
import qrcode
import os
import random
from kivy.utils import platform

# Set a mobile-friendly size for desktop testing
if platform not in ('android', 'ios'):
    Window.size = (400, 800)

# --- THEMES ---
THEMES = {
    'CYBER_BLUE': {
        'bg_top': '#050510', 'bg_bot': '#0f172a',
        'accent': '#00f0ff', 'glow': '#00f0ff',
        'input_bg': '#1e1b4b', 'fg': '#ffffff'
    },
    'NEON_PINK': {
        'bg_top': '#1a0510', 'bg_bot': '#2a0f1b',
        'accent': '#d946ef', 'glow': '#d946ef',
        'input_bg': '#380e28', 'fg': '#ffffff'
    },
    'TOXIC_GREEN': {
        'bg_top': '#051a05', 'bg_bot': '#0f2a0f',
        'accent': '#39ff14', 'glow': '#39ff14',
        'input_bg': '#0e280e', 'fg': '#ffffff'
    },
    'GOLD_MATRIX': {
        'bg_top': '#000000', 'bg_bot': '#0a0a0a',
        'accent': '#ffd700', 'glow': '#ffd700',
        'input_bg': '#1c1c1c', 'fg': '#ffffff'
    }
}

class ParticleWidget(Widget):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.particles = []
        Clock.schedule_interval(self.update_particles, 1.0 / 60.0)

    def update_particles(self, dt):
        with self.canvas:
            self.canvas.clear()
            # Draw bg
            Color(rgba=get_color_from_hex('#00000000')) # Transparent base
            
            # Spawn logic
            if len(self.particles) < 30:
                self.particles.append({
                    'x': random.randint(0, int(self.width or 400)),
                    'y': random.randint(0, int(self.height or 800)),
                    'vy': random.uniform(0.5, 2.0),
                    'size': random.randint(2, 5),
                    'alpha': random.uniform(0.1, 0.5)
                })

            for p in self.particles:
                p['y'] += p['vy']
                if p['y'] > self.height:
                    p['y'] = 0
                    p['x'] = random.randint(0, int(self.width))
                
                # Draw
                Color(0.5, 0.8, 1, p['alpha'])
                Ellipse(pos=(p['x'], p['y']), size=(p['size'], p['size']))

class ScanningLaser(Widget):
    laser_y = NumericProperty(0)
    
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.opacity = 0
    
    def scan(self, target_widget):
        self.opacity = 1
        self.width = target_widget.width
        self.x = target_widget.x
        
        anim = Animation(y=target_widget.top, duration=0) + \
               Animation(y=target_widget.y, duration=0.8) + \
               Animation(y=target_widget.top, duration=0.8) + \
               Animation(opacity=0, duration=0.2)
        anim.start(self)

KV = """
#:import get_color_from_hex kivy.utils.get_color_from_hex

<ParticleWidget>:
    canvas:
        # Drawn in python

<ScanningLaser>:
    canvas:
        Color:
            rgba: 0, 1, 1, 0.8 # Cyan Laser
        Line:
            points: [self.x, self.y, self.x + self.width, self.y]
            width: 2
        # Glow
        Color:
            rgba: 0, 1, 1, 0.3
        Rectangle:
            pos: self.x, self.y - 10
            size: self.width, 20


<MainScreen>:
    bg_color: '#050510'
    accent_color: '#00f0ff'
    
    canvas.before:
        Color:
            rgba: get_color_from_hex(self.bg_color)
        Rectangle:
            pos: self.pos
            size: self.size
            
    ParticleWidget:
        id: particles
        size_hint: 1, 1

    BoxLayout:
        orientation: 'vertical'
        padding: 30
        spacing: 20
        
        # --- Theme Switcher Row ---
        BoxLayout:
            size_hint_y: None
            height: 40
            spacing: 10
            Widget: # Spacer
            Button:
                text: "THEME"
                size_hint_x: None
                width: 100
                background_color: 0,0,0,0
                color: get_color_from_hex(root.accent_color)
                on_release: root.cycle_theme()
                canvas.before:
                    Color:
                        rgba: get_color_from_hex(root.accent_color)
                    Line:
                        rounded_rectangle: (self.x, self.y, self.width, self.height, 10)
                        width: 1
        
        Label:
            text: "Dhanvanth QR Code"
            font_size: '32sp'
            bold: True
            color: get_color_from_hex(root.accent_color)
            size_hint_y: None
            height: 60
            canvas.before:
                Color:
                    rgba: get_color_from_hex(root.accent_color)
                Line:
                    points: [self.center_x - 30, self.y, self.center_x + 30, self.y]
                    width: 2

        TextInput:
            id: input_text
            hint_text: "Enter Text or URL...."
            size_hint_y: 0.2
            font_size: '18sp'
            background_color: 0,0,0,0
            foreground_color: 1,1,1,1
            cursor_color: get_color_from_hex(root.accent_color)
            multiline: False
            padding: [15, 15]
            canvas.before:
                Color:
                    rgba: get_color_from_hex('#1e1b4b')
                RoundedRectangle:
                    pos: self.pos
                    size: self.size
                    radius: [15]
                Color:
                    rgba: get_color_from_hex(root.accent_color)
                Line:
                    rounded_rectangle: (self.x, self.y, self.width, self.height, 15)
                    width: 1

        Button:
            text: "INITIALIZE"
            size_hint_y: None
            height: 70
            font_size: '20sp'
            bold: True
            color: 0, 0, 0, 1
            background_color: 0,0,0,0
            on_release: root.generate_qr()
            canvas.before:
                Color:
                    rgba: get_color_from_hex(root.accent_color)
                RoundedRectangle:
                    pos: self.pos
                    size: self.size
                    radius: [10]
                Color: 
                    rgba: 1, 1, 1, 0.2
                RoundedRectangle:
                    pos: self.x, self.y + self.height/2
                    size: self.width, self.height/2
                    radius: [10, 10, 0, 0]

        FloatLayout:
            id: qr_area
            size_hint_y: 0.4
            
            Image:
                id: qr_image
                source: ''
                opacity: 0
                allow_stretch: True
                size_hint: None, None
                size: 250, 250
                pos_hint: {'center_x': 0.5, 'center_y': 0.5}

            ScanningLaser:
                id: laser
                size_hint: None, None
                height: 2
                opacity: 0

        Button:
            id: save_btn
            text: "DOWNLOAD"
            size_hint_y: None
            height: 0
            opacity: 0
            disabled: True
            background_color: 0,0,0,0
            color: get_color_from_hex('#ffffff')
            on_release: root.save_qr()
            canvas.before:
                Color:
                    rgba: get_color_from_hex('#10b981')
                RoundedRectangle:
                    pos: self.pos
                    size: self.size
                    radius: [30]
"""

class MainScreen(FloatLayout):
    bg_color = StringProperty('#050510')
    accent_color = StringProperty('#00f0ff')
    current_theme_idx = 0
    theme_names = list(THEMES.keys())

    def cycle_theme(self):
        self.current_theme_idx = (self.current_theme_idx + 1) % len(self.theme_names)
        t_name = self.theme_names[self.current_theme_idx]
        theme = THEMES[t_name]
        
        self.bg_color = theme['bg_top']
        self.accent_color = theme['accent']
        
        # Animate change?
        # For now direct property update triggers redraw

    def generate_qr(self):
        text = self.ids.input_text.text.strip()
        if not text:
            # Shake effect
            anim = Animation(x=self.ids.input_text.x+10, duration=0.05) + Animation(x=self.ids.input_text.x, duration=0.05)
            anim.start(self.ids.input_text)
            return

        try:
            # Generate logic (same as before)
            qr = qrcode.QRCode(version=1, box_size=10, border=1)
            qr.add_data(text)
            qr.make(fit=True)
            
            # Use current theme accent for QR? Or stick to standard
            # Let's use Theme Accent for QR Fill!
            fill_c = self.accent_color
            if fill_c == '#00f0ff': fill_c = '#00a8b3' # Darker version for contrast? No, QR needs contrast.
            # Best contrast is White background, Dark fill. 
            # OR Dark background, Light fill.
            # Let's do: Fill = Accent, Back = BG
            
            # Actually, standard scanners scan dark on light best.
            # Let's do Dark Purple fill on White again for safety, standard looks Pro.
            img = qr.make_image(fill_color="#101010", back_color="white").convert('RGBA')

            # --- Icon Logic (Rounded) ---
            try:
                if os.path.exists('icon.png'):
                    from PIL import Image as PilImage, ImageDraw
                    logo = PilImage.open('icon.png').convert("RGBA")
                    basewidth = int(img.size[0] * 0.22)
                    wpercent = (basewidth / float(logo.size[0]))
                    hsize = int((float(logo.size[1]) * float(wpercent)))
                    logo = logo.resize((basewidth, hsize), PilImage.Resampling.LANCZOS)
                    
                    mask = PilImage.new('L', logo.size, 0)
                    draw = ImageDraw.Draw(mask)
                    radius = int(min(logo.size) * 0.3) 
                    draw.rounded_rectangle([(0, 0), logo.size], radius=radius, fill=255)
                    
                    rounded_logo = PilImage.new('RGBA', logo.size, (0, 0, 0, 0))
                    rounded_logo.paste(logo, (0, 0), mask=mask)
                    
                    pos_x = (img.size[0] - logo.size[0]) // 2
                    pos_y = (img.size[1] - logo.size[1]) // 2
                    img.paste(rounded_logo, (pos_x, pos_y), rounded_logo)
            except Exception as e:
                print(e)
            
            self.temp_path = os.path.abspath("temp_qr.png")
            img.save(self.temp_path)
            
            # Reveal Animation
            qr_img = self.ids.qr_image
            qr_img.source = self.temp_path
            qr_img.reload()
            
            # Reset state for anim
            qr_img.opacity = 0
            qr_img.size_hint = (None, None)
            qr_img.size = (0, 0)
            
            # Pop up
            anim = Animation(size=(250, 250), opacity=1, duration=0.6, t='out_back')
            anim.start(qr_img)
            
            # Laser Scan
            self.ids.laser.scan(qr_img)
            
            # Show Save
            save = self.ids.save_btn
            if save.height == 0:
                anim_s = Animation(height=60, opacity=1, duration=0.5)
                anim_s.start(save)
                save.disabled = False

        except Exception as e:
            print(e)

    def save_qr(self):
        try:
            if platform == 'android':
                from android.storage import primary_external_storage_path
                from shutil import copyfile
                dir_path = os.path.join(primary_external_storage_path(), 'DCIM', 'NeonQR')
                if not os.path.exists(dir_path): os.makedirs(dir_path)
                filename = f"QR_{len(os.listdir(dir_path)) + 1}.png"
                copyfile(self.temp_path, os.path.join(dir_path, filename))
            else:
                import shutil
                shutil.copy(self.temp_path, f"Saved_QR_{random.randint(100,999)}.png")
            
            self.ids.save_btn.text = "SAVED!"
            Clock.schedule_once(lambda dt: setattr(self.ids.save_btn, 'text', "DOWNLOAD"), 2)
        except Exception as e:
            self.ids.save_btn.text = "ERROR"

class QRCodeApp(App):
    def build(self):
        self.icon = 'icon.png'
        Builder.load_string(KV)
        return MainScreen()

if __name__ == '__main__':
    QRCodeApp().run()
