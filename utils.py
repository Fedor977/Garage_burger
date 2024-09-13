from aiogram.types.inline_keyboard import InlineKeyboardMarkup, InlineKeyboardButton

def build_inline_menu(markup: InlineKeyboardMarkup, lst: list, prefix: str, in_row: int = 2):

    in_row = in_row # Sbros

    rows = len(lst) // in_row

    if len(lst) % in_row != 0:
        rows += 1

    start = 0
    end = in_row

    for i in range(rows):
        new_list = []
        for pk, name in lst[start:end]:
            new_list.append(
                InlineKeyboardButton(text=name, callback_data=f'{prefix}_{pk}') # category_1
            )
        markup.row(*new_list)
        start = end
        end += in_row
    if prefix == 'product':
        markup.row(
            InlineKeyboardButton(text='Назад', callback_data='main_menu'),
        )

