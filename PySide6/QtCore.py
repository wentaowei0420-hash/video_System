class _BoundSignal:
    def __init__(self):
        self._slots = []

    def connect(self, slot):
        if callable(slot):
            self._slots.append(slot)

    def emit(self, *args, **kwargs):
        for slot in list(self._slots):
            slot(*args, **kwargs)


class Signal:
    def __init__(self, *types):
        self._storage_name = None

    def __set_name__(self, owner, name):
        self._storage_name = f"__signal_{name}"

    def __get__(self, instance, owner):
        if instance is None:
            return self
        signal = getattr(instance, self._storage_name, None)
        if signal is None:
            signal = _BoundSignal()
            setattr(instance, self._storage_name, signal)
        return signal


class QObject:
    def __init__(self, *args, **kwargs):
        super().__init__()


class QThread(QObject):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    def start(self):
        run = getattr(self, "run", None)
        if callable(run):
            run()

    def quit(self):
        return None

    def wait(self, timeout=None):
        return True
