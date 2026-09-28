from PySide6.QtCore import Qt, QTimer
from PySide6.QtGui import QFont, QKeySequence, QShortcut
from PySide6.QtWidgets import (
    QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, QPushButton,
    QLabel, QSpinBox, QListWidget, QGroupBox, QMessageBox
)
from randomizer import Randomizer


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("pravKontu")
        self.randomizer = Randomizer()
        self.animation_timer = QTimer(self)
        self.animation_timer.setSingleShot(True)
        self.animation_timer.timeout.connect(self._tick)
        self.animation_steps = []
        self.step_index = 0
        self.final_number = None
        self._build_ui()
        self._setup_shortcuts()

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
        range_layout.addWidget(self.low_spin)
        range_layout.addWidget(QLabel("по"))
        self.high_spin = QSpinBox()
        self.high_spin.setRange(1, 36)
        self.high_spin.setValue(36)
        range_layout.addWidget(self.high_spin)
        apply_btn = QPushButton("Применить")
        apply_btn.clicked.connect(self._apply_range)
        range_layout.addWidget(apply_btn)
        left.addWidget(range_box)

        self.number_label = QLabel("?")
        self.number_label.setAlignment(Qt.AlignCenter)
        self.number_label.setFont(QFont("Arial", 76, QFont.Bold))
        left.addWidget(self.number_label, 1)

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
        self.resize(620, 420)

    def _setup_shortcuts(self):
        QShortcut(QKeySequence(Qt.Key_Return), self, activated=self._start_pick)
        QShortcut(QKeySequence(Qt.Key_Enter), self, activated=self._start_pick)

    def _apply_range(self):
        if self.animation_timer.isActive():
            return
        low = self.low_spin.value()
        high = self.high_spin.value()
        if low >= high:
            QMessageBox.warning(self, "Ошибка", "Нижняя граница должна быть меньше верхней")
            return
        self.randomizer.set_range(low, high)
        self.history_list.clear()
        self.number_label.setText("?")

    def _start_pick(self):
        if self.animation_timer.isActive():
            return
        self.final_number = self.randomizer.pick()
        self.pick_btn.setEnabled(False)
        self.animation_steps = self._build_steps()
        self.step_index = 0
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
            self.history_list.addItem(str(self.final_number))
            self.history_list.scrollToBottom()
            self.pick_btn.setEnabled(True)
            return
        self.number_label.setText(str(self.randomizer.flash_number()))
        interval = self.animation_steps[self.step_index]
        self.step_index += 1
        self.animation_timer.start(interval)

    def _reset_history(self):
        if self.animation_timer.isActive():
            return
        self.randomizer.reset_history()
        self.history_list.clear()
        self.number_label.setText("?")