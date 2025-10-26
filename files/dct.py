from bs4 import BeautifulSoup
import re

def parse_surebet_data(html_content):
    """
    Парсит HTML с данными о вилке и возвращает строку с данными
    """
    soup = BeautifulSoup(html_content, 'html.parser')
    surebet_record = soup.find('tbody', class_='surebet_record')
    
    if not surebet_record:
        return ""
    
    # Основные данные вилки
    main_data = {
        'id': surebet_record.get('data-id'),
        'profit': surebet_record.get('data-profit'),
        'roi': surebet_record.get('data-roi'),
        'age': surebet_record.get('data-age'),
        'age_minutes': surebet_record.get('data-age').replace(' мин', '') if surebet_record.get('data-age') else None
    }
    
    # Извлекаем процент прибыли
    profit_span = surebet_record.find('span', class_='profit')
    profit_percent = profit_span.get('data-profit') if profit_span else ""
    
    # Собираем данные по отдельным ставкам (плечам вилки)
    bets_data = []
    booker_rows = surebet_record.find_all('td', class_='booker')
    
    for i, booker_td in enumerate(booker_rows):
        # Букмекер
        booker_link = booker_td.find('a')
        booker_name = booker_link.text.strip() if booker_link else ""
        
        # Спорт
        sport_span = booker_td.find('span', class_='minor')
        sport = sport_span.text.strip() if sport_span else ""
        
        # Время события
        time_td = booker_td.find_next_sibling('td', class_='time')
        time_abbr = time_td.find('abbr') if time_td else None
        time_text = time_abbr.text.strip().replace('<br>', ' ') if time_abbr else ""
        
        # Событие
        event_td = time_td.find_next_sibling('td', class_='event')
        event_link = event_td.find('a') if event_td else None
        event_name = event_link.text.strip() if event_link else ""
        
        # Турнир
        tournament_span = event_td.find('span', class_='minor') if event_td else None
        tournament = tournament_span.text.strip() if tournament_span else ""
        
        # Тип ставки
        coeff_td = event_td.find_next_sibling('td', class_='coeff')
        coeff_abbr = coeff_td.find('abbr') if coeff_td else None
        bet_type = coeff_abbr.text.strip() if coeff_abbr else ""
        bet_description = coeff_abbr.get('data-bs-original-title') if coeff_abbr else ""
        
        # Коэффициент
        value_td = coeff_td.find_next_sibling('td', class_='value')
        value_link = value_td.find('a', class_='value_link') if value_td else None
        coefficient = value_link.text.strip() if value_link else ""
        
        # Формируем строку для текущей ставки
        bet_string = f"{booker_name}, {coefficient}, {event_name}, {tournament}, {bet_type}, {bet_description}"
        bets_data.append(bet_string)
    
    # Формируем итоговую строку в требуемом формате
    result_lines = []
    
    # Первая строка: прибыль и возраст
    result_lines.append(f"{profit_percent}, {main_data['age_minutes']}")
    
    # Добавляем данные по ставкам с двойным переносом строки
    for bet in bets_data:
        result_lines.append(bet)
    
    # Объединяем все строки с двойным переносом строки
    result_string = "\n\n".join(result_lines)
    
    return result_string

def read_and_parse_file(filename):
    """
    Читает файл и парсит данные о вилке
    """
    try:
        with open(filename, 'r', encoding='utf-8') as file:
            html_content = file.read()
        
        return parse_surebet_data(html_content)
    
    except FileNotFoundError:
        print(f"Файл {filename} не найден")
        return ""
    except Exception as e:
        print(f"Ошибка при обработке файла: {e}")
        return ""

# Пример использования
if __name__ == "__main__":
    filename = "index.txt"
    result = read_and_parse_file(filename)
    print(result)