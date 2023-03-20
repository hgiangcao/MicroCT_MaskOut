import tkinter.messagebox

import cv2
import numpy as np
import time
import os
from tqdm import tqdm
from tkinter import *
import tkinter.filedialog as filedialog
from tkinter import PanedWindow
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

def open_explore(path):
    if platform.system() == "Windows":
        os.startfile(path)
    elif platform.system() == "Darwin":
        subprocess.Popen(["open", path])
    else:
        subprocess.Popen(["xdg-open", path])

def get_folder_name(path):
    list_file = glob.glob(r""+path+"/"+"*.log")
    return os.path.split( list_file[0])[-1]

def get_file_name_patten(path):
    list_file = glob.glob(r""+path+"/"+"*.log")
    return os.path.split( list_file[0])[-1]


def count_image_file(path):
    list_file = glob.glob(r""+path+"/"+"*.bmp")
    return len(list_file)

def ask_for_reversed():
    answer = askyesno(
        title='Check Reversed Order',
        message='Is the image in reversed order?',
        icon=tkinter.messagebox.QUESTION)

    if answer:
        return True
    else:
        return False

def removeLastItem():

    if (len(data_dict)>0):
        data_dict.pop()
    print_list_folder()

def print_list_folder():
    global txt_mainText
    txt_mainText.config(state=NORMAL)
    txt_mainText.delete(1.0,END)
    for item in data_dict:
        reversedString = "Normal"
        if (item['isReversed']):
            reversedString = "Reversed"
        txt_mainText.insert(END,item['folder_name_2_level'].ljust(35,' ')+"\n"+ item['nFile']+" images".ljust(15,' ') +"\n" +reversedString+"\n")
        txt_mainText.insert(END,"------------------------------" )

    txt_mainText.config(state=DISABLED)

def getBrowseFolder():

    global root_path

    returnBrowseMaskFolder = filedialog.askopenfilename(initialdir = rootPath,filetypes = (("BMP",   "*.bmp"),
                                                       ("all files",  "*.*")))
    if len(returnBrowseMaskFolder)>0:
        print (returnBrowseMaskFolder)
        splitedStr = returnBrowseMaskFolder.split("/")

        selectedFolder = splitedStr[:-1]
        selectedFolder_2_level = selectedFolder[-2].ljust(10," ") +"\n"+ selectedFolder[-1]
        selectedFolder_nameOnly =  selectedFolder[-1]
        selectedFolder = '/'.join(selectedFolder) +"/"

        isReversed = ask_for_reversed()

        fileNamePatten = splitedStr[-1][:-12]
        nFile = str(count_image_file(selectedFolder))
        item ={
            'full_path': selectedFolder,
            'folder_name':selectedFolder_nameOnly,
            'folder_name_2_level': selectedFolder_2_level,
            'file_patten':fileNamePatten,
            'isReversed': isReversed,
            'nFile':nFile
        }

        data_dict.append(item)

        print_list_folder()

        lb_status.config(text="Added folder "+selectedFolder_nameOnly)
        lb_status.update()

def createFolder(path):
    try:
        os.mkdir(path)
    except OSError:
        print ("Creation of the directory %s failed" % path)
        return False
    else:
        print ("Successfully created the directory %s " % path)
        return True

def readBMPWithThred(fullPath):
    image_file = cv2.imread(fullPath, -1)
    image_file *= 2
    ret, npImage = cv2.threshold(image_file, 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)

    image_file = np.where(npImage>0,npImage,0)

    orig_h,orig_w = image_file.shape[0],image_file.shape[1]

    if (orig_h != h or orig_w != w):
        #image_file.resize((h,w))
        image_file = cv2.resize(image_file, dsize=(h, w), interpolation=cv2.INTER_CUBIC)

    return image_file

def readBMPOrig(fullPath):
    image_file = cv2.imread(fullPath, -1)
    #ret, npImage = cv2.threshold(image_file, 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)

    #image_file = np.where(npImage>0,npImage,0)

    orig_h,orig_w = image_file.shape[0],image_file.shape[1]

    # if (orig_h != h or orig_w != w):
    #     #image_file.resize((h,w))
    #     image_file = cv2.resize(image_file, dsize=(h, w), interpolation=cv2.INTER_CUBIC)

    return image_file

def generateMeanMask (save_path):

    # logging
    global txt_mainText
    txt_mainText.config(state=NORMAL)
    txt_mainText.insert(END,"-------------------------------- \n")
    txt_mainText.insert(END, "Start generate Mean Mask to \n" + save_path +" \n")
    txt_mainText.update()

    print("stack files...")
    stackedImg = np.zeros((nImage, h, h))
    countFile = np.zeros((nImage))
    print (len(data_dict))
    for item in data_dict:
        folderName = item['folder_name']
        folderName_full = item['full_path']
        countFileFolder= 0
        txt_mainText.insert(END, "Processing folder "+folderName+" ... \n  ")
        txt_mainText.update()
        for imageID in tqdm  (range(nImage)):
            if item['isReversed']:
                imageID_temp = nImage - imageID
            else:
                imageID_temp = imageID
            #print (imageID)

            imageIDX = startImageID + imageID_temp
            fileName = r""+item['file_patten']+str(imageIDX).zfill(8)+".bmp"
            #print (fileName)
            fullPath =  r""+folderName_full +"/" +fileName

            isFileExist = os.path.isfile(fullPath)
            if(isFileExist):
                #print(fullPath + "\n")
                image_file = readBMPWithThred(fullPath) # readBMPOrig(fullPath)
                stackedImg[imageID] += image_file
                countFile[imageID] +=1
                countFileFolder +=1


            lb_status.config(text="Processing " +item['folder_name']+" " +str(int(countFileFolder*100/int(item['nFile']))) +"%")
            txt_mainText.update()

        txt_mainText.insert(END, "Successfully process " + str(countFileFolder) + " files" + " \n",'done')
        txt_mainText.update()
        print("Folder", folderName, "has", str(countFileFolder), "files")

    print ("generate mean mask...")
    txt_mainText.insert(END, "Generating mean mask ... \n")
    txt_mainText.update()
    '''
    for imageID in tqdm(range (1270)):
        if (countFile[imageID]  > 0):
            stackedImg[imageID]/=countFile[imageID]
            lb_status.config(text="Generating mean mask " +str( int(imageID * 100 / 1270)) + "%")
            txt_mainText.update()
    '''
    nStackMask =20
    stepStack =nImage//nStackMask

    txt_mainText.insert(END, "Generating stacked mean mask ... \n")
    print ("Generate stacked mask ... ")
    txt_mainText.insert(END, "Saving "+str(nStackMask)+ " stacked mean mask ... \n")
    txt_mainText.update()
    for i in range (nStackMask):
        meanMask = np.mean(stackedImg[i*stepStack:(i+1)*stepStack],axis=0)
        #meanMask/=stepStack
        fileNameMean = save_path +"/"+ "mask_" + str(i) + "_8bit.bmp"
        print (fileNameMean)
        lb_status.config(text="Saving stacked mean mask " + str(i+1) +"/"+str(nStackMask))
        txt_mainText.update()
        meanMask = np.where(meanMask>0,1,0) * 255

        cv2.imwrite(r""+fileNameMean, meanMask.astype(np.uint16))


    txt_mainText.insert(END,"Done. Stacked masks was succesfully saved to \n"+ save_path,'done')
    txt_mainText.update()
    lb_status.config(text="Done generate stacked maskes")
    txt_mainText.config(state=DISABLED)

    open_explore(save_path)

def saveMeanMask():

    if len(data_dict) == 0:
        lb_status.config(text="No experiment loaded")
        return

    folder_selected = filedialog.askdirectory(initialdir = rootPath)
    folder_selected +="/MeanMask/"
    createFolder (folder_selected)

    generateMeanMask(folder_selected)
    print ("Done")

    getListMask(folder_selected, r_hight=resize_h, r_width=resize_w)
    lb_status.config(text="Done load " + str(len(data_dict)) + " maskes")



from control import *

#===============================================#

data_dict_mask = []

import platform
import subprocess

listMask = []
listMast_temp = []
listMast_temp_resize = []
listMast_original_resize = []
listMast_save = []

def reset_data():
    global listMask,listMast_temp,listMast_temp_resize,listMast_original_resize,listMast_save,data_dict_mask
    listMask = []
    listMast_temp = []
    listMast_temp_resize = []
    listMast_original_resize = []
    listMast_save = []
    data_dict_mask = []

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

        lb_status.config(text="Done load "+str(len(data_dict_mask))+" maskes")

def getListMask(maskFolder=None,r_hight=460,r_width = 460):
    global nMask, displayImage

    reset_data()

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
        data_dict_mask.append(item)

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
    currentMaskID%= (nMask+1)

    if (currentMaskID==0):
        currentMaskID=1

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

        brush_layer_outline =Image.fromarray(np.zeros((resize_h, resize_w)))
        draw_Image = ImageDraw.Draw(brush_layer_outline)
        rec = (from_x, from_y,to_x,to_y)
        draw_Image.ellipse(rec,  outline="#ffffff",width=3)

        displayImage = listMast_temp_resize[currentMaskID - 1] + (np.array(brush_layer_outline))

        updateDisplayImage()

        if (abs_coord_x <0 or abs_coord_x >= resize_w or abs_coord_y < 0 or abs_coord_y >= resize_w):
            root.config(cursor="arrow")

def mouse_click(event):
    global  displayImage,listMast_temp
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

        #to real image
        brush_layer = Image.fromarray(np.ones((h, w)))
        draw_Image = ImageDraw.Draw(brush_layer)
        scale = h/resize_h

        center_x = (int) (abs_coord_x * scale)
        center_y = (int) (abs_coord_y * scale)
        real_brush_size = (int) (brush_size *scale )

        from_y, to_y = max(0, center_y - real_brush_size), min(h - 1, center_y + real_brush_size)
        from_x, to_x = max(0, center_x - real_brush_size), min(h - 1, center_x + real_brush_size)

        rec = (from_x, from_y, to_x, to_y)
        draw_Image.ellipse(rec, fill="#000000", outline="#000000")

        listMast_temp[currentMaskID - 1] = (listMast_temp[currentMaskID - 1] * np.array(brush_layer))

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
        listMast_temp [currentMaskID - 1] *= 0
        displayImage = listMast_temp_resize[currentMaskID - 1]
        updateDisplayImage()
        lb_status.config(text="!!! Cleared mask " + data_dict_mask[currentMaskID - 1]['file_name'])
    else:
        raiseErrorNoMask()
# def Undo():
#     updateDisplayImage()
def Restore():
    global displayImage
    if (nMask>0):
        listMast_temp_resize[currentMaskID-1]  = np.copy(listMast_original_resize[currentMaskID-1])
        listMast_temp[currentMaskID - 1] = np.copy(listMask[currentMaskID - 1])
        displayImage = listMast_temp_resize[currentMaskID - 1]
        updateDisplayImage()
        lb_status.config(text="Restore to original mask " + data_dict_mask[currentMaskID - 1]['file_name'])
    else:
        raiseErrorNoMask()


def expand_mask(mask):
    expand_pixel = 5
    current_h, current_w = mask.shape[0],mask.shape[1]
    copy_mask = np.copy(mask)

    for i in range (expand_pixel,current_h-expand_pixel):
        for j in range (expand_pixel,current_w-expand_pixel):
            if (mask[i,j]>0):
                copy_mask[i-expand_pixel:i+expand_pixel,j-expand_pixel:j+expand_pixel] = mask[i,j]

    copy_mask = cv2.resize(copy_mask, dsize=(h, w), interpolation=cv2.INTER_LINEAR)

    return copy_mask

def Save():
    global  displayImage,listMast_temp
    #save current mask
    if(nMask>0):

        #copy_mask = expand_mask(listMast_temp_resize[currentMaskID-1])
        #cv2.imwrite(r"" + data_dict_mask[currentMaskID-1]['full_path'], (listMast_temp[currentMaskID-1]+copy_mask*255).astype(np.uint16))
        #displayImage = listMast_temp_resize[currentMaskID - 1]
        #updateDisplayImage()
        cv2.imwrite(r"" + data_dict_mask[currentMaskID - 1]['full_path'], (listMast_temp[currentMaskID - 1] * 255).astype(np.uint16))

        lb_status.config(text="Saved mask "+data_dict_mask[currentMaskID-1]['file_name'])
    else:
        raiseErrorNoMask()



imgtk = None
currentMaskID = 1
nMask = 0
displayImage = None
#==============================================#

if __name__ == '__main__':
    try:
        # main form
        root = Tk()  # create root window

        root.title("GUI Mask Out - chgiang@2023")
        root.config(background=background_color)
        root.geometry("710x510")
        #root.tk.call('tk', 'scaling', 1.0)
        #default_font = font.Font(family='Arial', size=11)
        default_font = tkfont.nametofont("TkDefaultFont")
        default_font.configure(size=11)
        root.option_add("*Font", default_font)

        main_frame =  PanedWindow(root, background="#313a4a",width=700)
        footer = Frame(root, background='#313a4a',highlightbackground="white", height=50)
        footer.pack(side="bottom", fill="x")

        # ----------LEFT FRAME-------------------#
        add_exp_frame = Frame(main_frame, background=background_color, width=300, highlightbackground="white", padx=20,pady=10)
        edit_mask_frame = Frame(main_frame, background=background_color, width=400, highlightbackground="white",padx=20,pady=10)
        main_frame.pack(side=TOP)
        main_frame.add(add_exp_frame)
        main_frame.add(edit_mask_frame)

        btn_expFolder = MyButton(add_exp_frame, text="Add Experiment folder", command=getBrowseFolder)
        btn_expFolder.grid(row=0, column=0, pady=20, padx=4,columnspan=2)

        #btn generate mean face
        btn_generateMask = MyButton(add_exp_frame, text="Generate", command=saveMeanMask,background_color='#4caf50')
        btn_generateMask.grid(row=2, column=1, pady=0, padx=0,sticky=tkinter.E)
        # btn generate mean face
        btn_remove = MyButton(add_exp_frame, text="Remove", command=removeLastItem)
        btn_remove.grid( row=2, column=0, pady=15, padx=4,sticky=tkinter.W)

        # text box
        #txt_mainText = Text(add_exp_frame, height=18, width=30, state='disabled', spacing1=5, background=background_color,padx=3,fg='#f0f0f0',pady=3,highlightthickness=0,borderwidth= 0)
        txt_mainText = scrolledtext.ScrolledText(add_exp_frame, height=13, width=30, state='disabled', spacing1=5,
                            background=background_color, padx=3, fg='#f0f0f0', pady=3, highlightthickness=0,
                            borderwidth=0)

        txt_mainText.tag_config('done', foreground="green")
        txt_mainText.grid(row=1, column=0, pady=12, padx=5, columnspan=2, sticky=tkinter.N)
        font = tkfont.Font(font=txt_mainText["font"])
        tab_width = font.measure(" " * 8)
        txt_mainText.config(tabs=tab_width)

        #----------RIGHT FRAME-------------------#
        btn_browseMaskFolder = MyButton(edit_mask_frame, text="Select Folder Mask", command=getBrowseMaskFolder)
        btn_browseMaskFolder.grid(row=0, column=0,columnspan=3, pady=20)

        imgtk = ImageTk.PhotoImage(image=Image.fromarray(np.zeros((resize_h, resize_w))))
        panelA = Label(edit_mask_frame, image=imgtk)
        panelA.image = imgtk
        panelA.grid(row=2, column=0, pady=10, padx=4, columnspan=3, sticky=tkinter.N)
        panelA.bind("<Motion>", mouse_move)
        panelA.bind("<Button-1>", mouse_click)
        panelA.bind("<Button-4 >", increase_brush_size)
        panelA.bind("<Button-5>", decrease_brush_size)
        # Prev
        btn_browseMaskFolder = MyButton(edit_mask_frame, text="<< Prev", command=selectPrevMask)
        btn_browseMaskFolder.grid(row=1, column=0, sticky=tkinter.W)
        # select folder
        btn_browseMaskFolder = MyButton(edit_mask_frame, text="Next >>", command=selectNextMask)
        btn_browseMaskFolder.grid(row=1, column=2, sticky=tkinter.E)
        # select Next

        lb_indicator = Label(edit_mask_frame, text="0/0", height=1,width=5, justify=CENTER,bg=background_color,fg='white')
        lb_indicator.grid(row=3, column=1)

        btn_browseMaskFolder = MyButton(edit_mask_frame, text="Clear",  command=Clear)
        btn_browseMaskFolder.grid(row=3, column=0, sticky=tkinter.W)


        btn_browseMaskFolder = MyButton(edit_mask_frame, text="Save", command=Save)
        btn_browseMaskFolder.grid(row=1, column=1, )

        btn_browseMaskFolder = MyButton(edit_mask_frame, text="Restore",  command=Restore)
        btn_browseMaskFolder.grid(row=3, column=2, sticky=tkinter.E)

        # ----------STATUS----------------------#
        lb_status = Label(footer, text="This is the status bar",background='light gray',height=1,width=120,  justify=LEFT,anchor="w")
        lb_status.grid(row=0, column=0, pady=0, padx=0, sticky=tkinter.W)

        root.mainloop()
    except Exception as e :
        print (e)
        print ("Some errror, just by pass")
        pass