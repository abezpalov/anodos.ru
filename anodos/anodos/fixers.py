

def to_slug(name):
    """ Переводит строку в Slug """

    name = name.lower()
    name = name.strip()
    dictionary = {'а': 'a', 'б': 'b', 'в': 'v', 'г': 'g', 'д': 'd', 'е': 'e', 'ё': 'e',
                  'ж': 'zh', 'з': 'z', 'и': 'i', 'й': 'i', 'к': 'k', 'л': 'l', 'м': 'm',
                  'н': 'n', 'о': 'o', 'п': 'p', 'р': 'r', 'с': 's', 'т': 't', 'у': 'u',
                  'ф': 'f', 'х': 'h', 'ц': 'c', 'ч': 'cz', 'ш': 'sh', 'щ': 'scz',
                  'ъ': '', 'ы': 'y', 'ь': '', 'э': 'e', 'ю': 'u', 'я': 'ja',
                  ',': '-', '?': '-', ' ': '-', '~': '-', '!': '-', '@': '-', '#': '-',
                  '$': '-', '%': '-', '^': '-', '&': '-', '*': '-', '(': '-', ')': '-',
                  '=': '-', '+': '-', ':': '-', ';': '-', '<': '-', '>': '-', '\'': '-',
                  '"': '-', '\\': '-', '/': '-', '№': '-', '[': '-', ']': '-', '{': '-',
                  '}': '-', 'ґ': '-', 'ї': '-', 'є': '-', 'Ґ': 'g', 'Ї': 'i', 'Є': 'e',
                  '—': '-', '.': '-'}

    for key in dictionary:
        name = name.replace(key, dictionary[key])

    while '--' in name:
        name = name.replace('--', '-')

    if name[0] == '-':
        name = name[1:]

    if name[-1] == '-':
        name = name[:-1]

    return name


def need_new_decimal_value(old, new, delta=0.001):
    """ Определяет приблизительным сравнением, необходимо ли записывать новое значение в базу."""

    if new is None:
        return False
    elif old is None:
        return True

    old = float(old)
    new = float(new)
    delta = float(delta)
    try:
        if old - new / new < delta:
            return False
    except ZeroDivisionError:
        return False
    return True


def fix_text(text):

    if text is None:
        return None

    dictionary = {'™': ''}
    for key in dictionary:
        text = text.replace(key, dictionary[key])

    while '  ' in text:
        text = text.replace('  ', ' ')
    while '/n/n' in text:
        text = text.replace('/n/n', '/n')
    text = text.replace(' : ', ': ')
    text = text.replace(' - ', ' — ')
    text = text.strip()
    return text


def fix_float(text):

    if text is None:
        return None

    dictionary = {' ': '', ',': '.'}
    for key in dictionary:
        text = text.replace(key, dictionary[key])

    text = text.strip()

    return float(text)


def string_to_words(name):
    name = name.lower()

    dictionary = {',': ' ', '?': ' ', '~': ' ', '!': ' ', '@': ' ', '#': ' ', '$': ' ',
                  '%': ' ', '^': ' ', '&': ' ', '*': ' ', '(': ' ', ')': ' ', '=': ' ',
                  '+': ' ', ':': ' ', ';': ' ', '<': ' ', '>': ' ', '\'': ' ', '"': ' ',
                  '\\': ' ', '/': ' ', '№': ' ', '[': ' ', ']': ' ', '{': ' ', '}': '-',
                  'ґ': ' ', 'ї': ' ', 'є': ' ', 'Ґ': ' ', 'Ї': ' ', 'Є': ' ', '—': ' ',
                  '\t': ' ', '\n': ' ', }

    for key in dictionary:
        name = name.replace(key, dictionary[key])

    while '  ' in name:
        name = name.replace('  ', ' ')

    name = name.strip()

    return name.split(' ')
