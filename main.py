import numpy as np

# Настраиваем Matplotlib на работу в фоновом режиме (без GUI)
import matplotlib
matplotlib.use('Agg') 
import matplotlib.pyplot as plt

from kivy.app import App
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.button import Button
from kivy.uix.textinput import TextInput
from kivy.uix.label import Label
from kivy.uix.gridlayout import GridLayout
from kivy.uix.scatterlayout import ScatterLayout

# Импортируем Kivy-холст для Matplotlib
from kivy_garden.matplotlib.backend_kivyagg import FigureCanvasKivyAgg

# Очистим текущие графики при запусках
plt.close('all')

def draw_cad_dimension(ax, p1, p2, text, color='blue', fs=28, offset=50, tick_size=15, extend_to_y=None):
    """
    Рисует размерную линию. Выносные линии теперь строго штриховые ('--'), 
    как и внутренние вспомогательные линии.
    """
    x1, y1 = p1
    x2, y2 = p2
    
    dx = x2 - x1
    dy = y2 - y1
    L = np.hypot(dx, dy)
    if L == 0: 
        return
    
    # Единичные векторы
    ux = dx / L
    uy = dy / L
    
    # Перпендикулярный вектор для выноса размера
    px = -uy
    py = ux
    
    # Точки самой размерной линии
    dx1, dy1 = x1 + px * offset, y1 + py * offset
    dx2, dy2 = x2 + px * offset, y2 + py * offset
    
    # Рисуем штриховые выносные линии ('--' вместо ':')
    if extend_to_y is not None:
        y_target1, y_target2 = extend_to_y
        ax.plot([x1, dx1], [y_target1, dy1], color='gray', linestyle='--', linewidth=1.5)
        ax.plot([x2, dx2], [y_target2, dy2], color='gray', linestyle='--', linewidth=1.5)
    else:
        direction = 1 if offset >= 0 else -1
        ax.plot([x1 + px * 5 * direction, dx1], [y1 + py * 5 * direction, dy1], color='gray', linestyle='--', linewidth=1.5)
        ax.plot([x2 + px * 5 * direction, dx2], [y2 + py * 5 * direction, dy2], color='gray', linestyle='--', linewidth=1.5)
    
    # Рисуем основную размерную линию
    ax.plot([dx1, dx2], [dy1, dy2], color=color, linewidth=2)
    
    # Рисуем засечки на концах размерной линии
    sx, sy = ux * tick_size, uy * tick_size
    p_x, p_y = px * tick_size, py * tick_size
    
    ax.plot([dx1 - sx/2 - p_x/2, dx1 + sx/2 + p_x/2], 
            [dy1 - sy/2 - p_y/2, dy1 + sy/2 + p_y/2], color=color, linewidth=3)
    ax.plot([dx2 - sx/2 - p_x/2, dx2 + sx/2 + p_x/2], 
            [dy2 - sy/2 - p_y/2, dy2 + sy/2 + p_y/2], color=color, linewidth=3)
    
    angle = np.degrees(np.arctan2(dy, dx))
    if angle > 90: 
        angle -= 180
    elif angle < -90: 
        angle += 180
        
    direction = 1 if offset >= 0 else -1
    tx = (dx1 + dx2) / 2 + px * 20 * direction
    ty = (dy1 + dy2) / 2 + py * 20 * direction
    
    ax.text(tx, ty, text, color=color, fontsize=fs, fontweight='bold',
            ha='center', va='center', rotation=angle)


class MetalmarkingApp(App):
    def build(self):
        self.title = "Калькулятор среза / Kalkulator cięcia"
        self.current_mode = 1
        
        self.main_layout = BoxLayout(orientation='vertical', padding=10, spacing=10)
        
        # --- БЛОК 1: Выбор режима ---
        self.mode_layout = BoxLayout(orientation='horizontal', size_hint_y=0.15, spacing=10)
        
        self.btn_mode1 = Button(
            text="Z-Переход\nPrzejście Z\n(3 дет. / 3 elem.)", 
            background_color=(0.2, 0.6, 1, 1),
            halign='center',
            valign='middle'
        )
        self.btn_mode1.bind(size=self.btn_mode1.setter('text_size'))
        
        self.btn_mode2 = Button(
            text="Один скос\nPojedynczy skos\n(2 дет. / 2 elem.)", 
            background_color=(0.4, 0.4, 0.4, 1),
            halign='center',
            valign='middle'
        )
        self.btn_mode2.bind(size=self.btn_mode2.setter('text_size'))
        
        self.btn_mode1.bind(on_press=self.set_mode_1)
        self.btn_mode2.bind(on_press=self.set_mode_2)
        
        self.mode_layout.add_widget(self.btn_mode1)
        self.mode_layout.add_widget(self.btn_mode2)
        self.main_layout.add_widget(self.mode_layout)
        
        # --- БЛОК 2: Динамические поля ввода ---
        self.inputs_container = BoxLayout(orientation='vertical', size_hint_y=0.30)
        self.inputs_grid = GridLayout(cols=2, spacing=5)
        self.inputs_container.add_widget(self.inputs_grid)
        self.main_layout.add_widget(self.inputs_container)
        
        # --- БЛОК 3: Кнопка расчета ---
        self.btn_calc = Button(
            text="ПОСТРОИТЬ ЧЕРТЕЖ\nRYSUJ WYKRES", 
            size_hint_y=0.1, 
            background_color=(0.2, 0.8, 0.2, 1), 
            font_size=50,
            halign='center',
            valign='middle'
        )
        self.btn_calc.bind(size=self.btn_calc.setter('text_size'))
        self.btn_calc.bind(on_press=self.calculate_and_draw)
        self.main_layout.add_widget(self.btn_calc)
        
        # --- БЛОК 4: Область для вывода графика ---
        self.chart_container = BoxLayout(orientation='vertical', size_hint_y=0.45)
        self.main_layout.add_widget(self.chart_container)
        
        self.setup_inputs()
        
        return self.main_layout

    def set_mode_1(self, instance):
        self.current_mode = 1
        self.btn_mode1.background_color = (0.2, 0.6, 1, 1)
        self.btn_mode2.background_color = (0.4, 0.4, 0.4, 1)
        self.setup_inputs()

    def set_mode_2(self, instance):
        self.current_mode = 2
        self.btn_mode1.background_color = (0.4, 0.4, 0.4, 1)
        self.btn_mode2.background_color = (0.2, 0.6, 1, 1)
        self.setup_inputs()

    def setup_inputs(self):
        self.inputs_grid.clear_widgets()
        self.inputs_dict = {}
        
        if self.current_mode == 1:
            fields = [
                ("Смещение 'a'\nPrzesunięcie 'a'\n(мм / mm)", "300"),
                ("Длина скоса 'b'\nDługość skosu 'b'\n(мм / mm)", "600"),
                ("Ширина 'c'\nSzerokość 'c'\n(мм / mm)", "50")
            ]
        else:
            fields = [
                ("Ширина детали 'c'\nSzerokość detalu 'c'\n(мм / mm)", "50"),
                ("Угол стыка\nKąt połączenia\n(градусы / stopnie)", "135")
            ]
            
        for label_text, default_val in fields:
            lbl = Label(text=label_text, size_hint_x=0.55, halign='center', valign='middle')
            lbl.bind(size=lbl.setter('text_size'))
            
            txt_input = TextInput(text=default_val, multiline=False, input_filter='float', size_hint_x=0.45)
            self.inputs_grid.add_widget(lbl)
            self.inputs_grid.add_widget(txt_input)
            
            self.inputs_dict[label_text] = txt_input

    def calculate_and_draw(self, instance):
        self.chart_container.clear_widgets()
        plt.close('all')
        
        try:
            values = {k: float(v.text) for k, v in self.inputs_dict.items()}
        except ValueError:
            self.chart_container.add_widget(Label(text="Ошибка / Błąd: Введите числа / Wpisz liczby!"))
            return

        fig, ax = plt.subplots(figsize=(10, 6))
        
        fs_labels = 28
        fs_title = 28
        
        if self.current_mode == 1:
            # ==========================================
            # РЕЖИМ 1: Z-образный стык
            # ==========================================
            a = values["Смещение 'a'\nPrzesunięcie 'a'\n(мм / mm)"]
            b = values["Длина скоса 'b'\nDługość skosu 'b'\n(мм / mm)"]
            c = values["Ширина 'c'\nSzerokość 'c'\n(мм / mm)"]
            
            if a >= b:
                self.chart_container.add_widget(Label(text="Ошибка: 'a' должно быть меньше 'b'!\nBłąd: 'a' musi być mniejsze niż 'b'!"))
                return
                
            alpha_rad = np.arcsin(a / b)
            alpha_deg = np.degrees(alpha_rad)
            
            joint_angle = 180.0 - alpha_deg
            
            cut_angle_deg = alpha_deg / 2.0
            cut_angle_rad = np.radians(cut_angle_deg)
            x_offset = c * np.tan(cut_angle_rad)
            dx = b * np.cos(alpha_rad)
            
            L_ends = max(200.0, c * 4)
            
            x_bottom = [0, L_ends, L_ends + dx - x_offset, L_ends + dx - x_offset + L_ends]
            y_bottom = [a, a, 0, 0]
            x_top = [0, L_ends + x_offset, L_ends + dx, L_ends + dx + L_ends]
            y_top = [a + c, a + c, c, c]
            
            # Отрисовка деталей
            ax.plot(x_bottom, y_bottom, color='black', linewidth=4)
            ax.plot(x_top, y_top, color='black', linewidth=4)
            ax.plot([L_ends, L_ends + x_offset], [a, a + c], color='red', linewidth=5)
            ax.plot([L_ends + dx - x_offset, L_ends + dx], [0, c], color='red', linewidth=5)
            
            # Торцы заготовок
            ax.plot([0, 0], [a, a + c], color='black', linewidth=4)
            ax.plot([L_ends + dx - x_offset + L_ends, L_ends + dx - x_offset + L_ends], [0, c], color='black', linewidth=4)
            
            # Горизонтальная ось (штриховая, серая)
            X_end = L_ends + dx - x_offset + L_ends
            ax.plot([L_ends + x_offset, X_end], [a + c, a + c], color='gray', linestyle='--', linewidth=1.5)
            
            # --- ОТРИСОВКА РАЗМЕРОВ ---
            draw_cad_dimension(ax, (0, a), (0, a+c), f'c = {c:.1f} мм/mm', color='blue', fs=fs_labels, offset=80)
            draw_cad_dimension(ax, (X_end, a + c), (X_end, c), f'a = {a:.1f} мм/mm', color='blue', fs=fs_labels, offset=80)
            draw_cad_dimension(ax, (L_ends + x_offset, a + c), (L_ends + dx, c), f'b = {b:.1f} мм/mm', color='purple', fs=fs_labels, offset=80)

            # ГОРИЗОНТАЛЬНАЯ ПРОЕКЦИЯ СНИЗУ
            dim_val = dx - 2 * x_offset
            draw_cad_dimension(ax, 
                               (L_ends + x_offset, 0), 
                               (L_ends + dx - x_offset, 0), 
                               f'{dim_val:.1f} мм/mm', 
                               color='teal', 
                               fs=fs_labels, 
                               offset=-160,
                               extend_to_y=(a + c, 0))

            # Угловая дуга
            center_x, center_y = L_ends, a
            angle_radius = min(120.0, c * 2.2)
            
            start_angle = np.pi
            end_angle = 2.0 * np.pi - alpha_rad
            
            theta = np.linspace(start_angle, end_angle, 100)
            arc_x = center_x + angle_radius * np.cos(theta)
            arc_y = center_y + angle_radius * np.sin(theta)
            
            ax.plot(arc_x, arc_y, color='purple', linewidth=2.5)
            ax.plot([arc_x[-1]], [arc_y[-1]], color='purple', marker='>')
            
            text_x = center_x - (angle_radius * 1.3)
            text_y = center_y - (angle_radius * 0.7)
            
            ax.text(text_x, text_y, f'{joint_angle:.1f}°', color='purple', 
                    fontsize=fs_labels, weight='bold', ha='center', va='center')

            title_text = (f"Угол стыка / Kąt połączenia: {joint_angle:.1f}°\n"
                          f"Скос / Skos (x) = {x_offset:.1f} мм/mm")
            ax.set_title(title_text, fontsize=fs_title, color='red', weight='bold', pad=20)

        else:
            # ==========================================
            # РЕЖИМ 2: Одиночный стык под углом
            # ==========================================
            c = values["Ширина детали 'c'\nSzerokość detalu 'c'\n(мм / mm)"]
            joint_angle = values["Угол стыка\nKąt połączenia\n(градусы / stopnie)"]
            
            if joint_angle <= 10 or joint_angle >= 170:
                self.chart_container.add_widget(Label(text="Угол должен быть от 10° до 170°!\nKąt musi być od 10° do 170°!"))
                return
            
            rot_deg = 180.0 - joint_angle
            rot_rad = np.radians(rot_deg)
            
            cut_angle_deg = rot_deg / 2.0
            cut_angle_rad = np.radians(cut_angle_deg)
            x_offset = c * np.tan(cut_angle_rad)
            
            L_flat = max(180.0, c * 4.0)
            
            ax.plot([0, L_flat], [0, 0], color='black', linewidth=4)
            ax.plot([0, L_flat - x_offset], [c, c], color='black', linewidth=4)
            ax.plot([0, 0], [0, c], color='black', linewidth=3)
            
            dir_x = np.cos(rot_rad)
            dir_y = np.sin(rot_rad)
            
            start_bottom_x, start_bottom_y = L_flat, 0
            start_top_x, start_top_y = L_flat - x_offset, c
            
            end_bottom_x = start_bottom_x + L_flat * dir_x
            end_bottom_y = start_bottom_y + L_flat * dir_y
            
            end_top_x = start_top_x + L_flat * dir_x
            end_top_y = start_top_y + L_flat * dir_y
            
            ax.plot([start_bottom_x, end_bottom_x], [start_bottom_y, end_bottom_y], color='black', linewidth=4)
            ax.plot([start_top_x, end_top_x], [start_top_y, end_top_y], color='black', linewidth=4)
            ax.plot([end_bottom_x, end_top_x], [end_bottom_y, end_top_y], color='black', linewidth=3)
            
            ax.plot([start_bottom_x, start_top_x], [start_bottom_y, start_top_y], color='red', linewidth=5)
            
            # Внутренняя линия: серая, штриховая ('--'), толщина 1.5
            ax.plot([L_flat - x_offset, L_flat - x_offset], [0, c], color='gray', linestyle='--', linewidth=1.5)
            
            draw_cad_dimension(ax, (L_flat - x_offset, 0), (L_flat, 0), f'x = {abs(x_offset):.1f} мм/mm', color='red', fs=fs_labels, offset=-60)
            draw_cad_dimension(ax, (0, 0), (0, c), f'c = {c:.1f} мм/mm', color='blue', fs=fs_labels, offset=60)
            
            center_x, center_y = start_top_x, start_top_y
            angle_radius = c * 1.5
            
            theta = np.linspace(np.pi, rot_rad, 100)
            arc_x = center_x + angle_radius * np.cos(theta)
            arc_y = center_y + angle_radius * np.sin(theta)
            
            ax.plot(arc_x, arc_y, color='purple', linewidth=2)
            ax.plot([arc_x[-1]], [arc_y[-1]], color='purple', marker='>')
            
            text_angle = (np.pi + rot_rad) / 2.0
            ax.text(center_x + angle_radius * 1.3 * np.cos(text_angle), 
                    center_y + angle_radius * 1.3 * np.sin(text_angle), 
                    f'{joint_angle:.1f}°', color='purple', fontsize=fs_labels, weight='bold', ha='center', va='center')

            title_text = (f"Угол / Kąt: {joint_angle:.1f}° \n"
                          f"Скос / Skos (x): {abs(x_offset):.1f} мм/mm")
            ax.set_title(title_text, fontsize=fs_title, color='darkgreen', weight='bold', pad=20)

        ax.set_aspect('equal')
        ax.axis('off')
        
        plt.tight_layout()
        
        scatter = ScatterLayout(
            do_rotation=False,
            do_scale=True,
            do_translation=True
        )
        
        canvas = FigureCanvasKivyAgg(fig)
        scatter.add_widget(canvas)
        self.chart_container.add_widget(scatter)

if __name__ == "__main__":
    MetalmarkingApp().run()
          
