from src.font_identify import solve_font

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

    # font_path = 'res/fonts/images/poke'
    # encoded_img = 'res/unown_a.png'
    # single_letter = 'res/unown_A.png'
    # l_char = 'A'

    # font_path = 'res/fonts/images/poke'
    # encoded_img = 'all_unown.png'
    # single_letter = 'all_a.png'
    # l_char = 'A'
    # letters = LETTERS

    # font_path = 'res/fonts/images/poke'
    # encoded_img = 'res/unown_m.png'

    font_path = 'res/fonts/files/Trees.otf'
    encoded_img = 'Trees.png'
    single_letter = 's.png'
    l_char = 's'

    solve_font(font_path, encoded_img, single_letter, l_char, LETTERS, 0.4)

if __name__ == '__main__':
    run()