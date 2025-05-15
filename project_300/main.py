from kivy.lang import Builder
from kivy.uix.screenmanager import ScreenManager, Screen, SlideTransition
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.gridlayout import GridLayout
from kivy.uix.textinput import TextInput
from kivy.uix.slider import Slider
from kivy.uix.image import Image
from kivy.uix.label import Label
from kivy.uix.button import Button
from kivy.properties import StringProperty, ListProperty, NumericProperty
from kivy.app import App
from kivy.core.window import Window
from kivy.uix.widget import Widget
from kivy.uix.behaviors import ButtonBehavior
from kivy.uix.floatlayout import FloatLayout
from kivy.animation import Animation
import json
import os
from kivy.utils import get_color_from_hex

# Define custom colors
COLORS = {
    'background': (0.6, 0.3, 0.1, 1),  # Brownish-orange
    'text': (1, 1, 1, 1),              # White
    'input_bg': (0.3, 0.15, 0.05, 1), # Darker brown for input backgrounds
    'slider': (1, 0.6, 0.2, 1),       # Orange
    'star': (1, 0.8, 0, 1),           # Gold
    'indicator': (1, 1, 1, 0.5),      # Semi-transparent white
    'indicator_active': (1, 1, 1, 1), # Solid white
}

Window.clearcolor = COLORS['background']

STAR_PATH = 'star.png'  # Placeholder, add a star image in the folder

class StarWidget(Image):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.source = STAR_PATH
        self.size_hint = (None, None)
        self.size = (32, 32)
        self.color = COLORS['star']

class LevelStepper(BoxLayout):
    value = NumericProperty(0)
    def __init__(self, on_value, **kwargs):
        super().__init__(orientation='horizontal', **kwargs)
        self.on_value = on_value
        self.dec_button = Button(text='-', size_hint_x=None, width=40, background_color=COLORS['slider'])
        self.dec_button.bind(on_press=self.decrement)
        self.value_input = TextInput(text=str(self.value), size_hint_x=None, width=40, multiline=False, input_filter='int', background_color=COLORS['input_bg'], foreground_color=COLORS['text'], font_size=18, padding=[5,5,5,5], cursor_color=COLORS['text'])
        self.value_input.bind(text=self.on_text_change)
        self.inc_button = Button(text='+', size_hint_x=None, width=40, background_color=COLORS['slider'])
        self.inc_button.bind(on_press=self.increment)
        self.star = StarWidget()
        self.star.opacity = 0
        self.add_widget(self.dec_button)
        self.add_widget(self.value_input)
        self.add_widget(self.inc_button)
        self.add_widget(self.star)
    def decrement(self, instance):
        if self.value > 0:
            self.value -= 1
            self.update_display()
    def increment(self, instance):
        if self.value < 100:
            self.value += 1
            self.update_display()
    def on_text_change(self, instance, value):
        try:
            val = int(value)
            if 0 <= val <= 100:
                self.value = val
                self.update_display()
        except ValueError:
            pass
    def update_display(self):
        self.value_input.text = str(self.value)
        self.star.opacity = 1 if self.value >= 100 else 0
        if self.on_value:
            self.on_value(self.value)

# Remove TaskRow as a GridLayout, make it a simple data class
class TaskRow:
    def __init__(self, row_idx, on_complete):
        self.row_idx = row_idx
        self.on_complete = on_complete
        self.task_input = TextInput(hint_text='Task/Skill', multiline=False)
        self.task_input.foreground_color = COLORS['text']
        self.levels = []
        self.stars = [0, 0, 0]
        for i in range(3):
            stepper = LevelStepper(self.make_level_callback(i))
            self.levels.append(stepper)
    def make_level_callback(self, idx):
        def callback(value):
            self.stars[idx] = 1 if value >= 100 else 0
            if sum(self.stars) == 3:
                self.animate_completion()
        return callback
    def animate_completion(self):
        # Animate all widgets in the row
        anims = []
        widgets = [self.task_input] + self.levels
        for w in widgets:
            anim = Animation(opacity=0, duration=0.5)
            anim.start(w)
            anims.append(anim)
        Animation(opacity=0, duration=0.5).bind(on_complete=lambda *x: self.on_complete(self.row_idx)).start(self.task_input)
    def clear_row(self):
        self.task_input.text = ''
        for stepper in self.levels:
            stepper.value = 0
            stepper.star.opacity = 0
            stepper.opacity = 1
        self.stars = [0, 0, 0]
        self.task_input.opacity = 1
    def get_data(self):
        return {
            'task': self.task_input.text,
            'levels': [stepper.value for stepper in self.levels]
        }
    def set_data(self, data):
        self.task_input.text = data.get('task', '')
        for i, val in enumerate(data.get('levels', [0,0,0])):
            self.levels[i].value = val
            self.levels[i].update_display()

class PageIndicator(BoxLayout):
    def __init__(self, total, current, **kwargs):
        super().__init__(orientation='horizontal', size_hint_y=None, height=24, spacing=8, **kwargs)
        for i in range(total):
            dot = Label(text='●', font_size=20, color=COLORS['indicator_active'] if i == current else COLORS['indicator'])
            self.add_widget(dot)

class PageScreen(Screen):
    def __init__(self, page_title, page_index=0, total_pages=3, **kwargs):
        super().__init__(**kwargs)
        self.page_title = page_title
        self.page_index = page_index
        self.total_pages = total_pages
        self.layout = BoxLayout(orientation='vertical', padding=[20, 20, 20, 20], spacing=16)
        self.heading = Label(text='Project 300', font_size=36, bold=True, size_hint_y=None, height=60, color=COLORS['text'])
        self.layout.add_widget(self.heading)
        self.indicator = PageIndicator(total_pages, page_index)
        self.layout.add_widget(self.indicator)
        self.title_input = TextInput(text=page_title, font_size=22, size_hint_y=None, height=44, multiline=False,
                                     foreground_color=COLORS['text'], background_color=COLORS['input_bg'], padding=[10,10,10,10], cursor_color=COLORS['text'])
        self.layout.add_widget(self.title_input)
        self.grid = GridLayout(cols=4, rows=4, spacing=8, size_hint_y=None, row_default_height=56)
        self.grid.bind(minimum_height=self.grid.setter('height'))
        self.grid.add_widget(Label(text='', size_hint_x=None, width=120, color=COLORS['text'], font_size=18, bold=True))
        for i in range(3):
            self.grid.add_widget(Label(text=f'Level {i+1}', size_hint_x=None, width=120, color=COLORS['text'], font_size=18, bold=True))
        self.rows = []
        for i in range(3):
            row = TaskRow(i, self.complete_row)
            self.rows.append(row)
            row.task_input.font_size = 18
            row.task_input.background_color = COLORS['input_bg']
            row.task_input.foreground_color = COLORS['text']
            row.task_input.padding = [10,10,10,10]
            row.task_input.cursor_color = COLORS['text']
            self.grid.add_widget(row.task_input)
            for stepper in row.levels:
                stepper.dec_button.background_color = COLORS['slider']
                stepper.inc_button.background_color = COLORS['slider']
                stepper.value_input.color = COLORS['text']
                stepper.value_input.font_size = 18
                self.grid.add_widget(stepper)
        self.layout.add_widget(self.grid)
        self.add_widget(self.layout)
        self.load_data()
    def complete_row(self, idx):
        self.rows[idx].clear_row()
        for i in range(idx+1, len(self.rows)):
            data = self.rows[i].get_data()
            self.rows[i-1].set_data(data)
        self.rows[-1].clear_row()
        self.save_data()
    def save_data(self):
        data = {
            'title': self.title_input.text,
            'rows': [row.get_data() for row in self.rows]
        }
        filename = f'page_{self.name}.json'
        with open(filename, 'w') as f:
            json.dump(data, f)
    def load_data(self):
        filename = f'page_{self.name}.json'
        if os.path.exists(filename):
            with open(filename, 'r') as f:
                data = json.load(f)
                self.title_input.text = data.get('title', self.page_title)
                for i, row_data in enumerate(data.get('rows', [])):
                    if i < len(self.rows):
                        self.rows[i].set_data(row_data)
    def update_indicator(self, current):
        self.layout.remove_widget(self.indicator)
        self.indicator = PageIndicator(self.total_pages, current)
        self.layout.add_widget(self.indicator, index=1)

class Project300App(App):
    def build(self):
        self.sm = ScreenManager(transition=SlideTransition())
        self.pages = []
        for i in range(3):
            page = PageScreen(f'Page {i+1}', page_index=i, total_pages=3, name=f'page_{i+1}')
            self.pages.append(page)
            self.sm.add_widget(page)
        Window.bind(on_keyboard=self.on_key)
        self._touch_start_x = None
        return self.sm
    def on_key(self, window, key, *args):
        idx = self.sm.screen_names.index(self.sm.current)
        if key == 276:  # left
            self.sm.transition.direction = 'right'
            self.sm.current = self.sm.previous()
            idx = max(0, idx-1)
        elif key == 275:  # right
            self.sm.transition.direction = 'left'
            self.sm.current = self.sm.next()
            idx = min(len(self.pages)-1, idx+1)
        self.pages[idx].update_indicator(idx)
    def on_start(self):
        Window.bind(on_touch_down=self.on_touch_down)
        Window.bind(on_touch_up=self.on_touch_up)
    def on_touch_down(self, window, touch):
        self._touch_start_x = touch.x
    def on_touch_up(self, window, touch):
        if self._touch_start_x is None:
            return
        dx = touch.x - self._touch_start_x
        idx = self.sm.screen_names.index(self.sm.current)
        if abs(dx) > 50:  # threshold for swipe
            if dx < 0:
                self.sm.transition.direction = 'left'
                self.sm.current = self.sm.next()
                idx = min(len(self.pages)-1, idx+1)
            else:
                self.sm.transition.direction = 'right'
                self.sm.current = self.sm.previous()
                idx = max(0, idx-1)
        self.pages[idx].update_indicator(idx)
        self._touch_start_x = None

if __name__ == '__main__':
    Project300App().run() 