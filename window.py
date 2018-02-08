import wx


class WindowBase:
    def __init__(self):
        pass

    def generate_layout(self):
        raise NotImplementedError

    def bind_events(self):
        raise NotImplementedError

    def unbind_events(self):
        raise NotImplementedError

    def on_exit(self):
        self.unbind_events()
        self.destroy()

    def destroy(self):
        pass