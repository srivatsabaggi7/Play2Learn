from kivy.uix.screenmanager import Screen
from kivy.uix.slider import Slider
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.label import Label
from kivy.uix.button import Button

class BudgetGameScreen(Screen):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.budget = 1000
        self.score = 0
        self.sliders = {}
        self.categories = ['Food', 'Transport', 'Entertainment', 'Savings']
        self.bind(on_enter=self.setup_ui)

    def setup_ui(self, *args):
        slider_box = BoxLayout(orientation="vertical", spacing=10)
        slider_box.clear_widgets()
        self.sliders.clear()

        # Create sliders for each category
        for category in self.categories:
            row = BoxLayout(orientation='horizontal', spacing=10, size_hint_y=None, height=50)
            
            label = Label(text=category, size_hint_x=0.4, color=(1, 1, 1, 1), font_size=20)
            slider = Slider(min=0, max=self.budget, step=50, size_hint_x=0.6)
            
            self.sliders[category] = slider
            row.add_widget(label)
            row.add_widget(slider)

            slider_box.add_widget(row)

        # Add back and score display row if not present
        if not self.ids.get('extra_controls'):
            footer = BoxLayout(size_hint_y=None, height=50, spacing=20, id='extra_controls')

            back_btn = Button(text="🔙 Home", size_hint_x=0.3, background_color=(0.6, 0.6, 0.9, 1))
            back_btn.bind(on_press=self.go_home)

            self.score_label = Label(text=f"Score: {self.score}", color=(1, 1, 1, 1), font_size=18)

            footer.add_widget(back_btn)
            footer.add_widget(self.score_label)

            self.ids.slider_box.parent.add_widget(footer)

    def check_total(self):
        total = sum(slider.value for slider in self.sliders.values())
        result_label = self.ids.result_label

        if total > self.budget:
            result_label.text = f"⚠️ Over budget by ₹{int(total - self.budget)}"
            result_label.color = (1, 0.4, 0.4, 1)
        elif total < self.budget:
            result_label.text = f"🪙 ₹{int(self.budget - total)} left unallocated"
            result_label.color = (1, 1, 0.5, 1)
        else:
            result_label.text = "✅ Perfect! You've used your full budget."
            result_label.color = (0.4, 1, 0.6, 1)
            self.score += 10
            if hasattr(self, 'score_label'):
                self.score_label.text = f"Score: {self.score}"
    def go_home(self, instance):
        self.manager.current = "home"