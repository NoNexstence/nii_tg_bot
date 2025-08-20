def convert_to_str(n):
    try:
        n = str(n).replace(' ', '').replace(',', '.')
        n = float(n)
        if n.is_integer():
            n = '{0:,}'.format(n).replace(',', ' ').replace('.', ',')
            n = n[:-2]
        else:
            n = '{0:,.2f}'.format(n)
            n = n.replace(',', ' ').replace('.', ',')
            if n.endswith(',00'):
                n = n[:-3]
            elif n.endswith(',0'):
                n = n[:-2]
            elif ',' in n and n.endswith('0'):
                n = n[:-1]
        return n
    except Exception as e:
        print(f"Ошибка: {e}")

def convert_to_float(n):
    if isinstance(n, str):
        n = n.replace(' ', '').replace(',', '.')
        return float(n)
    return float(n)

def find_dynamics(data):
    years = data.get('years')
    dynamics = {}
    plus_dynamics = 0
    minus_dynamics = 0
    for indicator in data[years[0]].keys():
        try:
            value_last_year = convert_to_float(data[years[0]][indicator])
            value_current_year = convert_to_float(data[years[1]][indicator])
            if value_last_year != 0:
                change_percent = ((value_current_year - value_last_year) / value_last_year) * 100
                dynamics[indicator] = convert_to_str(round(change_percent, 2))
                if change_percent > 0:
                    plus_dynamics += 1
                elif change_percent < 0:
                    minus_dynamics += 1

            else:
                dynamics[indicator] = '-'
        except (KeyError, TypeError):
            dynamics[indicator] = '-'

    data['dynamics'] = dynamics
    data['plus_dynamics'] = plus_dynamics
    data['minus_dynamics'] = minus_dynamics
    return data

