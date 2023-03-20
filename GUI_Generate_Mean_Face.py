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
        txt_mainText.insert(END,item['folder_name_2_level'].ljust(35,' ')+"  "+ item['nFile']+" images".ljust(15,' ') +reversedString+"\n")
    txt_mainText.config(state=DISABLED)

def getBrowseFolder():

    global root_path

    returnBrowseMaskFolder = filedialog.askopenfilename(initialdir = rootPath,filetypes = (("BMP",   "*.bmp"),
                                                       ("all files",  "*.*")))
    if len(returnBrowseMaskFolder)>0:
        print (returnBrowseMaskFolder)
        splitedStr = returnBrowseMaskFolder.split("/")

        selectedFolder = splitedStr[:-1]
        selectedFolder_2_level = selectedFolder[-2].ljust(10," ") +selectedFolder[-1]
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
    ret, npImage = cv2.threshold(image_file, 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)

    image_file = np.where(npImage>0,npImage,0)

    orig_h,orig_w = image_file.shape[0],image_file.shape[1]

    if (orig_h != h or orig_w != w):
        #image_file.resize((h,w))
        image_file = cv2.resize(image_file, dsize=(h, w), interpolation=cv2.INTER_CUBIC)

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
                image_file = readBMPWithThred(fullPath)
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
    for imageID in tqdm(range (1270)):
        if (countFile[imageID]  > 0):
            stackedImg[imageID]/=countFile[imageID]
            lb_status.config(text="Generating mean mask " +str( int(imageID * 100 / 1270)) + "%")
            txt_mainText.update()

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
    folder_selected = filedialog.askdirectory(initialdir = rootPath)
    folder_selected +="/MeanMask"
    createFolder (folder_selected)

    generateMeanMask(folder_selected)

    print ("Done")


if __name__ == '__main__':
    try:
        # main form
        root = Tk()  # create root window
        root.title("GUI Mask Out - chgiang@2023")
        root.config(background='#23242a')
        # root.config(bg="skyblue")
        root.geometry("680x440")
        default_font = tkfont.nametofont("TkDefaultFont")
        default_font.configure(size=11)
        root.option_add("*Font", default_font)

        # Create Frame widget
        # frame = Frame(root, width=960, height=400)
        # frame.grid_propagate(0)

        top_frame = Frame(root,background='#23242a')
        bottom_frame = Frame(root,background='#23242a')
        #line = Frame(root, height=1, width=300, bg="grey80", relief='groove')

        top_frame.pack(side=TOP)
        #line.pack(pady=0)
        bottom_frame.pack(side=BOTTOM)

        #select folder
        #lb_selectMaskFolder = Label(top_frame, text="Select Experiment Folder:")
        #input_browseMaskFolder = Entry(top_frame, text="", width=20)
        btn_browseMaskFolder = Button(top_frame, text="Add Experiment folder", command=getBrowseFolder, bg='#87CEEB')
        #lb_selectMaskFolder.grid(row=0, column=0, pady=20, padx=4)
        #input_browseMaskFolder.grid(row=0, column=1, pady=20, padx=4)
        btn_browseMaskFolder.grid(row=0, column=2, pady=20, padx=4)

        #btn generate mean face
        btn_browseMaskFolder = Button(bottom_frame, text="Generate Mean Face", command=saveMeanMask, bg='#87CEEB')
        btn_browseMaskFolder.grid(row=2, column=1, pady=15, padx=4)
        # btn generate mean face
        btn_browseMaskFolder = Button(bottom_frame, text="Remove Last Folder", command=removeLastItem, bg='#87CEEB')
        btn_browseMaskFolder.grid( row=2, column=0, pady=15, padx=4,sticky=tkinter.W)

        # text box
        txt_mainText = scrolledtext.ScrolledText(bottom_frame, height=14, width=70, state='disabled', spacing1=5)
        txt_mainText.tag_config('done', foreground="green")
        txt_mainText.grid(row=0, column=0, pady=10, padx=10, columnspan=2, sticky=tkinter.N)
        font = tkfont.Font(font=txt_mainText["font"])
        tab_width = font.measure(" " * 8)
        txt_mainText.config(tabs=tab_width)

        lb_status = Label(bottom_frame, text="Status bar",background='light gray',width=75,height=1, anchor="w", justify=LEFT)
        lb_status.grid(row=3, column=0, pady=0, padx=0, sticky=tkinter.W,columnspan=3)

        root.mainloop()
    except Exception as e :
        print (e)
        print ("Some errror, just by pass")
        pass