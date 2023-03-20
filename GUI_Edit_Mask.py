import tkinter.messagebox

import cv2
import numpy as np
import time
import os
from tqdm import tqdm
from tkinter import *
import tkinter.filedialog as filedialog
from PIL import Image, ImageTk
import glob
import tkinter.font as tkfont
from tkinter.messagebox import askokcancel, showinfo, WARNING,askyesno
from tkinter import scrolledtext
nImage = 1270
startImageID = 37
h,w = 1504,1504
resize_h, resize_w = 320,320
rootPath = r"/media/chgiang/DATA/home/giang/XuGi_DATA/Esegmentation/"

data_dict = []

import platform
import subprocess

listMask = []
listMast_temp = []
listMast_temp_resize = []
listMast_original_resize = []
listMast_save = []

def raiseErrorNoMask():
    lb_status.config(text="No mask is loaded yet!!!")
    lb_status.update()

def getBrowseMaskFolder():
    returnBrowseMaskFolder = filedialog.askopenfilename(initialdir = rootPath,filetypes = (("BMP",   "*.bmp"),
                                                       ("all files",  "*.*")))

    if (len(returnBrowseMaskFolder) > 0):
        splitedStr = returnBrowseMaskFolder.split("/")

        maskFolder = splitedStr[:-1]
        maskFolder = '/'.join(maskFolder) +"/"
        print (maskFolder)
        getListMask(maskFolder,r_hight=resize_h,r_width=resize_w)

        lb_status.config(text="Done load "+str(len(data_dict))+" maskes")

def getListMask(maskFolder=None,r_hight=460,r_width = 460):
    global nMask, displayImage
    nStackMask = 20
    for i in range (nStackMask):
        fileNameMean = r""+maskFolder + "mask_" + str(i) + "_8bit.bmp"
        mask = cv2.imread(fileNameMean, -1)

        if r_hight is not None and r_width is not None:
            resized_mask = cv2.resize(mask, dsize=(r_hight, r_width), interpolation=cv2.INTER_AREA)

        mask = np.where(mask > 0, 1, 0)
        listMask.append(mask)
        listMast_temp.append(np.copy(mask))
        listMast_temp_resize.append(resized_mask)
        listMast_original_resize.append(np.copy(resized_mask))

        item = {
            'full_path': fileNameMean,
            'file_name': "mask_" + str(i) + "_8bit.bmp"
        }
        data_dict.append(item)

    print ("done load",len(listMask),"maskes")
    nMask = len(listMask)

    displayImage = listMast_temp_resize[currentMaskID - 1]
    updateLabelIndicator()
    updateDisplayImage()


def updateLabelIndicator():
    global  lb_indicator
    lb_indicator.config(text=str(currentMaskID) + "/" + str(nMask))
    lb_indicator.update()

def updateDisplayImage():
    global imgtk,nMask
    if (nMask>0):

        #draw brush

        imgtk = ImageTk.PhotoImage(image=Image.fromarray(displayImage))
        panelA.configure(image=imgtk)

    else:
        raiseErrorNoMask()

    #print (resized_img.shape)


def selectNextMask():

    global currentMaskID,nMask,displayImage
    if (nMask==0):
        raiseErrorNoMask()
        return

    currentMaskID +=1
    currentMaskID%= (nMask +1)
    displayImage = listMast_temp_resize[currentMaskID-1]
    updateLabelIndicator()
    updateDisplayImage()
    lb_status.config(text="")
    lb_status.update()

def selectPrevMask():
    global currentMaskID,nMask,displayImage
    if (nMask==0):
        raiseErrorNoMask()
        return

    currentMaskID -=1
    if(currentMaskID <=0 ):
        currentMaskID = nMask
    displayImage = listMast_temp_resize[currentMaskID - 1]
    updateLabelIndicator()
    updateDisplayImage()
    lb_status.config(text="")
    lb_status.update()

#mouse move
brush_size = 50
brush_area = np.ones((brush_size*2,brush_size*2))*255
from PIL import Image, ImageDraw
def mouse_move(event):
    global displayImage
    if (nMask>0):
        root.config(cursor="cross")
        #Restore()
        abs_coord_x = panelA.winfo_pointerx() - panelA.winfo_rootx() -1
        abs_coord_y = panelA.winfo_pointery() - panelA.winfo_rooty() -1


        from_y, to_y = max(0, abs_coord_y - brush_size), min(resize_h - 1, abs_coord_y + brush_size)
        from_x, to_x = max(0, abs_coord_x - brush_size), min(resize_h - 1, abs_coord_x + brush_size)

        brush_layer_outline = Image.fromarray(np.zeros((resize_h, resize_w)))
        draw_Image = ImageDraw.Draw(brush_layer_outline)
        rec = (from_x, from_y,to_x,to_y)
        draw_Image.ellipse(rec, fill="#fff000", outline="#f00000",width=7)

        displayImage = listMast_temp_resize[currentMaskID - 1] + (1-np.array(brush_layer_outline))

        updateDisplayImage()

        if (abs_coord_x <0 or abs_coord_x >= resize_w or abs_coord_y < 0 or abs_coord_y >= resize_w):
            root.config(cursor="arrow")

def mouse_click(event):
    global  displayImage
    if (nMask>0):
        abs_coord_x = panelA.winfo_pointerx() - panelA.winfo_rootx() - 1
        abs_coord_y = panelA.winfo_pointery() - panelA.winfo_rooty() - 1

        from_y, to_y = max(0, abs_coord_y - brush_size), min(resize_h - 1, abs_coord_y + brush_size)
        from_x, to_x = max(0, abs_coord_x - brush_size), min(resize_h - 1, abs_coord_x + brush_size)

        brush_layer = Image.fromarray(np.ones((resize_h, resize_w)))
        draw_Image = ImageDraw.Draw(brush_layer)
        rec = (from_x, from_y, to_x, to_y)
        draw_Image.ellipse(rec, fill="#000000", outline="#000000")

        temp_display = listMast_temp_resize[currentMaskID - 1] * np.array(brush_layer)


        listMast_temp_resize[currentMaskID - 1] = temp_display
        displayImage  = listMast_temp_resize[currentMaskID - 1]

        updateDisplayImage()
        lb_status.config(text="Erased")
    else:
        raiseErrorNoMask()

def increase_brush_size(event):
    global  brush_size
    brush_size+=1
    brush_size = min(brush_size, 50)
    lb_status.config(text="Brush size " +str(brush_size))
    lb_status.update()

    mouse_move(event)


def decrease_brush_size(event):
    global brush_size
    brush_size-=1
    brush_size = max(brush_size,0)
    lb_status.config(text="Brush size " + str(brush_size))
    lb_status.update()
    mouse_move(event)

#image processing
def Clear():
    global displayImage
    if (nMask>0):
        listMast_temp_resize[currentMaskID-1] *=0
        displayImage = listMast_temp_resize[currentMaskID - 1]
        updateDisplayImage()
        lb_status.config(text="!!! Cleared mask " + data_dict[currentMaskID - 1]['file_name'])
    else:
        raiseErrorNoMask()
# def Undo():
#     updateDisplayImage()
def Restore():
    global displayImage
    if (nMask>0):
        listMast_temp_resize[currentMaskID-1]  = np.copy(listMast_original_resize[currentMaskID-1])
        displayImage = listMast_temp_resize[currentMaskID - 1]
        updateDisplayImage()
        lb_status.config(text="Restore to original mask " + data_dict[currentMaskID - 1]['file_name'])
    else:
        raiseErrorNoMask()
def Save():
    global  displayImage
    #save current mask
    if(nMask>0):
        cv2.imwrite(r"" + data_dict[currentMaskID-1]['full_path'], listMast_temp_resize[currentMaskID-1].astype(np.uint16))
        displayImage = listMast_temp_resize[currentMaskID - 1]
        updateDisplayImage()
        lb_status.config(text="Saved mask "+data_dict[currentMaskID-1]['file_name'])
    else:
        raiseErrorNoMask()



imgtk = None
currentMaskID = 1
nMask = 0
displayImage = None
if __name__ == '__main__':
    try:
        # main form
        root = Tk()  # create root window
        root.title("GUI Mask Out - chgiang@2023")
        # root.config(bg="skyblue")
        root.geometry("550x645")
        default_font = tkfont.nametofont("TkDefaultFont")
        default_font.configure(size=11)
        root.option_add("*Font", default_font)


        top_frame = Frame(root)
        bottom_frame = Frame(root)

        top_frame.pack(side=TOP)
        bottom_frame.pack(side=BOTTOM)


        #select folder
        btn_browseMaskFolder = Button(top_frame, text="Select Folder Mask", command=getBrowseMaskFolder)
        btn_browseMaskFolder.grid(row=0, column=1, pady=20, padx=4)

        # Prev
        btn_browseMaskFolder = Button(top_frame, text="<< Prev",command=selectPrevMask)
        btn_browseMaskFolder.grid(row=1, column=0,sticky=tkinter.W)
        # select folder
        btn_browseMaskFolder = Button(top_frame, text="Next >>",command=selectNextMask)
        btn_browseMaskFolder.grid(row=1, column=2,sticky=tkinter.E)
        # select Next

        lb_indicator = Label(top_frame, text="0/0", height=1,justify=CENTER)
        lb_indicator.grid(row=1, column=1,sticky=tkinter.W+tkinter.E)


        imgtk =  ImageTk.PhotoImage(image=Image.fromarray(np.zeros((480,480))))
        panelA = Label(top_frame, image=imgtk)
        panelA.image = imgtk
        panelA.grid(row=2, column=0, pady=4, padx=4,columnspan=3, sticky=tkinter.N)

        #bottom
        # Prev
        btn_browseMaskFolder = Button(top_frame, text="Clear", width=8, command=Clear)
        btn_browseMaskFolder.grid(row=3, column=0, sticky=tkinter.W)
        # select folder
        # btn_browseMaskFolder = Button(top_frame, text="Undo",width=8, command=Undo)
        # btn_browseMaskFolder.grid(row=3, column=1,sticky=tkinter.W+tkinter.E)

        btn_browseMaskFolder = Button(top_frame, text="Save",width=8, command=Save)
        btn_browseMaskFolder.grid(row=3, column=1,sticky=tkinter.W+tkinter.E)

        btn_browseMaskFolder = Button(top_frame, text="Restore",width=8, command=Restore)
        btn_browseMaskFolder.grid(row=3, column=2,sticky=tkinter.E)

        lb_status = Label(top_frame, text="Status bar", background='light gray', width=45, height=1, anchor="w",
                          justify=LEFT)
        lb_status.grid(row=4, column=0, pady=10, padx=10,columnspan=3, sticky=tkinter.W)

        panelA.bind("<Motion>", mouse_move)
        panelA.bind("<Button-1>", mouse_click)
        panelA.bind("<Button-4 >", increase_brush_size)
        panelA.bind("<Button-5>", decrease_brush_size)

        root.mainloop()
    except Exception as e :
        print (e)
        print ("Some errror, just by pass")
        pass