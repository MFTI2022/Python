import customtkinter as ctk
from PIL import Image, ImageTk

class ToolTip(ctk.CTkFrame):
    def __init__(self, parent, image_path, tooltip_text, **kwargs):
        super().__init__(parent, **kwargs)
        self.parent = parent
        self.tooltip_text = tooltip_text
        self.image_path = image_path
        self.icon_photo = None
        self.setup_ui()

    def setup_ui(self):
        # Используем прозрачный фон для канваса
        self.canvas = ctk.CTkCanvas(self, width=40, height=40, bg_color=None, borderwidth=1, relief="solid")
        self.canvas.pack()

        # Загрузка и сохранение изображения
        icon_image = Image.open(self.image_path).resize((50, 50), Image.LANCZOS)
        self.icon_photo = ImageTk.PhotoImage(icon_image)
        self.canvas.create_image(20, 20, image=self.icon_photo)

        # Подсказка при наведении
        self.tooltip = ctk.CTkLabel(self, text=self.tooltip_text, width=200, height=80, fg_color='grey', text_color='black', corner_radius=10)
        self.tooltip.pack_forget()

        # События для показа и скрытия подсказки
        self.canvas.bind("<Enter>", self.on_enter)
        self.canvas.bind("<Leave>", self.on_leave)

    def on_enter(self, event):
        self.tooltip.pack(pady=(0, 50))  # Выставляем подсказку ниже иконки
        self.tooltip.lift()              # Свойство поверх других элементов

    def on_leave(self, event):
        self.tooltip.pack_forget()

if __name__ == "__main__":
    root = ctk.CTk()
    hotkey_info = ToolTip(root, image_path="img/info.png", tooltip_text="Hotkey Information: Use 'a' to 'F12' for various controls", width=60, height=60)
    hotkey_info.pack(pady=20)
    root.mainloop()
