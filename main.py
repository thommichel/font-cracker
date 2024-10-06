from src.font_identify import FontCracker

LETTERS = ['a', 'b', 'c', 'd', 'e', 'f', 'g', 'h', 'i', 'j', 'k', 'l','m',\
           'n', 'o', 'p', 'q', 'r', 's', 't', 'u', 'v', 'w', 'x', 'y', 'z',\
           'A', 'B', 'C', 'D', 'E', 'F', 'G', 'H', 'I', 'J', 'K', 'L', 'M',\
           'N', 'O', 'P', 'Q', 'R', 'S', 'T', 'U', 'V', 'W', 'X', 'Y', 'Z']


def run():
    font_path = input('Enter the path of the font file/directory: ')
    msg_img_path = input('Enter the path of the encoded message image: ')
    letter_path = input('Enter the path of the single letter: ')
    letter_char = input('Enter the letter (case sensitive): ')
    threshold = float(input('Enter the percent match threshold [0 - 1]: '))

    FontCracker().solve_font(font_path, msg_img_path, letter_path, letter_char, LETTERS, threshold)

if __name__ == '__main__':
    run()