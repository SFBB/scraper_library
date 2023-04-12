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

    def print(self, text):
        print(text)

    def bar_update(self, delta: int):
        self.bar.update(delta)

    def bar_description(self, text):
        self.bar.set_description(text)

    def new_bar(self, length: int):
        self.bar = tqdm(total = length)
