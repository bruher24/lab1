import tkinter as tk
from tkinter import *
import sqlite3


class Game:
    def __init__(self):
        # Создаем таблицу, если ее еще нет
        self.init_db()

        # Загружаем существующие варианты
        self.variants = self.load_creatures_from_db()

        # Инициализируем переменные
        self.current_answer = None
        self.waiting_for_answer = False
        self.current_variant = -1
        self.waiting_for_name = False
        self.text_buffer = None
        self.new_name = None
        self.new_question = None
        self.new_answer = None
        self.adding_new = False
        self.log = []
        # Создаем основное окно
        self.root = tk.Tk()
        self.root.title('Quiz')
        self.root.geometry('450x300')

        # Создаем лейбл
        self.lbl = tk.Label(self.root, text='Нажмите "Начать игру"')
        self.lbl.place(x=225, y=100, anchor='center')

        # Создаем кнопку начала игры
        self.btn_start_game = tk.Button(self.root, text='Начать игру', command=self.play)
        self.btn_start_game.place(x=225, y=150, anchor='center')

        # Кнопка перезапуска
        self.btnReset = tk.Button(self.root, text='Перезапуск', fg='black', command=self.reset)
        self.btnReset.place(x=390, y=280, anchor='center')

        # Кнопка отображения лога игры
        self.btnLog = tk.Button(self.root, text='Показать путь до ответа', fg='black', command=self.show_log)

        # Кнопка отображения схемы БД
        self.btnBD = tk.Button(self.root, text='Показать БД', fg='black', command=self.show_bd)

        # Создаем кнопки Да/Нет
        self.btn_yes = tk.Button(self.root, text='Да', fg='green', command=self.yes_clicked)
        self.btn_no = tk.Button(self.root, text='Нет', fg='red', command=self.no_clicked)

        # Создаем поле для ввода
        self.text_input = tk.Entry(self.root, width=20)

        # Создаем кнопку ввода
        self.btn_confirm = tk.Button(self.root, text='Подтвердить', fg='green', command=self.confirm_clicked)

    # Запускаем игру
    def play(self):
        self.lbl.configure(text='Вы загадали животное?')
        self.btn_start_game.place_forget()

        self.btn_yes.place(x=175, y=150, anchor='center')
        self.btn_no.place(x=275, y=150, anchor='center')

        self.waiting_for_answer = True

    # Перезапуск игры
    def reset(self):
        self.current_answer = None
        self.waiting_for_answer = False
        self.current_variant = -1
        self.waiting_for_name = False
        self.text_buffer = None
        self.new_name = None
        self.new_question = None
        self.new_answer = None
        self.adding_new = False
        self.lbl.configure(text='Нажмите "Начать игру"')
        self.lbl.place(x=225, y=100, anchor='center')
        self.btn_start_game.place(x=225, y=150, anchor='center')
        self.btn_yes.place_forget()
        self.btn_no.place_forget()
        self.btn_confirm.place_forget()
        self.text_input.place_forget()
        self.btnLog.place_forget()

    # Отображение лога
    def show_log(self):
        output = ''
        self.log.pop(0)
        for word in self.log:
            if word == '0':
                word = 'Нет'
            elif word == '1':
                word = 'Да'
            output += word + '->'

        output = output[:-2]
        self.btnLog.place_forget()
        self.lbl.configure(text=output)

    # Отображение схемы БД
    def show_bd(self):
        print(1)

    # Нажатие "Да"
    def yes_clicked(self):
        self.current_answer = '1'
        self.log.append(self.current_answer)
        if not self.adding_new:
            self.process_answer()
        else:
            self.adding_new = False
            self.new_creature()

    # Нажатие "Нет"
    def no_clicked(self):
        self.current_answer = '0'
        self.log.append(self.current_answer)
        if not self.adding_new:
            self.process_answer()
        else:
            self.adding_new = False
            self.new_creature()

    # Нажатие "Подтвердить"
    def confirm_clicked(self):
        self.adding_new = True
        self.text_buffer = self.text_input.get().strip()
        if self.text_buffer:
            self.new_creature()

    # Спрашиваем данные о новом существе
    def new_creature(self):
        if self.new_name is None:
            self.new_name = self.text_buffer.capitalize()
            self.lbl.configure(text='Что отличает ' + self.new_name + '?')
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
        elif self.new_answer is None:
            self.new_answer = self.current_answer
            self.save_new_creature()
            self.lbl.configure(text='Спасибо! Я узнал новое животное!')
            self.btn_no.place_forget()
            self.btn_yes.place_forget()

    # Сохраняем новое существо в БД
    def save_new_creature(self):
        conn = self.get_db_connection()
        cursor = conn.cursor()

        cursor.execute("INSERT INTO variants (name, question, answer) VALUES (?, ?, ?)",
                       (self.new_name, self.new_question, self.new_answer))
        conn.commit()
        conn.close()
        self.variants = self.load_creatures_from_db()

    # Задаем вопрос, указанный для существа
    def ask_question(self):
        question = self.variants[self.current_variant]['question']
        self.lbl.configure(text=question)
        self.waiting_for_answer = True
        self.log.append(question)

    # Предполагаем имя существа
    def ask_name(self):
        question = 'Это ' + self.variants[self.current_variant]['name'] + '?'
        self.lbl.configure(text=question)
        self.waiting_for_answer = True
        self.waiting_for_name = True
        self.log.append(question)

    # Если игрок не загадал животное
    def cant_start(self):
        self.lbl.configure(text='Вы должны загадать животное, чтобы начать!')
        self.btn_no.place_forget()
        self.btn_yes.place_forget()

    # Сдаемся и просим добавить существо
    def give_up(self):
        self.lbl.configure(text="Я сдаюсь! Какое животное вы загадали?")
        self.btn_yes.place_forget()
        self.btn_no.place_forget()
        self.text_input.place(x=225, y=130, anchor='center')
        self.btn_confirm.place(x=225, y=180, anchor='center')
        self.waiting_for_answer = True
        self.waiting_for_name = False
        self.new_name = None
        self.new_question = None
        self.new_answer = None

    # Побеждаем
    def win(self):
        answer = 'Это точно ' + self.variants[self.current_variant]['name'] + '!'
        self.lbl.configure(text=answer)
        self.log.append(answer)
        self.btn_yes.place_forget()
        self.btn_no.place_forget()
        self.btnLog.place(x=225, y=100, anchor='center')

    # Обрабатываем ответ
    def process_answer(self):
        if not self.waiting_for_answer:
            return

        self.waiting_for_answer = False

        # Начало игры - первая попытка угадать
        if self.current_variant == -1:
            if self.current_answer == '1':
                self.current_variant += 1
                self.ask_name()
            else:
                self.cant_start()
            return

        # Процесс игры - задаем вопросы
        if not self.waiting_for_name:
            if str(self.current_answer) == str(self.variants[self.current_variant]['answer']):
                self.ask_name()
            else:
                self.current_variant += 1
                if self.current_variant < len(self.variants):
                    self.ask_question()
                else:
                    self.give_up()

        # Попытка угадать название
        else:
            if self.current_answer == '1':
                self.win()
            else:
                self.current_variant += 1
                if self.current_variant < len(self.variants):
                    self.ask_question()
                    self.waiting_for_name = False
                else:
                    self.give_up()

    # Подключение к БД
    def get_db_connection(self):
        conn = sqlite3.connect('database.db')
        conn.row_factory = sqlite3.Row
        return conn

    # Создаем таблицу и начальные данные, если не существует
    def init_db(self):
        conn = self.get_db_connection()
        cursor = conn.cursor()

        cursor.execute("""
            CREATE TABLE IF NOT EXISTS variants (
                id INTEGER PRIMARY KEY,
                name VARCHAR NOT NULL UNIQUE,
                question VARCHAR NOT NULL,
                answer TINYINT NOT NULL
            )
        """)

        cursor.execute("""
            INSERT OR IGNORE INTO variants (name, question, answer)
            VALUES ('Кот', 'Мяукает?', 1)
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

    # Запуск всего приложения
    def run(self):
        self.root.mainloop()


if __name__ == "__main__":
    game = Game()
    game.run()
