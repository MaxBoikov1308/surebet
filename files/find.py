import re

def save_bet(profit_value=0, input_file='index.txt', output_file='output.txt'):
    """
    Ищет структуру с заданным data-profit и сохраняет только её в файл
    
    Args:
        profit_value: значение data-profit для поиска (число или строка)
        input_file: путь к входному файлу (по умолчанию 'index.txt')
        output_file: путь к выходному файлу (по умолчанию 'output.txt')
    """
    # Преобразуем profit_value в строку для поиска
    profit_str = str(profit_value)
    
    try:
        with open(input_file, 'r', encoding='utf-8') as file:
            content = file.read()
        
        # Шаблон для поиска всей tbody структуры с нужным data-profit
        pattern = rf'(<tbody[^>]*data-profit\s*=\s*"{re.escape(profit_str)}"[^>]*>.*?</tbody>)'
        
        # Ищем все совпадения
        matches = re.findall(pattern, content, re.DOTALL | re.IGNORECASE)
        
        if matches:
            # Сохраняем найденные структуры в файл
            with open(output_file, 'w', encoding='utf-8') as file:
                for match in matches:
                    file.write(match + '\n\n')
            
            print(f"Найдено {len(matches)} структур с data-profit='{profit_value}'")
            print(f"Результат сохранен в файл: {output_file}")
        else:
            print(f"Структур с data-profit='{profit_value}' не найдено")
            
    except FileNotFoundError:
        print(f"Файл {input_file} не найден")
    except Exception as e:
        print(f"Произошла ошибка: {e}")

# Пример использования
if __name__ == "__main__":
    save_bet(profit_value=3.28, input_file='index.txt', output_file='index.txt')