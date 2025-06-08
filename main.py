from kivy.app import App
from kivy.uix.screenmanager import ScreenManager, Screen
from kivy.properties import NumericProperty, StringProperty, ListProperty, ObjectProperty
from kivy.clock import Clock
import sqlite3
from datetime import datetime

# --- Database functions --- #
def init_db():
    conn = sqlite3.connect("users.db")
    c = conn.cursor()
    c.execute('''CREATE TABLE IF NOT EXISTS users (username TEXT PRIMARY KEY, password TEXT)''')
    c.execute('''
        CREATE TABLE IF NOT EXISTS scores (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT,
            game TEXT,
            score INTEGER,
            date TEXT
        )
    ''')
    conn.commit()
    conn.close()

def register_user(username, password):
    try:
        conn = sqlite3.connect("users.db")
        c = conn.cursor()
        c.execute("INSERT INTO users VALUES (?, ?)", (username, password))
        conn.commit()
        return True
    except sqlite3.IntegrityError:
        return False
    finally:
        conn.close()

def validate_login(username, password):
    conn = sqlite3.connect("users.db")
    c = conn.cursor()
    c.execute("SELECT * FROM users WHERE username=? AND password=?", (username, password))
    result = c.fetchone()
    conn.close()
    return result is not None

def save_score(username, game, score):
    conn = sqlite3.connect("users.db")
    c = conn.cursor()
    date = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    c.execute("INSERT INTO scores (username, game, score, date) VALUES (?, ?, ?, ?)", (username, game, score, date))
    conn.commit()
    conn.close()

def get_scores(username):
    conn = sqlite3.connect("users.db")
    c = conn.cursor()
    c.execute("SELECT game, score, date FROM scores WHERE username=? ORDER BY date DESC LIMIT 10", (username,))
    results = c.fetchall()
    conn.close()
    return results


# --- Screens --- #
class LoginScreen(Screen):
    def login(self, username, password):
        if not username or not password:
            self.ids.login_status.text = "Please enter username and password"
            return
        if validate_login(username, password):
            self.manager.get_screen('menu').current_user = username
            self.manager.current = 'menu'
            self.ids.login_status.text = ''
        else:
            self.ids.login_status.text = "Invalid credentials"

    def go_to_register(self):
        self.manager.current = 'register'


class RegisterScreen(Screen):
    def register(self, username, password):
        if not username or not password:
            self.ids.register_status.text = "Please enter username and password"
            return
        if register_user(username, password):
            self.manager.current = 'login'
            self.ids.register_status.text = ''
        else:
            self.ids.register_status.text = "User already exists"

    def go_to_login(self):
        self.manager.current = 'login'


class MenuScreen(Screen):
    current_user = StringProperty('')

    def on_pre_enter(self):
        self.ids.welcome_label.text = f"Welcome, {self.current_user}"
        self.load_scores()

    def load_scores(self):
        self.ids.scores_box.clear_widgets()
        scores = get_scores(self.current_user)
        if not scores:
            from kivy.uix.label import Label
            self.ids.scores_box.add_widget(Label(text="No scores yet. Play games to see your results!", size_hint_y=None, height=30, color=(0.1, 0.6, 0.4, 1)))
        else:
            from kivy.uix.label import Label
            for game, score, date in scores:
                label = Label(text=f"{date[:16]} - {game}: {score}", size_hint_y=None, height=30, color=(0.1, 0.6, 0.4, 1))
                self.ids.scores_box.add_widget(label)


class BudgetGame(Screen):
    rent = NumericProperty(0)
    food = NumericProperty(0)
    fun = NumericProperty(0)
    feedback = StringProperty("")
    total_budget = NumericProperty(100)  # fixed budget

    def update_rent(self, value):
        self.rent = int(value)
        self.feedback = ""

    def update_food(self, value):
        self.food = int(value)
        self.feedback = ""

    def update_fun(self, value):
        self.fun = int(value)
        self.feedback = ""

    def calculate_budget(self):
        total = self.rent + self.food + self.fun
        if total > self.total_budget:
            self.feedback = f"Budget exceeded by {total - self.total_budget}! You lose."
        else:
            self.feedback = f"Good job! You stayed within the budget. Total spent: {total}"
    def reset(self):
        self.rent = 0
        self.food = 0
        self.fun = 0
        self.feedback = ""


class SituationGame(Screen):
    scenarios = ListProperty()
    current_index = NumericProperty(0)
    feedback = StringProperty('')
    score = NumericProperty(0)
    answered = False
    score_saved = False

    def on_enter(self):
        # Initialize quiz scenarios: question and dict of options with correctness
        self.scenarios = [
            ("You found a lost wallet. What do you do?", 
                {"Keep it": False, "Report it": True, "Ignore it": False}),
            ("Your friend is being bullied. You should?", 
                {"Join in": False, "Support your friend": True, "Walk away": False}),
            ("You see someone drop money on the street. You:", 
                {"Pick it up and keep": False, "Give it back": True, "Ignore": False}),
        ]
        self.reset_quiz()

    def reset_quiz(self):
        self.current_index = 0
        self.score = 0
        self.answered = False
        self.score_saved = False
        self.feedback = ''
        self.ids.next_btn.disabled = True
        self.load_question()

    def load_question(self):
        question, options = self.scenarios[self.current_index]
        self.ids.question_label.text = question

        buttons = [self.ids.opt1, self.ids.opt2, self.ids.opt3]
        for btn, (option_text, _) in zip(buttons, options.items()):
            btn.text = option_text
            btn.disabled = False

        self.feedback = ''
        self.answered = False
        self.ids.next_btn.disabled = True

    def answer(self, choice_text):
        if self.answered:
            return

        self.answered = True
        question, options = self.scenarios[self.current_index]
        is_correct = options.get(choice_text, False)

        if is_correct:
            self.feedback = "Correct! Well done."
            self.score += 1
        else:
            self.feedback = "Oops, that's not right."

        for btn in [self.ids.opt1, self.ids.opt2, self.ids.opt3]:
            btn.disabled = True

        self.ids.next_btn.disabled = False

    def next_question(self):
        if not self.answered:
            self.feedback = "Please select an answer first."
            return

        self.current_index += 1

        if self.current_index >= len(self.scenarios):
            self.ids.question_label.text = f"Quiz Finished! Your score: {self.score} / {len(self.scenarios)}"
            for btn in [self.ids.opt1, self.ids.opt2, self.ids.opt3]:
                btn.text = ''
                btn.disabled = True

            self.feedback = ''
            self.ids.next_btn.disabled = True

            if not self.score_saved:
                user = self.manager.get_screen('menu').current_user
                save_score(user, "Situation Game", self.score)
                self.score_saved = True
        else:
            self.load_question()
            self.ids.next_btn.disabled = True
class Play2Learn(App):
    def build(self):
        init_db()
        sm = ScreenManager()
        sm.add_widget(LoginScreen(name='login'))
        sm.add_widget(RegisterScreen(name='register'))
        sm.add_widget(MenuScreen(name='menu'))
        sm.add_widget(BudgetGame(name='budget_game'))
        sm.add_widget(SituationGame(name='situation_game'))
        sm.current = 'login'
        return sm


if __name__ == '__main__':
    Play2Learn().run()
