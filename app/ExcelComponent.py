from RPA.Excel.Files import Files


class Excel:
    def __init__(self, excel_file) -> None:
        self.excel_lib = Files()
        self.excel_file = excel_file

    def read_excel(self):
        self.excel_lib.open_workbook(self.excel_file)
        worksheet = self.excel_lib.read_worksheet_as_table(header=True)
        self.excel_lib.close_workbook()
        return worksheet

