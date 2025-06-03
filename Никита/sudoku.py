
import sys
import os
import random
import pandas as pd
from PyQt6 import QtGui, QtWidgets
from PyQt6.QtCore import Qt, QTimer
from PyQt6.QtWidgets import (
    QApplication, QMainWindow, QMessageBox, QLineEdit, QDialog,
    QVBoxLayout, QPushButton, QLabel
)
import time
from PyQt6 import uic

uifile = os.path.join(os.path.dirname(__file__), 'sudoku.ui')
Form, Base = uic.loadUiType(uifile)
class GeetSudokuTable:
    @staticmethod
    def read_file(filename='sudoku.csv'):
        try:
            fl = pd.read_csv(filename, header=None, sep=',', dtype=str)
            sudoku_list = []
            for row in fl.values.tolist():
                cleaned_row = [num.strip() for num in row if isinstance(num, str)]
                if len(cleaned_row) == 81:
                    int_row = [int(num) if num.isdigit() else 0 for num in cleaned_row]
                    sudoku_list.append(int_row)
                else:
                    print(f"GeetSudokuTable.read_file: Invalid row length: {len(cleaned_row)}, skipping.")
            return sudoku_list
        except FileNotFoundError:
            print(f"GeetSudokuTable.read_file: Error: File not found: {filename}")
            return None
        except Exception as e:
            print(f"GeetSudokuTable.read_file: Error: {e}")
            return None

    @staticmethod
    def take_table(filename='sudoku.csv'):
        data = GeetSudokuTable.read_file(filename)
        if data is None:
            return []
        tables = []
        for row in data:
            if len(row) == 81:
                table = row[:81]
                tables.append(table)
        if not tables:
            print(f"GeetSudokuTable.take_table: Error: No valid tables found in {filename}")
            return []
        sudoku_table = random.choice(tables)
        if not all(len(row) == 9 for row in [sudoku_table[i:i + 9] for i in range(0, 81, 9)]):
            print("GeetSudokuTable.take_table: Error: Sudoku table is not 9x9.")
            return []
        return [sudoku_table[i:i + 9] for i in range(0, 81, 9)]


class DifficultyDialog(QDialog):
    def __init__(self):
        super().__init__()
        self.setFixedHeight(200)
        self.setFixedWidth(300)
        self.setWindowTitle("DifficultyDialog")

        # Создание кнопок
        self.btn_trivial = QPushButton("Обычный", self)
        self.btn_timer = QPushButton("Режим с таймером", self)

        # Установка макета
        layout = QVBoxLayout()
        message = QLabel("Выберите сложность:")
        layout.addWidget(message)
        layout.addWidget(self.btn_trivial)
        layout.addWidget(self.btn_timer)
        self.setLayout(layout)

        # Подключение сигналов к слотам
        self.btn_trivial.clicked.connect(self.handle_trivial_click)
        self.btn_timer.clicked.connect(self.handle_timer_click)

    def handle_trivial_click(self):
        self.setDifficulty('trivial')

    def handle_timer_click(self):
        self.setDifficulty('timer')

    def setDifficulty(self, diff):
        self.difficulty = diff
        self.accept()

    def getDifficulty(self):
        return self.difficulty


class MainWindow(QMainWindow, Form):
    PATHS = {
        "trivial": 'sudoku.csv',
        "timer": 'sudoku.csv'
    }
    DIFFICULTY = "trivial"

    def __init__(self, difficulty):
        super(MainWindow, self).__init__()
        self.DIFFICULTY = difficulty
        # Initialize UI FIRST
        self.ui = Form()
        self.ui.setupUi(self)

        self.board = None
        self.game_frame = QtWidgets.QWidget()
        self.layout = QtWidgets.QGridLayout(self.game_frame)

        self.countdown_time = 300
        self.elapsed_time = self.countdown_time
        self.timer_running = False
        self.timer = QTimer(self)
        self.timer.timeout.connect(self.updateTimer)

        self.setWindowTitle("Sudoku")
        widget_size = self.ui.widget.size()
        self.setFixedSize(widget_size)

        self.ui.pushButtonReset.clicked.connect(self.reset)
        self.ui.pushButtonCheck.clicked.connect(self.check_sudoku)
        self.game_frame = QtWidgets.QWidget()

        self.ui.pushButton.clicked.connect(self.close_game)
        self.boards = self.getSudokuData(self.PATHS[self.DIFFICULTY])
        if self.boards is not None:
            self.createGame()
        else:
            self.showMessageBox("Error", "Could not load boards")
        if self.DIFFICULTY == "timer":
            self.ui.lcdNumber.show()
            self.elapsed_time = self.countdown_time
            self.start_timer()
            self.updateTimer()
        else:
            self.ui.lcdNumber.hide()

    def close_game(self):
        self.hide()
        QTimer.singleShot(0, self.showDifficultyDialog)

    def showDifficultyDialog(self):
        diff_dialog = DifficultyDialog()
        if diff_dialog.exec() == QDialog.DialogCode.Accepted:
            selected_difficulty = diff_dialog.difficulty
            if self.DIFFICULTY != selected_difficulty:
                self.DIFFICULTY = selected_difficulty
                self.stopTimer()
                if self.DIFFICULTY == "timer":
                    self.ui.lcdNumber.show()
                    self.elapsed_time = self.countdown_time
                    self.start_timer()
                    self.updateTimer()
                else:
                    self.ui.lcdNumber.hide()
                try:
                    self.boards = self.getSudokuData(self.PATHS[self.DIFFICULTY])
                    if self.boards is not None:
                        self.createGame()  # create the game when you change the difficulty
                    else:
                        self.showMessageBox("Error", "Could not load boards")
                except Exception as e:
                    self.showMessageBox("Error", "An unexpected error occurred: Check console.")
    def start_timer(self):
        if not self.timer_running:
            self.timer_running = True
            self.timer.start(1000)

    def stopTimer(self):
        if self.timer_running:
            self.timer_running = False
            self.timer.stop()

    def updateTimer(self):
        if self.timer_running:
            self.elapsed_time -= 1
            minutes, seconds = divmod(self.elapsed_time, 60)
            self.ui.lcdNumber.display(f"{minutes:02}:{seconds:02}")
            if self.elapsed_time <= 0:
                self.stopTimer()
                self.showMessageBox("Время закончилось!")

    def check_sudoku(self):
        solved = True
        self.stopTimer()
        timer_check_failed = False
        for i in range(9):
            for j in range(9):
                if self.timer_running and self.elapsed_time <= 0:
                    timer_check_failed = True
                    break
                val = self.getBoxDataIndex(i, j)
                self.setBoxData(i, j, 0)
                if not self.check(i, j, val):
                    solved = False
                    break
                self.setBoxData(i, j, val)
            if timer_check_failed:
                break
        if timer_check_failed:
            self.showMessageBox("Время закончилось!")
        elif not solved:
            self.showMessageBox("Судоку не решено!")
        else:
            self.showMessageBox("Вы решили судоку верно!")
            self.createGame()

    def createGame(self):
        if self.boards:
            self.board = self.boards
            try:
                self.create_sudoku_grid()
            except Exception as e:
                self.showMessageBox("Error","Could not create Sudoku grid. See console output for details.")
        else:
            self.showMessageBox("No Boards Left", "No boards found.")

    def create_sudoku_grid(self, ms=0):
        for i in range(9):
            for j in range(9):
                widget_name = f"p{i}{j}"
                widget = self.findChild(QtWidgets.QLineEdit, widget_name)
                if widget is not None:
                    widget.setText(str(self.board[i][j]) if self.board[i][j] != 0 else " ")
                    widget.setAlignment(Qt.AlignmentFlag.AlignCenter)
                    widget.setEnabled(self.board[i][j] == 0) # enable only when the board is 0.
                    if ms > 0:
                        time.sleep(ms / 20)

    def reset(self):
        self.stopTimer()
        self.clear()
        self.createGame()

    def clear(self):
        for i in range(9):
            for j in range(9):
                try:
                    cell_widget = getattr(self.ui, f"p{i}{j}")
                    if isinstance(cell_widget, QLineEdit):
                        cell_widget.clear()
                except AttributeError:
                    pass

    def solve(self, ms=0) -> bool:
        for i in range(9):
            for j in range(9):
                if self.getBoxDataIndex(i, j) == 0:
                    for val in range(1, 10):
                        time.sleep(ms)
                        if self.check(i, j, val):
                            self.setBoxData(i, j, val)
                            if self.solve(ms):
                                return True
                            self.setBoxData(i, j, 0)
                    return False
        return True

    def getBoxDataIndex(self, i, j) -> int:
        try:
            return int(getattr(self.ui, f"p{i}{j}").text())
        except (AttributeError, ValueError):
            return 0

    def setBoxData(self, i, j, value):
        try:
            getattr(self.ui, f"p{i}{j}").setText(str(value) if value != 0 else "")
        except AttributeError:
            pass

    def check(self, i, j, val):
        if val == 0:
            return True

        # Check if the value is valid in the row
        for col in range(9):
            if self.getBoxDataIndex(i, col) == val and col != j:
                return False

        # Check if the value is valid in the column
        for row in range(9):
            if self.getBoxDataIndex(row, j) == val and row != i:
                return False

        # Check if the value is valid in the 3x3 subgrid
        subgrid_row = (i // 3) * 3
        subgrid_col = (j // 3) * 3
        for row in range(subgrid_row, subgrid_row + 3):
            for col in range(subgrid_col, subgrid_col + 3):
                if self.getBoxDataIndex(row, col) == val and (row, col) != (i, j):
                    return False

        return True

    def showMessageBox(self, title, message = None):
        dlg = QMessageBox(self)
        dlg.setWindowTitle(title)
        if message is not None:
            dlg.setText(message)
        button = dlg.exec()

    def getSudokuData(self, file_path):
        try:
            board = GeetSudokuTable.take_table(filename=file_path)
            if not board:
                return None
            return board
        except Exception as e:
            return None

def main():
    app = QApplication(sys.argv)
    diff_dialog = DifficultyDialog()
    if diff_dialog.exec() == QDialog.DialogCode.Accepted:
        difficulty = diff_dialog.getDifficulty()
        window = MainWindow(difficulty)
        window.show()
        sys.exit(app.exec())


if __name__ == '__main__':
    main()