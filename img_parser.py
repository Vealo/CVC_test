from typing import Any

from paddleocr import PaddleOCR


class ImgParser:
    def __init__(self, lang: str = 'ru') -> None:
        self.current_lang = lang
        self.ocr = PaddleOCR(use_angle_cls=True, lang=lang)
        self.supported_languages = ['en', 'ru', 'fr', 'german', 'it', 'fr']

    def set_lang(self, lang: str = 'ru') -> str:
        if lang in self.supported_languages:
            self.ocr = PaddleOCR(use_angle_cls=True, lang=lang)
            return f'Установлен язык распознавания: {lang}'
        return f'Неподдерживаемый язык: {lang}. Пожалуйста, выберите из: {", ".join(self.supported_languages)}.'

    def parser(self, photo: Any, cls: bool = True) -> str:
        result = "\n".join([line[1][0] for line in self.ocr.ocr(photo, cls=cls)[0]])
        return result
