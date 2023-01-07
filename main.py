import tkinter as tk
import os
import csv
import json
from PIL.ImageTk import PhotoImage, Image
from random import choice


# def get_raw_words():
#    """Used to grab raw language list from Git for further translation. Not used directly in main application"""
#    r = requests.get("https://raw.githubusercontent.com/hermitdave/FrequencyWords/master/content/2018/fr/fr_50k.txt").text.split()
#    open(f'{PATH}languages/fr.csv', 'w').write('\n'.join(r[:3000:2]))

# Constants
PATH = os.getcwd().replace("\\", "/") + '/'
LEGEND = {'fr': 'French', 'de': 'German', 'es': 'Spanish'}

# Global variables
root = None
click_flag = 0
wait = True
config = ''
length_total = 0
select_word = ''
select_ans = ''
word_pair = {}
pair_index = 0
selected_language = {}

################## Main Stuff ###########################
def get_config():
    """ Gets config file info for transitions, previous state memory ect"""
    global config, length_total
    try:
        with open(f"{PATH}config.txt") as f:
            config = f.read().split('=')[1]
            if not config:
                config ='fr'
    except:
        with open(f"{PATH}config.txt", 'w') as f:
            f.write('text=fr')
        config = 'fr'
    length_total = len(list(csv.DictReader(open(f"{PATH}languages/{config}.csv", encoding='utf8'))))
    
def pause():
    global wait, button_stop, button_start
    wait = True
    try:
        button_stop.destroy()
    except NameError:
        pass
    
    button_start = tk.Button(root, image=start_img, bd=0, activebackground='teal', bg='teal', relief='flat', command=begin)
    button_start.place(x=450,y=580)

def begin():
    global wait, button_start, button_stop
    wait = False
    try:
        button_start.destroy()
    except NameError:
        pass
    
    button_stop = tk.Button(root, image=stop_img, bd=0, activebackground='teal', bg='teal', relief='flat', command=pause)
    button_stop.place(x=450,y=580)
    cardfront()

def save_progress():
    # Empties dictionary before re-assigning to it
    with open(f"{PATH}save.json") as saved:
        try:
            file:dict = json.load(saved)
            if config in file.keys():
                file[config] = {}
            saved.close()
        except json.JSONDecodeError: 
            file = {config:{}}
    
        finally: 
            file[config] = selected_language
    
    with open(f"{PATH}save.json",'w') as saved:
        json.dump(file, saved)
    
def get_word():
    """ Removes at random a new word from the saved language deck on display and updates display globals with new word data"""
    global select_word, select_ans, word_pair, pair_index
    save_progress()
    pair_index = choice(list(selected_language.keys()))
    word_pair = selected_language.pop(pair_index)
    select_word = word_pair[LEGEND[config]]
    select_ans = word_pair['English']

def wrong_new_card():
    """ Adds the popped word pair back to the deck and updating visuals"""
    selected_language.update({pair_index: word_pair})
    get_word()
    cardfront()

def right_new_card():
    """ Does not add the popped pair, updates visuals including deck progress"""
    get_word()
    cardfront()
    canvas.itemconfigure("score", text=f"{(length_total-len(selected_language))}/{length_total}")
    
def get_saved_language(language):
    """ Opens the selected language's data and updates config before updating details"""
    global selected_language
    with open(f"{PATH}config.txt", 'w') as f:
        f.write(f'text={language}')
    try:
        with open(f"{PATH}save.json") as saved:
            selected_language = json.load(saved)[language]
    except json.JSONDecodeError: 
        selected_language = csv.DictReader(open(f"{PATH}languages/{language}.csv", encoding='utf8'))
        
    pause()
    get_config()
    get_word()
    
    if type(root) == tk.Tk:
        canvas.delete('back','btxt1','btxt2','front','ftxt1','ftxt2')
        cardfront()
        canvas.itemconfigure("score", text=f"{(length_total-len(selected_language))}/{length_total}")
        
def new_cards():
    """Refreshes the deck and starts over by reloading the original file"""
    global selected_language
    selected_language = read_csv(f"{PATH}languages/{config}.csv", encoding='utf8').to_dict(orient='index')
    
    canvas.delete('back','btxt1','btxt2','front','ftxt1','ftxt2')
    pause()
    get_word()
    canvas.itemconfigure("score", text=f"{(length_total-len(selected_language))}/{length_total}")
    cardfront()

def cardfront():
    """ Main function to display the front of the card, 
        click_flag prevents clicking before the card flips to ensure proper card flip behavior"""
    global click_flag
    click_flag = 0
    canvas.delete('back','btxt1','btxt2') # tags represent canvas objects
    canvas.create_image(500,300, image=card_front, tag='front')
    canvas.create_text(500,200, text=LEGEND[config], font=("Times New Roman", 60,'bold'), tag='ftxt1')
    canvas.create_text(500,320, text=select_word, font=("Times New Roman", 45,'normal'), tag='ftxt2')
    canvas.tag_raise("score")
    if wait:
        return
    else:
        root.after(5000,cardback)
    
def cardback():
    global click_flag
    click_flag = 1
    canvas.delete('front','ftxt1','ftxt2')
    canvas.create_image(500,300, image=card_back, tag='back')
    canvas.create_text(500,200, text="English", font=("Times New Roman", 60,'bold'), tag='btxt1')
    canvas.create_text(500,320, text=select_ans, font=("Times New Roman", 45,'normal'), tag='btxt2')
    canvas.tag_raise("score")

def get_language_files():
    """ 
    Automatically adds any new language files to menu selection
    """
    language_file_directories = os.listdir(f"{PATH}languages/")
    for language_path in language_file_directories:
        with open(f"{PATH}languages/{language_path}") as f:
            name = f.readline().split(',')[0]
            lang = language_path[:2]
            language.add_command(label=name, command=lambda lang=lang:get_saved_language(lang))


get_config()

root = tk.Tk()
root.maxsize(width=1000, height=700)
root.minsize(width=1000, height=700)
root.title('Lingus')

canvas = tk.Canvas(root, bg='teal', height=700,width=1000)

card_front = PhotoImage(Image.open(f"images/card_front.png"))
card_back = PhotoImage(Image.open(f"images/card_back.png"))
right = PhotoImage(Image.open(f"images/right.png"))
wrong = PhotoImage(Image.open(f"images/wrong.png"))
start_img = PhotoImage(Image.open(f"images/start_button.png"))
stop_img = PhotoImage(Image.open(f"images/stop_button.png"))

get_saved_language(config)
canvas.create_text(750,100, text=f"{(length_total-len(selected_language))}/{length_total}", tag='score', font=("Times New Roman", 30))
canvas.pack()

button_right = tk.Button(root, image=right, bd=0, activebackground='teal', bg='teal', relief='flat', command=right_new_card)
button_wrong = tk.Button(root, image=wrong, bd=0, activebackground='teal', bg='teal', relief='flat', command=wrong_new_card)
button_wrong.place(x=150,y=580)
button_right.place(x=750,y=580)

cardfront()

# Mouse stuff
canvas.bind("<Button-1>", func=lambda event: cardfront() if click_flag == 1 else None)

# Menu Stuff!
menubar = tk.Menu(root, background='white', foreground='black', activebackground='white', activeforeground='black')  
file_menu = tk.Menu(menubar, tearoff=0, background='white', foreground='black')
language = tk.Menu(file_menu, tearoff=0, background='white', foreground='black')

get_language_files()

file_menu.add_command(label="New Deck", command=new_cards)
file_menu.add_cascade(label="Language", menu=language)  
file_menu.add_separator()  
file_menu.add_command(label="Exit", command=root.quit)  
menubar.add_cascade(label="File", menu=file_menu)
root.configure(menu=menubar)
root.mainloop()
