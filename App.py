import tkinter as tk
from tkinter import ttk, filedialog, messagebox
import networkx as nx
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from PIL import Image, ImageTk

from FSA import *


# TODO loading information and description
# TODO возможность не принимать какие-то префиксы и т.д.
class AutomataApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Learning Automata Tool")
        self.root.geometry("1100x640")

        # Frames
        self.control_frame = ttk.Frame(root, padding="10")
        self.control_frame.grid(row=0, column=0, sticky="nsew")

        self.canvas_frame = ttk.Frame(root, padding="10")
        self.canvas_frame.grid(row=0, column=1, sticky="nsew")

        # Control frame
        ttk.Label(self.control_frame, text="Learning Automata Tool", font=("Arial", 16)).grid(row=0, column=0, pady=10)

        # load
        # self.load_button = ttk.Button(self.control_frame, text="Load Automaton", command=self.load_automaton)
        # self.load_button.grid(row=1, column=0, pady=5, sticky="ew")

        # new string input
        self.add_string_label = ttk.Label(self.control_frame, text="Add String:")
        self.add_string_label.grid(row=2, column=0, pady=5)

        self.string_entry = ttk.Entry(self.control_frame)
        self.string_entry.grid(row=3, column=0, pady=5, sticky="ew")
        self.string_entry.insert(0, "")

        # acceptance_state
        self.acceptance_state = tk.StringVar(value="Accepted")
        self.accepted_radio = ttk.Radiobutton(self.control_frame, text="Accepted", variable=self.acceptance_state, value="Accepted")
        self.accepted_radio.grid(row=4, column=0, pady=5, sticky="w")

        self.rejected_radio = ttk.Radiobutton(self.control_frame, text="Rejected", variable=self.acceptance_state, value="Rejected")
        self.rejected_radio.grid(row=5, column=0, pady=5, sticky="w")

        # update automaton
        self.update_automaton_button = ttk.Button(self.control_frame, text="Update automata!", command=self.update_automaton)
        self.update_automaton_button.grid(row=6, column=0, pady=5, sticky="ew")

        # minimize automaton
        self.minimize_automaton_button = ttk.Button(self.control_frame, text="Minimize automata",
                                                  command=self.minimize_automaton)
        self.minimize_automaton_button.grid(row=7, column=0, pady=5, sticky="ew")

        # settings
        self.settings_label = ttk.Label(self.control_frame, text="Settings:")
        self.settings_label.grid(row=8, column=0, pady=5)

        # minimize every time
        self.on_step_minimization = tk.StringVar(value='Rejected')
        self.do_minimization_button = tk.Checkbutton(self.control_frame, text="Minimize of each step?",
                                                     variable=self.on_step_minimization,
                                                     onvalue='Accepted', offvalue='Rejected')
        self.do_minimization_button.grid(row=9, column=0, pady=5)

        # eps_acceptance
        self.eps_acceptance_state = tk.StringVar(value="Accepted")
        self.eps_acceptance_button = tk.Checkbutton(self.control_frame, text="Accept empty word?",
                                                     variable=self.eps_acceptance_state,
                                                     onvalue='Accepted', offvalue='Rejected',
                                                    command=self.change_eps_acceptance)
        self.eps_acceptance_button.grid(row=10, column=0, pady=5)

        # accepting regime
        self.accepting_regime = tk.StringVar(value="Strict")
        self.strict_regime_radio = ttk.Radiobutton(self.control_frame, text="Strict", variable=self.accepting_regime,
                                              value="Strict", command=self.change_accepting_regime)
        self.strict_regime_radio.grid(row=11, column=0, pady=5, sticky="w")

        self.adaptive_regime_radio = ttk.Radiobutton(self.control_frame, text="Adaptive", variable=self.accepting_regime,
                                              value="Adaptive", command=self.change_accepting_regime)
        self.adaptive_regime_radio.grid(row=12, column=0, pady=5, sticky="w")
        self.soft_regime_radio = ttk.Radiobutton(self.control_frame, text="Soft", variable=self.accepting_regime,
                                              value="Soft", command=self.change_accepting_regime)
        self.soft_regime_radio.grid(row=13, column=0, pady=5, sticky="w")

        # check string
        self.check_string_label = ttk.Label(self.control_frame, text="Add String to check:")
        self.check_string_label.grid(row=14, column=0, pady=5)

        self.check_string_entry = ttk.Entry(self.control_frame)
        self.check_string_entry.grid(row=15, column=0, pady=5, sticky="ew")
        self.check_string_entry.insert(0, "")

        # confirm check string
        self.update_automaton_button = ttk.Button(self.control_frame, text="Check acceptance",
                                                  command=self.check_string)
        self.update_automaton_button.grid(row=16, column=0, pady=5, sticky="ew")

        # result of checking
        self.check_result_label = ttk.Label(self.control_frame, text="")
        self.check_result_label.grid(row=17, column=0, pady=5)

        # clear
        self.clear_button = ttk.Button(self.control_frame, text="Clear automata", command=self.clear_automaton)
        self.clear_button.grid(row=18, column=0, pady=5, sticky="ew")


        # info
        self.info_button = ttk.Button(self.control_frame, text="Information and guide", command=self.show_info)
        self.info_button.grid(row=19, column=0, pady=5, sticky="ew")

        # Canvas
        self.canvas = tk.Canvas(self.canvas_frame, bg="white", width=800, height=600)
        self.h_scroll = ttk.Scrollbar(self.canvas_frame, orient=tk.HORIZONTAL, command=self.canvas.xview)
        self.v_scroll = ttk.Scrollbar(self.canvas_frame, orient=tk.VERTICAL, command=self.canvas.yview)
        self.canvas.configure(xscrollcommand=self.h_scroll.set, yscrollcommand=self.v_scroll.set)

        self.canvas.grid(row=0, column=0, sticky="nsew")
        self.h_scroll.grid(row=1, column=0, sticky="ew")
        self.v_scroll.grid(row=0, column=1, sticky="ns")

        self.canvas_frame.columnconfigure(0, weight=1)
        self.canvas_frame.rowconfigure(0, weight=1)
        self.image_id = None
        # self.image_label = tk.Label(self.canvas_frame)
        # self.image_label.pack(fill=tk.BOTH, expand=True)

        self.automaton = None
        self.clear_automaton()

    def load_automaton(self):
        file_path = filedialog.askopenfilename(
            title="Select Automaton File",
            filetypes=[("Text Files", "*.txt"), ("Json Files", "*.json")]
        )
        if not file_path:
            return

        try:
            fmt = file_path.split('.')[-1]
            if fmt == 'txt':
                self.automaton = DFA.read_txt(file_path)
            elif fmt == 'json':
                self.automaton = DFA.read_json(file_path)
            else:
                raise Exception('idk what format it is')
            self.draw_automaton('fsa_img/current_DFA')
            # messagebox.showinfo("Success", "Automaton loaded successfully!")
        except Exception as e:
            messagebox.showerror("Error", f"Failed to load automaton: {e}")

    def change_eps_acceptance(self):
        self.automaton.change_acceptance_of_empty_word(self.eps_acceptance_state.get() == 'Accepted')
        self.draw_automaton('fsa_img/current_DFA')

    def change_accepting_regime(self):
        self.automaton.undefined_string_acception_type = self.accepting_regime.get()
        self.draw_automaton('fsa_img/current_DFA')

    def draw_automaton(self, image_path):
        try:
            fmt = 'png'
            dot = self.automaton.visualize()
            dot.render(image_path, format=fmt, cleanup=True)

            image = Image.open(image_path + f'.{fmt}')
            self.photo = ImageTk.PhotoImage(image)
            self.canvas.delete("all")
            self.image_id = self.canvas.create_image(0, 0, anchor="nw", image=self.photo)

            self.canvas.config(scrollregion=self.canvas.bbox("all"))
        except Exception as e:
            messagebox.showerror("Error", f"Failed to visualize fsa: {e}")

    def minimize_automaton(self):
        try:
            self.automaton.minimize()
            self.draw_automaton('fsa_img/current_DFA')
        except Exception as e:
            messagebox.showerror("Error", f"Failed to minimize dfa: {e}")

    def update_automaton(self):
        """Updates the automaton based on the accepted and rejected strings."""
        try:
            self.automaton.add_string(self.string_entry.get(), self.acceptance_state.get() == 'Accepted')
            if self.on_step_minimization.get() == 'Accepted':
                self.automaton.minimize()
            self.draw_automaton('fsa_img/current_DFA')
        except Exception as e:
            messagebox.showerror("Error", f"Failed to add string to  dfa: {e}")

    def clear_automaton(self):
        self.automaton = DFA()
        self.automaton.change_acceptance_of_empty_word(self.eps_acceptance_state.get() == 'Accepted')
        self.automaton.undefined_string_acception_type = self.accepting_regime.get()
        self.draw_automaton('fsa_img/current_DFA')

    def check_string(self):
        acceptance = self.automaton.check_string(self.check_string_entry.get())
        self.check_result_label = ttk.Label(self.control_frame, text=str(acceptance))
        self.check_result_label.grid(row=17, column=0, pady=5)

    def show_info(self):
        # Да, messageboxы выглядят приближенно к ущербному
        messagebox.showinfo("Информация о программе",
                            """
                            Эта программа позволяет обучать ДКА.
                            Обучение: можно ввести строку и указать, должен ли автомат её принимать. Затем автомат обучится согласно настройкам обучения, отобразится его граф. Затем можно будет минимизировать полученный граф и проверить, какие строки он принимает.
                            Настройки обучения:
                            - Минимизация на каждом шагу. Это может привести к неточностям при распознавании строк, получившихся из ранее сжатых префиксов.
                            - Распознавания пустого слова - Да/Нет
                            - Тип допущения неизвестных слов: Строгое/Адаптивное/Нестрогое:
                              -Строгое: Допускает строго те, строки, которые были введены, как принимаемые
                              -Адаптивное: Допускает слова по принципу: если слово совпадает с ранее полученным, результат соответствует требуемому, если для символа в слове переход в другое состояние не может быть определён явно по предыдущим словам, автомат остаётся в текущем состоянии
                              -Нестрогое: Допускает все незапрещённые слова.
                            """)

    def demo_mode(self):
        return