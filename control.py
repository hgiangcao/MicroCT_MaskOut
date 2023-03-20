
from tkinter import Button,CENTER

background_color = '#313a4a'
button_color = '#1d5eff'

def MyButton(root,text,command,background_color=None,boderwidth = 0,highlightthickness=0,height=1,width=None):
    if (background_color==None):
        background_color = button_color
    button = Button(root, text=text, command=command, bg=background_color, borderwidth=boderwidth,
           highlightthickness=highlightthickness,height=height,fg="white",width=width)
    button.config(font='sans 11 bold')
    return button
