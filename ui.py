from PySide6.QtCore import Qt, QTimer, QSettings
from PySide6.QtGui import QFont, QKeySequence, QShortcut, QGuiApplication
from PySide6.QtWidgets import (
    QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, QPushButton,
    QLabel, QSpinBox, QListWidget, QGroupBox, QMessageBox,
    QDialog, QPlainTextEdit
)
from randomizer import Randomizer


class LogDialog(QDialog):
    def __init__(self, text, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Журнал")
        self.resize(600, 400)
        layout = QVBoxLayout(self)
        editor = QPlainTextEdit()
        editor.setReadOnly(True)
        editor.setPlainText(text if text else "Журнал пока пуст")
        layout.addWidget(editor)
        close_btn = QPushButton("Закрыть")
        close_btn.clicked.connect(self.accept)
        layout.addWidget(close_btn)


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("pravKontu")
        self.settings = QSettings("pravKontu", "pravKontu")
        self.randomizer = Randomizer()
        self.animation_timer = QTimer(self)
        self.animation_timer.setSingleShot(True)
        self.animation_timer.timeout.connect(self._tick)
        self.animation_steps = []
        self.step_index = 0
        self.final_number = None
        self.current_display = "?"
        self._build_ui()
        self._setup_shortcuts()
        self._load_settings()

    def _build_ui(self):
        central = QWidget()
        self.setCentralWidget(central)
        root = QHBoxLayout(central)

        left = QVBoxLayout()

        range_box = QGroupBox("Диапазон")
        range_layout = QHBoxLayout(range_box)
        range_layout.addWidget(QLabel("от"))
        self.low_spin = QSpinBox()
        self.low_spin.setRange(1, 36)
        self.low_spin.setValue(1)
        self.low_spin.valueChanged.connect(self._on_low_changed)
        range_layout.addWidget(self.low_spin)
        range_layout.addWidget(QLabel("по"))
        self.high_spin = QSpinBox()
        self.high_spin.setRange(1, 36)
        self.high_spin.setValue(36)
        self.high_spin.valueChanged.connect(self._on_high_changed)
        range_layout.addWidget(self.high_spin)
        apply_btn = QPushButton("Применить")
        apply_btn.clicked.connect(self._apply_range)
        range_layout.addWidget(apply_btn)
        left.addWidget(range_box)

        self.number_label = QLabel("?")
        self.number_label.setAlignment(Qt.AlignCenter)
        self.number_label.setFont(QFont("Arial", 76, QFont.Bold))
        left.addWidget(self.number_label, 1)

        self.counter_label = QLabel("")
        self.counter_label.setAlignment(Qt.AlignCenter)
        self.counter_label.setStyleSheet("color: #888; font-size: 12px;")
        left.addWidget(self.counter_label)

        self.pick_btn = QPushButton("Выбрать")
        self.pick_btn.clicked.connect(self._start_pick)
        left.addWidget(self.pick_btn)

        hint = QLabel("Кроме тыкания ЛКМ, можете нажать еще и Enter")
        hint.setAlignment(Qt.AlignCenter)
        hint.setStyleSheet("color: #666; font-size: 11px;")
        left.addWidget(hint)

        right = QVBoxLayout()
        history_box = QGroupBox("История")
        history_layout = QVBoxLayout(history_box)
        self.history_list = QListWidget()
        history_layout.addWidget(self.history_list)

        log_btn = QPushButton("Показать лог")
        log_btn.clicked.connect(self._show_log)
        history_layout.addWidget(log_btn)

        reset_btn = QPushButton("Сбросить историю")
        reset_btn.clicked.connect(self._reset_history)
        history_layout.addWidget(reset_btn)

        right.addWidget(history_box)

        root.addLayout(left, 3)
        root.addLayout(right, 1)

        self.setStyleSheet(
            "QMainWindow, QWidget { background: #f5f5f5; color: #222; }"
            "QPushButton { padding: 8px; font-size: 14px; }"
            "QGroupBox { font-size: 12px; }"
        )
        self.resize(620, 460)
        self._update_counter()

    def _setup_shortcuts(self):
        QShortcut(QKeySequence(Qt.Key_Return), self, activated=self._start_pick)
        QShortcut(QKeySequence(Qt.Key_Enter), self, activated=self._start_pick)
        QShortcut(QKeySequence.Copy, self, activated=self._copy_number)

    def _load_settings(self):
        low = int(self.settings.value("low", 1))
        high = int(self.settings.value("high", 36))
        if low < 1 or low > 36:
            low = 1
        if high < 1 or high > 36:
            high = 36
        if low >= high:
            low, high = 1, 36
        self.low_spin.blockSignals(True)
        self.high_spin.blockSignals(True)
        self.low_spin.setValue(low)
        self.high_spin.setValue(high)
        self.low_spin.blockSignals(False)
        self.high_spin.blockSignals(False)
        self.randomizer.set_range(low, high)
        self._update_counter()

    def _save_settings(self):
        self.settings.setValue("low", self.randomizer.low)
        self.settings.setValue("high", self.randomizer.high)

    def _on_low_changed(self, value):
        if value >= self.high_spin.value():
            self.high_spin.blockSignals(True)
            new_high = value + 1
            if new_high > 36:
                self.low_spin.blockSignals(True)
                self.low_spin.setValue(35)
                self.low_spin.blockSignals(False)
                new_high = 36
            self.high_spin.setValue(new_high)
            self.high_spin.blockSignals(False)

    def _on_high_changed(self, value):
        if value <= self.low_spin.value():
            self.low_spin.blockSignals(True)
            new_low = value - 1
            if new_low < 1:
                self.high_spin.blockSignals(True)
                self.high_spin.setValue(2)
                self.high_spin.blockSignals(False)
                new_low = 1
            self.low_spin.setValue(new_low)
            self.low_spin.blockSignals(False)

    def _apply_range(self):
        if self.animation_timer.isActive():
            return
        low = self.low_spin.value()
        high = self.high_spin.value()
        if low >= high:
            QMessageBox.warning(self, "Ошибка", "Нижняя граница должна быть меньше верхней")
            return
        self.randomizer.set_range(low, high)
        self._save_settings()
        self.history_list.clear()
        self.current_display = "?"
        self.number_label.setText("?")
        self._update_counter()

    def _start_pick(self):
        if self.animation_timer.isActive():
            return
        self.final_number = self.randomizer.pick()
        self.pick_btn.setEnabled(False)
        self.animation_steps = self._build_steps()
        self.step_index = 0
        self.current_display = str(self.final_number)
        self.number_label.setText(str(self.final_number))
        self.animation_timer.start(self.animation_steps[0])

    def _build_steps(self):
        total_ms = 5000
        n = 45
        raw = []
        for i in range(n):
            t = i / (n - 1)
            raw.append(25 + int((t ** 3) * 450))
        scale = total_ms / sum(raw)
        return [max(20, int(s * scale)) for s in raw]

    def _tick(self):
        if self.step_index >= len(self.animation_steps):
            self.number_label.setText(str(self.final_number))
            self.current_display = str(self.final_number)
            self.history_list.addItem(str(self.final_number))
            self.history_list.scrollToBottom()
            self.pick_btn.setEnabled(True)
            self._update_counter()
            return
        self.number_label.setText(str(self.randomizer.flash_number()))
        interval = self.animation_steps[self.step_index]
        self.step_index += 1
        self.animation_timer.start(interval)

    def _update_counter(self):
        self.counter_label.setText(
            f"осталось в мешке: {self.randomizer.remaining()} из {self.randomizer.total()}"
        )

    def _copy_number(self):
        if self.current_display and self.current_display != "?":
            QGuiApplication.clipboard().setText(self.current_display)

    def _show_log(self):
        text = self.randomizer.read_log()
        dialog = LogDialog(text, self)
        dialog.exec()

    def _reset_history(self):
        if self.animation_timer.isActive():
            return
        answer = QMessageBox.question(
            self,
            "Сбросить историю",
            "Точно сбросить историю и заново наполнить мешок?",
            QMessageBox.Yes | QMessageBox.No,
            QMessageBox.No
        )
        if answer != QMessageBox.Yes:
            return
        self.randomizer.reset_history()
        self.history_list.clear()
        self.current_display = "?"
        self.number_label.setText("?")
        self._update_counter()