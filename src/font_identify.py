from fontTools.ttLib import TTFont
from PIL import Image, ImageDraw, ImageFont
import os
import cv2 as cv
import numpy as np

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

class FontCracker():

    def __init__(self) -> None:
        self.progress = 0
        self.current_image = None
        self.message = ""
        self.output_image_path = "decoded_image.png"

    def print_letters(self, letters):
        print('[', end='')
        print(', '.join([f'({str(l.l_char)}, {l.prcnt_match})' for l in letters]), end='')
        print(']')

    def print_xy(self, letters):
        print('[', end='')
        print(', '.join([f'({str(l.l_char)}, {str(l.coord[0])}, {str(l.coord[1])})' for l in letters]))
        print(']')

    def average_letter(self, letters:list[Letter], key):
        tot = 0
        for l in letters:
            tot += key(l)
        return tot/len(letters)

    def crop_letter(self, letter):
        ind = np.nonzero(letter == 0)
        x = np.sort(ind[0])
        y = np.sort(ind[1])
        return letter[x[0]:x[-1], y[0]:y[-1]]

    def format_letter_png(self, letter_path, threshold=128):
        print(letter_path)
        template = cv.imread(letter_path, cv.IMREAD_UNCHANGED)
        l = letter_path[0]
        if template is None:
            return None
        trans_mask = template[:,:,3] == 0
        template[trans_mask] = [255, 255, 255, 255]
        template = cv.cvtColor(template, cv.COLOR_BGRA2GRAY)
        _, template = cv.threshold(template, threshold, 255, cv.THRESH_BINARY)
        template = self.crop_letter(template)
        return template

    def draw_letters(self, img_rgb, all_letters:list[Letter]):
        for l in all_letters:
            cv.rectangle(img_rgb, l.coord, (l.coord[0] + l.w, l.coord[1] + l.h), (211,211,211), -1)
            cv.putText(img_rgb,l.l_char,(l.coord[0], l.coord[1] + round(0.6*l.h)), cv.FONT_HERSHEY_SIMPLEX, 1,(0,0,255),2,cv.LINE_AA)

    def convert_to_txt(self, rows):
        out = '\n'.join([' '.join([''.join([l.l_char for l in word]) for word in row]) for row in rows])
        return out
        
    def iterate_letters(self, img_gray, font_path, letter_subset, match_thresh):
        all_letters = []
        for i, l in enumerate(letter_subset):
            print(f'Searching for all: {l}')
            letter = self.format_letter_png(f'{font_path}/{self.convert_letter_path(l)}.png')
            if letter is None:
                continue
            self.solve_letter(img_gray, letter, l, all_letters, match_thresh)
            self.progress = ((i+1)/len(letter_subset))*100
            print(f'{round(self.progress, 2)}% of letters have been searched')
        return all_letters

    def group_rows(self, letters):
        sorted_h:list[Letter] = sorted(letters, key=lambda x: x.coord[1])
        avg_h = self.average_letter(letters, lambda x: x.h)
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
                

    def identify_spaces(self, rows:list[list[Letter]]):
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
                
    def finalize_letters(self, letters):
        rows = self.group_rows(letters)
        spaced = self.identify_spaces(rows)
        self.message = self.convert_to_txt(spaced)
        with open('decoded_message.txt', 'w') as f:
            f.write(self.message)
        finalized = []
        for row in spaced:
            for word in row:
                finalized.extend(word)
        return finalized

    def solve_letter(self, img_gray, letter, letter_char, all_letters:list[Letter], threshold):
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
        

    def identify_scale(self, single_letter_path, known_letter_char, font_path):
        single = self.format_letter_png(single_letter_path)
        known = self.format_letter_png(f'{font_path}/{self.convert_letter_path(known_letter_char)}.png')
        single_dim = single.shape[::-1]
        known_dim = known.shape[::-1]
        scale = single_dim[1]/known_dim[1]
        return scale

    def scale_letters(self, font_path, output_path, letters, scale):
        if not os.path.exists(output_path):
            os.makedirs(output_path)
        for l in letters:
            orig = cv.imread(f'{font_path}/{self.convert_letter_path(l)}.png', cv.IMREAD_UNCHANGED)
            if orig is not None:
                _, w, h = orig.shape[::-1]
                new_size = (round(w*scale), round(h*scale))
                scaled = cv.resize(orig, new_size)
                cv.imwrite(f'{output_path}/{self.convert_letter_path(l)}.png', scaled)


    def match_letters(self, img_path, font_path, letter_subset=['a', 'b', 'c', 'd', 'e', 'f', 'g', 'h',
                                                    'i', 'j', 'k', 'l','m','n', 'o', 'p', 'q',
                                                    'r', 's', 't', 'u', 'v', 'w', 'x', 'y','z',
                                                    'A', 'B', 'C', 'D', 'E', 'F', 'G', 'H', 'I',
                                                    'J', 'K', 'L', 'M','N', 'O', 'P', 'Q', 'R',
                                                    'S', 'T', 'U', 'V', 'W', 'X', 'Y', 'Z'],
                                                    match_thresh = 0.6):
        img_rgb = cv.imread(img_path)
        img_gray = cv.cvtColor(img_rgb, cv.COLOR_BGR2GRAY)
        _, img_gray = cv.threshold(img_gray, 128, 255, cv.THRESH_BINARY)
        letters = self.iterate_letters(img_gray, font_path, letter_subset, match_thresh)
        final = self.finalize_letters(letters)
        self.draw_letters(img_rgb, final)
        cv.imwrite(self.output_image_path, img_rgb)

    def extract_font(self, font_path, output_path, size, letters):
        if not os.path.exists(output_path):
            os.makedirs(output_path)
        for letter in letters:
            font = TTFont(font_path)
            img = Image.new('RGBA', (size, size), (255, 255, 255, 0))
            draw = ImageDraw.Draw(img)
            font = ImageFont.truetype(font_path, size)
            draw.text((0, 0), letter, font=font, fill=(0, 0, 0))

            img.save(f'{output_path}/{self.convert_letter_path(letter)}.png')

    def adjust_font_scale(self, save_path, font_path, letter_path, letter_char, letters):
        print('Identifying scale...')
        if '.' in font_path:
            default_size = 100
            self.extract_font(font_path, save_path, default_size, letters)
            scale = self.identify_scale(letter_path, letter_char, save_path)
            self.extract_font(font_path, save_path, round(default_size*scale), letters)
        else:
            scale = self.identify_scale(letter_path, letter_char, font_path)
            self.scale_letters(font_path, save_path, letters, scale)
        print('Done')


    def convert_letter_path(self, letter:str):
        upper = '_u'
        lower = '_l'
        if not letter.isalpha():
            return letter
        if letter == letter.upper():
            return f'{letter.lower()}{upper}'
        else:
            return f'{letter}{lower}'
            

    def solve_font(self, font_path, message_path, letter_path, letter_char, letters, threshold):
        save_path = 'res/font_imgs'
        self.adjust_font_scale(save_path, font_path, letter_path, letter_char, letters)
        self.match_letters(message_path, save_path, letters, threshold)