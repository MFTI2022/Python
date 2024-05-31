import customtkinter as ctk

class CustomTimeEditDialog(ctk.CTkToplevel):
    """Пользовательское диалоговое окно для редактирования времени."""

    def __init__(self, parent, title, message, time_format='mm:ss'):
        super().__init__(parent)
        self.geometry("300x150")  # Установка размера окна
        self.title(title)
        self.parent = parent
        self.result = None
        self.time_format = time_format

        self.label = ctk.CTkLabel(self, text=message)
        self.label.pack(pady=10)

        self.entry = ctk.CTkEntry(self)
        self.entry.pack(pady=10)
        self.entry.bind("<Return>", self.submit)

        self.submit_button = ctk.CTkButton(self, text="Подтвердить", command=self.submit)
        self.submit_button.pack(pady=10)

        self.protocol("WM_DELETE_WINDOW", self.on_close)  # Обработка закрытия окна

        self.center_window()
        self.grab_set()

    def submit(self, event=None):
        time_text = self.entry.get()
        if self.time_format == 'mm:ss':
            try:
                minutes, seconds = map(int, time_text.split(':'))
                self.result = minutes * 60 + seconds
                self.destroy()
            except ValueError:
                self.label.configure(text="Пожалуйста, введите корректное время в формате мм:сс")
        else:  
            try:
                self.result = int(time_text)
                self.destroy()
            except ValueError:
                self.label.configure(text="Пожалуйста, введите корректное число секунд")

    def on_close(self):
        self.result = None  # Установка None, если окно закрыли без подтверждения
        self.destroy()

    def center_window(self):
        self.update_idletasks()  # Обновляет состояние окна для получения точных размеров
        width = self.winfo_width()
        height = self.winfo_height()
        x = (self.parent.winfo_width() // 2) - (width // 2) + self.parent.winfo_x()
        y = (self.parent.winfo_height() // 2) - (height // 2) + self.parent.winfo_y()
        self.geometry(f"+{x}+{y}")  # Установка позиции окна


