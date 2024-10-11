from src.font_identify import FontCracker

LETTERS = ['a', 'b', 'c', 'd', 'e', 'f', 'g', 'h', 'i', 'j', 'k', 'l','m',\
           'n', 'o', 'p', 'q', 'r', 's', 't', 'u', 'v', 'w', 'x', 'y', 'z',\
           'A', 'B', 'C', 'D', 'E', 'F', 'G', 'H', 'I', 'J', 'K', 'L', 'M',\
           'N', 'O', 'P', 'Q', 'R', 'S', 'T', 'U', 'V', 'W', 'X', 'Y', 'Z']


def run():
    # # Example 1
    # font_path = 'examples/fonts/Floralia.ttf'
    # msg_img_path = 'examples/flora.png'
    # letter_path = 'examples/flora_T.png'
    # letter_char = 'T'
    # threshold = 0.6

    # # Example 2
    # font_path = 'examples/fonts/Trees.otf'
    # msg_img_path = 'examples/trees.png'
    # letter_path = 'examples/trees_s.png'
    # letter_char = 's'
    # threshold = 0.4

    # Example 3
    # font_path = 'examples/fonts/unown'
    # msg_img_path = 'examples/unown.png'
    # letter_path = 'examples/unown__a.png'
    # letter_char = 'A'
    # threshold = 0.6

    # Example 4
    # font_path = 'examples/fonts/unown'
    # msg_img_path = 'examples/unown_all.png'
    # letter_path = 'examples/unown_all_A.png'
    # letter_char = 'A'
    # threshold = 0.6

    font_path = input('Enter the path of the font file/directory: ')
    msg_img_path = input('Enter the path of the encoded message image: ')
    letter_path = input('Enter the path of the single letter: ')
    letter_char = input('Enter the letter (case sensitive): ')
    threshold = float(input('Enter the percent match threshold [0 - 1]: '))

    FontCracker().solve_font(font_path, msg_img_path, letter_path, letter_char, LETTERS, threshold)

if __name__ == '__main__':
    run()