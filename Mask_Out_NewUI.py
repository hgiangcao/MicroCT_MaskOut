
from tkinter import *
import tkinter.filedialog as filedialog
import numpy as np
import tkinter.font as tkfont
from PIL import Image, ImageTk
import cv2

nImage = 1270
startImageID = 37
h,w = 1504,1504
resize_h, resize_w = 256,256
from customtkinter import CTkSlider

rootPath = r"/media/chgiang/DATA/home/giang/XuGi_DATA/Esegmentation/"
from Generate_Mean_Face_NewUI import get_folder_name, get_file_name_patten, count_image_file,ask_for_reversed,readBMPOrig,createFolder,open_explore

from control import background_color,MyButton
from tqdm import tqdm
import os
listMask = []
listMask_resize = []
listImage= []
listImage_resize = []
data_img_dict=[]
data_folder_dict= []
data_mask_dict =[]
listImgFileName = []


def reset_data():
    global listMask,listMask_resize,listImage,data_folder_dict,data_mask_dict,data_img_dict,listImgFileName
    listMask = []
    listMask_resize = []
    listImage = []
    data_folder_dict = []
    data_mask_dict = []
    data_img_dict = []
    listImgFileName = []

def getListImage(item,r_hight=256,r_width=256):
    global listImage,slider_imagek,currentImageID
    folderName = item['folder_name']
    folderName_full = item['full_path']

    for imageID in tqdm(range(nImage)):
        if item['isReversed']:
            imageID_temp = nImage - imageID
        else:
            imageID_temp = imageID
        # print (imageID)

        imageIDX = startImageID + imageID_temp
        fileName = r"" + item['file_patten'] + str(imageIDX).zfill(8) + ".bmp"
        # print (fileName)
        fullPath = r"" + folderName_full + "/" + fileName

        isFileExist = os.path.isfile(fullPath)
        if (isFileExist):
            # print(fullPath + "\n")
            image_file = readBMPOrig(fullPath)
            #listImage.append(image_file)
            listImgFileName.append(fullPath)

            if r_hight is not None and r_width is not None :
                resized_img = cv2.resize(image_file, dsize=(r_hight, r_width), interpolation=cv2.INTER_AREA)
                listImage_resize.append (resized_img)

        lb_status.config(text="Loading data ..." + str((int)(imageID/nImage*100))+ "%")
        lb_status.update()

    print ("done load ",len(listImage), "images")

    #reconfig slider
    #slider_image = CTkSlider(main_frame, from_=1, to=len(listImage), number_of_steps=len(listImage), width=300, command=slideImage)
    #slider_image.set(0)
    #slider_image.grid(row=3, column=0, columnspan=3, pady=4, padx=4)

    currentImageID = 1
    updateDisplayImage()

def getBrowseFolder():
    global root_path,data_folder_dict

    
    returnBrowseMaskFolder = filedialog.askopenfilename(initialdir=rootPath, filetypes=(("BMP", "*.bmp"),
                                                                                        ("all files", "*.*")))
    if len(returnBrowseMaskFolder) > 0:
        root.config(cursor="watch")
        lb_status.config(text="Loading sequence images ...")
        lb_status.update()


        print(returnBrowseMaskFolder)
        splitedStr = returnBrowseMaskFolder.split("/")

        selectedFolder = splitedStr[:-1]
        selectedFolder_2_level = selectedFolder[-2].ljust(10, " ") + "\n" + selectedFolder[-1]
        selectedFolder_nameOnly = selectedFolder[-1]
        selectedFolder = '/'.join(selectedFolder) + "/"

        isReversed = ask_for_reversed()

        fileNamePatten = splitedStr[-1][:-12]
        nFile = str(count_image_file(selectedFolder))
        item = {
            'full_path': selectedFolder,
            'folder_name': selectedFolder_nameOnly,
            'folder_name_2_level': selectedFolder_2_level,
            'file_patten': fileNamePatten,
            'isReversed': isReversed,
            'nFile': nFile
        }

        data_folder_dict.append(item)

        #get list image only one
        getListImage(item,resize_h,resize_w)

        #print_list_folder()

        #update mask button
        btn_selectMask.config(state=NORMAL)

        lb_status.config(text="Added folder " + selectedFolder_nameOnly)
        lb_status.update()

    root.config(cursor="")


def getBrowseMaskFolder():

    returnBrowseMaskFolder = filedialog.askopenfilename(initialdir = rootPath,filetypes = (("BMP",   "*.bmp"),
                                                       ("all files",  "*.*")))

    if (len(returnBrowseMaskFolder) > 0):
        splitedStr = returnBrowseMaskFolder.split("/")

        maskFolder = splitedStr[:-1]
        maskFolder = '/'.join(maskFolder) +"/"
        print (maskFolder)
        getListMask(maskFolder,r_hight=resize_h,r_width=resize_w)

        # update mask button
        btn_Process.config(state=NORMAL)

        lb_status.config(text="Done load "+str(len(data_mask_dict))+" maskes")

def getListMask(maskFolder=None,r_hight=460,r_width = 460):
    global nMask, displayImage,displayImage_mask,currentMaskID,listMask

    #reset_data()

    nStackMask = 20
    for i in range (nStackMask):
        fileNameMean = r""+maskFolder + "mask_" + str(i) + "_8bit.bmp"
        mask = cv2.imread(fileNameMean, -1)

        if r_hight is not None and r_width is not None:
            resized_mask = cv2.resize(mask, dsize=(r_hight, r_width), interpolation=cv2.INTER_AREA)

        mask = np.where(mask > 0, 1, 0)
        listMask.append(mask)

        listMask_resize.append(resized_mask)

        item = {
            'full_path': fileNameMean,
            'file_name': "mask_" + str(i) + "_8bit.bmp"
        }
        data_mask_dict.append(item)

    print ("done load ",len(listMask),len(listMask_resize),"maskes")
    nMask = len(listMask)

   #updateLabelIndicator()
    currentMaskID = 1

    updateDisplayImage()


def slideImage(event):
    global  currentImageID,currentMaskID,displayImage_mask,nImage,nMask

    if (len(listMask_resize)>0):
        stepStack = nImage // nMask

        value =(int) (slider_image.get())

        currentMaskID =  min(value//stepStack+1,20)

        currentImageID = min(value,len(listImage_resize))

        #update label
        lb_mask_id.config(text=str(currentMaskID)+"/20")
        lb_img_id.config(text=str(currentImageID)+"/"+str(nImage))
        lb_processed_id.config(text=str(currentImageID) + "/" + str(nImage))

        #update image
        updateDisplayImage()

import shutil

def expand_mask(mask,orig_h, orig_w):
    expand_pixel = 5
    current_h, current_w = mask.shape[0],mask.shape[1]
    copy_mask = np.copy(mask)

    for i in range (expand_pixel,current_h-expand_pixel):
        for j in range (expand_pixel,current_w-expand_pixel):
            if (mask[i,j]>0):
                copy_mask[i-expand_pixel:i+expand_pixel,j-expand_pixel:j+expand_pixel] = mask[i,j]

    copy_mask = cv2.resize(copy_mask, dsize=(orig_h, orig_w), interpolation=cv2.INTER_LINEAR)

    copy_mask =  np.where(copy_mask > 0, 1, 0)

    return copy_mask

import glob

def process(): #main function
    global tempListImgID,listImgFile,data_folder_dict
    print (data_folder_dict)
    item = data_folder_dict[0]
    root.config(cursor="watch")
    root.update()

    folderName_full = item['full_path']

    for imageID in tqdm(range(nImage)):
        if item['isReversed']:
            imageID_temp = nImage - imageID
        else:
            imageID_temp = imageID

        imageIDX = startImageID + imageID_temp
        fileName = r"" + item['file_patten'] + str(imageIDX).zfill(8) + ".bmp"

        fullPath = r"" + folderName_full + "/" + fileName
        isFileExist = os.path.isfile(fullPath)
        if (isFileExist):
            image_file = readBMPOrig(fullPath)
            listImage.append(image_file)

        lb_status.config(text="Loading data ..." + str((int)(imageID/nImage*50))+ "%")
        lb_status.update()

    orig_h, orig_w =listImage[0].shape[0],listImage[0].shape[1]

    mainFolderName = item['full_path']
    # create folder
    processedFolder = r"" + mainFolderName + "/processed"
    createFolder(processedFolder)
    countPoint = 0
    stepStack = nImage // nMask

    listEnhenceMask = []
    for maskID in range (len(listMask_resize)):
        enhence_mask = expand_mask(listMask_resize[maskID],orig_h, orig_w)
        listEnhenceMask.append(enhence_mask)

    for i in tqdm(range(len(listImage))):
        fileName = listImgFileName[i].split("/")[-1]

        maskID = min(i // stepStack, nMask - 1)

        #mask = listMask[maskID]

        enhence_mask  = listEnhenceMask[maskID] #expand_mask(listMask_resize[maskID])

        img = listImage[i]

        maskedImage = img*enhence_mask

        fileName = processedFolder + "/" + fileName
        #print (fileName)
        cv2.imwrite(fileName, maskedImage.astype(np.uint16))

        lb_status.config(text="Saving data ..." +  str((int)(i/nImage*50 + 50))+ "%")
        lb_status.update()

    # 20220705_20 um_15__IR_rec.log
    # copy log file
    logfileName = r"" + item['file_patten'] + ".log"
    sourceFile = r"" + mainFolderName + "/" + logfileName
    targetFile = processedFolder + "/" + logfileName
    #print(sourceFile)
    #print(targetFile)
    try:
        shutil.copyfile(sourceFile, targetFile)
        print("done copy log file")
    except:
        print("error copy log file")

    #print("total:", countPoint, "points")
    #print("Done processed", len(listImgFile), "files")
    lb_status.config(text="Done save "+str((len(listImage_resize)))+"files")
    open_explore(mainFolderName)
    root.config(cursor="")

def updateDisplayImage():
    #display mask img
    global  currentImageID,currentMaskID,listImage,listMask_resize

    if (len(listMask_resize) > 0):
        imgMasktk = ImageTk.PhotoImage(image=Image.fromarray(listMask_resize[currentMaskID - 1]))
        panelMask.configure(image=imgMasktk)
        panelMask.image=imgMasktk
    if (len(listImage_resize) > 0):
        imgtk = ImageTk.PhotoImage(image=Image.fromarray(listImage_resize[currentImageID - 1]))
        panelOrig.configure(image=imgtk)
        panelOrig.image=imgtk

        if (len(listMask_resize) > 0):
            #process
            img = listImage_resize[currentImageID - 1]
            mask = listMask_resize[currentMaskID-1]
            maskoutImage = np.zeros((resize_h,resize_h, 3))
            maskoutImage[:, :, 0] = img * (mask)
            maskoutImagetk = ImageTk.PhotoImage(image=Image.fromarray(maskoutImage.astype(np.uint8)))
            panelResult.configure(image=maskoutImagetk)
            panelResult.image = maskoutImagetk

blank_image = Image.fromarray(np.ones((resize_w,resize_h)))
currentMaskID = 1
currentImageID = 1
nMask = 0
displayImage_mask = None

if __name__ == '__main__':
    try:
        # main form
        root = Tk()  # create root window
        blank_imagetk = ImageTk.PhotoImage(image=blank_image)

        root.title("GUI Mask Out - chgiang@2023")
        root.config(background=background_color)
        root.geometry("860x460")
        #root.tk.call('tk', 'scaling', 1.0)
        #default_font = font.Font(family='Arial', size=11)
        default_font = tkfont.nametofont("TkDefaultFont")
        default_font.configure(size=11)
        root.option_add("*Font", default_font)

        main_frame = Frame(root, width=860, height=430,background=background_color,pady=30)
        main_frame.pack(side=TOP)

        #3 button
        btn_selectExperiment = MyButton(main_frame, text="Select Experiment",command=getBrowseFolder)
        btn_selectMask= MyButton(main_frame, text="Select Masks",command=getBrowseMaskFolder)
        btn_selectMask.config(state=DISABLED)
        btn_Process = MyButton(main_frame, text="Process!!!",background_color='green',command=process)
        btn_Process.config(state=DISABLED)

        btn_selectExperiment.grid(row=0, column=0, pady=4, padx=4)
        btn_selectMask.grid(row=0, column=1, pady=4, padx=4)
        btn_Process.grid(row=0, column=2, pady=4, padx=4)

        panelOrig = Label(main_frame, image=blank_imagetk)
        panelOrig.image = blank_image
        panelMask = Label(main_frame, image=blank_imagetk)
        panelMask.image = blank_image
        panelResult = Label(main_frame, image=blank_imagetk)
        panelResult.image = blank_image

        panelOrig.grid(row=1, column=0, pady=10, padx=10)
        panelMask.grid(row=1, column=1, pady=10, padx=10)
        panelResult.grid(row=1, column=2, pady=10, padx=10)

        lb_img_id = Label(main_frame, text="0/0")
        lb_mask_id =Label(main_frame, text="0/0")
        lb_processed_id = Label(main_frame, text="0/0")
        lb_img_id.grid(row=2, column=0, pady=10, padx=10)
        lb_mask_id.grid(row=2, column=1, pady=10, padx=10)
        lb_processed_id.grid(row=2, column=2, pady=10, padx=10)

        slider_image = CTkSlider(main_frame, from_=1, to=nImage,number_of_steps=nImage,width=300,command=slideImage)
        slider_image.set(0)
        slider_image.grid(row=3, column=0, columnspan=3, pady=4, padx=4)


        lb_status = Label(main_frame, text="This is the status bar",background='light gray',height=1,width=106,  justify=LEFT,anchor="w")
        lb_status.grid(row=4, column=0, pady=20, padx=0,columnspan=3)


        root.mainloop()
    except Exception as e :
        print (e)
        print ("Some errror, just by pass")
        pass