import sqlite3
import tkinter as tk
import uuid
import os
import sys
from tkinter import messagebox

import ttkbootstrap as ttk
from ttkbootstrap.constants import *


class Game:
    def __init__(self):
        self.init_db()

        self.full_variants = self.load_creatures_from_db()

        self.variants = self.build_tree(self.full_variants)

        self.current_answer = None
        self.waiting_for_answer = False
        self.waiting_for_name = False
        self.current_obj = None
        self.current_variant = None
        self.text_buffer = None
        self.new_parent_answer = None
        self.new_answer = None
        self.new_question = None
        self.new_name = None
        self.last_answer = None
        self.adding_new = False
        self.log = []

        self.root = ttk.Window(
            title='Угадайка: мифические существа',
            themename='darkly',
            size=(500, 400),
            resizable=(False, False)
        )
        self.setup_ui()

    def setup_ui(self):
        # Основной фрейм для центрирования содержимого
        self.main_frame = ttk.Frame(self.root)
        self.main_frame.pack(fill='both', expand=True, padx=20, pady=20)

        # Центральный фрейм для основного содержимого
        self.center_frame = ttk.Frame(self.main_frame)
        self.center_frame.pack(expand=True, fill='both', pady=20)

        self.lbl = ttk.Label(
            self.center_frame,
            text='Нажмите "Начать игру"',
            font=('Helvetica', 12),
            anchor='center',
            wraplength=400
        )
        self.lbl.pack(pady=20)

        # Фрейм для кнопки начала игры
        self.start_frame = ttk.Frame(self.center_frame)
        self.start_frame.pack(pady=10)

        self.btn_start_game = ttk.Button(
            self.start_frame,
            text='Начать игру',
            command=self.play,
            bootstyle='success',
            width=15
        )
        self.btn_start_game.pack(pady=10)

        # Фрейм для кнопок Да/Нет
        self.yes_no_frame = ttk.Frame(self.center_frame)

        self.btn_yes = ttk.Button(
            self.yes_no_frame,
            text='Да',
            command=self.yes_clicked,
            bootstyle='success',
            width=10
        )
        self.btn_yes.pack(side='left', padx=10)

        self.btn_no = ttk.Button(
            self.yes_no_frame,
            text='Нет',
            command=self.no_clicked,
            bootstyle='danger',
            width=10
        )
        self.btn_no.pack(side='left', padx=10)

        # Фрейм для ввода текста
        self.input_frame = ttk.Frame(self.center_frame)

        self.text_input = ttk.Entry(
            self.input_frame,
            width=25,
            font=('Helvetica', 10)
        )
        self.text_input.pack(pady=5)

        self.btn_confirm = ttk.Button(
            self.input_frame,
            text='Подтвердить',
            command=self.confirm_clicked,
            bootstyle='primary'
        )
        self.btn_confirm.pack(pady=5)

        # Фрейм для кнопки показа лога
        self.log_frame = ttk.Frame(self.center_frame)

        self.btn_log = ttk.Button(
            self.log_frame,
            text='Показать путь до ответа',
            command=self.show_log,
            bootstyle='secondary'
        )
        self.btn_log.pack(pady=10)

        # Нижний фрейм для кнопок управления
        self.bottom_frame = ttk.Frame(self.main_frame)
        self.bottom_frame.pack(side='bottom', fill='x', pady=10)

        # Левый фрейм для кнопок поиска и БД
        self.left_bottom_frame = ttk.Frame(self.bottom_frame)
        self.left_bottom_frame.pack(side='left')

        self.btn_search = ttk.Button(
            self.left_bottom_frame,
            text='Поиск существа',
            command=self.open_search_window,
            bootstyle='info'
        )
        self.btn_search.pack(side='left', padx=5)

        self.btn_bd = ttk.Button(
            self.left_bottom_frame,
            text='Показать БД',
            command=self.show_bd,
            bootstyle='info'
        )
        self.btn_bd.pack(side='left', padx=5)

        # Правый фрейм для кнопки перезапуска
        self.right_bottom_frame = ttk.Frame(self.bottom_frame)
        self.right_bottom_frame.pack(side='right')

        self.btnReset = ttk.Button(
            self.right_bottom_frame,
            text='Перезапуск',
            command=self.reset,
            bootstyle='secondary'
        )
        self.btnReset.pack(side='right', padx=5)

    def build_tree(self, variants):
        nodes = {}
        root = None

        for item in variants:
            node_id = item['id']
            nodes[node_id] = {
                'id': node_id,
                'is_question': item['is_question'],
                'name': item['name'],
                'yes': {},
                'no': {}
            }
            if item['parent_id'] is None:
                root = node_id

        for item in variants:
            if item['parent_id'] is not None:
                parent = nodes[item['parent_id']]
                key = 'yes' if item['parent_answer'] else 'no'
                parent[key][str(item['id'])] = nodes[item['id']]

        return {str(root): nodes[root]} if root is not None else {}

    def play(self):
        self.lbl.configure(text='Вы загадали мифическое существо?')
        self.btn_start_game.pack_forget()
        self.yes_no_frame.pack(pady=10)
        self.waiting_for_answer = True

    def reset(self):
        self.current_answer = None
        self.waiting_for_answer = False
        self.waiting_for_name = False
        self.current_obj = None
        self.current_variant = None
        self.text_buffer = None
        self.new_parent_answer = None
        self.new_answer = None
        self.new_question = None
        self.new_name = None
        self.last_answer = None
        self.adding_new = False
        self.log = []

        # Скрываем все дополнительные элементы
        self.yes_no_frame.pack_forget()
        self.input_frame.pack_forget()
        self.log_frame.pack_forget()

        # Показываем начальное состояние
        self.lbl.configure(text='Нажмите "Начать игру"')
        self.btn_start_game.pack(pady=10)
        self.variants = self.build_tree(self.full_variants)

    def show_log(self):
        output = ''
        self.log.pop(0)
        counter = 0
        for word in self.log:
            counter += 1

            if word == '0':
                word = 'Нет'
            elif word == '1':
                word = 'Да'

            output += word + '->'

            if counter == 5:
                output += '\n'
                counter = 0

        if output[-2:] == '->':
            output = output[:-2]

        self.log_frame.pack_forget()
        self.lbl.configure(text=output)

    def show_bd(self):
        db_window = tk.Toplevel(self.root)
        db_window.title("Структура базы данных")
        db_window.geometry("600x400")

        tree_frame = ttk.Frame(db_window)
        tree_frame.pack(fill='both', expand=True, padx=10, pady=10)

        tree = ttk.Treeview(tree_frame, columns=("type", "answer"), show="tree headings")
        tree.column("#0", width=300, anchor='w')
        tree.column("type", width=100, anchor='center')
        tree.column("answer", width=100, anchor='center')

        tree.heading("#0", text="Вопрос / Существо")
        tree.heading("type", text="Тип")
        tree.heading("answer", text="Ответ родителя")

        # Исправляем цвета для темной темы
        tree.tag_configure('question', background='#3d3d3d', foreground='white')
        tree.tag_configure('creature', background='#2d2d2d', foreground='white')

        scrollbar = ttk.Scrollbar(tree_frame, orient='vertical', command=tree.yview)
        tree.configure(yscrollcommand=scrollbar.set)
        scrollbar.pack(side='right', fill='y')
        tree.pack(side='left', fill='both', expand=True)

        conn = self.get_db_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM variants ORDER BY parent_id, parent_answer")
        items = cursor.fetchall()
        conn.close()

        items_by_id = {item['id']: item for item in items}
        node_ids = {}

        roots = [item for item in items if item['parent_id'] is None]

        def add_node(parent_tree_id, db_item):
            item_text = db_item['name']
            item_type = "Вопрос" if db_item['is_question'] else "Существо"
            parent_answer = db_item['parent_answer']
            if parent_answer is None:
                answer_text = ''
            elif parent_answer == 1:
                answer_text = 'Да'
            else:
                answer_text = 'Нет'

            tag = 'question' if db_item['is_question'] else 'creature'

            tree_id = tree.insert(parent_tree_id, "end", text=item_text,
                                  values=(item_type, answer_text), tags=tag)
            node_ids[db_item['id']] = tree_id

            children = [item for item in items if item['parent_id'] == db_item['id']]
            for child in children:
                add_node(tree_id, child)

        for root_item in roots:
            add_node("", root_item)

        for node in tree.get_children():
            tree.item(node, open=True)

    def open_search_window(self):
        search_window = tk.Toplevel(self.root)
        search_window.title("Поиск существа")
        search_window.geometry("400x150")

        lbl = tk.Label(search_window, text="Введите название существа:")
        lbl.pack(pady=10)

        entry = tk.Entry(search_window, width=30)
        entry.pack(pady=5)

        def search_creature():
            name = entry.get().strip().lower().capitalize()
            if not name:
                messagebox.showwarning("Предупреждение", "Введите название существа")
                return

            conn = self.get_db_connection()
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM variants WHERE name = ? AND is_question = 0", (name,))
            creature = cursor.fetchone()

            if creature:
                self.show_creature_path(creature, search_window)
            else:
                messagebox.showinfo("Результат поиска", f"Существо '{name}' не найдено в базе данных")

            conn.close()

        search_btn = tk.Button(search_window, text="Найти", command=search_creature)
        search_btn.pack(pady=5)

    def show_creature_path(self, creature, parent_window):
        path_window = tk.Toplevel(parent_window)
        path_window.title(f"Путь до существа: {creature['name']}")
        path_window.geometry("500x300")

        path = self.get_path_to_creature(creature['id'])

        text_widget = tk.Text(path_window, wrap='word')
        text_widget.pack(fill='both', expand=True, padx=10, pady=10)

        if path:
            text_widget.insert(tk.END, f"Путь до существа '{creature['name']}':\n\n")

            first_node = path[0]
            if first_node['is_question']:
                text_widget.insert(tk.END, f"1. Вопрос: {first_node['name']}\n")
            else:
                text_widget.insert(tk.END, f"1. Существо: {first_node['name']}\n")

            for i in range(1, len(path)):
                current_node = path[i]
                previous_answer = current_node['answer']

                answer_text = "Да" if previous_answer else "Нет"
                text_widget.insert(tk.END, f"   Ответ: {answer_text}\n")

                if current_node['is_question']:
                    text_widget.insert(tk.END, f"{i + 1}. Вопрос: {current_node['name']}\n")
                else:
                    text_widget.insert(tk.END, f"{i + 1}. Существо: {current_node['name']}\n")

            text_widget.insert(tk.END, f"   Ответ: Да\n")
            text_widget.insert(tk.END, f"{len(path) + 1}. Это точно {creature['name']}!\n")
        else:
            text_widget.insert(tk.END, f"Не удалось построить путь до существа '{creature['name']}'")

        text_widget.config(state='disabled')

    def get_path_to_creature(self, creature_id):
        path = []
        current_id = creature_id
        conn = self.get_db_connection()

        while current_id:
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM variants WHERE id = ?", (current_id,))
            current_node = cursor.fetchone()

            if not current_node:
                break

            parent_answer = None
            if current_node['parent_id']:
                cursor.execute("SELECT parent_answer FROM variants WHERE id = ?", (current_id,))
                answer_row = cursor.fetchone()
                if answer_row:
                    parent_answer = answer_row['parent_answer']

            node_info = {
                'id': current_node['id'],
                'name': current_node['name'],
                'is_question': current_node['is_question'],
                'answer': parent_answer
            }
            path.insert(0, node_info)

            current_id = current_node['parent_id']

        conn.close()
        return path

    def yes_clicked(self):
        self.current_answer = '1'
        self.log.append(self.current_answer)
        if not self.adding_new:
            self.process_answer()
        else:
            self.adding_new = False
            self.new_creature()

    def no_clicked(self):
        self.current_answer = '0'
        self.log.append(self.current_answer)
        if not self.adding_new:
            self.process_answer()
        else:
            self.adding_new = False
            self.new_creature()

    def confirm_clicked(self):
        self.adding_new = True
        self.text_buffer = self.text_input.get().strip()
        if self.text_buffer:
            self.new_creature()

    def new_creature(self):
        if str(self.current_obj['is_question']) == '1':
            self.new_name = self.text_buffer.capitalize()
            self.new_parent_answer = self.current_answer
            self.save_new_creature()
            self.lbl.configure(text='Спасибо! Я узнал новое существо!')
            self.input_frame.pack_forget()
            self.text_input.delete(0, tk.END)
        elif self.new_name is None:
            self.new_name = self.text_buffer.capitalize()
            self.lbl.configure(text='Что отличает ' + self.new_name + ' от ' + self.current_obj['name'] + '?')
            self.text_input.delete(0, tk.END)
            self.waiting_for_answer = True
        elif self.new_question is None:
            self.new_question = self.text_buffer.capitalize()
            if not self.new_question.endswith('?'):
                self.new_question += '?'
            self.lbl.configure(text='Для ' + self.new_name + ' ответ "Да" или "Нет"?')
            self.input_frame.pack_forget()
            self.yes_no_frame.pack(pady=10)
            self.text_input.delete(0, tk.END)
            self.waiting_for_answer = True
        elif self.new_parent_answer is None:
            self.new_parent_answer = self.current_answer
            self.save_new_creature()
            self.lbl.configure(text='Спасибо! Я узнал новое существо!')
            self.yes_no_frame.pack_forget()

    def save_new_creature(self):
        conn = self.get_db_connection()
        cursor = conn.cursor()

        new_parent_id = self.current_obj['id']

        if str(self.current_obj['is_question']) == '0':
            new_parent_id = str(uuid.uuid4())
            cursor.execute("""
                           INSERT
                           OR IGNORE INTO variants (id, name, parent_answer, parent_id, is_question)
                VALUES (?, ?, ?, ?, ?)
                           """,
                           (new_parent_id, self.new_question, self.last_answer, str(self.current_obj['id']), 1))

        cursor.execute("""
                       INSERT
                       OR IGNORE INTO variants (id, name, parent_answer, parent_id, is_question)
                    VALUES (?, ?, ?, ?, ?)
                       """,
                       (str(uuid.uuid4()), self.new_name, self.new_parent_answer, new_parent_id, 0))

        conn.commit()
        conn.close()

        self.full_variants = self.load_creatures_from_db()
        self.variants = self.build_tree(self.full_variants)

    def ask_question(self):
        self.current_obj = self.variants[str(self.current_variant)]
        question = self.variants[str(self.current_variant)]['name']
        self.lbl.configure(text=question)
        self.waiting_for_answer = True
        self.waiting_for_name = False
        self.log.append(question)

    def ask_name(self):
        self.current_obj = self.variants[str(self.current_variant)]
        question = 'Это ' + self.variants[str(self.current_variant)]['name'] + '?'
        self.lbl.configure(text=question)
        self.waiting_for_answer = True
        self.waiting_for_name = True
        self.log.append(question)

    def cant_start(self):
        self.lbl.configure(text='Вы должны загадать мифическое существо, чтобы начать!')
        self.yes_no_frame.pack_forget()

    def give_up(self):
        self.lbl.configure(text="Я сдаюсь! Какое существо вы загадали?")
        self.yes_no_frame.pack_forget()
        self.input_frame.pack(pady=10)
        self.waiting_for_answer = True
        self.waiting_for_name = False
        self.new_name = None
        self.new_question = None
        self.new_answer = None
        self.new_parent_answer = None
        self.last_answer = self.current_answer

    def win(self):
        answer = 'Это точно ' + self.variants[str(self.current_variant)]['name'] + '!'
        self.lbl.configure(text=answer)
        self.log.append(answer)
        self.yes_no_frame.pack_forget()
        self.log_frame.pack(pady=10)

    def process_answer(self):
        if not self.waiting_for_answer:
            return

        self.waiting_for_answer = False

        if self.current_variant is None:
            if self.current_answer == '1':
                self.current_variant = 1
                self.ask_name()
            else:
                self.cant_start()
            return

        if not self.waiting_for_name:
            if str(self.current_answer) == '1':
                self.variants = self.variants[str(self.current_variant)]['yes']
            else:
                self.variants = self.variants[str(self.current_variant)]['no']
            if len(self.variants) > 0:
                self.current_variant = next(iter(self.variants))
                self.ask_name()
            else:
                self.give_up()

        else:
            if self.current_answer == '1':
                self.win()
            else:
                self.variants = self.variants[str(self.current_variant)]['no']
                if len(self.variants) > 0:
                    self.current_variant = next(iter(self.variants))
                    self.ask_question()
                else:
                    self.give_up()

    def get_db_path(self):
        if getattr(sys, 'frozen', False):
            base_path = os.path.dirname(sys.executable)
        else:
            base_path = os.path.dirname(os.path.abspath(__file__))

        return os.path.join(base_path, 'database.db')

    def get_db_connection(self):
        db_path = self.get_db_path()
        conn = sqlite3.connect(db_path)
        conn.row_factory = sqlite3.Row
        return conn

    def init_db(self):
        db_path = self.get_db_path()

        os.makedirs(os.path.dirname(db_path), exist_ok=True)

        conn = self.get_db_connection()
        cursor = conn.cursor()

        cursor.execute("""
                       CREATE TABLE IF NOT EXISTS variants
                       (
                           id
                           VARCHAR
                           PRIMARY
                           KEY,
                           parent_id
                           VARCHAR,
                           parent_answer
                           TINYINT,
                           is_question
                           TINYINT,
                           name
                           VARCHAR
                           NOT
                           NULL
                           UNIQUE
                       )
                       """)

        cursor.execute("SELECT COUNT(*) as count FROM variants")
        count = cursor.fetchone()['count']

        if count == 0:
            cursor.execute("""
                           INSERT INTO variants (id, parent_id, parent_answer, is_question, name)
                           VALUES (1, NULL, NULL, 0, 'Феникс')
                           """)

        conn.commit()
        conn.close()

    def load_creatures_from_db(self):
        conn = self.get_db_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM variants")
        creatures = cursor.fetchall()
        conn.close()
        return creatures

    def run(self):
        self.root.mainloop()


if __name__ == "__main__":
    game = Game()
    game.run()
