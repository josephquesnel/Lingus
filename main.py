import tkinter as tk
import os
import csv
import json
from PIL.ImageTk import PhotoImage, Image
from random import choice
from pandas import read_csv


# def get_raw_words():
#    """Used to grab raw language list from Git for further translation. Not used directly in main application"""
#    r = requests.get("https://raw.githubusercontent.com/hermitdave/FrequencyWords/master/content/2018/fr/fr_50k.txt").text.split()
#    open(f'{PATH}languages/fr.csv', 'w').write('\n'.join(r[:3000:2]))

# Constants
PATH = os.getcwd().replace("\\", "/") + '/'
LEGEND = {'fr': 'French', 'de': 'German', 'es': 'Spanish'}

# Global variables
root = None
wait = True
length_total = 0
word_pair = {}
pair_index = 0
selected_language = {}


################## Main Stuff ###########################

## AWFUL FUNCTIONS TOO MANY GLOBAL VARIABLES
## FIXXXXXXXXXXXX
## NEED TO FIX:
## 

def get_config():
    """ Gets config file info for transitions, previous state memory ect"""
    try:
        with open(f"{PATH}config.txt") as f:
            config = f.read().split('=')[1]
            if not config:
                return 'fr'
            return config
    except:
        with open(f"{PATH}config.txt", 'w') as f:
            f.write('text=fr')
        return 'fr'

def set_config(language):
    with open(f"{PATH}config.txt", 'w') as f:
        f.write(f'text={language}')

def get_language_length():
    """ Gets the total length of the current (configured) language"""
    config = get_config()
    try:
        with open(f"{PATH}languages/{config}.csv") as lang_file: 
            return len(list(csv.DictReader(lang_file)))
    except FileNotFoundError:
        raise FileNotFoundError("config.txt has a language name that isnt in the language folder.")

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

def save_progress():
    # Tries to find and rewrite the old save with a new one.
    config = get_config()
    try:
        with open(f"{PATH}save.json") as old_save:
            new_save:dict = json.load(old_save)
            old_save.close()
    except json.JSONDecodeError: 
        new_save = {config:{}}
    
    finally:
        new_save[config] = selected_language
        
        with open(f"{PATH}save.json",'w') as saved:
            json.dump(new_save, saved)
    
def get_word():
    """ Removes at random a new word from the saved language deck on display and updates display globals with new word data"""
    global word_pair, pair_index
    save_progress()
    pair_index = choice(list(selected_language.keys()))    
    word_pair = selected_language.pop(pair_index)
    select_word = word_pair[LEGEND[get_config()]]
    select_ans = word_pair['English']
    
    canvas.delete('back','btxt1','btxt2','front','ftxt1','ftxt2')
    canvas.itemconfigure("score", text=f"{(length_total-len(selected_language))}/{length_total}")
    cardfront(select_word,select_ans)

def wrong_new_card():
    """ Adds the popped word pair back to the deck and updating visuals"""
    selected_language.update({pair_index: word_pair})
    get_word()

def right_new_card():
    """ Does not add the popped pair, updates visuals including deck progress"""
    get_word()
    
def get_saved_language_data(language):
    """ Sets the config to new language and returns the save"""
    
    set_config(language)
    try:
        with open(f"{PATH}save.json") as saved:
            new_save = json.load(saved)[language]
    
    except (KeyError , json.JSONDecodeError) :
        fix_save = json.load(open(f"{PATH}save.json"))
        fix_save[language] = read_csv(f"{PATH}languages/{language}.csv", encoding='utf8').to_dict(orient='index')
        new_save = fix_save[language]
        
        with open(f"{PATH}save.json", "w") as saved:
            json.dump(fix_save, saved)
        print("Debug, keyerror/ decoder error somehow... resetting language data")
            
    except FileNotFoundError:
        with open(f"{PATH}save.json", "w") as saved:
            new_save = read_csv(f"{PATH}languages/{language}.csv", encoding='utf8').to_dict(orient='index')
            json.dump({language:new_save}, saved)
            
    return new_save

def menu_switch_language(language):
    """ Switches the language to the new one, for menu selection"""
    global selected_language, length_total
    selected_language = get_saved_language_data(language)
    length_total = get_language_length()
    
    pause()
    get_word()
    
        
def new_cards():
    """Refreshes the deck and starts over by reloading the original file"""
    global selected_language
    selected_language = read_csv(f"{PATH}languages/{get_config()}.csv", encoding='utf8').to_dict(orient='index')
    
    pause()
    get_word()

def cardfront(select_word, select_ans):
    """ Main function to display the front of the card"""
    canvas.delete('back','btxt1','btxt2') # tags represent canvas objects
    canvas.create_image(500,300, image=card_front, tag='front')
    canvas.create_text(500,200, text=LEGEND[get_config()], font=("Times New Roman", 60,'bold'), tag='ftxt1')
    canvas.create_text(500,320, text=select_word, font=("Times New Roman", 45,'normal'), tag='ftxt2')
    canvas.tag_raise("score")
    if wait:
        return
    else:
        root.after(5000,cardback,(select_word, select_ans))
    
def cardback(select_word, select_ans):
    canvas.delete('front','ftxt1','ftxt2')
    canvas.create_image(500,300, image=card_back, tag='back')
    canvas.create_text(500,200, text="English", font=("Times New Roman", 60,'bold'), tag='btxt1')
    canvas.create_text(500,320, text=select_ans, font=("Times New Roman", 45,'normal'), tag='btxt2')
    canvas.tag_raise("score")
    
    # click mouse to reset card flip
    canvas.bind("<Button-1>", func=lambda event: cardfront(select_word, select_ans) )

def get_language_files():
    """ 
    Automatically adds any new language files to menu selection
    """
    language_file_directories = os.listdir(f"{PATH}languages/")
    for language_path in language_file_directories:
        with open(f"{PATH}languages/{language_path}") as f:
            name = f.readline().split(',')[0]
            lang = language_path[:2]
            language_menu.add_command(label=name, command=lambda lang=lang:menu_switch_language(lang))


root = tk.Tk()
root.maxsize(width=1000, height=700)
root.minsize(width=1000, height=700)
root.title('Lingus')

canvas = tk.Canvas(root, bg='teal', height=700,width=1000)
canvas.create_text(750,100, text=f"", tag='score', font=("Times New Roman", 30))
canvas.pack()

card_front = PhotoImage(Image.open(f"images/card_front.png"))
card_back = PhotoImage(Image.open(f"images/card_back.png"))
right = PhotoImage(Image.open(f"images/right.png"))
wrong = PhotoImage(Image.open(f"images/wrong.png"))
start_img = PhotoImage(Image.open(f"images/start_button.png"))
stop_img = PhotoImage(Image.open(f"images/stop_button.png"))

selected_language = get_saved_language_data(get_config())
length_total = get_language_length()

get_word()
pause()

button_right = tk.Button(root, image=right, bd=0, activebackground='teal', bg='teal', relief='flat', command=right_new_card)
button_wrong = tk.Button(root, image=wrong, bd=0, activebackground='teal', bg='teal', relief='flat', command=wrong_new_card)
button_wrong.place(x=150,y=580)
button_right.place(x=750,y=580)

# Menu Stuff!
menubar = tk.Menu(root, background='white', foreground='black', activebackground='white', activeforeground='black')  
file_menu = tk.Menu(menubar, tearoff=0, background='white', foreground='black')
language_menu = tk.Menu(file_menu, tearoff=0, background='white', foreground='black')

get_language_files()

file_menu.add_command(label="New Deck", command=new_cards)
file_menu.add_cascade(label="Language", menu=language_menu)  
file_menu.add_separator()  
file_menu.add_command(label="Exit", command=root.quit)  
menubar.add_cascade(label="File", menu=file_menu)
root.configure(menu=menubar)
root.mainloop()
