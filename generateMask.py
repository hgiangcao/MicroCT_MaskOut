from plyfile import PlyData, PlyElement
from PIL import Image
import numpy as np
import os
import pyvista as pv
from tqdm import tqdm
import cv2
from utils import *

import numpy as np
import matplotlib.pyplot as plt
from mpl_toolkits.mplot3d.art3d import Poly3DCollection

from skimage import measure
from skimage.draw import ellipsoid

scale = 5
skip =  5
listFolderID = [4,5,6,7,8]
nImage = 1270
startImageID = 37
rootPath = "/media/chgiang/DATA/home/giang/XuGi_DATA/Esegmentation/"  # 20221102_20_um_3_Rec/"
h = 1504

'20220510_20 um_4_.log'
import glob
from os import listdir
from os.path import isfile, join
def get_folder_name(path):
    list_file = glob.glob(r""+path+"/"+"*.log")
    return os.path.split( list_file[0])[-1]

def count_image_file(path):
    list_file = glob.glob(r""+path+"/"+"*.bmp")
    return len(list_file)

# def editFileWithSpace(folderPath,search_str=' ',replace_str = '_'):
#     filenames = os.listdir(folderPath)
#     for filename in filenames:
#         os.rename(os.path.join(folderPath, filename), os.path.join(folderPath, filename.replace(search_str, replace_str)))
#
#     print ("Done edit",len(filenames),"files")

# def editAllFileNameWithSpace():
#     for folderID in listFolderID:
#         folderName = rootPath +  "20220426_20_um_" + str(folderID) + "_Rec"
#         editFileWithSpace (folderName)
'''
def createPLY(verties,surface,colors,fileName, isSaveMesh = False):
    colors = colors.astype("int")
    strX = "ply\n format ascii 1.0\nelement vertex " + str(verties.shape[0])+\
            "\nproperty float x\nproperty float y\nproperty float z\nproperty uint8 red\nproperty uint8 green\nproperty uint8 blue\n"

    if (isSaveMesh):
        strX += "element face "+str(surface.shape[0]) +"\n"
        strX += "property list uchar int vertex_index\n"
    strX += "end_header\n"

    for i in range (verties.shape[0]):
        strX += str(verties[i,0]) + " "+ str(verties[i,1]) + " " + str(verties[i,2])  + " " + str(colors[i]) + " "+  str(colors[i]) + " " + str(colors[i])
        if (not isSaveMesh):
            if (i!= verties.shape[0]-1):
                strX += "\n"
        else:
            strX+="\n"

    if (isSaveMesh):
        for i in range (surface.shape[0]):
            strX +=  str(len(surface[i])) +" " + str(int (surface[i,2])) + " "+ str(int (surface[i,1])) + " " + str(int (surface[i,0]))
            if (i!= surface.shape[0]-1):
                strX+="\n"

    text_file = open(fileName, "w")
    n = text_file.write(strX)
    text_file.close()
'''

def readBMPWithThred(fullPath):
    image_file = cv2.imread(fullPath, -1)
    ret, npImage = cv2.threshold(image_file, 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)

    image_file = np.where(npImage>0,npImage,0)

    return image_file

'''
def readBMPOrig(fullPath):
    image_file = cv2.imread(fullPath, -1)
    #print(np.min(image_file), np.max(image_file))
    return image_file
'''

def generateMask ():
    print("stack files...")
    stackedImg = np.zeros((nImage, h, h))
    countFile = np.zeros((nImage))
    print (len(listFolderNames))
    for folderID in range (len(listFolderNames)):
        folderName = listFolderNames[folderID]
        folderName_full = listFolderNames_full[folderID]
        countFileFolder= 0
        print(folderName_full)

        for imageID in tqdm  (range(nImage)):
            if folderID in [0,1]:
                imageID_temp = nImage - imageID
            else:
                imageID_temp = imageID
            #print (imageID)
            imageIDX = startImageID + imageID_temp
            fileName = r""+folderName[:-4]+"__IR_rec"+str(imageIDX).zfill(8)+".bmp"
            #print (fileName)
            fullPath =  r""+folderName_full +"/" +fileName

            isFileExist = os.path.isfile(fullPath)
            if(isFileExist):
                #print(fullPath + "\n")
                image_file = readBMPWithThred(fullPath)
                stackedImg[imageID] += image_file
                countFile[imageID] +=1
                countFileFolder +=1
        print("Folder", folderName, "has", str(countFileFolder), "files")



    print ("generate mean mask...")

    for imageID in tqdm(range (1270)):
        if (countFile[imageID]  > 0):
            stackedImg[imageID]/=countFile[imageID]

    nStackMask =20
    stepStack =nImage//nStackMask
    print ("Generate stacked mask ... ")

    for i in range (nStackMask):
        meanMask = np.mean(stackedImg[i*stepStack:(i+1)*stepStack],axis=0)
        #meanMask/=stepStack
        fileNameMean = rootPath + "Mean_Mask/" + "mask_" + str(i) + "_8bit.bmp"
        print (fileNameMean)
        meanMask = np.where(meanMask>0,1,0) * 255

        cv2.imwrite(fileNameMean, meanMask.astype(np.uint16))
'''
def readMask():
    nStackMask = 20
    listMask = []
    for i in range (nStackMask):
        fileNameMean = rootPath + "Mean_Mask/" + "mask_" + str(i) + "_8bit.bmp"
        mask = cv2.imread(fileNameMean, -1)
        print (mask.shape)
        mask = np.where(mask > 0, 1, 0)
        listMask.append(mask)
    return listMask

'''
'''
def updatePC(img,cube,depth,color=255):
    #resize
    img = (img * 255).astype (np.uint8)
    h, w = img.shape[0] // scale, img.shape[1] // scale
    img = cv2.resize(img, (h, w), interpolation=cv2.INTER_AREA)



    for i in range (0,img.shape[0],1):
        for j in range(0,img.shape[1],1):
            if (img[i,j]>0):
                cube[i,j,int (depth)] = color

    return cube
'''
'''
def generateMaskedBMP(folderName,folderID,listMask):
    nStackMask = 20
    stepStack = nImage // nStackMask

    cube = np.zeros((750 // scale * 2, 750 // scale * 2, 750 // scale * 2))

    for imageID in tqdm(range(0, nImage,skip)):
        imageIDX = startImageID + imageID
        fileName = "20220426_20_um_" + str(folderID) + "__rec" + str(imageIDX).zfill(8) + ".bmp"
        fullPath = rootPath + folderName + "/" + fileName
        isFileExist = os.path.isfile(fullPath)
        if (isFileExist):
            maskID = min(imageID//stepStack,nStackMask-1)
            mask = listMask[maskID]
            image_file = readBMPOrig(fullPath)
            masked_image_file = image_file #* mask
            #print (np.min(masked_image_file),np.max(masked_image_file))
            fileName=  rootPath + folderName+"_Test" + "/" + fileName
            cv2.imwrite(fileName, masked_image_file.astype(np.uint16))

            #color = min(255, 10 + 256 // nStackMask * maskID)
            #cube = updatePC(masked_image_file,cube,depth=  imageID/skip,color = color)

    #verts, faces, normals, values = measure.marching_cubes(cube, 0)
    #print(verts.shape, faces.shape, values.shape)
    #plyFile = rootPath + folderName+"_Processed" + "/"
    #createPLY(verts, faces, values, plyFile + folderName+".ply", isSaveMesh=True)
    #editFileWithSpace( rootPath + folderName+"_Test" + "/", search_str='_um_', replace_str=' um_')
'''
listFolderNames = []
listFolderNames_full = []
if __name__ == '__main__':
    #/media/chgiang/DATA/home/giang/XuGi_DATA/chuot/Esegmentation/1
    #/media/chgiang/DATA/home/giang/XuGi_DATA/chuot/Esegmentation/1


    for folderID in listFolderID:
        folder_path = rootPath + "/" + str(folderID)
        folder_name = get_folder_name(folder_path)[:-4] # remove ".log"
        print(folder_name)
        folder_name += "Rec"
        listFolderNames.append(folder_name)
        listFolderNames_full.append(folder_path + "/" + folder_name + "/")
        print (folder_path+"/"+folder_name)
        n_image_file = count_image_file(folder_path+"/"+folder_name)


        print ("folder",folder_path,"has",n_image_file,"files")

    #editAllFileNameWithSpace()
    generateMask()
    # listMask = readMask()
    # folderName = "20220426_20_um_3_Rec"
    # generateMaskedBMP (folderName= folderName,folderID=3,listMask = listMask)
    #generatePC(folderName=folderName,folderID=1,listMask=listMask, isSavePly = True)



