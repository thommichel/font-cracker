import os
import cv2 as cv
import numpy as np
import math


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
        w_perc = 0.55
        h_perc = 0.55
        within_w = abs(other.coord[0] - self.coord[0]) <= self.w*w_perc or abs(other.coord[0] - self.coord[0]) <= other.w*w_perc
        within_h = abs(other.coord[1] - self.coord[1]) <= self.h*h_perc or abs(other.coord[1] - self.coord[1]) <= other.h*h_perc
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

def within_delta_of_any(points, point, dx, dy):
    for p in points:
        if abs(p[0] - point[0]) <= dx and abs(p[1] - point[1]) <= dy:
            return True
    return False

def print_letters(letters):
    print('[', end='')
    print(', '.join([f'({str(l.l_char)}, {l.prcnt_match})' for l in letters]), end='')
    print(']')

def print_xy(letters):
    print('[', end='')
    print(', '.join([f'({str(l.l_char)}, {str(l.coord[0])}, {str(l.coord[1])})' for l in letters]))
    print(']')

def average_scale(all_letters:list[Letter]):
    scale_sum = 0
    for letter in all_letters:
        scale_sum += letter.scale
    return scale_sum/len(all_letters)

def average_height(all_letters:list[Letter]):
    height_sum = 0
    for letter in all_letters:
        height_sum += letter.h
    return height_sum/len(all_letters)

def average_letter(letters:list[Letter], key):
    tot = 0
    for l in letters:
        tot += key(l)
    return tot/len(letters)

def average_xy(all_letters:list[Letter]):
    xy_sum = [0,0]
    for letter in all_letters:
        xy_sum[0] += letter.coord[0]
        xy_sum[1] += letter.coord[1]
    xy_sum[0] /= len(all_letters)
    xy_sum[1] /= len(all_letters)
    return xy_sum

def crop_letter(letter):
    ind = np.nonzero(letter == 0)
    x = np.sort(ind[0])
    y = np.sort(ind[1])
    return letter[x[0]:x[-1], y[0]:y[-1]]

def resize_to_width(img, width):
    w, h = img.shape[::-1]
    res = w/h
    new_size = (round(width), round(width/res))
    return cv.resize(img, new_size)

def format_letter_png(letter_path:str, threshold=128):
    template = cv.imread(letter_path, cv.IMREAD_UNCHANGED)

    l = letter_path.split('.png')[0][-1]

    if template is None:
        return None
    cv.imwrite(f'test/{l}-orig.png', template)
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

def convert_to_txt(rows, path):
    out = '\n'.join([' '.join([''.join([l.l_char for l in word]) for word in row]) for row in rows])
    with open(path, 'w') as f:
        f.write(out)
    

def iterate_letters(img_gray, font_path, letter_subset):
    bound_optimal = 1
    count = 0
    prev_len = 0
    set_scale_after = 5
    all_letters = []
    for i, l in enumerate(letter_subset):
        print(f'Searching for all: {l}')
        letter = format_letter_png(f'{font_path}/{l}.png')
        if letter is None:
            continue
        cv.imwrite(f'test/{l}.png', letter)
        if bound_optimal:
            solve_letter(img_gray, letter, l, all_letters, bound_optimal=bound_optimal)
        else:
            solve_letter(img_gray, letter, l, all_letters)
            if len(all_letters) > prev_len:
                count += 1
            if count > set_scale_after:
                bound_optimal = average_scale(all_letters)
        print(f'{round(100*((i+1)/len(letter_subset)),2)}% of letters have been searched')
    return all_letters

def group_rows(letters):
    sorted_h:list[Letter] = sorted(letters, key=lambda x: x.coord[1])
    avg_h = average_height(letters)
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

def check_invalid_heights(rows:list[list[Letter]]):
    fixed_rows = []
    for row in rows:
        avg_xy = average_xy(row)
        avg_h = average_height(row)
        fixed = []
        for l in row:
            f = l
            i = 0
            num_rep = len(f.replaced)
            while i < num_rep and abs(float(f.coord[1] + f.h)-float(avg_xy[1] + avg_h)) > avg_h * 0.02:
                f = l.replaced[i]
                i += 1
            fixed.append(f)
        fixed_rows.append(fixed)
    return fixed_rows

def check_invalid_widths(spaced_rows:list[list[list[Letter]]]):
    fixed_rows = []
    for row in spaced_rows:
        fixed_row = []
        for word in row:
            fixed_word = []
            avg_xy = average_xy(word)
            avg_h = average_height(word)
            avg_delta = 0
            for i in range(1, len(word)):
                avg_delta += word[i].coord[0] - (word[i-1].coord[0] + word[i-1].w)
            avg_delta /= len(word)
            for i in range(len(word)-1):
                f = word[i]
                j = 0
                while j < len(word[i].replaced) and (abs(avg_delta - (word[i+1].coord[0] - (f.coord[0] + f.w))) > avg_delta*0.5 or abs(float(f.coord[1])-float(avg_xy[1])) > avg_h * 0.08):
                    f = word[i].replaced[j]
                    j += 1
                fixed_word.append(f)
            fixed_word.append(word[-1])
            fixed_row.append(fixed_word)
        fixed_rows.append(fixed_row)
    return fixed_rows
            

def identify_spaces(rows:list[list[Letter]]):
    lines = []
    for row in rows:
        line = []
        word = [row[0]]
        avg_w = average_letter(row, lambda x: x.w)
        for i in range(1, len(row)):
            if row[i].coord[0] - (row[i-1].coord[0] + row[i-1].w) > avg_w*0.5:
                line.append(word)
                word = []
            word.append(row[i])
        if word:
            line.append(word)
        lines.append(line)
    return lines
            
def finalize_letters(letters):
    rows = group_rows(letters)
    fixed_rows = check_invalid_heights(rows)
    spaced = identify_spaces(fixed_rows)
    final_spaced = check_invalid_widths(spaced)
    convert_to_txt(final_spaced, 'decoded_message.txt')
    finalized = []
    for row in final_spaced:
        for word in row:
            finalized.extend(word)
    return finalized

def solve_letter(img_gray, letter, letter_char, all_letters:list[Letter], bound_optimal=0, threshold=0.55):
    dim = letter.shape[::-1]
    if not bound_optimal:
        w_lo = math.floor(dim[0]*0.7)
        w_hi = math.ceil(dim[0]*1.3)
    else:
        delta = 3
        bound_optimal = round(bound_optimal*dim[0])
        w_lo = bound_optimal-delta
        w_hi = bound_optimal+delta
    for width in range(w_lo, w_hi):
        resized = resize_to_width(letter, width)
        res = cv.matchTemplate(img_gray,resized,cv.TM_CCOEFF_NORMED)
        loc = np.where(res >= threshold)
        for pt in zip(*loc[::-1]):
            new_letter = Letter(pt, letter_char, res[pt[1],pt[0]], dim[0], dim[1], width/dim[0])
            if new_letter in all_letters:
                overlap = all_letters.index(new_letter)
                if all_letters[overlap] < new_letter:
                    old = all_letters.pop(overlap)
                    all_letters.append(new_letter)
                    new_letter.replace(old)
                else:
                    all_letters[overlap].replace(new_letter)
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


def solve_font(img_path, font_path, letter_subset=['a', 'b', 'c', 'd', 'e', 'f', 'g', 'h',
                                                   'i', 'j', 'k', 'l','m','n', 'o', 'p', 'q',
                                                   'r', 's', 't', 'u', 'v', 'w', 'x', 'y','z',
                                                   'A', 'B', 'C', 'D', 'E', 'F', 'G', 'H', 'I',
                                                   'J', 'K', 'L', 'M','N', 'O', 'P', 'Q', 'R',
                                                   'S', 'T', 'U', 'V', 'W', 'X', 'Y', 'Z']):
    img_rgb = cv.imread(img_path)
    img_copy = cv.imread(img_path)
    img_gray = cv.cvtColor(img_rgb, cv.COLOR_BGR2GRAY)
    _, img_gray = cv.threshold(img_gray, 128, 255, cv.THRESH_BINARY)
    cv.imwrite('test/gray.png', img_gray)
    letters = iterate_letters(img_gray, font_path, letter_subset)
    draw_letters(img_copy, letters)
    cv.imwrite('test/_res_before.png', img_copy)
    final = finalize_letters(letters)
    draw_letters(img_rgb, final)
    cv.imwrite('decoded_image.png', img_rgb)

if __name__ == '__main__':
    # solve_font('res/flora.png','res/fonts/images/flora')
    solve_font('../res/unown_a.png','res/fonts/images/poke')
    # solve_font('../res/unown_m.png','res/fonts/images/poke')
    # solve_font('../unown.png','poke')
    # solve_font('../res/trees.png','res/fonts/images/trees')


'''
Tree font does not work.
Manual scale set?


Identify scale by using the vouls and changing scale until a match is found with a very high correctness


SHOULD ACTUALLY WORK

- Find contours
- Get contour of 3 letter
- Find correct scale based on those letters
- Search on remaining contours instead of main picture??
    - How to know how many contours to expect??


'''