from src.font_file_extract import extract_font
from src.font_identify import solve_font, identify_scale, scale_letters

LETTERS = ['a', 'b', 'c', 'd', 'e', 'f', 'g', 'h', 'i', 'j', 'k', 'l','m',\
           'n', 'o', 'p', 'q', 'r', 's', 't', 'u', 'v', 'w', 'x', 'y', 'z',\
           'A', 'B', 'C', 'D', 'E', 'F', 'G', 'H', 'I', 'J', 'K', 'L', 'M',\
           'N', 'O', 'P', 'Q', 'R', 'S', 'T', 'U', 'V', 'W', 'X', 'Y', 'Z']

# LETTERS = ['A', 'B', 'C', 'D', 'E', 'F', 'G', 'H', 'I', 'J', 'K', 'L', 'M',\
#            'N', 'O', 'P', 'Q', 'R', 'S', 'T', 'U', 'V', 'W', 'X', 'Y', 'Z']
# 
# LETTERS = ['F', 'C', 'I', 'A', 'B']

# LETTERS = ['s']

# LETTERS = ['a', 'b', 'c', 'd', 'e', 'f', 'g', 'h', 'i', 'j', 'k', 'l','m',\
#            'n', 'o', 'p', 'q', 'r', 's', 't', 'u', 'v', 'w', 'x', 'y', 'z']

# LETTERS = ['a', 'b', 'c', 'd', 'e', 'f', 'g', 'h', 'i', 'j', 'k', 'l','m',\
#            'n', 'o', 'p', 'q', 'r', 's', 't', 'u', 'v', 'w', 'x', 'y', 'z',\
#            'A', 'B', 'C', 'D', 'E', 'F', 'G', 'H', 'J', 'K', 'L', 'M',\
#            'N', 'O', 'P', 'Q', 'R', 'S', 'T', 'U', 'V', 'W', 'X', 'Y']


# LETTERS = ['I', 'K', 'A', 'Z']

# LETTERS = ['F']

def run():
    font_path = 'res/fonts/files/Floralia.otf'
    encoded_img = 'res/flora.png'
    single_letter = 'res/flora_T.png'
    l_char = 'T'

    font_path = 'res/fonts/images/poke'
    encoded_img = 'res/unown_a.png'
    single_letter = 'res/unown_A.png'
    l_char = 'A'

    # font_path = 'res/fonts/images/poke'
    # encoded_img = 'res/unown_m.png'

    # font_path = 'res/fonts/files/Trees.otf'
    # encoded_img = 'Trees.png'
    # single_letter = 's.png'
    # l_char = 's'

    if '.' in font_path:
        default_size = 100
        extract_font(font_path, 'res/font_imgs', default_size, LETTERS)
        scale = identify_scale(single_letter, l_char, 'res/font_imgs')
        extract_font(font_path, 'res/font_imgs', default_size*scale, LETTERS)
        font_path = 'res/font_imgs'
    else:
        print('scaling')
        scale = identify_scale(single_letter, l_char, font_path)
        scale_letters(font_path, f'{font_path}-scaled', LETTERS, scale)
        font_path = f'{font_path}-scaled'
    solve_font(encoded_img, font_path, LETTERS)

if __name__ == '__main__':
    run()