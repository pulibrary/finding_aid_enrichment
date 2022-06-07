import pandas as pd

class OcrData:
    def __init__(self, path):
        self._path = path
        self._frame = pd.DataFrame()
    @property
    def frame(self):
        if self._frame.empty:
            self.read_frame()
        return self._frame

    def read_frame(self):
        with open(self._path, "r", encoding="utf-8"):
            self._frame = pd.read_csv(path)
            
        
    def text(self, threshold=1):
        frame = self.frame
        tframe = frame[frame.conf > threshold]
        tframe = tframe.reset_index()
        tframe = tframe.fillna("")
        lines = tframe.groupby(['page_num', 'block_num', 'par_num', 'line_num'])['text'].apply(lambda x: ' '.join(list(x))).tolist()
        return "\n".join(lines)
