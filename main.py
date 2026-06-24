from kivy.app import App
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.floatlayout import FloatLayout
from kivy.uix.gridlayout import GridLayout
from kivy.uix.label import Label
from kivy.uix.button import Button
from kivy.uix.textinput import TextInput
from kivy.uix.scrollview import ScrollView
from kivy.uix.slider import Slider
from kivy.uix.image import Image
from kivy.storage.jsonstore import JsonStore
from kivy.core.window import Window
from kivy.graphics import Color, Rectangle, Line, Ellipse
from kivy.uix.screenmanager import ScreenManager, Screen, FadeTransition
from kivy.utils import platform, get_color_from_hex
from datetime import datetime
import os

# Hintergrundfarbe des Fensters
Window.clearcolor = (0.1, 0.1, 0.1, 1)

# Skalierung NUR für den PC - Auf Android wird automatisch Fullscreen genutzt!
if platform not in ('android', 'ios'):
    Window.size = (540, 1170)


class GreenBoxRow(BoxLayout):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.orientation = 'vertical'
        with self.canvas.before:
            Color(0.15, 0.55, 0.25, 1)
            self.rect = Rectangle(size=self.size, pos=self.pos)
        self.bind(size=self._update_rect, pos=self._update_rect)

        self.lbl_prefix = Label(
            text="Heute:", font_size='22sp', bold=True, size_hint=(1, 0.4),
            halign='center', valign='bottom'
        )
        self.lbl_activity = Label(
            text="", font_size='34sp', bold=True, size_hint=(1, 0.6),
            halign='center', valign='top', markup=True
        )
        self.lbl_prefix.bind(size=lambda l, s: setattr(l, 'text_size', s))
        self.lbl_activity.bind(size=lambda l, s: setattr(l, 'text_size', s))

        self.add_widget(self.lbl_prefix)
        self.add_widget(self.lbl_activity)

    def _update_rect(self, instance, value):
        self.rect.size = instance.size
        self.rect.pos = instance.pos


class EvaluationGraph(BoxLayout):
    def __init__(self, store, **kwargs):
        super().__init__(**kwargs)
        self.store = store
        self.days_to_show = 30
        self.bind(pos=self.redraw, size=self.redraw)

    def set_days(self, days):
        self.days_to_show = days
        self.redraw()

    def redraw(self, *args):
        self.canvas.clear()
        with self.canvas:
            Color(0.13, 0.13, 0.13, 1)
            Rectangle(pos=self.pos, size=self.size)

            pad_x = 20
            pad_y = 20
            w = self.width - 2 * pad_x
            h = self.height - 2 * pad_y
            x0 = self.x + pad_x
            y0 = self.y + pad_y

            Color(0.3, 0.3, 0.3, 1)
            Line(rectangle=(x0, y0, w, h), width=1)

            Color(0.2, 0.2, 0.2, 1)
            for i in range(1, 10):
                if i != 5:
                    Line(points=[x0, y0 + (i / 10) * h, x0 + w, y0 + (i / 10) * h], width=1)

            Color(0.4, 0.4, 0.4, 1)
            Line(points=[x0, y0 + h / 2, x0 + w, y0 + h / 2], width=1.5)

            now = datetime.now()
            wb_data = self.store.get('wellbeing')['history'] if self.store.exists('wellbeing') else []
            stress_data = self.store.get('stress')['history'] if self.store.exists('stress') else []
            cold_data = self.store.get('cold')['history'] if self.store.exists('cold') else []
            med_data = self.store.get('meditation')['history'] if self.store.exists('meditation') else []

            def calculate_coordinates(data, is_habit=False, habit_y_fixed=0):
                points = []
                for entry in data:
                    try:
                        dt = datetime.strptime(entry['date'], "%d.%m.%Y - %H:%M")
                    except ValueError:
                        continue
                    days_ago = (now - dt).days + (now - dt).seconds / 86400.0
                    if days_ago <= self.days_to_show:
                        x_pct = (self.days_to_show - days_ago) / self.days_to_show
                        x = x0 + x_pct * w
                        if is_habit:
                            if entry.get('status') == 1:
                                y_pct = (habit_y_fixed + 5) / 10
                                y = y0 + y_pct * h
                                points.append((x, y))
                        else:
                            val = entry.get('score', 0)
                            y_pct = (val + 5) / 10
                            y = y0 + y_pct * h
                            points.append((x, y))
                points.sort(key=lambda p: p[0])
                return points

            wb_pts = calculate_coordinates(wb_data)
            stress_pts = calculate_coordinates(stress_data)
            cold_pts = calculate_coordinates(cold_data, is_habit=True, habit_y_fixed=3.5)
            med_pts = calculate_coordinates(med_data, is_habit=True, habit_y_fixed=-3.5)

            if len(wb_pts) > 1:
                Color(0.2, 0.8, 0.2, 1)
                Line(points=[coord for pt in wb_pts for coord in pt], width=2.5)
                for pt in wb_pts: Ellipse(pos=(pt[0] - 3, pt[1] - 3), size=(6, 6))
            elif len(wb_pts) == 1:
                Color(0.2, 0.8, 0.2, 1)
                Ellipse(pos=(wb_pts[0][0] - 4, wb_pts[0][1] - 4), size=(8, 8))

            if len(stress_pts) > 1:
                Color(0.8, 0.2, 0.2, 1)
                Line(points=[coord for pt in stress_pts for coord in pt], width=2.5)
                for pt in stress_pts: Ellipse(pos=(pt[0] - 3, pt[1] - 3), size=(6, 6))
            elif len(stress_pts) == 1:
                Color(0.8, 0.2, 0.2, 1)
                Ellipse(pos=(stress_pts[0][0] - 4, stress_pts[0][1] - 4), size=(8, 8))

            Color(0.2, 0.7, 1, 1)
            for pt in cold_pts: Ellipse(pos=(pt[0] - 5, pt[1] - 5), size=(10, 10))
            Color(1, 0.8, 0.2, 1)
            for pt in med_pts: Ellipse(pos=(pt[0] - 5, pt[1] - 5), size=(10, 10))


class TrainingRotationApp(App):
    def build(self):
        self.store = JsonStore('training_state.json')
        self.cold_filter = 30
        self.med_filter = 30

        if self.store.exists('workout_list'):
            self.workouts = self.store.get('workout_list')['data']
        else:
            self.workouts = ["Dehnen/Cardio", "Kraftsport", "Dehnen/Cardio", "Bodyweight"]
            self.store.put('workout_list', data=self.workouts)

        if self.store.exists('state'):
            self.current_index = self.store.get('state')['index']
        else:
            self.current_index = 0

        self.root_layout = BoxLayout(orientation='vertical')
        self.sm = ScreenManager(transition=FadeTransition())

        # --- SCREEN REGISTRIERUNG ---
        self.screen_home = Screen(name="Home")
        self.screen_home.add_widget(self.create_home_layout())
        self.sm.add_widget(self.screen_home)

        self.screen_impressum = Screen(name="Impressum")
        self.screen_impressum.add_widget(self.create_impressum_layout())
        self.sm.add_widget(self.screen_impressum)

        self.screen_training = Screen(name="Training")
        self.screen_training.add_widget(self.create_training_layout())
        self.sm.add_widget(self.screen_training)

        self.screen_settings = Screen(name="TrainingSettings")
        self.screen_settings.add_widget(self.create_settings_layout())
        self.sm.add_widget(self.screen_settings)

        self.screen_wellbeing = Screen(name="Wohlbefinden")
        self.screen_wellbeing.add_widget(self.create_wellbeing_layout())
        self.sm.add_widget(self.screen_wellbeing)

        self.screen_stress = Screen(name="Stress")
        self.screen_stress.add_widget(self.create_stress_layout())
        self.sm.add_widget(self.screen_stress)

        self.screen_cold = Screen(name="Kälte")
        self.screen_cold.add_widget(self.create_cold_layout())
        self.sm.add_widget(self.screen_cold)

        self.screen_meditation = Screen(name="Meditation")
        self.screen_meditation.add_widget(self.create_meditation_layout())
        self.sm.add_widget(self.screen_meditation)

        self.screen_eval = Screen(name="Auswertung")
        self.screen_eval.add_widget(self.create_evaluation_layout())
        self.sm.add_widget(self.screen_eval)

        self.root_layout.add_widget(self.sm)
        return self.root_layout

    # ==========================================
    # GLOBALE HEADER-FUNKTION
    # ==========================================
    def create_header(self):
        # Header größer (28sp) und HGC in Petrol (#004C55)
        lbl = Label(
            text="[color=#004C55][b]H[/b][/color]olistic [color=#004C55][b]G[/b][/color]ame [color=#004C55][b]C[/b][/color]hanger",
            markup=True, font_size='28sp', size_hint=(1, 0.1), halign='center', valign='middle'
        )
        lbl.bind(size=lambda l, s: setattr(l, 'text_size', s))
        return lbl

    # ==========================================
    # LAYOUTGENERIERUNG
    # ==========================================

    def create_home_layout(self):
        layout = BoxLayout(orientation='vertical', padding=15, spacing=10)
        layout.add_widget(self.create_header())

        # Matrix (2/3 des Bildschirms)
        grid_container = BoxLayout(orientation='vertical', size_hint=(1, 0.66), padding=10)
        grid = GridLayout(cols=2, rows=3, spacing=15)
        tabs = ["Training", "Wohlbefinden", "Stress", "Kälte", "Meditation", "Auswertung"]
        for tab in tabs:
            btn = Button(text=tab, font_size='18sp', bold=True, background_color=(0.15, 0.55, 0.25, 1))
            btn.bind(on_press=self.switch_screen)
            grid.add_widget(btn)
        grid_container.add_widget(grid)
        layout.add_widget(grid_container)

        # Unterer Bereich (1/3 des Bildschirms)
        bottom_area = FloatLayout(size_hint=(1, 0.26))
        # Impressum Button mit Farbe #F4C542
        btn_impressum = Button(
            text="Impressum", font_size='14sp', size_hint=(None, None), size=(110, 45),
            pos_hint={'x': 0.05, 'center_y': 0.5}, background_color=(0.3, 0.3, 0.3, 1),
            color=get_color_from_hex('#F4C542'), bold=True
        )
        btn_impressum.bind(on_press=lambda x: self.switch_screen_name("Impressum"))
        bottom_area.add_widget(btn_impressum)
        layout.add_widget(bottom_area)

        return layout

    def create_impressum_layout(self):
        layout = BoxLayout(orientation='vertical', padding=20, spacing=15)
        layout.add_widget(self.create_header())

        # Titel im Text ebenfalls in #F4C542 eingefärbt
        content = Label(
            text="[color=#F4C542][b]Impressum[/b][/color]\n\n[Hier werden später deine rechtlichen Angaben eingefügt.]",
            halign='center', valign='middle', size_hint=(1, 0.72), markup=True)
        content.bind(size=content.setter('text_size'))
        layout.add_widget(content)

        btn_back = Button(text="ZURÜCK", font_size='18sp', size_hint=(1, 0.1), background_color=(0.2, 0.2, 0.2, 1),
                          bold=True)
        btn_back.bind(on_press=lambda x: self.switch_screen_name("Home"))
        layout.add_widget(btn_back)
        return layout

    def create_training_layout(self):
        layout = BoxLayout(orientation='vertical', padding=15, spacing=10)
        layout.add_widget(self.create_header())

        top_bar = BoxLayout(orientation='horizontal', size_hint=(1, 0.08))
        top_bar.add_widget(Label(size_hint_x=0.8))
        btn_settings = Button(text="...", font_size='25sp', bold=True, size_hint=(None, 1), width=60,
                              background_color=(0.45, 0.45, 0.45, 1))
        btn_settings.bind(on_press=self.open_settings)
        top_bar.add_widget(btn_settings)
        layout.add_widget(top_bar)

        display_box = BoxLayout(orientation='vertical', size_hint=(1, 0.52), spacing=10)
        self.row_prev = BoxLayout(orientation='vertical', size_hint=(1, 0.2))
        lbl_prev_pre = Label(text="Gestern:", font_size='16sp', color=(0.6, 0.6, 0.6, 1),
                             size_hint=(1, 0.4), halign='center', valign='bottom')
        lbl_prev_pre.bind(size=lambda l, s: setattr(l, 'text_size', s))
        self.lbl_prev_act = Label(markup=True, font_size='18sp', color=(0.6, 0.6, 0.6, 1),
                                  size_hint=(1, 0.6), halign='center', valign='top')
        self.lbl_prev_act.bind(size=lambda l, s: setattr(l, 'text_size', s))
        self.row_prev.add_widget(lbl_prev_pre);
        self.row_prev.add_widget(self.lbl_prev_act)

        self.row_curr = GreenBoxRow(size_hint=(1, 0.6))

        self.row_next = BoxLayout(orientation='vertical', size_hint=(1, 0.2))
        lbl_next_pre = Label(text="Morgen:", font_size='16sp', color=(0.6, 0.6, 0.6, 1),
                             size_hint=(1, 0.4), halign='center', valign='bottom')
        lbl_next_pre.bind(size=lambda l, s: setattr(l, 'text_size', s))
        self.lbl_next_act = Label(markup=True, font_size='18sp', color=(0.6, 0.6, 0.6, 1),
                                  size_hint=(1, 0.6), halign='center', valign='top')
        self.lbl_next_act.bind(size=lambda l, s: setattr(l, 'text_size', s))
        self.row_next.add_widget(lbl_next_pre);
        self.row_next.add_widget(self.lbl_next_act)

        display_box.add_widget(self.row_prev);
        display_box.add_widget(self.row_curr);
        display_box.add_widget(self.row_next)
        layout.add_widget(display_box)

        self.btn_done = Button(text="ERLEDIGT", font_size='22sp', size_hint=(1, 0.1),
                               background_color=(0.2, 0.6, 0.8, 1), bold=True)
        self.btn_done.bind(on_press=self.next_workout)
        layout.add_widget(self.btn_done)

        btn_home = Button(text="HOME", font_size='18sp', size_hint=(1, 0.1), background_color=(0.2, 0.2, 0.2, 1),
                          bold=True)
        btn_home.bind(on_press=lambda x: self.switch_screen_name("Home"))
        layout.add_widget(btn_home)

        self.update_ui()
        return layout

    def create_settings_layout(self):
        layout = BoxLayout(orientation='vertical', padding=20, spacing=15)
        layout.add_widget(self.create_header())
        layout.add_widget(
            Label(text="[b]Trainings-Routinen bearbeiten[/b]", markup=True, font_size='20sp', size_hint=(1, 0.1)))

        self.routines_box = BoxLayout(orientation='vertical', size_hint_y=None, spacing=10)
        self.routines_box.bind(minimum_height=self.routines_box.setter('height'))
        scroll = ScrollView(size_hint=(1, 0.62))
        scroll.add_widget(self.routines_box)
        layout.add_widget(scroll)

        btn_add = Button(text="Neue Routine hinzufügen", size_hint=(1, 0.1), background_color=(0.4, 0.4, 0.4, 1))
        btn_add.bind(on_press=lambda x: self.add_routine_row(""))
        layout.add_widget(btn_add)

        bottom_box = BoxLayout(orientation='horizontal', size_hint=(1, 0.1), spacing=15)
        btn_discard = Button(text="Verwerfen", background_color=(0.8, 0.2, 0.2, 1), bold=True)
        btn_discard.bind(on_press=self.discard_settings)
        btn_save = Button(text="Speichern", background_color=(0.2, 0.8, 0.2, 1), bold=True)
        btn_save.bind(on_press=self.save_settings)
        bottom_box.add_widget(btn_discard);
        bottom_box.add_widget(btn_save)
        layout.add_widget(bottom_box)
        return layout

    def create_wellbeing_layout(self):
        layout = BoxLayout(orientation='vertical', padding=15, spacing=10)
        layout.add_widget(self.create_header())
        layout.add_widget(
            Label(text="[b]Wie geht es dir heute?[/b]", markup=True, font_size='22sp', size_hint=(1, 0.08)))

        self.wellbeing_label = Label(text="[b][color=#AAAAAA]0[/color][/b]", markup=True, font_size='50sp',
                                     size_hint=(1, 0.15))
        layout.add_widget(self.wellbeing_label)
        self.wellbeing_slider = Slider(min=-5, max=5, value=0, step=1, size_hint=(1, 0.1))
        self.wellbeing_slider.bind(value=self.on_wellbeing_slider_change)
        layout.add_widget(self.wellbeing_slider)

        scale_labels = BoxLayout(orientation='horizontal', size_hint=(1, 0.05))
        scale_labels.add_widget(Label(text="-5 (Schlecht)", halign='left', color=(0.8, 0.2, 0.2, 1)))
        scale_labels.add_widget(Label(text="+5 (Sehr gut)", halign='right', color=(0.2, 0.8, 0.2, 1)))
        layout.add_widget(scale_labels)

        btn_confirm = Button(text="BESTÄTIGEN", font_size='20sp', size_hint=(1, 0.1),
                             background_color=(0.2, 0.6, 0.8, 1), bold=True)
        btn_confirm.bind(on_press=self.save_wellbeing)
        layout.add_widget(btn_confirm)
        layout.add_widget(Label(text="Letzte Eingaben (Max. 90):", color=(0.6, 0.6, 0.6, 1), size_hint=(1, 0.04)))

        self.wellbeing_history_box = BoxLayout(orientation='vertical', size_hint_y=None, spacing=5)
        self.wellbeing_history_box.bind(minimum_height=self.wellbeing_history_box.setter('height'))
        scroll = ScrollView(size_hint=(1, 0.2))
        scroll.add_widget(self.wellbeing_history_box)
        layout.add_widget(scroll)

        btn_action_box = BoxLayout(orientation='horizontal', size_hint=(1, 0.08), spacing=10)
        btn_del = Button(text="Letzten Eintrag löschen", font_size='12sp', background_color=(0.8, 0.5, 0.2, 1),
                         bold=True)
        btn_del.bind(on_press=lambda x: self.delete_last_entry('wellbeing'))
        btn_reset = Button(text="Reset Einträge", font_size='12sp', background_color=(0.8, 0.3, 0.2, 1), bold=True)
        btn_reset.bind(on_press=lambda x: self.reset_entries('wellbeing'))
        btn_action_box.add_widget(btn_del);
        btn_action_box.add_widget(btn_reset)
        layout.add_widget(btn_action_box)

        btn_home = Button(text="HOME", font_size='18sp', size_hint=(1, 0.1), background_color=(0.2, 0.2, 0.2, 1),
                          bold=True)
        btn_home.bind(on_press=lambda x: self.switch_screen_name("Home"))
        layout.add_widget(btn_home)

        self.update_wellbeing_history_ui()
        return layout

    def create_stress_layout(self):
        layout = BoxLayout(orientation='vertical', padding=15, spacing=10)
        layout.add_widget(self.create_header())
        layout.add_widget(
            Label(text="[b]Wie gestresst warst du heute?[/b]", markup=True, font_size='22sp', size_hint=(1, 0.08)))

        self.stress_label = Label(text="[b][color=#AAAAAA]0[/color][/b]", markup=True, font_size='50sp',
                                  size_hint=(1, 0.15))
        layout.add_widget(self.stress_label)
        self.stress_slider = Slider(min=-5, max=5, value=0, step=1, size_hint=(1, 0.1))
        self.stress_slider.bind(value=self.on_stress_slider_change)
        layout.add_widget(self.stress_slider)

        scale_labels = BoxLayout(orientation='horizontal', size_hint=(1, 0.05))
        scale_labels.add_widget(Label(text="-5 (Entspannt)", halign='left', color=(0.2, 0.8, 0.2, 1)))
        scale_labels.add_widget(Label(text="+5 (Gestresst)", halign='right', color=(0.8, 0.2, 0.2, 1)))
        layout.add_widget(scale_labels)

        btn_confirm = Button(text="BESTÄTIGEN", font_size='20sp', size_hint=(1, 0.1),
                             background_color=(0.2, 0.6, 0.8, 1), bold=True)
        btn_confirm.bind(on_press=self.save_stress)
        layout.add_widget(btn_confirm)
        layout.add_widget(Label(text="Letzte Eingaben (Max. 90):", color=(0.6, 0.6, 0.6, 1), size_hint=(1, 0.04)))

        self.stress_history_box = BoxLayout(orientation='vertical', size_hint_y=None, spacing=5)
        self.stress_history_box.bind(minimum_height=self.stress_history_box.setter('height'))
        scroll = ScrollView(size_hint=(1, 0.2))
        scroll.add_widget(self.stress_history_box)
        layout.add_widget(scroll)

        btn_action_box = BoxLayout(orientation='horizontal', size_hint=(1, 0.08), spacing=10)
        btn_del = Button(text="Letzten Eintrag löschen", font_size='12sp', background_color=(0.8, 0.5, 0.2, 1),
                         bold=True)
        btn_del.bind(on_press=lambda x: self.delete_last_entry('stress'))
        btn_reset = Button(text="Reset Einträge", font_size='12sp', background_color=(0.8, 0.3, 0.2, 1), bold=True)
        btn_reset.bind(on_press=lambda x: self.reset_entries('stress'))
        btn_action_box.add_widget(btn_del);
        btn_action_box.add_widget(btn_reset)
        layout.add_widget(btn_action_box)

        btn_home = Button(text="HOME", font_size='18sp', size_hint=(1, 0.1), background_color=(0.2, 0.2, 0.2, 1),
                          bold=True)
        btn_home.bind(on_press=lambda x: self.switch_screen_name("Home"))
        layout.add_widget(btn_home)

        self.update_stress_history_ui()
        return layout

    def create_cold_layout(self):
        layout = BoxLayout(orientation='vertical', padding=15, spacing=10)
        layout.add_widget(self.create_header())
        layout.add_widget(Label(text="[b]Kälte[/b]", markup=True, font_size='24sp', size_hint=(1, 0.08)))

        self.lbl_cold_stats = Label(text="", markup=True, font_size='18sp', halign='center', size_hint=(1, 0.15))
        self.lbl_cold_stats.bind(size=self.lbl_cold_stats.setter('text_size'))
        layout.add_widget(self.lbl_cold_stats)

        btn_box = BoxLayout(orientation='horizontal', size_hint=(1, 0.12), spacing=15)
        btn_done = Button(text="ERLEDIGT", font_size='18sp', background_color=(0.2, 0.7, 0.3, 1), bold=True)
        btn_done.bind(on_press=lambda x: self.save_habit('cold', 1))
        btn_not_done = Button(text="NICHT ERLEDIGT", font_size='18sp', background_color=(0.5, 0.5, 0.5, 1), bold=True)
        btn_not_done.bind(on_press=lambda x: self.save_habit('cold', 0))
        btn_box.add_widget(btn_not_done);
        btn_box.add_widget(btn_done)
        layout.add_widget(btn_box)

        filter_box = BoxLayout(orientation='horizontal', size_hint=(1, 0.08), spacing=10)
        btn_30 = Button(text="30 Tage", background_color=(0.2, 0.6, 0.8, 1), bold=True)
        btn_30.bind(on_press=lambda x: self.change_habit_filter('cold', 30))
        btn_60 = Button(text="60 Tage", background_color=(0.2, 0.2, 0.2, 1), bold=True)
        btn_60.bind(on_press=lambda x: self.change_habit_filter('cold', 60))
        btn_90 = Button(text="90 Tage", background_color=(0.2, 0.2, 0.2, 1), bold=True)
        btn_90.bind(on_press=lambda x: self.change_habit_filter('cold', 90))
        filter_box.add_widget(btn_30);
        filter_box.add_widget(btn_60);
        filter_box.add_widget(btn_90)
        self.filter_buttons_cold = {30: btn_30, 60: btn_60, 90: btn_90}
        layout.add_widget(filter_box)

        layout.add_widget(Label(text="Gefilterter Verlauf:", color=(0.5, 0.5, 0.5, 1), size_hint=(1, 0.05)))

        self.cold_history_box = BoxLayout(orientation='vertical', size_hint_y=None, spacing=5)
        self.cold_history_box.bind(minimum_height=self.cold_history_box.setter('height'))
        scroll = ScrollView(size_hint=(1, 0.24))
        scroll.add_widget(self.cold_history_box)
        layout.add_widget(scroll)

        btn_action_box = BoxLayout(orientation='horizontal', size_hint=(1, 0.08), spacing=10)
        btn_del = Button(text="Letzten Eintrag löschen", font_size='12sp', background_color=(0.8, 0.5, 0.2, 1),
                         bold=True)
        btn_del.bind(on_press=lambda x: self.delete_last_entry('cold'))
        btn_reset = Button(text="Reset Einträge", font_size='12sp', background_color=(0.8, 0.3, 0.2, 1), bold=True)
        btn_reset.bind(on_press=lambda x: self.reset_entries('cold'))
        btn_action_box.add_widget(btn_del);
        btn_action_box.add_widget(btn_reset)
        layout.add_widget(btn_action_box)

        btn_home = Button(text="HOME", font_size='18sp', size_hint=(1, 0.1), background_color=(0.2, 0.2, 0.2, 1),
                          bold=True)
        btn_home.bind(on_press=lambda x: self.switch_screen_name("Home"))
        layout.add_widget(btn_home)

        self.update_habit_ui('cold', self.lbl_cold_stats, self.cold_history_box, "Kälte", self.cold_filter)
        return layout

    def create_meditation_layout(self):
        layout = BoxLayout(orientation='vertical', padding=15, spacing=10)
        layout.add_widget(self.create_header())
        layout.add_widget(Label(text="[b]Meditation[/b]", markup=True, font_size='24sp', size_hint=(1, 0.08)))

        self.lbl_meditation_stats = Label(text="", markup=True, font_size='18sp', halign='center', size_hint=(1, 0.15))
        self.lbl_meditation_stats.bind(size=self.lbl_meditation_stats.setter('text_size'))
        layout.add_widget(self.lbl_meditation_stats)

        btn_box = BoxLayout(orientation='horizontal', size_hint=(1, 0.12), spacing=15)
        btn_done = Button(text="ERLEDIGT", font_size='18sp', background_color=(0.2, 0.6, 0.8, 1), bold=True)
        btn_done.bind(on_press=lambda x: self.save_habit('meditation', 1))
        btn_not_done = Button(text="NICHT ERLEDIGT", font_size='18sp', background_color=(0.5, 0.5, 0.5, 1), bold=True)
        btn_not_done.bind(on_press=lambda x: self.save_habit('meditation', 0))
        btn_box.add_widget(btn_not_done);
        btn_box.add_widget(btn_done)
        layout.add_widget(btn_box)

        filter_box = BoxLayout(orientation='horizontal', size_hint=(1, 0.08), spacing=10)
        btn_30 = Button(text="30 Tage", background_color=(0.2, 0.6, 0.8, 1), bold=True)
        btn_30.bind(on_press=lambda x: self.change_habit_filter('meditation', 30))
        btn_60 = Button(text="60 Tage", background_color=(0.2, 0.2, 0.2, 1), bold=True)
        btn_60.bind(on_press=lambda x: self.change_habit_filter('meditation', 60))
        btn_90 = Button(text="90 Tage", background_color=(0.2, 0.2, 0.2, 1), bold=True)
        btn_90.bind(on_press=lambda x: self.change_habit_filter('meditation', 90))
        filter_box.add_widget(btn_30);
        filter_box.add_widget(btn_60);
        filter_box.add_widget(btn_90)
        self.filter_buttons_med = {30: btn_30, 60: btn_60, 90: btn_90}
        layout.add_widget(filter_box)

        layout.add_widget(Label(text="Gefilterter Verlauf:", color=(0.5, 0.5, 0.5, 1), size_hint=(1, 0.05)))

        self.meditation_history_box = BoxLayout(orientation='vertical', size_hint_y=None, spacing=5)
        self.meditation_history_box.bind(minimum_height=self.meditation_history_box.setter('height'))
        scroll = ScrollView(size_hint=(1, 0.24))
        scroll.add_widget(self.meditation_history_box)
        layout.add_widget(scroll)

        btn_action_box = BoxLayout(orientation='horizontal', size_hint=(1, 0.08), spacing=10)
        btn_del = Button(text="Letzten Eintrag löschen", font_size='12sp', background_color=(0.8, 0.5, 0.2, 1),
                         bold=True)
        btn_del.bind(on_press=lambda x: self.delete_last_entry('meditation'))
        btn_reset = Button(text="Reset Einträge", font_size='12sp', background_color=(0.8, 0.3, 0.2, 1), bold=True)
        btn_reset.bind(on_press=lambda x: self.reset_entries('meditation'))
        btn_action_box.add_widget(btn_del);
        btn_action_box.add_widget(btn_reset)
        layout.add_widget(btn_action_box)

        btn_home = Button(text="HOME", font_size='18sp', size_hint=(1, 0.1), background_color=(0.2, 0.2, 0.2, 1),
                          bold=True)
        btn_home.bind(on_press=lambda x: self.switch_screen_name("Home"))
        layout.add_widget(btn_home)

        self.update_habit_ui('meditation', self.lbl_meditation_stats, self.meditation_history_box, "Meditation",
                             self.med_filter)
        return layout

    def create_evaluation_layout(self):
        main_layout = BoxLayout(orientation='vertical', padding=15, spacing=10)
        main_layout.add_widget(self.create_header())
        main_layout.add_widget(
            Label(text="[b]Langzeit-Auswertung[/b]", markup=True, font_size='22sp', size_hint=(1, 0.08)))

        legend_box = BoxLayout(orientation='horizontal', size_hint=(1, 0.06), spacing=5)
        legend_box.add_widget(Label(text="[color=#55FF55]• Wohlbefinden[/color]", markup=True, font_size='11sp'))
        legend_box.add_widget(Label(text="[color=#FF5555]• Stress[/color]", markup=True, font_size='11sp'))
        legend_box.add_widget(Label(text="[color=#33B2FF]• Kälte[/color]", markup=True, font_size='11sp'))
        legend_box.add_widget(Label(text="[color=#FFCC33]• Meditation[/color]", markup=True, font_size='11sp'))
        main_layout.add_widget(legend_box)

        graph_area = BoxLayout(orientation='horizontal', size_hint=(1, 0.46))
        y_axis = BoxLayout(orientation='vertical', size_hint_x=0.08)
        y_axis.add_widget(Label(text="+5", color=(0.7, 0.7, 0.7, 1), valign='top', halign='right'))
        y_axis.add_widget(Label(text="0", color=(0.5, 0.5, 0.5, 1), valign='middle', halign='right'))
        y_axis.add_widget(Label(text="-5", color=(0.7, 0.7, 0.7, 1), valign='bottom', halign='right'))
        for lbl in y_axis.children: lbl.bind(size=lbl.setter('text_size'))
        graph_area.add_widget(y_axis)

        self.graph_widget = EvaluationGraph(self.store)
        graph_area.add_widget(self.graph_widget)
        main_layout.add_widget(graph_area)

        x_axis = BoxLayout(orientation='horizontal', size_hint=(1, 0.04), padding=(Window.width * 0.08, 0, 0, 0))
        self.lbl_x_start = Label(text="Vor 30 Tagen", color=(0.5, 0.5, 0.5, 1), halign='left')
        self.lbl_x_start.bind(size=self.lbl_x_start.setter('text_size'))
        self.lbl_x_end = Label(text="Heute", color=(0.5, 0.5, 0.5, 1), halign='right')
        self.lbl_x_end.bind(size=self.lbl_x_end.setter('text_size'))
        x_axis.add_widget(self.lbl_x_start);
        x_axis.add_widget(self.lbl_x_end)
        main_layout.add_widget(x_axis)

        filter_box = BoxLayout(orientation='horizontal', size_hint=(1, 0.08), spacing=10)
        btn_30 = Button(text="30 Tage", background_color=(0.2, 0.6, 0.8, 1), bold=True)
        btn_30.bind(on_press=lambda x: self.change_graph_range(30))
        btn_60 = Button(text="60 Tage", background_color=(0.2, 0.2, 0.2, 1), bold=True)
        btn_60.bind(on_press=lambda x: self.change_graph_range(60))
        btn_90 = Button(text="90 Tage", background_color=(0.2, 0.2, 0.2, 1), bold=True)
        btn_90.bind(on_press=lambda x: self.change_graph_range(90))
        filter_box.add_widget(btn_30);
        filter_box.add_widget(btn_60);
        filter_box.add_widget(btn_90)
        self.filter_buttons = {30: btn_30, 60: btn_60, 90: btn_90}
        main_layout.add_widget(filter_box)

        btn_home = Button(text="HOME", font_size='18sp', size_hint=(1, 0.1), background_color=(0.2, 0.2, 0.2, 1),
                          bold=True)
        btn_home.bind(on_press=lambda x: self.switch_screen_name("Home"))
        main_layout.add_widget(btn_home)

        return main_layout

    # ==========================================
    # LOGIK & FUNKTIONEN
    # ==========================================

    def switch_screen_name(self, name):
        if name in [s.name for s in self.sm.screens]:
            self.sm.current = name
            if name == "Auswertung":
                self.graph_widget.redraw()

    def switch_screen(self, instance):
        self.switch_screen_name(instance.text)

    def change_graph_range(self, days):
        self.graph_widget.set_days(days)
        self.lbl_x_start.text = f"Vor {days} Tagen"
        for d, btn in self.filter_buttons.items():
            btn.background_color = (0.2, 0.6, 0.8, 1) if d == days else (0.2, 0.2, 0.2, 1)

    def change_habit_filter(self, key, days):
        if key == 'cold':
            self.cold_filter = days
            for d, btn in self.filter_buttons_cold.items():
                btn.background_color = (0.2, 0.6, 0.8, 1) if d == days else (0.2, 0.2, 0.2, 1)
            self.update_habit_ui('cold', self.lbl_cold_stats, self.cold_history_box, "Kälte", self.cold_filter)
        elif key == 'meditation':
            self.med_filter = days
            for d, btn in self.filter_buttons_med.items():
                btn.background_color = (0.2, 0.6, 0.8, 1) if d == days else (0.2, 0.2, 0.2, 1)
            self.update_habit_ui('meditation', self.lbl_meditation_stats, self.meditation_history_box, "Meditation",
                                 self.med_filter)

    def next_workout(self, instance):
        if not self.workouts: return
        self.current_index = (self.current_index + 1) % len(self.workouts)
        self.store.put('state', index=self.current_index)
        self.update_ui()

    def update_ui(self):
        if not self.workouts:
            self.lbl_prev_act.text = "[i]Keine Routinen[/i]"
            self.row_curr.lbl_activity.text = "[b]Keine Routinen[/b]"
            self.lbl_next_act.text = "[i]Keine Routinen[/i]"
            return
        if self.current_index >= len(self.workouts): self.current_index = 0
        prev_idx = (self.current_index - 1) % len(self.workouts)
        next_idx = (self.current_index + 1) % len(self.workouts)
        self.lbl_prev_act.text = f"[i]{self.workouts[prev_idx]}[/i]"
        self.row_curr.lbl_activity.text = f"[b]{self.workouts[self.current_index]}[/b]"
        self.lbl_next_act.text = f"[i]{self.workouts[next_idx]}[/i]"

    def open_settings(self, instance):
        self.routines_box.clear_widgets()
        for workout in self.workouts: self.add_routine_row(workout)
        self.switch_screen_name("TrainingSettings")

    def add_routine_row(self, text):
        row = BoxLayout(orientation='horizontal', size_hint_y=None, height=50, spacing=10)
        ti = TextInput(text=text, font_size='18sp', multiline=False, background_color=(0.9, 0.9, 0.9, 1))
        btn_minus = Button(text="-", font_size='25sp', bold=True, size_hint_x=0.2, background_color=(0.8, 0.2, 0.2, 1))
        btn_minus.bind(on_press=lambda btn: self.routines_box.remove_widget(row))
        row.add_widget(ti);
        row.add_widget(btn_minus)
        self.routines_box.add_widget(row)

    def discard_settings(self, instance):
        self.switch_screen_name("Training")

    def save_settings(self, instance):
        new_workouts = []
        for row in reversed(self.routines_box.children):
            for widget in row.children:
                if isinstance(widget, TextInput):
                    txt = widget.text.strip()
                    if txt: new_workouts.append(txt)
        if new_workouts:
            self.workouts = new_workouts
            self.store.put('workout_list', data=self.workouts)
            self.update_ui()
        self.switch_screen_name("Training")

    def delete_last_entry(self, key):
        if self.store.exists(key):
            data = self.store.get(key)['history']
            if data:
                data.pop()  # Letztes Element (neuster Eintrag) löschen
                self.store.put(key, history=data)

                # UI direkt aktualisieren
                if key == 'wellbeing':
                    self.update_wellbeing_history_ui()
                elif key == 'stress':
                    self.update_stress_history_ui()
                elif key == 'cold':
                    self.update_habit_ui('cold', self.lbl_cold_stats, self.cold_history_box, "Kälte", self.cold_filter)
                elif key == 'meditation':
                    self.update_habit_ui('meditation', self.lbl_meditation_stats, self.meditation_history_box,
                                         "Meditation", self.med_filter)

    def on_wellbeing_slider_change(self, instance, value):
        score = int(value)
        color = "55FF55" if score > 0 else ("FF5555" if score < 0 else "AAAAAA")
        text = f"+{score}" if score > 0 else f"{score}"
        self.wellbeing_label.text = f"[b][color=#{color}]{text}[/color][/b]"

    def save_wellbeing(self, instance):
        now = datetime.now().strftime("%d.%m.%Y - %H:%M")
        history = self.store.get('wellbeing')['history'] if self.store.exists('wellbeing') else []
        history.append({"date": now, "score": int(self.wellbeing_slider.value)})
        self.store.put('wellbeing', history=history[-90:])
        self.update_wellbeing_history_ui()
        self.wellbeing_slider.value = 0

    def update_wellbeing_history_ui(self):
        self.wellbeing_history_box.clear_widgets()
        if self.store.exists('wellbeing'):
            for entry in reversed(self.store.get('wellbeing')['history']):
                score = entry['score']
                score_text = f"[color=#55FF55]+{score}[/color]" if score > 0 else (
                    f"[color=#FF5555]{score}[/color]" if score < 0 else "[color=#AAAAAA]0[/color]")
                row = BoxLayout(orientation='horizontal', size_hint_y=None,
                                height=50)  # Höhe erhöht für bessere Lesbarkeit
                lbl_date = Label(text=entry['date'], font_size='14sp', halign='left', valign='middle', size_hint_x=0.7)
                lbl_score = Label(text=score_text, markup=True, font_size='16sp', bold=True, halign='right',
                                  valign='middle', size_hint_x=0.3)
                lbl_date.bind(size=lbl_date.setter('text_size'));
                lbl_score.bind(size=lbl_score.setter('text_size'))
                row.add_widget(lbl_date);
                row.add_widget(lbl_score)
                self.wellbeing_history_box.add_widget(row)

    def on_stress_slider_change(self, instance, value):
        score = int(value)
        color = "FF5555" if score > 0 else ("55FF55" if score < 0 else "AAAAAA")
        text = f"+{score}" if score > 0 else f"{score}"
        self.stress_label.text = f"[b][color=#{color}]{text}[/color][/b]"

    def save_stress(self, instance):
        now = datetime.now().strftime("%d.%m.%Y - %H:%M")
        history = self.store.get('stress')['history'] if self.store.exists('stress') else []
        history.append({"date": now, "score": int(self.stress_slider.value)})
        self.store.put('stress', history=history[-90:])
        self.update_stress_history_ui()
        self.stress_slider.value = 0

    def update_stress_history_ui(self):
        self.stress_history_box.clear_widgets()
        if self.store.exists('stress'):
            for entry in reversed(self.store.get('stress')['history']):
                score = entry['score']
                score_text = f"[color=#FF5555]+{score}[/color]" if score > 0 else (
                    f"[color=#55FF55]{score}[/color]" if score < 0 else "[color=#AAAAAA]0[/color]")
                row = BoxLayout(orientation='horizontal', size_hint_y=None, height=50)  # Höhe erhöht
                lbl_date = Label(text=entry['date'], font_size='14sp', halign='left', valign='middle', size_hint_x=0.7)
                lbl_score = Label(text=score_text, markup=True, font_size='16sp', bold=True, halign='right',
                                  valign='middle', size_hint_x=0.3)
                lbl_date.bind(size=lbl_date.setter('text_size'));
                lbl_score.bind(size=lbl_score.setter('text_size'))
                row.add_widget(lbl_date);
                row.add_widget(lbl_score)
                self.stress_history_box.add_widget(row)

    def save_habit(self, key, status):
        now = datetime.now().strftime("%d.%m.%Y - %H:%M")
        history = self.store.get(key)['history'] if self.store.exists(key) else []
        history.append({"date": now, "status": status})
        self.store.put(key, history=history[-90:])
        if key == 'cold':
            self.update_habit_ui('cold', self.lbl_cold_stats, self.cold_history_box, "Kälte", self.cold_filter)
        else:
            self.update_habit_ui('meditation', self.lbl_meditation_stats, self.meditation_history_box, "Meditation",
                                 self.med_filter)

    def update_habit_ui(self, key, lbl_stats, box_history, name, filter_days):
        box_history.clear_widgets()
        if not self.store.exists(key):
            lbl_stats.text = f"Noch keine Daten für {name} vorhanden."
            return
        history = self.store.get(key)['history']
        now = datetime.now()
        filtered_entries = []
        for entry in history:
            try:
                dt = datetime.strptime(entry['date'], "%d.%m.%Y - %H:%M")
                if (now - dt).days < filter_days: filtered_entries.append(entry)
            except ValueError:
                continue
        total = len(filtered_entries)
        done = sum(1 for e in filtered_entries if e['status'] == 1)
        pct = (done / total * 100) if total > 0 else 0
        lbl_stats.text = f"Quote ({filter_days} Tage): [b][color=#33B2FF]{pct:.1f}%[/color][/b]\n({done} von {total} Tagen erledigt)"

        for entry in reversed(filtered_entries):
            status_text = "[color=#55FF55]Erledigt[/color]" if entry[
                                                                   'status'] == 1 else "[color=#888888]Nicht erledigt[/color]"
            row = BoxLayout(orientation='horizontal', size_hint_y=None, height=50)  # Höhe erhöht
            lbl_date = Label(text=entry['date'], font_size='14sp', halign='left', valign='middle', size_hint_x=0.6)
            lbl_status = Label(text=status_text, markup=True, font_size='15sp', bold=True, halign='right',
                               valign='middle', size_hint_x=0.4)
            lbl_date.bind(size=lbl_date.setter('text_size'));
            lbl_status.bind(size=lbl_status.setter('text_size'))
            row.add_widget(lbl_date);
            row.add_widget(lbl_status)
            box_history.add_widget(row)

    def reset_entries(self, key):
        if self.store.exists(key): self.store.delete(key)
        if key == 'wellbeing':
            self.update_wellbeing_history_ui()
        elif key == 'stress':
            self.update_stress_history_ui()
        elif key == 'cold':
            self.update_habit_ui('cold', self.lbl_cold_stats, self.cold_history_box, "Kälte", self.cold_filter)
        elif key == 'meditation':
            self.update_habit_ui('meditation', self.lbl_meditation_stats, self.meditation_history_box, "Meditation",
                                 self.med_filter)


if __name__ == '__main__':
    TrainingRotationApp().run()
