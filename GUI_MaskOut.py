import cv2
import numpy as np
import time
import os
from tqdm import tqdm

scale = 5
skip =  5
h,w = 1504,1504
nImage = 1270
nMaxImage = 100
startImageID = 37
idx =0 
img = np.zeros((h,w))
nStackMask = 20
stepStack = nImage // nStackMask


#rootPath = "C:\\chuot\\20220426_20 um_3_Rec\\"
rootPath = r"/media/chgiang/DATA/home/giang/XuGi_DATA/Esegmentation/"  # 20221102_20_um_3_Rec/"
listImgFile = []
listImg= []
listMask = []
listMaskedImg = []
listImgID = []
cube = []#np.zeros((750 // scale * 2, 750 // scale * 2, 750 // scale * 2))
PC = []

def createPLY(verties,fileName):
    strX = "ply\n format ascii 1.0\nelement vertex " + str(verties.shape[0])+\
            "\nproperty float x\nproperty float y\nproperty float z\nproperty uint8 red\nproperty uint8 green\nproperty uint8 blue\n"

    strX += "end_header\n"

    for i in range (verties.shape[0]):
        strX += str(verties[i,0]) + " "+ str(verties[i,1]) + " " + str(verties[i,2])  + " " + str(1) + " "+  str(1) + " " + str(1)
        
        strX+="\n"

    

    text_file = open(r""+fileName, "w")
    n = text_file.write(strX)
    text_file.close()
    print ("done create",fileName,"file")



def getListMask(maskFolder=None,hight=None,width = None):
    nStackMask = 20
    for i in range (nStackMask):
        fileNameMean = r""+maskFolder + "mask_" + str(i) + "_8bit.bmp"
        mask = cv2.imread(fileNameMean, -1)

        if hight is not None and width is not None:
            mask = cv2.resize(mask, dsize=(hight, width), interpolation=cv2.INTER_AREA)

        #print (mask.shape)
        mask = np.where(mask > 0, 1, 0)
        listMask.append(mask)
    print ("done load",len(listMask),"maskes")

def getListImgFile(folder,fileNamePrefix):
    tempListImgID=[]
    tempListImgFile = []
    for idx in range (nImage):
        fullPath = r""+folder+"/" + fileNamePrefix+str(idx+startImageID).zfill(8)+".bmp"
        #print (fullPath)
        isFileExist = os.path.isfile(fullPath)
        if(isFileExist):
            tempListImgID.append(idx)
            tempListImgFile.append(fullPath)

    nValidImage =len(tempListImgFile) # min(nMaxImage,len(tempListImgFile))
    step= int(len(tempListImgFile)//nValidImage) 

    print (nValidImage,"Files",step,"steps")

    for i in range (0,len(tempListImgFile),step):
        listImgID.append(tempListImgID[i])
        listImgFile.append(tempListImgFile[i])

    print ("done load",len(listImgFile)," images")


def readBMPWithThred(fullPath,hight=None,width = None):
    isFileExist = os.path.isfile(fullPath)
    if(isFileExist):
        #print (fullPath)
        image_file = cv2.imread(r""+fullPath, -1)

        if hight is not None and width is not None:
            image_file = cv2.resize(image_file, dsize=(hight, width), interpolation=cv2.INTER_AREA)

        #ret, npImage = cv2.threshold(image_file, 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)

        #image_file = np.where(npImage>0,npImage,0)

        return image_file
    else:
        return None
def getListImg(folder=""):
    global cube
    countPoint = 0
    for fullPath in tqdm(listImgFile, desc='listImgFile') :
        returnImage = readBMPWithThred(r""+fullPath,hight=h,width=w)

        if(returnImage is not None):
            _1s = np.where(returnImage>0,1,0).sum()
            countPoint +=_1s

            listImg.append(returnImage)

    print ("total:",countPoint,"points")
    

def generateMaskedImg():
    for value in range (len(listImgFile)):
        img = listImg[value]
        idx = listImgID[value]
        maskID = min(idx//stepStack,nStackMask-1)
        mask = listMask[maskID]
        listMaskedImg.append (img*mask)

def generateCube():
    global cube
    for maskImg in listMaskedImg:
        cube.append(maskImg)

    cube = np.array(cube)
    cube = np.transpose(cube,(1,2,0))

def generatePC():
    global cube
    generateCube()
    
    h,w,d = cube.shape
    verts = []
    skipDepth = d/h
    print (skipDepth,d//skipDepth)

    for x in range (h):
        for y in range (w):
            for tz in range (0,int(d//skipDepth)):
                z = (int)(tz*skipDepth)
                if (cube[x,y,z]):
                    verts.append([x,y,tz])

    verts = np.array(verts)
    plyFileName = ""
    createPLY(verts,plyFileName + "test.ply")
    

def getNextImage(x):
    global imageIDX
    global img
    global panelA,panelB,panelC,panelD
    global cube
    value = slider_image.get()
    img = listImg[value]
    idx = listImgID[value]
    maskID = min(idx//stepStack,nStackMask-1)
    mask = listMask[maskID]

    maskedImagetemp = listMaskedImg[value]

    maskedImage = np.zeros((h,w,3))
    maskedImage[:,:,0]= img
    maskedImage[:,:,1],maskedImage[:,:,2]=  img*(1-mask),img*(1-mask)

    maskoutImage = np.zeros((h,w,3))
    maskoutImage[:,:,0]= img*(mask)
    #maskoutImage[:,:,1],maskoutImage[:,:,2]=  img*(1-mask) ,img*(1-mask)
        
    resized_img =  cv2.resize(img, dsize=(160, 160), interpolation=cv2.INTER_AREA)
    resized_mask =  cv2.resize(mask, dsize=(160, 160), interpolation=cv2.INTER_AREA)
    resized_maskedImage =  cv2.resize(maskedImage, dsize=(160, 160), interpolation=cv2.INTER_AREA)
    resized_maskoutImage =  cv2.resize(maskoutImage, dsize=(160, 160), interpolation=cv2.INTER_AREA)
    

    imgtk = ImageTk.PhotoImage(image=Image.fromarray(resized_img))
    maskedImagetk = ImageTk.PhotoImage(image=Image.fromarray(resized_maskedImage.astype(np.uint8)))
    masktk = ImageTk.PhotoImage(image=Image.fromarray(mask*255))
    maskoutImagetk =  ImageTk.PhotoImage(image=Image.fromarray(resized_maskoutImage.astype(np.uint8)))
    

    if (panelA is None):
        panelA = Label(top_frame,image=imgtk)
        panelA.image = imgtk
        panelA.grid(row=1, column=0, pady=4, padx = 4)

        #masktk = ImageTk.PhotoImage(image=Image.fromarray(mask*255))
        panelB = Label(top_frame,image=masktk)
        panelB.image = masktk
        panelB.grid(row=1, column=1, pady=4, padx = 4)

        #maskedImagetk = ImageTk.PhotoImage(image=Image.fromarray(maskedImage))
        panelC = Label(top_frame,image=maskedImagetk)
        panelC.image = maskedImagetk
        panelC.grid(row=1, column=2, pady=4, padx = 4)

        panelD = Label(top_frame,image=maskoutImagetk)
        panelD.image = maskoutImagetk
        panelD.grid(row=1, column=3, pady=4, padx = 4)

        #4 labels
        lb_origImage = Label(top_frame, text="Orig image")
        lb_origImage.grid(row=2, column=0, padx = 4)
        lb_mask = Label(top_frame, text="Mask")
        lb_mask.grid(row=2, column=1,  padx = 4)
        lb_segmentImage = Label(top_frame, text="Segmented image")
        lb_segmentImage.grid(row=2, column=2,  padx = 4)
        lb_maskedImage = Label(top_frame, text="Masked-out image")
        lb_maskedImage.grid(row=2, column=3, padx = 4)

        #process button
        lb_process = Button(top_frame, text="Process!", command=process)
        lb_process.grid(row=3, column=1,columnspan=2, pady=4, padx = 4)

    else:
        panelA.configure(image=imgtk)
        panelB.configure(image=masktk)
        panelC.configure(image=maskedImagetk)
        panelD.configure(image=maskoutImagetk)
        panelA.image = imgtk
        panelB.image = masktk
        panelC.image = maskedImagetk
        panelD.image = maskoutImagetk


mainFolderName, fileNamePrefix ="",""
############# GUI events ########
def getBrowseFolder():
    global slider_image
    global mainFolderName, fileNamePrefix
    returnBrowseFolder = filedialog.askopenfilename(initialdir = rootPath,filetypes = (("BMP",   "*.bmp"),
                                                       ("all files",  "*.*")))
    input_browseFolder.delete(1, END)  # Remove current text in entry
    input_browseFolder.insert(0, returnBrowseFolder)  # Insert the 'path'
    #print (input_path)
    mainFolderName,fileNamePrefix = parseFileName(returnBrowseFolder)

    #process the rest of file
    getListImgFile(folder=mainFolderName,fileNamePrefix=fileNamePrefix)
    getListImg()
    generateMaskedImg()

    #tracker
    slider_image = Scale(top_frame,  from_=0, to=len(listImgFile)-1,  command=getNextImage,    orient=HORIZONTAL,length= 300)
    slider_image.grid(row=0, column=1,columnspan=2, pady=4, padx = 4)
    process()


def getBrowseMaskFolder():
    returnBrowseMaskFolder =  filedialog.askopenfilename(initialdir = rootPath,filetypes = (("BMP",   "*.bmp"),
                                                       ("all files",  "*.*")))
    input_browseMaskFolder.delete(1, END)  # Remove current text in entry
    input_browseMaskFolder.insert(0, returnBrowseMaskFolder)  # Insert the 'path'
    #input_browseMaskFolder.disable()
    splitedStr = returnBrowseMaskFolder.split("/")

    maskFolder = splitedStr[:-1]
    maskFolder = '/'.join(maskFolder) +"/"
    print (maskFolder)
    getListMask(maskFolder,hight=h,width=w)

def parseFileName(input_str):
    print (input_str)
    splitedStr = input_str.split("/")
    folderName = splitedStr[:-1]
    folderName = '/'.join(folderName) +"/"
    fileName = splitedStr[-1]

    fileNamePrefix = fileName[:-12]
    return folderName,fileNamePrefix

def createFolder(path):
    try:
        os.mkdir(path)
    except OSError:
        print ("Creation of the directory %s failed" % path)
        return False
    else:
        print ("Successfully created the directory %s " % path)
        return True
import shutil


def process(): #main function
    #create folder
    processedFolder = r""+mainFolderName+"/processed"
    createFolder(processedFolder)
    countPoint = 0
    for i in tqdm(range (len(listImgFile))):
        fileName = listImgFile[i].split("/")[-1]
        maskedImage = listMaskedImg[i]
        _1s = np.where(maskedImage>0,1,0).sum()
        countPoint +=_1s

        fileName=  processedFolder+ "/" + fileName
        cv2.imwrite(fileName, maskedImage.astype(np.uint16))

    #20220705_20 um_15__IR_rec.log
    #copy log file
    logfileName =  r""+listImgFile[i].split("/")[-1][:-12]+".log"
    sourceFile = r""+mainFolderName+ "/" + logfileName
    targetFile =  processedFolder+ "/" + logfileName
    print (sourceFile)
    print (targetFile)
    try:
        shutil.copyfile(sourceFile, targetFile)
        print("done copy log file")
    except:
        print("error copy log file")

    print ("total:",countPoint,"points")
    print ("Done processed",len(listImgFile),"files")

    #outputMaskedFile

    #copy other files

########## GUI #######

from tkinter import *
import tkinter.filedialog as filedialog
from PIL import Image, ImageTk

panelA = None
panelB = None
panelC = None
panelD = None
slider_image = None
btn_process = None

if __name__ == '__main__':
    #listMask = getListMask()
    #getListImgFile(folder="")
    #getListImg(folder="")
    
    #generateMaskedImg()
    #generateCube()
    #generatePC()



    #main form
    root = Tk()  # create root window
    root.title("GUI Mask Out - chgiang@2022")
    #root.config(bg="skyblue")
    root.geometry("760x420")
    # Create Frame widget
    #frame = Frame(root, width=960, height=400)
    #frame.grid_propagate(0)

    top_frame = Frame(root,width=760, height=320)
    bottom_frame = Frame(root,width=760, height=80)
    line = Frame(root, height=1, width=400, bg="grey80", relief='groove')

    top_frame.pack(side=TOP)
    line.pack(pady=10)
    bottom_frame.pack(side=BOTTOM)

    lb_selectFolder = Label(bottom_frame, text="Select Folder:")
    input_browseFolder = Entry(bottom_frame, text="", width=40)
    btn_browseFolder = Button(bottom_frame, text="Browse", command=getBrowseFolder)
    # lb_selectFolder.pack(side="left", padx=10, pady=10)
    # input_browseFolder.pack(side="left", padx=10, pady=10)
    # btn_browseFolder.pack(side="left", padx=10, pady=10)
    lb_selectFolder.grid(row=0, column=0, pady=4, padx = 4)
    input_browseFolder.grid(row=0, column=1, pady=4, padx = 4)
    btn_browseFolder.grid(row=0, column=2, pady=4, padx = 4)

    lb_selectMaskFolder = Label(bottom_frame, text="Select Mask Folder:")
    input_browseMaskFolder = Entry(bottom_frame, text="", width=40)
    btn_browseMaskFolder = Button(bottom_frame, text="Browse Mask", command=getBrowseMaskFolder)
    lb_selectMaskFolder.grid(row=1, column=0, pady=4, padx = 4)
    input_browseMaskFolder.grid(row=1, column=1, pady=4, padx = 4)
    btn_browseMaskFolder.grid(row=1, column=2, pady=4, padx = 4)

    root.mainloop()