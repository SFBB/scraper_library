from abc import ABC, abstractmethod
from tqdm import tqdm



class view_base(ABC):
    def __init__(self, **kwargs):
        pass

    @abstractmethod
    def print(self, text):
        pass

    def bar_update(self, delta: int):
        pass

    def bar_description(self, text):
        pass

    def new_bar(self, length: int):
        pass

class view_bash(view_base):
    def __intt__(self, **kwargs):
        super(view_bash, self).__init__(**kwargs)
        self.bar = None
        self.length = 0
        self.progress = 0

    def __del__(self):
        if self.bar is not None:
            self.bar.close()

    def print(self, text):
        print(text)

    def bar_update(self, delta: int):
        if self.bar is not None:
            self.bar.update(delta)

            self.progress += delta
            if self.progress >= self.length:
                self.bar.close()
                self.bar = None
                self.length = 0
                self.progress = 0

    def bar_description(self, text):
        if self.bar is not None:
            self.bar.set_description(text)

    def new_bar(self, length: int):
        self.bar = tqdm(total = length)
        self.length = length
        self.progress = 0

