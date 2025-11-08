import pandas as pd

class MiniLegalAI:
    def __init__(self, workbook_path):
        self.workbook_path = workbook_path
        self.data = self.load_workbook()

    def load_workbook(self):
        """تحميل ملف Excel بأمان دون تركه مفتوحًا"""
        if not self.workbook_path or not os.path.exists(self.workbook_path):
            return None
        
        with pd.ExcelFile(self.workbook_path) as xls:
            # افترض أن لدينا عدة sheets نحتاجها
            sheets = xls.sheet_names
            data_dict = {}
            for sheet in sheets:
                data_dict[sheet] = pd.read_excel(xls, sheet_name=sheet)
            return data_dict

    def advanced_search(self, query, top_n=3):
        """محاكاة البحث الذكي"""
        # هنا يمكن استخدام self.data بدل فتح الملف كل مرة
        # مجرد مثال: إرجاع نتائج dummy
        results = []
        if self.data:
            for i in range(min(top_n, 3)):
                results.append({
                    "text": f"نص قانوني تجريبي {i+1} لبحث '{query}'",
                    "example": f"مثال {i+1}",
                    "reference": f"المادة {i+1}",
                    "score": 95 - i*5
                })
        return results

    def reload(self):
        """إعادة تحميل البيانات إذا تم تحديث الملف"""
        self.data = self.load_workbook()