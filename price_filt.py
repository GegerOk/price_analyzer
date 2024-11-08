import os
import pandas as pd


class PriceAnalyzer:
    def __init__(self, directory):
        self.directory = directory
        self.data = pd.DataFrame()

    def load_prices(self):
        """Сканирует папку и загружает данные из файлов прайс-листов."""
        for filename in os.listdir(self.directory):
            if 'price' in filename and filename.endswith('.csv'):
                filepath = os.path.join(self.directory, filename)
                df = pd.read_csv(filepath, sep=';', encoding='utf-8')
                product_col = next((col for col in df.columns if col.lower() in [
                                   'название', 'продукт', 'товар', 'наименование']), None)
                price_col = next(
                    (col for col in df.columns if col.lower() in ['цена', 'розница']), None)
                weight_col = next((col for col in df.columns if col.lower() in [
                                  'фасовка', 'масса', 'вес']), None)

                if product_col and price_col and weight_col:
                    df = df[[product_col, price_col, weight_col]]
                    df.columns = ['название', 'цена', 'вес']
                    df['файл'] = filename
                    df['цена за кг'] = df['цена'] / df['вес']
                    self.data = pd.concat([self.data, df], ignore_index=True)

    def find_text(self, text):
        """Ищет позиции, содержащие текст в названии, и возвращает их."""
        filtered_data = self.data[self.data['название'].str.contains(
            text, case=False)]
        return filtered_data.sort_values(by='цена за кг')

    def export_to_html(self, output_file):
        """Экспортирует данные в HTML файл."""
        html_data = self.data.to_html(index=False)
        with open(output_file, 'w', encoding='utf-8') as f:
            f.write(html_data)


def main():
    directory = input("Введите путь к папке с прайс-листами: ")
    output_html_file = "prices_output.html"

    analyzer = PriceAnalyzer(directory)
    analyzer.load_prices()

    while True:
        search_text = input(
            "Введите текст для поиска (или 'exit' для выхода): ")
        if search_text.lower() == "exit":
            print("Работа завершена.")
            break
        results = analyzer.find_text(search_text)
        if not results.empty:
            print(results[['название', 'цена', 'вес', 'файл',
                  'цена за кг']].to_string(index=True))
        else:
            print("Товары не найдены.")
    analyzer.export_to_html(output_html_file)
    print(f"Данные экспортированы в файл: {output_html_file}")


if __name__ == "__main__":
    main()
