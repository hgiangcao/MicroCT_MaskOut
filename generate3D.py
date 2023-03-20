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


scale = 2
skip =  2

print (cv2.THRESH_BINARY , cv2.THRESH_OTSU)

def editFileWithSpace(folderPath):
    filenames = os.listdir(folderPath)
    for filename in filenames:
        os.rename(os.path.join(folderPath, filename), os.path.join(folderPath, filename.replace(' ', '_')))

    print ("Done edit",len(filenames),"files")


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
            strX +=  str(len(surface[i])) +" " + str(int (surface[i,0])) + " "+ str(int (surface[i,1])) + " " + str(int (surface[i,2]))
            if (i!= surface.shape[0]-1):
                strX+="\n"

    text_file = open(fileName, "w")
    n = text_file.write(strX)
    text_file.close()

cubes = np.zeros ((750//scale*2,750//scale*2,750//scale*2))


def readBMP(root_path,folder_name,fileName,depth = 0,curentVerticesIDX=0,maxDepth = 1000) :
    global nMask
    global cubes
    global  mask_files
    vertices= []
    colors = []
    surfaces = []
    # image_file = Image.open(fileName)
    # npImage = np.array(image_file)

    image_file = cv2.imread(root_path+folder_name+fileName)

    image_file = cv2.cvtColor(image_file, cv2.COLOR_BGR2GRAY)

    h,w = image_file.shape[0]//scale,image_file.shape[1]//scale
    #
    image_file = cv2.resize(image_file, (h,w), interpolation = cv2.INTER_AREA)

    stepMask = maxDepth// nMask
    maskIndex = min(nMask-1,int (depth//stepMask))
    #print (maskIndex)


    #mask_files = (maskIndex > 0)*mask_files[maskIndex]

    image_file *= mask_files[maskIndex]
    r = min(255, 10 + 256//nMask * maskIndex)


    cv2.imwrite(root_path+"/test/"+fileName,image_file)


    # applying Otsu thresholding
    # as an extra flag in binary
    # thresholding
    ret, npImage = cv2.threshold(image_file, 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)


    # alpha = 1.5 # Contrast control (1.0-3.0)
    # beta = 50  # Brightness control (0-100)
    #
    # image_file = cv2.convertScaleAbs(image_file, alpha=alpha, beta=beta)
    #npImage = image_file

    for i in range (0,npImage.shape[0],1):
        for j in range(0,npImage.shape[1],1):
            if (npImage[i,j]>0):

                cubes[i,j,int (depth)] =r # image_file[i, j] # [image_file[i, j], r, image_file[i, j]]# image_file[i,j]

                vertices.append([i,j,depth])
                #vertices.append([i+scale, j, depth])
                #vertices.append([i, j+scale, depth])
                #vertices.append([i+scale, j + scale, depth])
                # surfaces.append([curentVerticesIDX+2,curentVerticesIDX+3,curentVerticesIDX+1,curentVerticesIDX])
                # curentVerticesIDX += 4
                #
                # vertices.append([i, j, depth])
                # vertices.append([i + scale, j, depth])
                # vertices.append([i + scale, j, depth+scale])
                # vertices.append([i,j, depth+scale])
                # surfaces.append([curentVerticesIDX + 2, curentVerticesIDX + 3, curentVerticesIDX , curentVerticesIDX+ 1])
                # curentVerticesIDX += 4
                #
                colors.append([image_file[i, j], r, image_file[i, j]])
                # colors.append([image_file[i, j], image_file[i, j], image_file[i, j]])
                # colors.append([image_file[i, j], image_file[i, j], image_file[i, j]])
                # colors.append([image_file[i, j], image_file[i, j], image_file[i, j]])
                # colors.append([image_file[i, j], image_file[i, j], image_file[i, j]])
                # colors.append([image_file[i, j], image_file[i, j], image_file[i, j]])
                # colors.append([image_file[i, j], image_file[i, j], image_file[i, j]])
                # colors.append([image_file[i, j], image_file[i, j], image_file[i, j]])
                # colors.append([image_file[i+scale, j], image_file[i+scale, j], image_file[i+scale, j]])
                # colors.append([image_file[i, j+scale], image_file[i, j+scale], image_file[i, j+scale]])
                # colors.append([image_file[i+scale, j + scale], image_file[i+scale, j + scale], image_file[i+scale, j + scale]])

    return np.array(vertices),np.array(colors),npImage,surfaces,curentVerticesIDX

def generatePC(folderName=None,root_path=None, isSave = False):
    global  cubes
    #get list file
    curentVerticesIDX =0
    folderName = "20221102_20_um_7_Rec/"
    root_path = "/media/chgiang/DATA/home/giang/XuGi_DATA/"  # 20221102_20_um_3_Rec/"
    # editFileWithSpace(root_path)
    listFiles = os.listdir("/media/chgiang/DATA/home/giang/XuGi_DATA/"+folderName)
    idx = []
    images = []



    print(len(listFiles[0]))
    print(len(listFiles[1]))

    for f in listFiles:
        #print (f)
        idx.append(int(f[25:32]))

    idx = np.array(idx)
    idx = np.sort(idx)

    globalVertices = np.zeros((0, 3))
    globalColors = np.zeros((0, 3))
    globalSurface = np.zeros((0, 4))

    for i in tqdm(range(0, idx.shape[0], skip)):
        fileName = "20221102_20_um_7__IR_rec"+ str(idx[i]).zfill(8) + ".bmp"
        # print (fileName)

        currentVertices, currentColors, image,currentSurface,curentVerticesIDX = readBMP(root_path,folderName, fileName, i/skip ,curentVerticesIDX=curentVerticesIDX,maxDepth=idx.shape[0]//skip)

        # print (currentVertices.shape)
        images.append(image)

        if (currentVertices.shape[0]!=0):
            globalVertices = np.vstack([globalVertices, currentVertices])
            globalColors = np.vstack([globalColors, currentColors])
        #globalSurface= np.vstack([globalSurface, currentSurface])


    # print("finale Vertices", globalVertices.shape)
    # print("finale Surface", globalSurface.shape)

    mean =np.array([globalVertices[:,0].mean(),globalVertices[:,1].mean(),globalVertices[:,2].mean()])
    # print (mean)
    globalVertices -=mean
    # print(globalVertices[:, 0].max() - globalVertices[:, 0].min())
    # print(globalVertices[:, 1].max() - globalVertices[:, 1].min())
    # print(globalVertices[:, 2].max() - globalVertices[:, 2].min())

    maxX, minX =globalVertices[:, 0].max() , globalVertices[:, 0].min()
    maxY, minY =globalVertices[:, 1].max() , globalVertices[:, 1].min()
    maxZ,minZ =globalVertices[:, 2].max() , globalVertices[:, 2].min()

    flag = False
    print ("cubes",(cubes>0).sum())

    print(minX, maxX)
    print(minY, maxY)
    print(minZ, maxZ)

    # newcube = cubes.copy()
    # #while (not flag):
    # step = 2
    # for i in tqdm(range (1,cubes.shape[0]-2,1)):
    #     for j in range (1,cubes.shape[1]-2,1):
    #         for k in range (1,cubes.shape[2]-2,1):
    #
    #             if ((cubes[i-1:i+2,j-1:j+2,k-1:k+2] >0).sum()>15):
    #                 newcube[i,j,k]  = 0
    #
    #
    # print ("newcube",(newcube>0).sum())
    #
    # verts, faces, normals, values = measure.marching_cubes(newcube, 0)
    verts, faces, normals, values = measure.marching_cubes(cubes, 0)

    print (verts.shape, faces.shape,values.shape)


    if (isSave):
        createPLY(verts,faces, values, "test_5.ply",isSaveMesh=True)

    return globalVertices, globalColors,globalSurface,images



nFolder = 12
root_path ="/media/chgiang/DATA/home/giang/XuGi_DATA/" #20221102_20_um_3_Rec/"
#editFileWithSpace(root_path)
listFiles = os.listdir("/media/chgiang/DATA/home/giang/XuGi_DATA/20221102_20_um_1_Rec/")
idx = []

nMask = 10
mask_files = []
for i in range (nMask):
    mask_fileName = root_path +"mean_mask_"+str(i)+".png"
    print (mask_fileName)
    mask_file = cv2.imread(mask_fileName)
    print (mask_file.shape)
    mask_file = cv2.cvtColor(mask_file, cv2.COLOR_BGR2GRAY)
    print (mask_file.shape[0],mask_file.shape[1])
    h,w = mask_file.shape[0]//scale,mask_file.shape[1]//scale
    mask_file = cv2.resize(mask_file, (h,w), interpolation = cv2.INTER_AREA)
    mask_file = mask_file > 0
    mask_files.append(mask_file)


print (len(listFiles[0]))
print (len(listFiles[1]))

for f in listFiles:
    #print (f)
    idx.append(int (f[25:32]))

idx = np.array(idx)
idx = np.sort(idx)

# for iFolder in range (nFolder+1):
#     folderName = "20221102_20_um_" + str(iFolder) + "_Rec/"
#     editFileWithSpace(root_path + folderName)

def saveMeanFace():
    nMask = 10
    stacked_masked = np.zeros((nMask,1476, 1476))
    folderMean = "20221102_20_um_" + str(0) + "_Rec/"
    stepMask = idx.shape[0]//nMask
    for iImage in tqdm(range(idx.shape[0])):
        meanFace = np.zeros((1476,1476))
        for iFolder in range(1, nFolder + 1):
            folderName = "20221102_20_um_" + str(iFolder) + "_Rec/"
            fileName = "20221102_20_um_"+str(iFolder)+"__IR_rec" + str(idx[iImage]).zfill(8) + ".bmp"

            fullPath = root_path+folderName + fileName
            #print (fullPath)
            image_file = cv2.imread(fullPath,-1)

            #image_file = cv2.cvtColor(image_file, cv2.COLOR_BGR2GRAY)

            #print (image_file.shape)
            meanFace+=image_file
            idxMask = (iImage//stepMask)
            stacked_masked[idxMask] +=image_file



        fileNameMean = root_path +folderMean + "20221102_20_um_" + str(0) + "__IR_rec" + str(idx[iImage]).zfill(8) + ".bmp"
        np.clip(meanFace, 0, 255, out=meanFace)
        cv2.imwrite(fileNameMean, (meanFace).astype(np.uint16))

        for i in range (nMask):
            fileNameMean = root_path + "to_get_mask_"+str(i)+"_8bit.bmp"
            np.clip(stacked_masked[i], 0, 255, out=stacked_masked[i])
            cv2.imwrite(fileNameMean, stacked_masked[i].astype(np.uint8))



def saveMesh(points):
    cloud = pv.PolyData(points)
    surf = cloud.delaunay_2d(alpha=0.010)
    surf.save("test2.ply",binary=False)


if __name__ == '__main__':

    #saveMeanFace()
    # globalVertices, globalColors, images = generatePC(folderName="20221102_20_um_4_Rec")
    # print (globalVertices.shape,globalColors.shape)

    #cube =np.zeros((1000,1000,1000))

    globalVertices, globalColors,globalSurface,images = generatePC(isSave=True)
    # saveMesh(globalVertices)