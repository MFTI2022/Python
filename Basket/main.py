import customtkinter as ctk
from PIL import Image, ImageTk
from Dialog import CustomTimeEditDialog
from ToolTip import ToolTip
import os
import pygame

class BasketballScoreboardApp:
    def __init__(self, master):
        self.master = master
        self.master.title("Окно зрителей")
        self.master.geometry("1920x1080")
        self.setup_hotkeys(self.master)

        # Загрузка и установка фона для окна зрителей
        self.background_image = Image.open("img/dynamoSK.jpg").resize((1920, 1080), Image.LANCZOS)
        self.background_photo = ImageTk.PhotoImage(self.background_image)

        self.spectator_frame = ctk.CTkFrame(self.master)
        self.spectator_frame.pack(fill=ctk.BOTH, expand=True)
        self.spectator_canvas = ctk.CTkCanvas(self.spectator_frame, width=1920, height=1080)
        self.spectator_canvas.pack(fill=ctk.BOTH, expand=True)
        self.spectator_canvas.create_image(0, 0, image=self.background_photo, anchor=ctk.NW)

        self.spectator_frame.bind("<Configure>", self.resize_background)

        # Очки, таймер и фолы для окна зрителей
        self.score_team1 = 0
        self.score_team2 = 0
        self.timer_running = False
        self.timer_seconds = 600  # 10 минут на четверть
        self.shot_clock_seconds = 24  # Время на атаку
        self.team1_fouls = 0
        self.team2_fouls = 0
        self.in_break = False
        self.quarter = 1
        self.team1_name = "Команда 1"
        self.team2_name = "Команда 2"

        # Окно оператора
        self.operator_window = ctk.CTkToplevel(self.master)
        self.operator_window.title("Окно оператора")
        self.operator_window.geometry("960x540")
        self.operator_window.configure(bg='black')
        self.create_operator_controls()
        self.setup_hotkeys(self.operator_window)

        # Централизованный виджет для четверти, времени и времени на атаку
        self.create_center_display()

        # Отображение очков, таймера и фолов
        self.display_scores()
        self.display_timer()
        self.display_fouls()
        self.display_shot_clock()
        self.display_quarter_time()

        # Загрузка иконки карандаша
        self.pencil_image = Image.open("img/pencil.jpg").resize((50, 50), Image.LANCZOS)
        self.pencil_photo = ImageTk.PhotoImage(self.pencil_image)

        # Загрузка звуков
        pygame.init()
        self.load_sounds()

        # Добавление иконок редактирования
        self.add_edit_buttons()

    # Загрузка звукового файла
    def load_sounds(self):
        sound_path = os.path.join("sounds", "time-limit.mp3")
        self.time_limit_sound = pygame.mixer.Sound(sound_path)

    def play_time_limit_sound(self):
        self.time_limit_sound.play()

    def setup_hotkeys(self, window):
        window.bind('<a>', lambda event: self.increase_team1_score(1))
        window.bind('<F2>', lambda event: self.decrease_team1_score(1))
        window.bind('<F3>', lambda event: self.increase_team2_score(1))
        window.bind('<F4>', lambda event: self.decrease_team2_score(1))

        window.bind('<F5>', lambda event: self.increase_team1_fouls())
        window.bind('<F6>', lambda event: self.decrease_team1_fouls())
        window.bind('<F7>', lambda event: self.increase_team2_fouls())
        window.bind('<F8>', lambda event: self.decrease_team2_fouls())

        window.bind('<F9>', lambda event: self.start_timer())
        window.bind('<F10>', lambda event: self.stop_timer())
        window.bind('<F11>', lambda event: self.reset_timer())

        window.bind('<F12>', lambda event: self.reset_shot_clock())

    def resize_background(self, event):
        new_width = event.width
        new_height = event.height
        self.background_image_resized = self.background_image.resize((new_width, new_height), Image.LANCZOS)
        self.background_photo_resized = ImageTk.PhotoImage(self.background_image_resized)
        self.spectator_canvas.create_image(0, 0, image=self.background_photo_resized, anchor=ctk.NW)
        self.update_display()

    def display_scores(self):
        self.spectator_canvas.create_text(370, 540, text=f"{self.team1_name}: {self.score_team1}", fill="white", font=("Arial", 72))
        self.spectator_canvas.create_text(2190, 540, text=f"{self.team2_name}: {self.score_team2}", fill="white", font=("Arial", 72))

    def display_timer(self):
        minutes = self.timer_seconds // 60
        seconds = self.timer_seconds % 60
        self.spectator_canvas.create_text(1280, 180, text=f"\n{minutes:02}:{seconds:02}", fill="#c60c30", font=("Arial", 96))

    def display_fouls(self):
        color_team1 = "#a500ff" if self.team1_fouls % 5 == 0 and self.team1_fouls != 0 else "white"
        color_team2 = "#a500ff" if self.team2_fouls % 5 == 0 and self.team2_fouls != 0 else "white"

        self.spectator_canvas.create_text(370, 620, text=f"Фолы: {self.team1_fouls}", fill=color_team1,
                                          font=("Arial", 48))
        self.spectator_canvas.create_text(2190, 620, text=f"Фолы: {self.team2_fouls}", fill=color_team2,
                                          font=("Arial", 48))

    def display_shot_clock(self):
        self.spectator_canvas.create_text(1280, 1360, text=f"{self.shot_clock_seconds}", fill="#f8f435", font=("Arial", 96))

    def display_quarter_time(self, is_break=False):
        if is_break:
            display_text = "Перерыв"
        else:
            display_text = f"Четверть {self.quarter}"
        self.spectator_canvas.create_text(1280, 80, text=display_text, fill="#c60c30", font=("Arial", 96))
        self.quarter_label.configure(text=display_text)

    def create_center_display(self):
        self.quarter_label = ctk.CTkLabel(self.operator_window, text=f"Четверть {self.quarter}", text_color='white', font=("Arial", 36))
        self.quarter_label.place(relx=0.5, rely=0.3, anchor=ctk.CENTER)

        self.time_label = ctk.CTkLabel(self.operator_window, text=f"{self.timer_seconds // 60:02}:{self.timer_seconds % 60:02}", text_color='white', font=("Arial", 36))
        self.time_label.place(relx=0.5, rely=0.4, anchor=ctk.CENTER)

        self.shot_clock_label = ctk.CTkLabel(self.operator_window, text=f"{self.shot_clock_seconds}", text_color='red', font=("Arial", 36))
        self.shot_clock_label.place(relx=0.5, rely=0.5, anchor=ctk.CENTER)

    def create_operator_controls(self):
        self.team1_name_var = ctk.StringVar()
        self.team2_name_var = ctk.StringVar()

        entry_frame = ctk.CTkFrame(self.operator_window)
        entry_frame.pack(side=ctk.TOP, fill=ctk.X, padx=10, pady=10)

        self.team1_entry = ctk.CTkEntry(entry_frame, textvariable=self.team1_name_var, placeholder_text="Название команды 1", width=200)
        self.team1_entry.pack(side=ctk.LEFT, padx=10, pady=10)

        self.team2_entry = ctk.CTkEntry(entry_frame, textvariable=self.team2_name_var, placeholder_text="Название команды 2", width=200)
        self.team2_entry.pack(side=ctk.RIGHT, padx=10, pady=10)

        # Кнопка для сохранения названий команд
        self.save_button = ctk.CTkButton(entry_frame, text="Сохранить", command=self.save_team_names, fg_color='orange', text_color='black')
        self.save_button.pack(side=ctk.TOP, pady=10)

        self.validation_label = ctk.CTkLabel(self.operator_window, text="", text_color='red')
        self.validation_label.pack(side=ctk.TOP, pady=5)

        # Контейнеры для отображения информации о командах
        self.team1_info_frame = ctk.CTkFrame(self.operator_window)
        self.team2_info_frame = ctk.CTkFrame(self.operator_window)

        # Контейнеры для управления очками и фолами
        self.score_and_foul_frame_team1 = ctk.CTkFrame(self.operator_window)
        self.score_and_foul_frame_team2 = ctk.CTkFrame(self.operator_window)

        # Управление таймером
        self.timer_frame = ctk.CTkFrame(self.operator_window)
        self.timer_frame.pack(side=ctk.BOTTOM, pady=10)

        self.start_timer_button = ctk.CTkButton(self.timer_frame, text="Старт Таймера", command=self.start_timer, fg_color='#D3D3D3', text_color_disabled='black', state=ctk.DISABLED)
        self.start_timer_button.pack(side=ctk.LEFT, padx=10)
        self.stop_timer_button = ctk.CTkButton(self.timer_frame, text="Стоп Таймера", command=self.stop_timer, fg_color='#D3D3D3', text_color_disabled='black', state=ctk.DISABLED)
        self.stop_timer_button.pack(side=ctk.LEFT, padx=10)
        self.reset_timer_button = ctk.CTkButton(self.timer_frame, text="Сброс Таймера", command=self.reset_timer, fg_color='#D3D3D3', text_color_disabled='black', state=ctk.DISABLED)
        self.reset_timer_button.pack(side=ctk.LEFT, padx=10)

        # Управление временем на атаку
        self.shot_clock_frame = ctk.CTkFrame(self.operator_window)
        self.shot_clock_frame.pack(side=ctk.BOTTOM, pady=10)

        self.reset_shot_clock_button = ctk.CTkButton(self.shot_clock_frame, text="Сброс Времени на Атаку", command=self.reset_shot_clock, fg_color='#D3D3D3', text_color_disabled='black', state=ctk.DISABLED)
        self.reset_shot_clock_button.pack(side=ctk.LEFT, padx=10)

        # Управление четвертью
        self.quarter_frame = ctk.CTkFrame(self.operator_window)
        self.quarter_frame.pack(side=ctk.BOTTOM, pady=10)

        self.next_quarter_button = ctk.CTkButton(self.quarter_frame, text="Следующая Четверть", command=self.next_quarter, fg_color='#D3D3D3', text_color_disabled='black', state=ctk.DISABLED)
        self.next_quarter_button.pack(side=ctk.LEFT, padx=10)

    def add_edit_buttons(self):
        self.edit_time_button = ctk.CTkButton(self.operator_window, image=self.pencil_photo, text="",
                                              command=self.edit_main_timer, fg_color=self.operator_window["background"],
                                              width=20)
        self.edit_time_button.place(relx=0.55, rely=0.4, anchor=ctk.W)

        self.edit_shot_clock_button = ctk.CTkButton(self.operator_window, image=self.pencil_photo, text="",
                                                    command=self.edit_shot_clock_timer,
                                                    fg_color=self.operator_window["background"], width=20)
        self.edit_shot_clock_button.place(relx=0.55, rely=0.5, anchor=ctk.W)

    def edit_main_timer(self):
        dialog = CustomTimeEditDialog(self.master, "Редактировать основное время",
                                      "Введите новое время в формате мм:сс", 'mm:ss')
        self.master.wait_window(dialog)  # Ждем закрытия диалога

        if dialog.result is not None:
            new_time = dialog.result
            if 0 <= new_time <= 600:
                self.timer_seconds = new_time
                self.update_display()
            else:
                print("Время должно быть в пределах от 0 до 600 секунд")

    def edit_shot_clock_timer(self):
        dialog = CustomTimeEditDialog(self.master, "Редактировать время на атаку", "Введите новое время в секундах:",
                                      'ss')
        self.master.wait_window(dialog)  # Ждем закрытия диалога

        if dialog.result is not None:
            new_shot_time = dialog.result
            if 0 <= new_shot_time <= 24:
                self.shot_clock_seconds = new_shot_time
                self.update_display()
            else:
                print("Время должно быть в пределах от 0 до 24 секунд")

    def save_team_names(self):
        team1_name = self.team1_name_var.get()
        team2_name = self.team2_name_var.get()

        if not team1_name or not team2_name:
            self.validation_label.configure(text="Введите название команд")
            return

        self.validation_label.configure(text="")
        self.team1_name = team1_name
        self.team2_name = team2_name
        self.team1_entry.pack_forget()
        self.team2_entry.pack_forget()
        self.save_button.pack_forget()

        # Отображение названий команд и информации о них
        self.team1_info_frame.pack(side=ctk.LEFT, padx=10, pady=10)
        self.team2_info_frame.pack(side=ctk.RIGHT, padx=10, pady=10)

        ctk.CTkLabel(self.team1_info_frame, text=self.team1_name, text_color='white', font=("Arial", 30)).pack()
        self.score_team1_label = ctk.CTkLabel(self.team1_info_frame, text=f"Очки: {self.score_team1}", text_color='white', font=("Arial", 30))
        self.score_team1_label.pack()
        self.fouls_team1_label = ctk.CTkLabel(self.team1_info_frame, text=f"Фолы: {self.team1_fouls}", text_color='white', font=("Arial", 30))
        self.fouls_team1_label.pack()

        ctk.CTkLabel(self.team2_info_frame, text=self.team2_name, text_color='white', font=("Arial", 30)).pack()
        self.score_team2_label = ctk.CTkLabel(self.team2_info_frame, text=f"Очки: {self.score_team2}", text_color='white', font=("Arial", 30))
        self.score_team2_label.pack()
        self.fouls_team2_label = ctk.CTkLabel(self.team2_info_frame, text=f"Фолы: {self.team2_fouls}", text_color='white', font=("Arial", 30))
        self.fouls_team2_label.pack()

        # Создание кнопок для управления очками и фолами после сохранения команд
        self.create_score_and_foul_buttons()

        # Отображение таймера и четверти
        self.display_quarter_time()
        self.display_timer()

        self.update_display()
        self.update_operator_labels()

        # Создание и отображение ToolTip только после сохранения команд
        if not hasattr(self, 'tooltip'):
            self.tooltip = ToolTip(self.operator_window, image_path="img/info.png",
                                   tooltip_text="\nУправление:\n"
                                                "a: Увеличить счет 1 команды\n"
                                                "F2: Уменьшить счет 1 команды\n"
                                                "F3: Увеличить счет 2 команды\n"
                                                "F4: Уменьшить счет 1 команды\n"
                                                "F5: +Фол 1 команде\n"
                                                "F6: -Фол 1 команде\n"
                                                "F7: +Фол 2 команде\n"
                                                "F8: -Фол 2 команде\n"
                                                "F9: Старт Таймера\n"
                                                "F10: Стоп Таймера\n"
                                                "F11: Сброс Таймера\n"
                                                "F12: Сброс времени на атаку")
            self.tooltip.place(relx=0.5, rely=0.03, anchor=ctk.N)

        # Активация кнопок
        self.activate_buttons()

    def create_score_and_foul_buttons(self):
        self.score_and_foul_frame_team1.pack(side=ctk.LEFT, padx=10, pady=10)
        ctk.CTkButton(self.score_and_foul_frame_team1, text="+1", command=lambda: self.increase_team1_score(1), fg_color='grey', text_color='black', width=50, height=30).pack(side=ctk.TOP, pady=5)
        ctk.CTkButton(self.score_and_foul_frame_team1, text="+2", command=lambda: self.increase_team1_score(2), fg_color='grey', text_color='black', width=50, height=30).pack(side=ctk.TOP, pady=5)
        ctk.CTkButton(self.score_and_foul_frame_team1, text="+3", command=lambda: self.increase_team1_score(3), fg_color='grey', text_color='black', width=50, height=30).pack(side=ctk.TOP, pady=5)
        ctk.CTkButton(self.score_and_foul_frame_team1, text="Фол", command=self.increase_team1_fouls, fg_color='grey', text_color='black', width=50, height=30).pack(side=ctk.TOP, pady=5)

        timeout_btn_team1 = ctk.CTkButton(self.score_and_foul_frame_team1, text="Тайм-аут",
                                          command=lambda: self.start_timeout(1), fg_color='#3585f8', text_color='white',
                                          width=50, height=30)
        timeout_btn_team1.pack(side=ctk.BOTTOM, pady=5)

        self.score_and_foul_frame_team2.pack(side=ctk.RIGHT, padx=10, pady=10)
        ctk.CTkButton(self.score_and_foul_frame_team2, text="+1", command=lambda: self.increase_team2_score(1), fg_color='grey', text_color='black', width=50, height=30).pack(side=ctk.TOP, pady=5)
        ctk.CTkButton(self.score_and_foul_frame_team2, text="+2", command=lambda: self.increase_team2_score(2), fg_color='grey', text_color='black', width=50, height=30).pack(side=ctk.TOP, pady=5)
        ctk.CTkButton(self.score_and_foul_frame_team2, text="+3", command=lambda: self.increase_team2_score(3), fg_color='grey', text_color='black', width=50, height=30).pack(side=ctk.TOP, pady=5)
        ctk.CTkButton(self.score_and_foul_frame_team2, text="Фол", command=self.increase_team2_fouls, fg_color='grey', text_color='black', width=50, height=30).pack(side=ctk.TOP, pady=5)

        timeout_btn_team2 = ctk.CTkButton(self.score_and_foul_frame_team2, text="Тайм-аут",
                                          command=lambda: self.start_timeout(2), fg_color='#3585f8', text_color='white',
                                          width=50, height=30)
        timeout_btn_team2.pack(side=ctk.BOTTOM, pady=5)

    def activate_buttons(self):
        self.start_timer_button.configure(state=ctk.NORMAL, fg_color='#00ff11', text_color='black')
        self.stop_timer_button.configure(state=ctk.NORMAL, fg_color='#f50538', text_color='black')
        self.reset_timer_button.configure(state=ctk.NORMAL, fg_color='orange', text_color='black')
        self.reset_shot_clock_button.configure(state=ctk.NORMAL, fg_color='#ff6361', text_color='black')
        self.next_quarter_button.configure(state=ctk.NORMAL, fg_color='#2bd2ff', text_color='black')

        # Команда 1
        widgets_team1 = self.score_and_foul_frame_team1.winfo_children()
        widgets_team1[0].configure(state=ctk.NORMAL, fg_color='#3be06d')
        widgets_team1[1].configure(state=ctk.NORMAL, fg_color='#c60c30')
        widgets_team1[2].configure(state=ctk.NORMAL, fg_color='#5634b5')
        widgets_team1[3].configure(state=ctk.NORMAL, fg_color='#de4313')

        # Команда 2
        widgets_team2 = self.score_and_foul_frame_team2.winfo_children()
        widgets_team2[0].configure(state=ctk.NORMAL, fg_color='#3be06d')
        widgets_team2[1].configure(state=ctk.NORMAL, fg_color='#c60c30')
        widgets_team2[2].configure(state=ctk.NORMAL, fg_color='#5634b5')
        widgets_team2[3].configure(state=ctk.NORMAL, fg_color='#de4313')

    def increase_team1_score(self, points=1):
        self.score_team1 += points
        self.shot_clock_seconds = 24
        self.update_display()
        self.update_operator_labels()

    def increase_team2_score(self, points=1):
        self.score_team2 += points
        self.shot_clock_seconds = 24
        self.update_display()
        self.update_operator_labels()

    def start_timer(self):
        if not self.timer_running:
            self.timer_running = True
            self.update_timer()

    def stop_timer(self):
        self.timer_running = False

    def reset_timer(self):
        self.timer_running = False
        self.timer_seconds = 600
        self.update_display()

    def increase_team1_fouls(self):
        self.team1_fouls += 1
        self.stop_timer()
        self.update_display()
        self.update_operator_labels()

    def increase_team2_fouls(self):
        self.team2_fouls += 1
        self.stop_timer()
        self.update_display()
        self.update_operator_labels()

    def decrease_team1_score(self, points=1):
        if self.score_team1 > 0:
            self.score_team1 -= points
            self.update_display()

    def decrease_team2_score(self, points=1):
        if self.score_team2 > 0:
            self.score_team2 -= points
            self.update_display()

    def decrease_team1_fouls(self):
        if self.team1_fouls > 0:
            self.team1_fouls -= 1
            self.update_display()

    def decrease_team2_fouls(self):
        if self.team2_fouls > 0:
            self.team2_fouls -= 1
            self.update_display()

    def decrease_timer(self):
        if self.timer_seconds > 0:
            self.timer_seconds -= 60
            self.update_display()

    def decrease_shot_clock(self):
        if self.shot_clock_seconds > 0:
            self.shot_clock_seconds -= 1
            self.update_display()
    def reset_shot_clock(self):
        self.shot_clock_seconds = 24
        self.update_display()

    def next_quarter(self):
        if self.quarter < 4:
            self.quarter += 1
            self.timer_seconds = 600                   # Сброс таймера на 10 минут для новой четверти
            self.shot_clock_seconds = 24               # Сброс времени атаки
            self.timer_running = True
            self.display_quarter_time(is_break=False)  # Обновление отображения четверти
            self.update_display()
            self.update_timer()

    def update_timer(self):
        if self.timer_running:
            if self.in_break:
                if self.timer_seconds > 0:
                    self.timer_seconds -= 1
                if self.timer_seconds == 0:
                    self.in_break = False
                    self.next_quarter()
            else:
                if self.timer_seconds > 0:
                    self.timer_seconds -= 1
                    if self.shot_clock_seconds > 0:
                        self.shot_clock_seconds -= 1
                        if self.shot_clock_seconds == 0:
                            self.shot_clock_seconds = 24
                            self.stop_timer()
                            self.play_time_limit_sound()
                if self.timer_seconds == 0:
                    if self.quarter < 4:
                        self.in_break = True
                        self.timer_seconds = 120
                        self.shot_clock_seconds = 24
                        self.display_quarter_time(is_break=True)
                    else:
                        self.timer_running = False
                        self.display_quarter_time(is_break=False)
            self.update_display()
            self.master.after(1000, self.update_timer)

    def update_display(self):
        # Очистка текущего содержимого холста
        self.spectator_canvas.delete("all")
        self.spectator_canvas.create_image(0, 0, image=self.background_photo_resized, anchor=ctk.NW)

        self.display_scores()
        self.display_timer()
        self.display_fouls()
        self.display_shot_clock()
        self.display_quarter_time(is_break=self.in_break)
        self.update_operator_labels()
        self.update_center_display()

    def update_operator_labels(self):
        if hasattr(self, 'score_team1_label'):
            self.score_team1_label.configure(text=f"Очки: {self.score_team1}")
        if hasattr(self, 'score_team2_label'):
            self.score_team2_label.configure(text=f"Очки: {self.score_team2}")

        # Изменение цвета в зависимости от количества фолов
        color_team1 = "#a500ff" if self.team1_fouls % 5 == 0 and self.team1_fouls != 0 else "white"
        color_team2 = "#a500ff" if self.team2_fouls % 5 == 0 and self.team2_fouls != 0 else "white"

        if hasattr(self, 'fouls_team1_label'):
            self.fouls_team1_label.configure(text=f"Фолы: {self.team1_fouls}", text_color=color_team1)
        if hasattr(self, 'fouls_team2_label'):
            self.fouls_team2_label.configure(text=f"Фолы: {self.team2_fouls}", text_color=color_team2)

    def update_center_display(self):
        if self.in_break:
            self.quarter_label.configure(text="Перерыв")
            self.time_label.configure(text=f"{self.timer_seconds // 60:02}:{self.timer_seconds % 60:02}")
        else:
            self.quarter_label.configure(text=f"Четверть {self.quarter}")
            self.time_label.configure(text=f"{self.timer_seconds // 60:02}:{self.timer_seconds % 60:02}")

        self.shot_clock_label.configure(text=f"{self.shot_clock_seconds}")


if __name__ == "__main__":
    ctk.set_appearance_mode("dark")
    ctk.set_default_color_theme("green")

    root = ctk.CTk()
    app = BasketballScoreboardApp(root)
    root.mainloop()
