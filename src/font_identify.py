import os
import cv2 as cv
import numpy as np
from src.font_file_extract import extract_font


class Letter():
    def __init__(self, coord, letter, prcnt_match, w, h, scale):
        self.coord = coord
        self.l_char = letter
        self.prcnt_match = prcnt_match
        self.scale = scale
        self.w = round(w*scale)
        self.h = round(h*scale)
        self.replaced: list[Letter] = []

    def __eq__(self, other: "Letter") -> bool:
        w_perc = 0.9
        h_perc = 0.9
        if self.coord[0] > other.coord[0]:
            within_w = self.coord[0] - other.coord[0]  < other.w * w_perc
        else:
            within_w = other.coord[0] - self.coord[0]  < self.w * w_perc
        if self.coord[1] > other.coord[1]:
            within_h = self.coord[1] - other.coord[1]  < other.h * h_perc
        else:
            within_h = other.coord[1] - self.coord[1]  < self.h * h_perc
        return within_w and within_h
    
    def __str__(self) -> str:
        return f'{self.l_char}[{self.prcnt_match}]'
    
    def __gt__(self, other) -> bool:
        return self.prcnt_match > other.prcnt_match
    
    def __lt__(self, other) -> bool:
        return self.prcnt_match < other.prcnt_match
    
    def replace(self, letter: "Letter"):
        to_replace = [letter]
        to_replace.extend(letter.replaced)
        for l in to_replace:
            self._insort(l)
    
    def _insort(self, letter:"Letter"):
        i = 0
        while i < len(self.replaced) and letter.prcnt_match < self.replaced[i].prcnt_match:
            i += 1
        self.replaced.insert(i, letter)

def print_letters(letters):
    print('[', end='')
    print(', '.join([f'({str(l.l_char)}, {l.prcnt_match})' for l in letters]), end='')
    print(']')

def print_xy(letters):
    print('[', end='')
    print(', '.join([f'({str(l.l_char)}, {str(l.coord[0])}, {str(l.coord[1])})' for l in letters]))
    print(']')

def average_letter(letters:list[Letter], key):
    tot = 0
    for l in letters:
        tot += key(l)
    return tot/len(letters)

def crop_letter(letter):
    ind = np.nonzero(letter == 0)
    x = np.sort(ind[0])
    y = np.sort(ind[1])
    return letter[x[0]:x[-1], y[0]:y[-1]]

def format_letter_png(letter_path:str, threshold=128):
    template = cv.imread(letter_path, cv.IMREAD_UNCHANGED)
    if template is None:
        return None
    trans_mask = template[:,:,3] == 0
    template[trans_mask] = [255, 255, 255, 255]
    template = cv.cvtColor(template, cv.COLOR_BGRA2GRAY)
    _, template = cv.threshold(template, threshold, 255, cv.THRESH_BINARY)
    template = crop_letter(template)
    return template

def draw_letters(img_rgb, all_letters:list[Letter]):
    for l in all_letters:
        cv.rectangle(img_rgb, l.coord, (l.coord[0] + l.w, l.coord[1] + l.h), (211,211,211), -1)
        cv.putText(img_rgb,l.l_char,(l.coord[0], l.coord[1] + round(0.6*l.h)), cv.FONT_HERSHEY_SIMPLEX, 1,(0,0,255),2,cv.LINE_AA)

def convert_to_txt(rows):
    out = '\n'.join([' '.join([''.join([l.l_char for l in word]) for word in row]) for row in rows])
    return out
    
def iterate_letters(img_gray, font_path, letter_subset, match_thresh):
    all_letters = []
    for i, l in enumerate(letter_subset):
        print(f'Searching for all: {l}')
        letter = format_letter_png(f'{font_path}/{l}.png')
        if letter is None:
            continue
        solve_letter(img_gray, letter, l, all_letters, match_thresh)
        print(f'{round(100*((i+1)/len(letter_subset)),2)}% of letters have been searched')
    return all_letters

def group_rows(letters):
    sorted_h:list[Letter] = sorted(letters, key=lambda x: x.coord[1])
    avg_h = average_letter(letters, lambda x: x.h)
    rows = []
    row = [sorted_h[0]]
    for i in range(1, len(sorted_h)):
        if sorted_h[i].coord[1] - sorted_h[i-1].coord[1] > avg_h*0.7:
            rows.append(row)
            row = [sorted_h[i]]
        else:
            row.append(sorted_h[i])
    if row:
        rows.append(row)

    sorted_rows = []
    for r in rows:
        sorted_rows.append(sorted(r, key=lambda x: x.coord[0]))
    return sorted_rows
            

def identify_spaces(rows:list[list[Letter]]):
    lines = []
    for row in rows:
        line = []
        word = [row[0]]
        avg_gap = 0
        for i in range(1, len(row)):
            avg_gap += (row[i].coord[0] - (row[i-1].coord[0] + row[i-1].w))/len(row)
        for i in range(1, len(row)):
            if row[i].coord[0] - (row[i-1].coord[0] + row[i-1].w) > avg_gap*1.5:
                line.append(word)
                word = []
            word.append(row[i])
        if word:
            line.append(word)
        lines.append(line)
    return lines
            
def finalize_letters(letters):
    rows = group_rows(letters)
    spaced = identify_spaces(rows)
    msg = convert_to_txt(spaced)
    with open('decoded_message.txt', 'w') as f:
        f.write(msg)
    finalized = []
    for row in spaced:
        for word in row:
            finalized.extend(word)
    return finalized

def solve_letter(img_gray, letter, letter_char, all_letters:list[Letter], threshold):
    dim = letter.shape[::-1]
    res = cv.matchTemplate(img_gray,letter,cv.TM_CCOEFF_NORMED)
    loc = np.where(res >= threshold)
    for pt in zip(*loc[::-1]):
        new_letter = Letter(pt, letter_char, res[pt[1],pt[0]], dim[0], dim[1], 1)
        if new_letter in all_letters:
            overlaping = [l for l in all_letters if l == new_letter]
            overlaping = sorted(overlaping, key=lambda x: x.prcnt_match)
            i = 0
            while i < len(overlaping) and overlaping[i] < new_letter:
                all_letters.remove(overlaping[i])
                new_letter.replace(overlaping[i])
                i += 1
            if i >= len(overlaping):
                all_letters.append(new_letter)
            else:
                for i in range(i, len(overlaping)):
                    all_letters[all_letters.index(overlaping[i])].replace(new_letter)
        else:
            all_letters.append(new_letter)
    

def identify_scale(single_letter_path, known_letter_char, font_path):
    single = format_letter_png(single_letter_path)
    known = format_letter_png(f'{font_path}/{known_letter_char}.png')

    single_dim = single.shape[::-1]
    known_dim = known.shape[::-1]
    scale = single_dim[1]/known_dim[1]
    return scale

def scale_letters(font_path, output_path, letters, scale):
    if not os.path.exists(output_path):
        os.makedirs(output_path)
    for l in letters:
        orig = cv.imread(f'{font_path}/{l}.png', cv.IMREAD_UNCHANGED)
        if orig is not None:
            _, w, h = orig.shape[::-1]
            new_size = (round(w*scale), round(h*scale))
            scaled = cv.resize(orig, new_size)
            cv.imwrite(f'{output_path}/{l}.png', scaled)


def match_letters(img_path, font_path, letter_subset=['a', 'b', 'c', 'd', 'e', 'f', 'g', 'h',
                                                   'i', 'j', 'k', 'l','m','n', 'o', 'p', 'q',
                                                   'r', 's', 't', 'u', 'v', 'w', 'x', 'y','z',
                                                   'A', 'B', 'C', 'D', 'E', 'F', 'G', 'H', 'I',
                                                   'J', 'K', 'L', 'M','N', 'O', 'P', 'Q', 'R',
                                                   'S', 'T', 'U', 'V', 'W', 'X', 'Y', 'Z'],
                                                   match_thresh = 0.6):
    img_rgb = cv.imread(img_path)
    img_gray = cv.cvtColor(img_rgb, cv.COLOR_BGR2GRAY)
    _, img_gray = cv.threshold(img_gray, 128, 255, cv.THRESH_BINARY)
    letters = iterate_letters(img_gray, font_path, letter_subset, match_thresh)
    final = finalize_letters(letters)
    draw_letters(img_rgb, final)
    cv.imwrite('decoded_image.png', img_rgb)

def adjust_font_scale(save_path, font_path, letter_path, letter_char, letters):
    print('Identifying scale...')
    if '.' in font_path:
        default_size = 100
        extract_font(font_path, save_path, default_size, letters)
        scale = identify_scale(letter_path, letter_char, save_path)
        extract_font(font_path, save_path, default_size*scale, letters)
    else:
        scale = identify_scale(letter_path, letter_char, font_path)
        scale_letters(font_path, save_path, letters, scale)
    print('Done')

def solve_font(font_path, message_path, letter_path, letter_char, letters, threshold):
    save_path = 'res/font_imgs'
    adjust_font_scale(save_path, font_path, letter_path, letter_char, letters)
    match_letters(message_path, save_path, letters, threshold)