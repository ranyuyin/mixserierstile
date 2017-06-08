#coding: utf-8
import os,glob,gdal,numpy,sys
from scipy import stats
if __name__== "__main__":
    gdal.SetConfigOption('GDAL_FILENAME_IS_UTF8', 'NO')  # 解决中文路径
    rootdir = sys.argv[1]
    mixmode = sys.argv[2]
    mainyear=os.path.join(rootdir,sys.argv[3])
    if mixmode!='mode' and mixmode!='any':
        print ('模式不正确！')
    else:
        #rootdir=r'C:\Users\catfi\Desktop\wgz\Class Merge'
        mixdir=os.path.join(rootdir,'mixedimg-'+mixmode)
        subfoldlist = glob.glob(os.path.join(rootdir,'????'))
        subfoldlist = [os.path.join(rootdir, i) for i in subfoldlist if os.path.isdir(os.path.join(rootdir, i))]
        subfoldlist.index(mainyear)
        #继续子文件夹
        subfoldlist5d = glob.glob(os.path.join(mainyear, '*_*'))
        subfoldlist5d = [os.path.join(mainyear, i) for i in subfoldlist5d if os.path.isdir(os.path.join(mainyear, i))]
        imlist=[]
        for sub5d in subfoldlist5d:
            imlist+=(glob.glob(os.path.join(sub5d,'*.hdr')))
        gridlist5d=[os.path.split(os.path.split(fname)[0])[-1][0:7] for fname in imlist]
        gridlist=[os.path.split(fname)[-1][0:7] for fname in imlist]
        imfullnamelist=[]
        for i_sceneID in range(len(gridlist)):

            imfullnamelist.append([glob.glob(os.path.join(subfold,gridlist5d[i_sceneID]+'*',gridlist[i_sceneID]+'*.hdr'))[0][0:-4]
                                   for subfold in subfoldlist
                                  if len(glob.glob(os.path.join(subfold,gridlist5d[i_sceneID]+'*',gridlist[i_sceneID]+'*.hdr')))>0])
        if not os.path.exists(mixdir):
            os.mkdir(mixdir)
        for i_sceneID in range(len(imfullnamelist)):
            mixdir5d=os.path.join(mixdir,gridlist5d[i_sceneID])
            if not os.path.exists(mixdir5d):
                os.mkdir(mixdir5d)

            oimname=os.path.join(mixdir5d,os.path.split(imfullnamelist[i_sceneID][0])[-1][0:7]+'.tif')
            dataset = gdal.Open(imfullnamelist[i_sceneID][0])
            colortable=dataset.GetRasterBand(1).GetColorTable().Clone()
            sceneArray=numpy.zeros((dataset.RasterXSize,dataset.RasterYSize,len(imfullnamelist[i_sceneID])),numpy.uint8)
            for i in range(len(imfullnamelist[i_sceneID])):
                dataset = gdal.Open(imfullnamelist[i_sceneID][i])
                sceneArray[:,:,i]=dataset.ReadAsArray(0, 0, dataset.RasterXSize, dataset.RasterYSize)
            if mixmode=='mode':
                #统计众数
                sceneArray[sceneArray==0]=255
                mixArray,countArray=stats.mode(sceneArray,2)
                omixArray=mixArray[:,:,0]
                omixArray[omixArray == 255] = 0
            elif mixmode=='any':
                #统计any
                sceneArray[sceneArray == 0] = 255
                mixArray, countArray = stats.mode(sceneArray, 2)
                omixArray = mixArray[:, :, 0]
                omixArray[omixArray == 255] = 0
                omixArray[(sceneArray==1).any(2)]=1

            driver = gdal.GetDriverByName('GTiff')
            mixdataset=driver.Create(oimname, dataset.RasterXSize,dataset.RasterYSize,1,gdal.GDT_Byte)
            mixdataset.SetGeoTransform(dataset.GetGeoTransform())
            mixdataset.SetProjection(dataset.GetProjection())
            if mixmode == 'mode' or mixmode=='any':
                mixdataset.GetRasterBand(1).SetColorTable(colortable)
            mixdataset.GetRasterBand(1).WriteArray(omixArray)
            del mixdataset
