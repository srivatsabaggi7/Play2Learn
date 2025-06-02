from kivy.uix.screenmanager import Screen
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.button import Button
from kivy.uix.label import Label

class SituationGameScreen(Screen):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.score = 0
        self.scenarios = [
            {
                "situation": "Your friend asks you to lie for them at school. What do you do?",
                "options": [
                    "Lie to help your friend.",
                    "Explain that you’re uncomfortable lying.",
                    "Ignore the situation."
                ],
                "correct": 1
            },
            {
                "situation": "You find a wallet on the street. What do you do?",
                "options": [
                    "Take the cash and leave the wallet.",
                    "Turn it in to the police.",
                    "Ignore it and walk away."
                ],
                "correct": 1
            },
            {
                "situation": "Someone is being bullied in class. What do you do?",
                "options": [
                    "Stand up to the bully respectfully.",
                    "Join in with the bully.",
                    "Do nothing to stay safe."
                ],
                "correct": 0
            }
        ]
        self.current_index = 0
        self.bind(on_enter=self.load_scenario)

    def load_scenario(self, *args):
        box = self.ids.situation_box
        box.clear_widgets()

        if self.current_index >= len(self.scenarios):
            box.add_widget(Label(text="🎉 You've completed all scenarios!", color=(0.6, 1, 0.6, 1), font_size=22))
            self.ids.score_label.text = f"Score: {self.score}"
            return

        scenario = self.scenarios[self.current_index]

        box.add_widget(Label(text=scenario["situation"], font_size=22, color=(1, 1, 1, 1), size_hint_y=None, height=80))

        for idx, option in enumerate(scenario["options"]):
            btn = Button(text=option,
                         size_hint_y=None,
                         height=50,
                         background_color=(0.3, 0.5, 0.8, 1))
            btn.bind(on_press=lambda btn, i=idx: self.check_answer(i))
            box.add_widget(btn)

        # Back + Score Display
        if not self.ids.get('footer_controls'):
            footer = BoxLayout(size_hint_y=None, height=50, spacing=20, id='footer_controls')

            back_btn = Button(text="🔙 Home", size_hint_x=0.3, background_color=(0.6, 0.6, 0.9, 1))
            back_btn.bind(on_press=self.go_home)

            self.score_label = Label(text=f"Score: {self.score}", color=(1, 1, 1, 1), font_size=18)

            footer.add_widget(back_btn)
            footer.add_widget(self.score_label)
            self.ids.situation_box.parent.add_widget(footer)

    def check_answer(self, selected_index):
        correct = self.scenarios[self.current_index]['correct']
        result_label = self.ids.result_label

        if selected_index == correct:
            result_label.text = "✅ Correct choice!"
            result_label.color = (0.4, 1, 0.6, 1)
            self.score += 10
        else:
            result_label.text = "❌ That might not be the best decision."
            result_label.color = (1, 0.4, 0.4, 1)

        if hasattr(self, 'score_label'):
            self.score_label.text = f"Score: {self.score}"

        self.current_index += 1
        self.load_scenario()
    def go_home(self, instance):
        self.manager.current = "home"