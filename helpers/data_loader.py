import os
import pandas as pd

class DataLoader:
    def __init__(self):
        self.loaded_data = {}

    def load_csv(self, file_path, sheet_name=None):
        """تحميل CSV/Excel بأمان"""
        if not os.path.exists(file_path):
            return None
        if file_path.endswith(".csv"):
            df = pd.read_csv(file_path)
        else:
            with pd.ExcelFile(file_path) as xls:
                df = pd.read_excel(xls, sheet_name=sheet_name or 0)
        return df