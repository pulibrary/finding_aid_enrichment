"""The adam Page module

The Page module encapsulates OCR and NER.

  Typical usage:

  page = Page(path_to_image)
  page_text = page.text
  page_hocr = page.hocr
  page_alto = page.alto

"""

try:
    from PIL import Image
except ImportError:
    import Image
import pytesseract
import spacy


class Page:
    """Encapsulates OCR and NER processes.

    The class could eventually be refactored to take OCR
    and NER objects as injections.

    """
    def __init__(self, page_image):
        self._image_file = page_image
        self._text = False
        self._hocr = False
        self._alto = False
        self._nlp = False
        self._doc = False

    @property
    def image_file(self):
        return self._image_file

    @property
    def text(self):
        if not self._text:
            self.do_ocr_to_string()
        return self._text

    @property
    def hocr(self):
        if not self._hocr:
            self.do_ocr_to_hocr()
        return self._hocr

    @property
    def alto(self):
        if not self._alto:
            self.do_ocr_to_alto()
        return self._alto

    @property
    def doc(self):
        if not self._doc:
            self.do_nlp()
        return self._doc

    def do_ocr_to_string(self):
        self._text = pytesseract.image_to_string(Image.open(self.image_file))

    def do_ocr_to_hocr(self):
        self._hocr = pytesseract.image_to_pdf_or_hocr(
            Image.open(self.image_file), extension='hocr')

    def do_ocr_to_alto(self):
        self._alto = pytesseract.image_to_alto_xml(
            Image.open(self.image_file))

    def do_nlp(self):
        if not self._nlp:
            self._nlp = spacy.load('en_core_web_trf')
        self._doc = self._nlp(self.text)
        return self._doc
