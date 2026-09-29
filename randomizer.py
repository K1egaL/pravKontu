import secrets
import sys
from datetime import datetime
from pathlib import Path


class Randomizer:
    def __init__(self, low=1, high=36):
        self.low = low
        self.high = high
        self.bag = []
        self.history = []
        self._refill()

    def _refill(self):
        self.bag = list(range(self.low, self.high + 1))

    def set_range(self, low, high):
        self.low = low
        self.high = high
        self.history = []
        self._refill()
        self._log(f"диапазон изменен на {low}-{high}")

    def pick(self):
        if not self.bag:
            self._refill()
            self._log("мешок пуст, новый круг")
        index = secrets.randbelow(len(self.bag))
        number = self.bag.pop(index)
        self.history.append(number)
        self._log(f"выпало {number}, осталось в мешке {len(self.bag)}")
        return number

    def flash_number(self):
        return secrets.randbelow(self.high - self.low + 1) + self.low

    def reset_history(self):
        self.history = []
        self._refill()
        self._log("история сброшена, мешок полон")

    def remaining(self):
        return len(self.bag)

    def total(self):
        return self.high - self.low + 1

    def _log_path(self):
        if getattr(sys, "frozen", False):
            base = Path(sys.executable).parent
        else:
            base = Path(__file__).parent
        return base / "pravKontu_log.txt"

    def read_log(self):
        try:
            return self._log_path().read_text(encoding="utf-8")
        except OSError:
            return ""

    def _log(self, message):
        try:
            stamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            with open(self._log_path(), "a", encoding="utf-8") as f:
                f.write(f"{stamp} - {message}\n")
        except OSError:
            pass