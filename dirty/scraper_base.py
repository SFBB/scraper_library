from abc import ABC, abstractmethod
import os



class scraper_base(ABC):
    def __init__(self, **kwargs):
        pass

    @abstractmethod
    def run(self):
        pass

class scraper_base_with_saving(scraper_base):
    def __init__(self, **kwargs):
        super(scraper_base_with_saving).__init__(**kwargs)
        self.file_name = ""

    def run(self):
        try:
            self.file_has_existed = os.path.exists(self.file_name)
            self.run_with_saving()
        except Exception as e:
            self.clean_file()
            raise e

    @abstractmethod
    def run_with_saving(self):
        pass

    def clean_file(self):
        if os.path.exists(self.file_name) and not self.file_has_existed:
            os.remove(self.file_name)
