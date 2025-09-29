import tkinter as tk
import uuid
from tkinter import ttk
from tkinter import *
import sqlite3
from tkinter import messagebox


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

        self.root = tk.Tk()
        self.root.title('Угадайка: мифические существа')
        self.root.geometry('450x300')

        self.lbl = tk.Label(self.root, text='Нажмите "Начать игру"')
        self.lbl.place(x=225, y=100, anchor='center')

        self.btn_start_game = tk.Button(self.root, text='Начать игру', command=self.play)
        self.btn_start_game.place(x=225, y=150, anchor='center')

        self.btnReset = tk.Button(self.root, text='Перезапуск', fg='black', command=self.reset)
        self.btnReset.place(x=390, y=280, anchor='center')

        self.btn_log = tk.Button(self.root, text='Показать путь до ответа', fg='black', command=self.show_log)

        self.btn_bd = tk.Button(self.root, text='Показать БД', fg='black', command=self.show_bd)
        self.btn_bd.place(x=390, y=240, anchor='center')

        self.btn_search = tk.Button(self.root, text='Поиск существа', fg='black', command=self.open_search_window)
        self.btn_search.place(x=70, y=280, anchor='center')

        self.btn_yes = tk.Button(self.root, text='Да', fg='green', command=self.yes_clicked)
        self.btn_no = tk.Button(self.root, text='Нет', fg='red', command=self.no_clicked)

        self.text_input = tk.Entry(self.root, width=20)

        self.btn_confirm = tk.Button(self.root, text='Подтвердить', fg='green', command=self.confirm_clicked)

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
        self.btn_start_game.place_forget()

        self.btn_yes.place(x=175, y=150, anchor='center')
        self.btn_no.place(x=275, y=150, anchor='center')

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
        self.lbl.configure(text='Нажмите "Начать игру"')
        self.lbl.place(x=225, y=100, anchor='center')
        self.btn_start_game.place(x=225, y=150, anchor='center')
        self.btn_yes.place_forget()
        self.btn_no.place_forget()
        self.btn_confirm.place_forget()
        self.text_input.place_forget()
        self.btn_log.place_forget()
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

        if output[-2:] != '\n':
            output = output[:-2]

        self.btn_log.place_forget()
        self.lbl.configure(text=output)

    def show_bd(self):
        db_window = tk.Toplevel(self.root)
        db_window.title("Структура базы данных")
        db_window.geometry("600x400")

        tree_frame = ttk.Frame(db_window)
        tree_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)

        tree = ttk.Treeview(tree_frame, columns=("type", "answer"), show="tree headings")
        tree.column("#0", width=300, anchor=tk.W)
        tree.column("type", width=100, anchor=tk.CENTER)
        tree.column("answer", width=100, anchor=tk.CENTER)

        tree.heading("#0", text="Вопрос / Существо")
        tree.heading("type", text="Тип")
        tree.heading("answer", text="Ответ родителя")

        tree.tag_configure('question', background='#e6f3ff')
        tree.tag_configure('creature', background='#f0f8e6')

        scrollbar = ttk.Scrollbar(tree_frame, orient=tk.VERTICAL, command=tree.yview)
        tree.configure(yscrollcommand=scrollbar.set)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

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
                                  values=(item_type, answer_text), tags=(tag))
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

        text_widget = tk.Text(path_window, wrap=tk.WORD)
        text_widget.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)

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

        text_widget.config(state=tk.DISABLED)

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
            self.btn_confirm.place_forget()
            self.text_input.delete(0, END)
            self.text_input.place_forget()
        elif self.new_name is None:
            self.new_name = self.text_buffer.capitalize()
            self.lbl.configure(text='Что отличает ' + self.new_name + ' от ' + self.current_obj['name'] + '?')
            self.text_input.delete(0, END)
            self.waiting_for_answer = True
        elif self.new_question is None:
            self.new_question = self.text_buffer.capitalize()
            if not self.new_question.endswith('?'):
                self.new_question += '?'
            self.lbl.configure(text='Для ' + self.new_name + ' ответ "Да" или "Нет"?')
            self.text_input.place_forget()
            self.btn_confirm.place_forget()
            self.btn_yes.place(x=175, y=150, anchor='center')
            self.btn_no.place(x=275, y=150, anchor='center')
            self.text_input.delete(0, END)
            self.waiting_for_answer = True
        elif self.new_parent_answer is None:
            self.new_parent_answer = self.current_answer
            self.save_new_creature()
            self.lbl.configure(text='Спасибо! Я узнал новое существо!')
            self.btn_no.place_forget()
            self.btn_yes.place_forget()

    def save_new_creature(self):
        conn = self.get_db_connection()
        cursor = conn.cursor()

        new_parent_id = self.current_obj['id']

        if str(self.current_obj['is_question']) == '0':
            new_parent_id = str(uuid.uuid4())
            cursor.execute("""
                INSERT OR IGNORE INTO variants (id, name, parent_answer, parent_id, is_question)
                VALUES (?, ?, ?, ?, ?)
            """,
                           (new_parent_id, self.new_question, self.last_answer, str(self.current_obj['id']), 1))

        cursor.execute("""
                    INSERT OR IGNORE INTO variants (id, name, parent_answer, parent_id, is_question)
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
        self.btn_no.place_forget()
        self.btn_yes.place_forget()

    def give_up(self):
        self.lbl.configure(text="Я сдаюсь! Какое существо вы загадали?")
        self.btn_yes.place_forget()
        self.btn_no.place_forget()
        self.text_input.place(x=225, y=130, anchor='center')
        self.btn_confirm.place(x=225, y=180, anchor='center')
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
        self.btn_yes.place_forget()
        self.btn_no.place_forget()
        self.btn_log.place(x=225, y=150, anchor='center')

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

    def get_db_connection(self):
        import sys
        import os

        if getattr(sys, 'frozen', False):
            base_path = sys._MEIPASS
        else:
            base_path = os.path.dirname(os.path.abspath(__file__))

        db_path = os.path.join(base_path, 'database.db')
        conn = sqlite3.connect(db_path)
        conn.row_factory = sqlite3.Row
        return conn

    def init_db(self):
        conn = self.get_db_connection()
        cursor = conn.cursor()

        cursor.execute("""
            CREATE TABLE IF NOT EXISTS variants (
                id VARCHAR PRIMARY KEY,
                parent_id VARCHAR,
                parent_answer TINYINT,
                is_question TINYINT,
                name VARCHAR NOT NULL UNIQUE
            )
        """)

        cursor.execute("""
            INSERT OR IGNORE INTO variants (id, parent_id, parent_answer, is_question, name)
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
