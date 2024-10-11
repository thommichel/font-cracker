# Font-Cracker
I hardly know her

## Installation

This project has been tested on Python **3.10.12** and **3.11.9**

Clone the repo into a directory using 

`git clone https://github.com/thommichel/font-cracker.git`

Then enter the directory by running

`cd font-cracker`

### Virtual Environment

Using a virtual environment is recommended to ensure packages are installed correctly.

Install one using one of the following depending on your version of python

- `python3.10 -m venv .venv`

- `python3.11 -m venv .venv` 

### Packages

Once the virtual environment is setup, install the required packages by running

`pip install -r requirements.txt`

## Font Cracking CLI

To solve a font run the main CLI python program by running

`python ./main.py`

You will then have to enter 5 items:

1. The path to the font file (`.ttf` or `.otf`) that the message is encoded in

2. The path to the image of the encoded message

3. The path to the image of one of the letters in the message image. **IMPORTANT: THIS IMAGE BUT BE AT THE SAME SCALE/MAGNIFICATION OF THE PREVIOUS IMAGE** this is needed to identify the font size of the encoded message. An easy way to ensure this is by duplicating the encoded message image and cropping out one of the letters. It is ok if the letter is surrounded by white space. Check `examples/trees_s.png` for reference

4. The actual letter of the image from step 3. In the example of `examples/trees_s.png` this would simply be `s`. Keep in mind that this is case senstive so make sure the letter matches the case of the letter in the font

5. The percent threshold. This threshold determines what percent of a match the letter must be in order to be considered. The lower this is, the more accurate the program will be, but the longer it will take. This must be a float between 0 and 1. If some letters cannot be identified, rerun the program at a lower threshhold.

For other examples of inputs, look at the commented out examples in `main.py`

### Font File Alternatives

If instead of a `.ttf` or `.otf` file, a folder will all of the letters as images is found instead, it can be used instead of a font file. For this to work ensure each letter matches the following format

lower case letter: `a` --> `a_l.png`

upper case letter: `A` --> `a_u.png`

where `_l` signifies lower case and `_u` signifies upper case

This folder can then be entered instead of a font file in the CLI. Look at `examples/fonts/unown` for reference