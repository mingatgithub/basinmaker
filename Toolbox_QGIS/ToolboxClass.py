
from qgis.core import *
import qgis
from qgis.analysis import QgsNativeAlgorithms
from simpledbf import Dbf5
import os
import sys
import numpy as np
import shutil
from shutil import copyfile
import tempfile
import copy
import pandas as pd
import sqlite3
from GetBasinoutlet import Getbasinoutlet,Nextcell
from Generatecatinfo import Generatecatinfo,Generatecatinfo_riv,calculateChannaln,Writecatinfotodbf,Streamorderanddrainagearea
from WriteRavenInputs import writelake,Writervhchanl









def checklakeboundary(lake1,lid,p_row,p_col):
    numnonlake = 0
    nonlakedir = np.full(10,-999)
    if lake1[p_row + 0,p_col + 1] != lid:
        numnonlake = numnonlake + 1
        nonlakedir[numnonlake] = 0
    if lake1[p_row + 1,p_col + 1] != lid:
        numnonlake = numnonlake + 1
        nonlakedir[numnonlake] = 1
    if lake1[p_row + 1,p_col + 0] != lid:
        numnonlake = numnonlake + 1
        nonlakedir[numnonlake] = 2
    if lake1[p_row + 1,p_col - 1] != lid:
        numnonlake = numnonlake + 1
        nonlakedir[numnonlake] = 3
    if lake1[p_row + 0,p_col - 1] != lid:
        numnonlake = numnonlake + 1
        nonlakedir[numnonlake] = 4
    if lake1[p_row - 1,p_col - 1] != lid:
        numnonlake = numnonlake + 1
        nonlakedir[numnonlake] = 5
    if lake1[p_row - 1,p_col + 0] != lid:
        numnonlake = numnonlake + 1
        nonlakedir[numnonlake] = 6
    if lake1[p_row - 1,p_col + 1] != lid:
        numnonlake = numnonlake + 1
        nonlakedir[numnonlake] = 7
    return numnonlake,nonlakedir
    


########## Return row and column number of a specific catchment's outlet  
# hylake       : a dataframe from HydroLAKE database containing all infromation about lakes 
# noncnlake    : a two dimension array of lakes that are not connected by river network 
# NonConLThres : the flow accumulation 2D array  
# dir    : the flow direction 2D array
# nrows, ncols  : maximum number of rows and columns in the basin 2D array   
# return crow,ccol  : row and column id of the catchment outlet.

def Dirpoints2(N_dir,p_row,p_col,lake1,lid,goodpoint,k,ncols,nrows):
    ndir = copy.copy(N_dir)
    ip = copy.copy(k) + 1
#dir 1
    if lake1[p_row + 0,p_col + 1] == lid:  #### it is a lake cell
        if p_row + 1 >= nrows-3 or p_col + 1 >= ncols - 3 or p_row - 1 <= 2 or p_col - 1 <= 2:   ### lake not at the boundary of domain
            numnonlake = 99
        else:
            numnonlake,nonlakedir = checklakeboundary(lake1,lid,p_row + 0,p_col + 1)
        if numnonlake != 0: # it is a boundary lake cell
            tt = goodpoint[goodpoint[:,0] == p_row + 0,]
            if len(tt[tt[:,1] == p_col + 1,]) < 1:#### the point not exist in good points which store all boundary points
                ndir[p_row + 0,p_col + 1] = 16   ### change the flow direction of new point to old points
                goodpoint[ip,0] = p_row + 0
                goodpoint[ip,1] = p_col + 1
                ip = ip + 1
#dir 2
    if lake1[p_row + 1,p_col + 1] == lid:
        if p_row + 1 >= nrows-3 or p_col + 1 >= ncols - 3 or p_row - 1 <= 2 or p_col - 1 <= 2:   ### lake not at the boundary of domain
            numnonlake = 99
        else:
            numnonlake,nonlakedir = checklakeboundary(lake1,lid,p_row + 1,p_col + 1)
        if numnonlake != 0:
            tt = goodpoint[goodpoint[:,0] == p_row + 1,]
            if len(tt[tt[:,1] == p_col + 1,]) < 1:
                ndir[p_row + 1,p_col + 1] = 32
                goodpoint[ip,0] = p_row + 1
                goodpoint[ip,1] = p_col + 1
                ip = ip + 1
#dir 3
    if lake1[p_row + 1,p_col + 0] == lid:
        if p_row + 1 >= nrows-3 or p_col + 1 >= ncols - 3 or p_row - 1 <= 2 or p_col - 1 <= 2:   ### lake not at the boundary of domain
            numnonlake = 99
        else:
            numnonlake,nonlakedir = checklakeboundary(lake1,lid,p_row + 1,p_col + 0)
        if numnonlake != 0:
            tt = goodpoint[goodpoint[:,0] == p_row + 1,]
            if len(tt[tt[:,1] == p_col + 0,]) < 1:
                ndir[p_row + 1,p_col + 0] = 64
                goodpoint[ip,0] = p_row + 1
                goodpoint[ip,1] = p_col + 0
                ip = ip + 1
#dir 4
    if lake1[p_row + 1,p_col - 1] == lid:
        if p_row + 1 >= nrows-3 or p_col + 1 >= ncols - 3 or p_row - 1 <= 2 or p_col - 1 <= 2:   ### lake not at the boundary of domain
            numnonlake = 99
        else:
            numnonlake,nonlakedir = checklakeboundary(lake1,lid,p_row + 1,p_col - 1)
        if numnonlake != 0:
            tt = goodpoint[goodpoint[:,0] == p_row + 1,]
            if len(tt[tt[:,1] == p_col - 1,]) < 1:
                ndir[p_row + 1,p_col - 1] = 128
                goodpoint[ip,0] = p_row + 1
                goodpoint[ip,1] = p_col - 1
                ip = ip + 1
#dir 5
    if lake1[p_row + 0,p_col - 1] == lid:
        if p_row + 1 >= nrows-3 or p_col + 1 >= ncols - 3 or p_row - 1 <= 2 or p_col - 1 <= 2:   ### lake not at the boundary of domain
            numnonlake = 99
        else:
            numnonlake,nonlakedir = checklakeboundary(lake1,lid,p_row + 0,p_col - 1)
        if numnonlake != 0:
            tt = goodpoint[goodpoint[:,0] == p_row + 0,]
            if len(tt[tt[:,1] == p_col - 1,]) < 1:
                ndir[p_row + 0,p_col - 1] = 1
                goodpoint[ip,0] = p_row + 0
                goodpoint[ip,1] = p_col - 1
                ip = ip + 1
#dir 6
    if lake1[p_row - 1,p_col - 1] == lid:
        if p_row + 1 >= nrows-3 or p_col + 1 >= ncols - 3 or p_row - 1 <= 2 or p_col - 1 <= 2:  ### lake not at the boundary of domain
            numnonlake = 99
        else:
            numnonlake,nonlakedir = checklakeboundary(lake1,lid,p_row - 1,p_col - 1)
        if numnonlake != 0:
            tt = goodpoint[goodpoint[:,0] == p_row - 1,]
            if len(tt[tt[:,1] == p_col - 1,]) < 1:
                ndir[p_row - 1,p_col - 1] = 2
                goodpoint[ip,0] = p_row - 1
                goodpoint[ip,1] = p_col - 1
                ip = ip + 1
#dir 7
    if lake1[p_row - 1,p_col + 0] == lid:
        if p_row + 1 >= nrows-3 or p_col + 1 >= ncols - 3 or p_row - 1 <= 2 or p_col - 1 <= 2: ### lake not at the boundary of domain
            numnonlake = 99
        else:
            numnonlake,nonlakedir = checklakeboundary(lake1,lid,p_row - 1,p_col + 0)
        if numnonlake != 0:
            tt = goodpoint[goodpoint[:,0] == p_row - 1,]
            if len(tt[tt[:,1] == p_col + 0,]) < 1:
                ndir[p_row - 1,p_col + 0] = 4
                goodpoint[ip,0] = p_row - 1
                goodpoint[ip,1] = p_col + 0
                ip = ip + 1
#dir 8
    if lake1[p_row - 1,p_col + 1] == lid:
        if p_row + 1 >= nrows-3 or p_col + 1 >= ncols - 3 or p_row - 1 <= 2 or p_col - 1 <= 2:  ### lake not at the boundary of domain
            numnonlake = 99
        else:
            numnonlake,nonlakedir = checklakeboundary(lake1,lid,p_row - 1,p_col + 1)
        if numnonlake != 0:
            tt = goodpoint[goodpoint[:,0] == p_row - 1,]
            if len(tt[tt[:,1] == p_col + 1,]) < 1:
                ndir[p_row - 1,p_col + 1] = 8
                goodpoint[ip,0] = p_row - 1
                goodpoint[ip,1] = p_col + 1
                ip = ip + 1
#    arcpy.AddMessage(goodpoint[goodpoint[:,0]>0,])
    return ndir,goodpoint,ip

def ChangeDIR(dir,lake1,acc,ncols,nrows,outlakeids,nlakegrids,cat3):
    ndir = copy.copy(dir)
    for i in range(0,len(outlakeids)):
        lid = outlakeids[i,0]
        goodpoint = np.full((20000,2),-99999)
        lrowcol = np.argwhere(lake1==lid).astype(int)
        
        if len(lrowcol) > nlakegrids and outlakeids[i,1] > 0.9:   ### smaller than nlakegrids or smaller than 0.9
            continue
        if outlakeids[i,1] > 0.97: ### smaller than 0.97
            continue
            
        prow,pcol = Getbasinoutlet(lid,lake1,acc,dir,nrows,ncols)

        goodpoint[0,0] = prow
        goodpoint[0,1] = pcol
        if prow >= nrows - 1 or pcol == ncols  - 1:
            continue
        ip = 0
        k = 0
        ipo = -1
        while ip > ipo:
            for i in range(0,len(goodpoint[goodpoint[:,0]>0,])):
                if i > ipo:
                    trow = goodpoint[i,0]
                    tcol = goodpoint[i,1]
                    if trow >= nrows - 1 or tcol == ncols  - 1:
                        continue
                    ndir,goodpoint,k1= Dirpoints2(ndir,trow,tcol,lake1,lid,goodpoint,k,ncols,nrows)
                    k = k1 - 1
            ipo = ip
            ip = len(goodpoint[goodpoint[:,0]>0,]) - 1
            k = ip
    return ndir

  
def Checklake(prow,pcol,nrows,ncols,lid,lake):
    noout=0
    ### double check if the head stream cell is nearby the lake, if near by the lake the stream was ignored
    if prow != 0 and prow != nrows -1 and pcol != 0 and pcol != ncols-1:
        if lake[prow-1,pcol+1] == lid:
            noout=1
        if lake[prow-1,pcol-1] == lid:
            noout=1
        if lake[prow-1,pcol] == lid:
            noout=1
        if lake[prow,pcol+1] == lid:
            noout=1
        if lake[prow,pcol-1] == lid:
            noout=1
        if lake[prow+1,pcol-1] == lid:
            noout=1
        if lake[prow+1,pcol+1] == lid:
            noout=1
        if lake[prow+1,pcol] == lid:
            noout=1
    return noout
############################################################################33

####################################################################3
def Checkcat(prow,pcol,nrows,ncols,lid,lake):
    noout=0
    ### double check if the head stream cell is nearby the lake, if near by the lake the stream was ignored
    if prow != 0 and prow != nrows -1 and pcol != 0 and pcol != ncols-1:
        if not lake[prow-1,pcol+1] == lid:
            noout=1 + noout
        if not lake[prow-1,pcol-1] == lid:
            noout=1 + noout
        if not lake[prow-1,pcol] == lid:
            noout=1 + noout
        if not lake[prow,pcol+1] == lid:
            noout=1 + noout
        if not lake[prow,pcol-1] == lid:
            noout=1 + noout
        if not lake[prow+1,pcol-1] == lid:
            noout=1 + noout
        if not lake[prow+1,pcol+1] == lid:
            noout=1 + noout
        if not lake[prow+1,pcol] == lid:
            noout=1 + noout
    return noout

###################################################################3

def selectlake(hylake,noncnlake,NonConLThres,hylakeinfo):
#    arcpy.AddMessage("123asdfasdfasdfasd")
    sl_lake = copy.copy(hylake)
    arlakeid = np.unique(noncnlake)
    arlakeid = arlakeid[arlakeid>=0]
    for i in range(0,len(arlakeid)):
        sl_lid = arlakeid[i] ### get lake id
        sl_rowcol = np.argwhere(noncnlake==sl_lid).astype(int) ### get the row and col of lake
        sl_nrow = sl_rowcol.shape[0]
        slakeinfo = hylakeinfo.loc[hylakeinfo['Hylak_id'] == sl_lid]
        if len(slakeinfo) <=0:
            continue
        if slakeinfo.iloc[0]['Lake_area'] >= NonConLThres:
            sl_lake[sl_rowcol[:,0],sl_rowcol[:,1]] = sl_lid
    return sl_lake

def selectlake2(hylake,Lakehres,hylakeinfo):
    sl_lake = copy.copy(hylake)
    arlakeid = np.unique(sl_lake)
    arlakeid = arlakeid[arlakeid>=0]
    for i in range(0,len(arlakeid)):
        sl_lid = arlakeid[i] ### get lake id
        sl_rowcol = np.argwhere(sl_lake==sl_lid).astype(int) ### get the row and col of lake
        sl_nrow = sl_rowcol.shape[0]
        slakeinfo = hylakeinfo.loc[hylakeinfo['Hylak_id'] == sl_lid]
        if len(slakeinfo)<=0:
#            print("Lake excluded     asdfasd " + str(sl_lid))
            sl_lake[sl_rowcol[:,0],sl_rowcol[:,1]] = -9999
            continue
        if slakeinfo.iloc[0]['Lake_area'] < Lakehres:
#            print("Lake excluded     due to area " + str(sl_lid))
            sl_lake[sl_rowcol[:,0],sl_rowcol[:,1]] = -9999
    return sl_lake

##################################################################3

def check_lakecatchment(cat3,lake,fac,fdir,bsid,nrows,ncols):
    cat = copy.copy(cat3)
    arlakeid = np.unique(lake)
    arlakeid = arlakeid[arlakeid>=0]
    outlakeids = np.full((1000000,2),-99999.999)
    for i in range(0,len(arlakeid)):
        lakeid = arlakeid[i]
        lrowcol = np.argwhere(lake==lakeid).astype(int)
        lakacc = np.full((len(lrowcol),3),-9999)
        lakacc[:,0] = lrowcol[:,0]
        lakacc[:,1] = lrowcol[:,1]
        lakacc[:,2] = fac[lrowcol[:,0],lrowcol[:,1]]
        lakacc = lakacc[lakacc[:,2].argsort()]
        lorow = lakacc[len(lakacc)-1,0]
        locol = lakacc[len(lakacc)-1,1]  ###### lake outlet row and col
        arclakeid = cat[lorow,locol]  ####### lake catchment id 
        lakecatrowcol = np.argwhere(cat==arclakeid).astype(int)    #### lake catchment cells 
        Lakeincat1 = lake[lakecatrowcol[:,0],lakecatrowcol[:,1]]
        nlake = np.argwhere(Lakeincat1==lakeid).astype(int)
        outlakeids[i,0] = lakeid
        outlakeids[i,1] = float(len(nlake)/len(lrowcol)) 
#        print(lakeid,arclakeid,len(nlake),len(lrowcol),float(len(nlake)/len(lrowcol))) 
    outlakeids= outlakeids[outlakeids[:,0] > 0]
    return outlakeids
######################################################################3
def Addobspoints(obs,pourpoints,boid,cat):
    obsids = np.unique(obs)
    obsids = obsids[obsids>=0]
    for i in range(0,len(obsids)):
        rowcol = np.argwhere(obs==obsids[i]).astype(int)
        if cat[rowcol[0,0],rowcol[0,1]] > 0:
            if pourpoints[rowcol[0,0],rowcol[0,1]] < 0:
                pourpoints[rowcol[0,0],rowcol[0,1]] = boid + obsids[i]
    return pourpoints

####################################################################
def CE_mcat4lake(cat1,lake,fac,fdir,bsid,nrows,ncols,Pourpoints):
    #####adjust for some lakes was divided into two catchment beacuse of flow direction and in stream. double check each lake
    ##### and decide if need to merge these catchment into one lake catchment.
    cat = copy.copy(cat1)
    arlakeid = np.unique(lake)
    arlakeid = arlakeid[arlakeid>=0]
    outlakeids = np.full((1000000,2),-99999.999)
    outi = 0
    for i in range(0,len(arlakeid)):
        lakeid = arlakeid[i]
        lrowcol = np.argwhere(lake==lakeid).astype(int)
        lakacc = np.full((len(lrowcol),3),-9999)
        lakacc[:,0] = lrowcol[:,0]
        lakacc[:,1] = lrowcol[:,1]
        lakacc[:,2] = fac[lrowcol[:,0],lrowcol[:,1]]
        lakacc = lakacc[lakacc[:,2].argsort()]
        lorow = lakacc[len(lakacc)-1,0]
        locol = lakacc[len(lakacc)-1,1]  ###### lake outlet row and col
        arclakeid = cat[lorow,locol]  ####### lake catchment id 
        lakecatrowcol = np.argwhere(cat==arclakeid).astype(int)    #### lake catchment cells 
        Lakeincat1 = lake[lakecatrowcol[:,0],lakecatrowcol[:,1]]
        nlake = np.argwhere(Lakeincat1==lakeid).astype(int) 

        lakenrow,lakencol = Nextcell(fdir,lorow,locol)
        if lakenrow < 0 or lakencol < 0:
            lakedowcatid = -999
        else:
            if lakenrow >= nrows or lakencol >= ncols:
                continue
            lakedowcatid = cat[lakenrow,lakencol]
        # if not arclakeid < bsid and arclakeid > blid:
        #     continue
        arcatid,catcounts = np.unique(cat[lrowcol[:,0],lrowcol[:,1]],return_counts=True) ###### all catchment id containing this lake
        tarid = 0
        ### if there are more than 1 catchment in cat1, determine if they need to be combined
        ### check if these catchment flow into the lake if it is true, change catchment id into lake catchment id
        if len(arcatid)>1:  #
#            if float(len(lakecatrowcol))/float(len(lrowcol)) < 0.9: #and len(lrowcol) < 10000: #: float(max(catcounts))/float(len(lrowcol)) < 0.8 and 
            outlakeids[outi,0] = lakeid
            outlakeids[outi,1] = float(len(nlake))/float(len(lrowcol))
#            print(outlakeids[outi,0],outlakeids[outi,1])
            outi = outi + 1
            for j in range(0,len(arcatid)):
                crowcol = np.argwhere(cat==arcatid[j]).astype(int)
                catacc = np.full((len(crowcol),3),-9999)
                catacc[:,0] = crowcol[:,0]
                catacc[:,1] = crowcol[:,1]
                catacc[:,2] = fac[crowcol[:,0],crowcol[:,1]]
                catacc = catacc[catacc[:,2].argsort()]
                catorow = catacc[len(catacc)-1,0]
                catocol = catacc[len(catacc)-1,1] ### catchment outlet
                Lakeincat = lake[crowcol[:,0],crowcol[:,1]]
                nlake = np.argwhere(Lakeincat==lakeid).astype(int)
                nrow,ncol = Nextcell(fdir,catorow,catocol) #####Get the next row and col of downstream catchment
                if nrow < 0 or ncol < 0:
                    continue
                if nrow < nrows and ncol < ncols:
               ### if downstream catchment is target lake,and this catchment is an lakeinflow catchment combine them
                    if cat[nrow,ncol] == arclakeid and float(len(nlake))/float(len(crowcol)) > 0.1 and cat[catorow,catocol] > bsid:
                        cat[crowcol[:,0],crowcol[:,1]] = arclakeid
                    if float(len(nlake))/float(len(lrowcol)) > 0.1 and cat[catorow,catocol] > bsid and cat[catorow,catocol] != lakedowcatid:
#                        arcpy.AddMessage("2")
                        cat[crowcol[:,0],crowcol[:,1]] = arclakeid
#                        if cat[catorow,catocol] != arclakeid and cat[nrow,ncol] != arclakeid:
#                            print lakeid
                    if cat[nrow,ncol] > bsid and arcatid[j] > bsid:  #### lake input cat route to another lake input catch
                        cat[crowcol[:,0],crowcol[:,1]] = cat[nrow,ncol]
        pp = Pourpoints[lrowcol[:,0],lrowcol[:,1]]
        pp = np.unique(pp)
        pp = pp[pp > 0]
        if len(pp) == 1:
            cat[lrowcol[:,0],lrowcol[:,1]] = arclakeid
    outlakeids= outlakeids[outlakeids[:,0] > 0]
    return cat,outlakeids
###################################################33
def CE_mcat4lake2(cat1,lake,fac,fdir,bsid,nrows,ncols,Pourpoints):
    cat = copy.copy(cat1)
    arlakeid = np.unique(lake)
    arlakeid = arlakeid[arlakeid>=0]
    for i in range(0,len(arlakeid)):
        lakeid = arlakeid[i]
        lrowcol = np.argwhere(lake==lakeid).astype(int)
        lakacc = np.full((len(lrowcol),3),-9999)
        lakacc[:,0] = lrowcol[:,0]
        lakacc[:,1] = lrowcol[:,1]
        lakacc[:,2] = fac[lrowcol[:,0],lrowcol[:,1]]
        lakacc = lakacc[lakacc[:,2].argsort()]
        lorow = lakacc[len(lakacc)-1,0]
        locol = lakacc[len(lakacc)-1,1]  ###### lake outlet row and col
        arclakeid = cat1[lorow,locol]
        pp = Pourpoints[lorow,locol]
        pp = np.unique(pp)
        pp = pp[pp > 0]
        if len(pp) == 1:
            if arclakeid < 0:
                cat[lrowcol[:,0],lrowcol[:,1]] = pp
            else:
                cat[lrowcol[:,0],lrowcol[:,1]] = arclakeid
#### For some reason pour point was missing in non-contribute catchment 
    Pours = np.unique(Pourpoints)
    Pours = Pours[Pours>0]
    for i in range(0,len(Pours)):
        pourid = Pours[i]
        rowcol = Pourpoints == pourid
        if cat[rowcol] < 0:
            nout = Checkcat(rowcol[0,0],rowcol[0,1],nrows,ncols,pourid,cat)
            if len(cat[cat == pourid]) > 0 and nout < 8:
                cat[rowcol] = pourid
    rowcol1 = fac > 0
    rowcol2 = cat < 0
    noncontribuite = np.logical_and(rowcol1, rowcol2)
    cat[noncontribuite] = 2*max(np.unique(cat)) + 1
    return cat
######################################################
def CE_Lakeerror(fac,fdir,lake,cat2,bsid,blid,boid,nrows,ncols,cat):
    Watseds = copy.copy(cat2)
    Poups = np.unique(Watseds)
    Poups = Poups[Poups>=0]
    ##### Part 2, remove some small catchment which is not lake catchment
    out = np.full((len(Poups),4),-9999)
    for i in range(0,len(Poups)):
        catid = Poups[i]
        if catid > boid:
            continue #### do nothing for observation catchments
        rowcol = np.argwhere(Watseds==catid).astype(int)
        catacc = np.full((len(rowcol),3),-9999)
        catacc[:,0] = rowcol[:,0]
        catacc[:,1] = rowcol[:,1]
        catacc[:,2] = fac[rowcol[:,0],rowcol[:,1]]
        catacc = catacc[catacc[:,2].argsort()].astype(int)
        rowcol[0,0] = catacc[len(catacc)-1,0]
        rowcol[0,1] = catacc[len(catacc)-1,1]
        nrow,ncol = Nextcell(fdir,rowcol[0,0],rowcol[0,1])### get the downstream catchment id
        if nrow < 0 or ncol < 0:
            continue
        if nrow < nrows and ncol < ncols:
            if len(rowcol) < 10 and Watseds[rowcol[0,0],rowcol[0,1]] > bsid:
                Watseds[catacc[:,0],catacc[:,1]] = Watseds[nrow,ncol]
            if len(rowcol) < 10 and Watseds[rowcol[0,0],rowcol[0,1]] < blid:
                Watseds[catacc[:,0],catacc[:,1]] = Watseds[nrow,ncol]
    return Watseds

#########################################33
def GenerateFinalPourpoints(fac,fdir,lake,cat3,bsid,blid,boid,nrows,ncols,cat,obs):
    Poups = copy.copy(cat3)
    Poups[:,:]=-9999
    GWat = copy.copy(cat3)
    GWatids = np.unique(cat3)
    GWatids = GWatids[GWatids>=0]
    ncatid = 1
    for i in range(0,len(GWatids)):
        trow,tcol = Getbasinoutlet(GWatids[i],GWat,fac,fdir,nrows,ncols)
#        arcpy.AddMessage("result     " +str(trow) +"    " +str(tcol))
        Poups[trow,tcol] = ncatid
        ncatid = ncatid + 1
    OWat = copy.copy(cat)
    OWatids = np.unique(cat)
    OWatids = OWatids[OWatids>=0]
    for i in range(0,len(OWatids)):
        trow,tcol = Getbasinoutlet(OWatids[i],OWat,fac,fdir,nrows,ncols)
        if not GWat[trow,tcol] >= blid:
            if Poups[trow,tcol] < 0:
                Poups[trow,tcol] = ncatid
                ncatid = ncatid + 1
    obsids = np.unique(obs)
    obsids = obsids[obsids>0]
    for i in range(0,len(obsids)):
        rowcol = np.argwhere(obs==obsids[i]).astype(int)
        if Poups[rowcol[0,0],rowcol[0,1]] < 0 and lake[rowcol[0,0],rowcol[0,1]] < 0:
            Poups[rowcol[0,0],rowcol[0,1]] = ncatid
            ncatid = ncatid + 1
    return Poups
#######
####
# ####################################################33


def GenerPourpoint(cat,lake,Str,nrows,ncols,blid,bsid,bcid,fac,hydir):
    GP_cat = copy.copy(cat)
    sblid = copy.copy(blid)
    ############### Part 1 Get all pourpoints of hydroshed catchment
    arcatid = np.unique(cat)#### cat all catchment idd
    arcatid = arcatid[arcatid>=0]
    catoutloc = np.full((len(arcatid),3),-9999)
    for i in range(0,len(arcatid)):
        catid = arcatid[i]
        catrowcol = np.argwhere(cat==catid).astype(int)
        trow,tcol = Getbasinoutlet(catid,cat,fac,hydir,nrows,ncols)
        GP_cat[catrowcol[:,0],catrowcol[:,1]]=-9999   ### set the catment cells into null
        GP_cat[trow,tcol]=bcid #### change the outlet of catchment into wid
        bcid = bcid + 1
        catoutloc[i,0] = catid  ## catchment id
        catoutloc[i,1] = trow  #### catchment pourpont row
        catoutloc[i,2] = tcol  #### catchment pourpont col
#    writeraster(outFolder+subid+"_Pourpoints_1.asc",GP_cat)

    ##################Part 2 Get pourpoints of Lake inflow streams
    arlakeid = np.unique(lake)
    arlakeid = arlakeid[arlakeid>=0]
    for i in range(0,len(arlakeid)): #### loop for each lake
        lid = arlakeid[i]       ##### obtain lake id 
        rowcol = np.argwhere(lake==lid.astype(int))  ### got row anc col of lake grids 
        nrow = rowcol.shape[0]  ### number of grids of the lake 
        Stridinlake = np.full(nrow,-9999)  #### 
        Stridinlake[:] = Str[rowcol[:,0],rowcol[:,1]]  ### get all stream with in the lake domain 
        Strid_L  = np.unique(Stridinlake[np.argwhere(Stridinlake > 0).astype(int)]) ### Get unique stream id of sach stream 
        ##### find the intercept point of stream and lake
        for j in range(0,len(Strid_L)):  #### loop for each stream intercept with lake
            strid = Strid_L[j]
            strrowcol = np.argwhere(Str == strid).astype(int)
            nstrrow = strrowcol.shape[0]
            Strchek = np.full((nstrrow,4),-9999)##### 0 row, 1 col, 2 fac,
            Strchek[:,0] = strrowcol[:,0]
            Strchek[:,1] = strrowcol[:,1]
            Strchek[:,2] = fac[strrowcol[:,0],strrowcol[:,1]]
            Strchek[:,3] = lake[strrowcol[:,0],strrowcol[:,1]]
            Strchek = Strchek[Strchek[:,2].argsort()].astype(int)
            
            ###3 find the first intersection point between river and lake 
            Grids_Lake_river = np.where(Strchek[:,3] == lid)
            irowst = np.nanmin(Grids_Lake_river)
            Intersection_Grid_row = Strchek[irowst,0]
            Intersection_Grid_col = Strchek[irowst,1]

            noout = 0
            ### double check if the head stream cell is nearby the lake
            if Strchek[0,0] != 0 and Strchek[0,0] != nrows -1 and Strchek[0,1] != 0 and Strchek[0,1] != ncols-1:
                noout = Checklake(Strchek[0,0],Strchek[0,1],nrows,ncols,lid,lake)            
            ####
            
            if irowst != 0: ## is the stream is not start within the lake 
                if lake[Strchek[irowst-1,0],Strchek[irowst-1,1]] == -9999:  ### double check 
                    ##### this means the stream connect two lakes, so must assign an pourpoints
                    if len(np.unique(lake[Strchek[0:irowst,0],Strchek[0:irowst,1]])) >= 3:
                        GP_cat[Strchek[irowst-1,0],Strchek[irowst-1,1]] = bsid
                        bsid = bsid + 1

                    ##### the head stream celll is not nearby the lake
                    if noout == 0:
                        GP_cat[Strchek[irowst-1,0],Strchek[irowst-1,1]] = bsid
                        bsid = bsid + 1
            #### it is possible that two steam combine together near the lake, double check if the stream conncet to
            # anotehr stream and this steam is not witin the lake
            if irowst == 0 or noout == 1:
                nostr = Str[Strchek[0,0],Strchek[0,1]]
                a = 0
                orowcol = np.full((8,3),-9999)
                if Strchek[0,0] != 0 and Strchek[0,0] != nrows -1 and Strchek[0,1] != 0 and Strchek[0,1] != ncols-1:
                    if Str[Strchek[0,0]-1,Strchek[0,1]+1] != -9999 and lake[Strchek[0,0]-1,Strchek[0,1]+1] == -9999:
                        orowcol[a,0] = Strchek[0,0]-1
                        orowcol[a,1] = Strchek[0,1]+1
                        orowcol[a,2] = Str[Strchek[0,0]-1,Strchek[0,1]+1]
                        a = a+1
                    if Str[Strchek[0,0]-1,Strchek[0,1]-1] != -9999 and lake[Strchek[0,0]-1,Strchek[0,1]-1] == -9999:
                        orowcol[a,0] = Strchek[0,0]-1
                        orowcol[a,1] = Strchek[0,1]-1
                        orowcol[a,2] = Str[Strchek[0,0]-1,Strchek[0,1]-1]
                        a = a+1
                    if Str[Strchek[0,0]-1,Strchek[0,1]] != -9999 and lake[Strchek[0,0]-1,Strchek[0,1]] == -9999:
                        orowcol[a,0] = Strchek[0,0]-1
                        orowcol[a,1] = Strchek[0,1]-0
                        orowcol[a,2] = Str[Strchek[0,0]-1,Strchek[0,1]-0]
                        a = a+1
                    if Str[Strchek[0,0],Strchek[0,1]+1] != -9999 and lake[Strchek[0,0],Strchek[0,1]+1] == -9999:
                        orowcol[a,0] = Strchek[0,0]-0
                        orowcol[a,1] = Strchek[0,1]+1
                        orowcol[a,2] = Str[Strchek[0,0]-0,Strchek[0,1]+1]
                        a = a+1
                    if Str[Strchek[0,0],Strchek[0,1]-1] != -9999 and lake[Strchek[0,0],Strchek[0,1]-1] == -9999:
                        orowcol[a,0] = Strchek[0,0]-0
                        orowcol[a,1] = Strchek[0,1]-1
                        orowcol[a,2] = Str[Strchek[0,0]-0,Strchek[0,1]-1]
                        a = a+1
                    if Str[Strchek[0,0]+1,Strchek[0,1]-1] != -9999 and lake[Strchek[0,0]+1,Strchek[0,1]-1] == -9999:
                        orowcol[a,0] = Strchek[0,0]+1
                        orowcol[a,1] = Strchek[0,1]-1
                        orowcol[a,2] = Str[Strchek[0,0]+1,Strchek[0,1]-1]
                        a = a+1
                    if Str[Strchek[0,0]+1,Strchek[0,1]+1] != -9999 and lake[Strchek[0,0]+1,Strchek[0,1]+1] == -9999:
                        orowcol[a,0] = Strchek[0,0]+1
                        orowcol[a,1] = Strchek[0,1]+1
                        orowcol[a,2] = Str[Strchek[0,0]+1,Strchek[0,1]+1]
                        a = a+1
                    if Str[Strchek[0,0]+1,Strchek[0,1]] != -9999 and lake[Strchek[0,0]+1,Strchek[0,1]] == -9999:
                        orowcol[a,0] = Strchek[0,0]+1
                        orowcol[a,1] = Strchek[0,1]-0
                        orowcol[a,2] = Str[Strchek[0,0]+1,Strchek[0,1]-0]
                        a = a+1
                if a > 0:
                    for ka in range(0,a):
                        nostr =orowcol[ka,2]  ## up stream stram id 
                        srowcol = np.argwhere(Str==nostr).astype(int)
                        snrow = srowcol.shape[0]
                        iStrchek = np.full((snrow,4),-9999)##### 0 row, 1 col, 2 fac,
                        iStrchek[:,0] = srowcol[:,0]
                        iStrchek[:,1] = srowcol[:,1]
                        iStrchek[:,2] = fac[srowcol[:,0],srowcol[:,1]]
                        iStrchek = iStrchek[iStrchek[:,2].argsort()]
                        noout = Checklake(iStrchek[0,0],iStrchek[0,1],nrows,ncols,lid,lake)
                        Lakinstr = np.full(snrow,-9999)
                        Lakinstr[:] = lake[srowcol[:,0],srowcol[:,1]]
                        d = np.argwhere(Lakinstr==lid).astype(int)  #### the connected stream should not within the lake
                        if len(d) < 1 and noout == 0:
                            GP_cat[orowcol[ka,0],orowcol[ka,1]] = bsid
                            bsid = bsid + 1
################################################################################
################## Part 3Get Lake pourpoint id and remove cat pourpoint that contribute to lake
#    writeraster(outFolder+"Pourpoints_2.asc",GP_cat)
    for i in range(0,len(arlakeid)):
        lakeid = arlakeid[i]
        lrowcol = np.argwhere(lake==lakeid).astype(int)
        arcatid = np.unique(cat[lrowcol[:,0],lrowcol[:,1]]) ## Get all catchment that intercept with lake
        lakeacc = np.full((len(lrowcol),3),-9999)
        lakeacc[:,0] = lrowcol[:,0]
        lakeacc[:,1] = lrowcol[:,1]
        lakeacc[:,2] = fac[lrowcol[:,0],lrowcol[:,1]]
        lakeacc = lakeacc[lakeacc[:,2].argsort()]
        maxcatid = cat[lakeacc[len(lakeacc)-1,0],lakeacc[len(lakeacc)-1,1]] ### Get the catchment id that will keeped
        
        ### remove the all pourpoints close to lake pourpoints
        if lakeacc[len(lakeacc)-1,0] != 0 and lakeacc[len(lakeacc)-1,0] != nrows -1 and lakeacc[len(lakeacc)-1,1] != 0 and lakeacc[len(lakeacc)-1,1] != ncols-1:
            GP_cat[lakeacc[len(lakeacc)-1,0]-1,lakeacc[len(lakeacc)-1,1]-1]=-9999 
            GP_cat[lakeacc[len(lakeacc)-1,0]+1,lakeacc[len(lakeacc)-1,1]-1]=-9999
            GP_cat[lakeacc[len(lakeacc)-1,0],lakeacc[len(lakeacc)-1,1]-1]=-9999
            GP_cat[lakeacc[len(lakeacc)-1,0]+1,lakeacc[len(lakeacc)-1,1]]=-9999
            GP_cat[lakeacc[len(lakeacc)-1,0]+1,lakeacc[len(lakeacc)-1,1]+1]=-9999
            GP_cat[lakeacc[len(lakeacc)-1,0],lakeacc[len(lakeacc)-1,1]+1]=-9999
            GP_cat[lakeacc[len(lakeacc)-1,0]-1,lakeacc[len(lakeacc)-1,1]]=-9999
            
        ### remove pourpoints that not equal to maxcatid 
        for j in range(0,len(arcatid)):
            if arcatid[j] != maxcatid:
                crowcol = np.argwhere(cat==arcatid[j]).astype(int)
                checkcat = np.full((len(crowcol),4),-9999)
                checkcat[:,0] = crowcol[:,0]
                checkcat[:,1] = crowcol[:,1]
                checkcat[:,2] = GP_cat[crowcol[:,0],crowcol[:,1]]
                checkcat[:,3] = fac[crowcol[:,0],crowcol[:,1]]
                checkcat = checkcat[checkcat[:,3].argsort()]
                dele = checkcat[checkcat[:,2]<blid].astype(int)   #### do not delete the lake and strem ids
                GP_cat[dele[:,0],dele[:,1]]=-9999
                
                ### add keep catchment in case the catchment outlet is at the boundary of the domain
                nrow,ncol = Nextcell(hydir,checkcat[len(checkcat)-1,0],checkcat[len(checkcat)-1,1])
                if nrow > 0 or ncol >0:
                    if nrow >= nrows or ncols >= ncols:
                        continue
                    if cat[nrow,ncol] < 0:
                        GP_cat[checkcat[len(checkcat)-1,0],checkcat[len(checkcat)-1,1]] = bcid
                        bcid = bcid + 1
                        
        #### add lake outlet 
        GP_cat[lakeacc[len(lakeacc)-1,0],lakeacc[len(lakeacc)-1,1]]= sblid
        sblid = sblid + 1
    return GP_cat
###################################################################3



##################################################################3


###################################################################3

##### out has two column the first column has sub id , the second has down sub id 
def Defcat(out,outletid):
    otsheds = np.full((1,1),outletid)
    Shedid = np.full((10000000,1),-99999999999999999)
    psid = 0
    rout = copy.copy(out)
    while len(otsheds) > 0:
        noutshd = np.full((10000000,1),-999999999999999)
        poshdid = 0
        for i in range(0,len(otsheds)):
            Shedid[psid] = otsheds[i]
            psid = psid + 1
            irow = np.argwhere(rout[:,1]==otsheds[i]).astype(int)
            for j in range(0,len(irow)):
                noutshd[poshdid] = rout[irow[j],0]
                poshdid = poshdid + 1
        noutshd = np.unique(noutshd)
        otsheds = noutshd[noutshd>=0]
    Shedid = np.unique(Shedid)
    Shedid = Shedid[Shedid>=0]
    return Shedid
###########
    
############    
class LRRT:
    def __init__(self, dem_in = '#',dir_in = '#',hyshdply = '#',WidDep = '#',Lakefile = '#'
                                     ,Landuse = '#',Landuseinfo = '#',obspoint = '#',OutHyID = -1 ,OutHyID2 = -1, 
                                     OutputFolder = '#',ProjectNM = '#'):
        self.Path_dem_in = dem_in
        self.Path_dir_in = dir_in
        self.Path_hyshdply_in = hyshdply
        self.Path_WiDep_in = WidDep
        self.Path_Lakefile_in = Lakefile
        self.Path_Landuse_in = Landuse
        self.Path_Landuseinfo_in = Landuseinfo
        self.Path_obspoint_in = obspoint
        self.Path_OutputFolder = OutputFolder
        

        
        self.OutHyID = OutHyID
        self.OutHyID2 = OutHyID2
        
        self.ProjectNM = ProjectNM
        
        self.OutputFolder = os.path.join(self.Path_OutputFolder,self.ProjectNM)
        
        if not os.path.exists(self.OutputFolder):
	           os.makedirs(self.OutputFolder)         
        
        self.Raveinputsfolder = self.OutputFolder + '/'+'RavenInput/'
                
        self.qgisPP = os.environ['QGISPrefixPath']
        self.RoutingToolPath = os.environ['RoutingToolFolder']
                
        self.grassdb =os.path.join(tempfile.gettempdir(), 'grassdata_toolbox',self.ProjectNM)
        if not os.path.exists(self.grassdb):
	           os.makedirs(self.grassdb) 
        os.environ['GISDBASE'] = self.grassdb 
		
        self.grass_location_geo = 'Geographic'
        self.grass_location_pro = 'Projected'
        
        self.tempfolder = os.path.join(tempfile.gettempdir(), 'grassdata_toolbox_temp',self.ProjectNM)

        if not os.path.exists(self.tempfolder):
	           os.makedirs(self.tempfolder)
        
        
        self.sqlpath = os.path.join(self.grassdb,'Geographic\\PERMANENT\\sqlite\\sqlite.db')       
        self.cellSize = -9.9999
        self.SpRef_in = '#'
        self.ncols = -9999
        self.nrows = -9999
        self.Path_Maskply = '#'
        self.Path_dem = os.path.join(self.tempfolder,'dem.tif')
        self.Path_demproj = os.path.join(self.tempfolder,'dem_proj.tif')
        self.Path_allLakeply = os.path.join(self.tempfolder,'Hylake.shp')
        self.Path_WidDepLine = os.path.join(self.tempfolder,'WidDep.shp')
        self.Path_ObsPoint = os.path.join(self.tempfolder,'obspoint.shp')
        self.Path_Landuseinfo = os.path.join(self.tempfolder,'landuseinfo.csv')
        self.Path_allLakeRas = os.path.join(self.tempfolder,'hylakegdal.tif')
        self.Path_finalcatinfo_riv = os.path.join(self.tempfolder,'catinfo_riv.csv')
        self.Path_finalcatinfo_cat = os.path.join(self.tempfolder,'catinfo_cat.csv')
        self.Path_finalcatinfo = os.path.join(self.tempfolder,'catinfo.csv')
        self.Path_finalcatinfo_riv_type = os.path.join(self.tempfolder,'catinfo_riv.csvt')
        self.Path_finalcatinfo_type = os.path.join(self.tempfolder,'catinfo.csvt')
        self.Path_alllakeinfoinfo = os.path.join(self.tempfolder,'hylake.csv')
        self.Path_Maskply = os.path.join(self.tempfolder, 'HyMask2.shp')
       
########################################################################################
### Remove tempfolders

#########################################################################################
##### function to enerate mask based on the most donwstream polygon id
##### Output: For using hydroshed products the output is a mask polygon: self.Path_Maskply
#####         For using non hydroshed product, the output is a mask based on either dem or 
#####              a rough watershed delineaiton resut. depend on Path_OutletPoint value
#####              at the same time flow directio and accumulation is caculated for this region 
    def Generatmaskregion(self,Path_OutletPoint = '#'):
        #### g
        ### Set up QGIS enviroment 
        QgsApplication.setPrefixPath(self.qgisPP, True)
        Qgs = QgsApplication([],False)
        Qgs.initQgis()
        from qgis import processing
        from processing.core.Processing import Processing   
        feedback = QgsProcessingFeedback()
        Processing.initialize()
        QgsApplication.processingRegistry().addProvider(QgsNativeAlgorithms())

        if self.OutHyID > 0:
            hyinfocsv = self.Path_hyshdply_in[:-3] + "dbf"
            tempinfo = Dbf5(hyinfocsv)
            hyshdinfo = tempinfo.to_dataframe().values 
           
            HydroBasins1 = Defcat(hyshdinfo,self.OutHyID) ### return fid of polygons that needs to be select 
            if self.OutHyID > 0:
                HydroBasins2 = Defcat(hyshdinfo,self.OutHyID2)            
    ###  exculde the Ids in HydroBasins2 from HydroBasins1
                for i in range(len(HydroBasins2)):
                    rows =np.argwhere(HydroBasins1 == HydroBasins2[i])
                    HydroBasins1 = np.delete(HydroBasins1, rows)
                HydroBasins = HydroBasins1            
            else:
                HydroBasins = HydroBasins1
        
    ### Load HydroSHED Layers 
            hyshedl12 = QgsVectorLayer(self.Path_hyshdply_in, "")
        
    ### Build qgis selection expression
            where_clause = '"HYBAS_ID" IN'+ " ("
            for i in range(0,len(HydroBasins)):
                if i == 0:
                    where_clause = where_clause + str(HydroBasins[i])
                else:
                    where_clause = where_clause + "," + str(HydroBasins[i])
            where_clause = where_clause + ")"
    
            req = QgsFeatureRequest().setFlags( QgsFeatureRequest.NoGeometry )
            req.setFilterExpression(where_clause)
            it = hyshedl12.getFeatures( req )
        
        ### obtain all feature id of selected polygons
            selectedFeatureID = []
    
            for feature in it:
    #        print(feature.id())
                selectedFeatureID.append(feature.id())
            
            hyshedl12.select(selectedFeatureID)   ### select with polygon id
        
        # Save selected polygons to output 
            _writer = QgsVectorFileWriter.writeAsVectorFormat(hyshedl12, os.path.join(self.tempfolder, 'HyMask.shp'), "UTF-8", hyshedl12.crs(), "ESRI Shapefile", onlySelected=True)
            processing.run('gdal:dissolve', {'INPUT':os.path.join(self.tempfolder, 'HyMask.shp'),'FIELD':'MAIN_BAS','OUTPUT':self.Path_Maskply})
            
            del hyshedl12
            
        else:
            r_dem_layer = QgsRasterLayer(self.Path_dem_in, "") ### load DEM raster as a  QGIS raster object to obtain attribute        
            self.cellSize = float(r_dem_layer.rasterUnitsPerPixelX())  ### Get Raster cell size
            self.SpRef_in = r_dem_layer.crs().authid()   ### get Raster spatialReference id
            params = {'INPUT': self.Path_dem_in, 'format': 'GTiff', 'OUTPUT': self.Path_dem}
            processing.run('gdal:translate',params)
            import grass.script as grass
            from grass.script import array as garray
            import grass.script.setup as gsetup
            from grass.pygrass.modules.shortcuts import general as g
            from grass.pygrass.modules.shortcuts import raster as r
            from grass.pygrass.modules import Module
            from grass_session import Session
            
            os.environ.update(dict(GRASS_COMPRESS_NULLS='1',GRASS_COMPRESSOR='ZSTD',GRASS_VERBOSE='1'))
            PERMANENT = Session()
            PERMANENT.open(gisdb=self.grassdb, location=self.grass_location_geo,create_opts=self.SpRef_in)
            
            grass.run_command("r.import", input = self.Path_dem, output = 'dem', overwrite = True)
            grass.run_command('g.region', raster='dem')
            #### create watershed mask or use dem as mask
            if Path_OutletPoint != '#':
                grass.run_command('r.watershed',elevation = 'dem', drainage = 'dir_grass',accumulation = 'acc_grass',flags = 's', overwrite = True)
                grass.run_command('r.water.outlet',input = 'dir_grass', output = 'wat_mask', coordinates  = Path_OutletPoint,overwrite = True)
                grass.run_command('r.mask'  , raster='wat_mask', maskcats = '*',overwrite = True)
                grass.run_command('g.region', raster='wat_mask',overwrite = True)
            else:
                grass.run_command('r.mask'  , raster='dem', maskcats = '*',overwrite = True)
            
            grass.run_command('r.out.gdal', input = 'MASK',output = os.path.join(self.tempfolder, 'Mask1.tif'),format= 'GTiff',overwrite = True)
            processing.run("gdal:polygonize", {'INPUT':os.path.join(self.tempfolder, 'Mask1.tif'),'BAND':1,'FIELD':'DN','EIGHT_CONNECTEDNESS':False,'EXTRA':'','OUTPUT':os.path.join(self.tempfolder, 'HyMask.shp')})
            processing.run('gdal:dissolve', {'INPUT':os.path.join(self.tempfolder, 'HyMask.shp'),'FIELD':'DN','OUTPUT':self.Path_Maskply})
            PERMANENT.close()
            del r_dem_layer
        Qgs.exit()
        
        return 

##################################################################################################  
#### functions to preprocess data, Output:
##  self.Path_dem,self.cellSize,self.SpRef_in
##  
    def Generateinputdata(self):

        QgsApplication.setPrefixPath(self.qgisPP, True)
        Qgs = QgsApplication([],False)
        Qgs.initQgis()
        from qgis import processing
        from processing.core.Processing import Processing
        from processing.tools import dataobjects
           
        feedback = QgsProcessingFeedback()
        Processing.initialize()
        QgsApplication.processingRegistry().addProvider(QgsNativeAlgorithms())
        context = dataobjects.createContext()
        context.setInvalidGeometryCheck(QgsFeatureRequest.GeometryNoCheck)
    
        r_dem_layer = QgsRasterLayer(self.Path_dem_in, "") ### load DEM raster as a  QGIS raster object to obtain attribute        
        self.cellSize = float(r_dem_layer.rasterUnitsPerPixelX())  ### Get Raster cell size
        self.SpRef_in = r_dem_layer.crs().authid()   ### get Raster spatialReference id
        print("Working with a  sptail reference  :   " , r_dem_layer.crs().description(), "      ", self.SpRef_in )
        print("The cell cize is   ",self.cellSize)
    
        if  self.OutHyID > 0:   #### input is using hydroshed  hydroshed polygons 
            params = {'INPUT': self.Path_dem_in,'MASK': self.Path_Maskply,'NODATA': -9999,'ALPHA_BAND': False,'CROP_TO_CUTLINE': True,
                                                                    'KEEP_RESOLUTION': True,
                                                                    'OPTIONS': 'COMPRESS=LZW',
                                                                    'DATA_TYPE': 0,  # Byte
                                                                    'OUTPUT': self.Path_dem}
            dem = processing.run('gdal:cliprasterbymasklayer',params)  #### extract dem
        
        copyfile(os.path.join(self.RoutingToolPath,'catinfo_riv.csvt'),os.path.join(self.tempfolder,'catinfo_riv.csvt')) 
        copyfile(os.path.join(self.RoutingToolPath,'catinfo_riv.csvt'),os.path.join(self.tempfolder,'catinfo_cat.csvt')) 
###### set up GRASS environment for translate vector to rasters and clip rasters
        import grass.script as grass
        from grass.script import array as garray
        import grass.script.setup as gsetup
        from grass.pygrass.modules.shortcuts import general as g
        from grass.pygrass.modules.shortcuts import raster as r
        from grass.pygrass.modules import Module
        from grass_session import Session
    
       
        os.environ.update(dict(GRASS_COMPRESS_NULLS='1',GRASS_COMPRESSOR='ZSTD',GRASS_VERBOSE='-1'))
        PERMANENT = Session()
        PERMANENT.open(gisdb=self.grassdb, location=self.grass_location_geo,create_opts=self.SpRef_in)
        ###  hydroshed product use cliped dem to setup g.region and g.mask 
        ###  non hydroshed product the g.region and g.mask is defined in generatemask funciton 
        if self.OutHyID > 0:   
            grass.run_command("r.import", input = self.Path_dem, output = 'dem', overwrite = True)
            grass.run_command('r.mask'  , raster='dem', maskcats = '*',overwrite = True)
            grass.run_command('g.region', raster='dem')

        strtemp_array = garray.array(mapname="dem")
        self.ncols = int(strtemp_array.shape[1])
        self.nrows = int(strtemp_array.shape[0])

        ### process vector data, clip and import 
        processing.run("native:clip", {'INPUT':self.Path_Lakefile_in,'OVERLAY':self.Path_Maskply,'OUTPUT':self.Path_allLakeply},context = context)
        processing.run("native:clip", {'INPUT':self.Path_WiDep_in,'OVERLAY':self.Path_Maskply,'OUTPUT':self.Path_WidDepLine},context = context)
        processing.run("native:clip", {'INPUT':self.Path_obspoint_in,'OVERLAY':self.Path_Maskply,'OUTPUT':self.Path_ObsPoint},context = context)
        grass.run_command("v.import", input = self.Path_WidDepLine, output = 'WidDep', overwrite = True)
        grass.run_command("v.import", input = self.Path_ObsPoint, output = 'obspoint', overwrite = True)
        grass.run_command("v.import", input = self.Path_allLakeply, output = 'Hylake', overwrite = True)


        if self.Path_dir_in != '#':  ### Hydroshed provided with dir 
            grass.run_command("r.external", input = self.Path_dir_in, output = 'dir_in', overwrite = True)
            grass.run_command("r.clip", input = 'dir_in', output = 'dir_Arcgis', overwrite = True, flags = 'r')
            grass.run_command('r.reclass', input='dir_Arcgis',output = 'dir_grass',rules =os.path.join(self.RoutingToolPath,'Arcgis2GrassDIR.txt'), overwrite = True)
        else:  ### non hydroshed if dir has been build 
            dirbuid = grass.find_file('dir_grass', element = 'cell')
            if (len(dirbuid['file']) <=0):
                grass.run_command('r.watershed',elevation = 'dem', drainage = 'dir_grass', accumulation = 'acc_grass',flags = 's', overwrite = True)
            grass.run_command('r.reclass', input='dir_grass',output = 'dir_Arcgis',rules = os.path.join(self.RoutingToolPath,'Grass2ArcgisDIR.txt'), overwrite = True)
    
        copyfile(self.Path_Landuseinfo_in, self.Path_Landuseinfo) 
        grass.run_command("r.external", input = self.Path_Landuse_in, output = 'landuse_in', overwrite = True)
        grass.run_command("r.clip", input = 'landuse_in', output = 'landuse', overwrite = True)        
    
        ### change lake vector to lake raster.... with -at option 
        os.system('gdal_rasterize -at -of GTiff -a_nodata -9999 -a Hylak_id -tr  '+ str(self.cellSize) + "  " +str(self.cellSize) +"   " + "\"" +  self.Path_allLakeply +"\""+ "    "+ "\""+self.Path_allLakeRas+"\"")
        grass.run_command("r.in.gdal", input = self.Path_allLakeRas, output = 'alllakeraster_in', overwrite = True)
        grass.run_command('r.mapcalc',expression = 'alllake = int(alllakeraster_in)',overwrite = True)
        grass.run_command("r.null", map = 'alllake', setnull = -9999)
        ### rasterize other vectors 
        grass.run_command('v.to.rast',input = 'WidDep',output = 'width',use = 'attr',attribute_column = 'WIDTH',overwrite = True)
        grass.run_command('v.to.rast',input = 'WidDep',output = 'depth',use = 'attr',attribute_column = 'DEPTH',overwrite = True)
        grass.run_command('v.to.rast',input = 'WidDep',output = 'qmean',use = 'attr',attribute_column = 'Q_Mean2',overwrite = True)
        grass.run_command('v.to.rast',input = 'obspoint',output = 'obs',use = 'attr',attribute_column = 'Obs_ID',overwrite = True)

        PERMANENT.close()
        del r_dem_layer
        Qgs.exit()
#####################################################################################################

####################################################################################################3
                
    def WatershedDiscretizationToolset(self,accthresold):
        import grass.script as grass
        from grass.script import array as garray
        import grass.script.setup as gsetup
        from grass.pygrass.modules.shortcuts import general as g
        from grass.pygrass.modules.shortcuts import raster as r
        from grass.pygrass.modules import Module
        from grass_session import Session

        os.environ.update(dict(GRASS_COMPRESS_NULLS='1',GRASS_COMPRESSOR='ZSTD',GRASS_VERBOSE='-1'))
        PERMANENT = Session()
        PERMANENT.open(gisdb=self.grassdb, location=self.grass_location_geo,create_opts=self.SpRef_in)


        if self.Path_dir_in == '#':  ### did not provide dir, use dem to generate watershed. recommand !!
            grass.run_command('r.stream.extract',elevation = 'dem',accumulation = 'acc_grass',threshold =accthresold,stream_raster = 'str_grass_r',
                              stream_vector = 'str_grass_v',overwrite = True)
        else:
        ## generate correct stream raster, when the dir is not derived from dem. for Hydroshed Cases 
            grass.run_command('r.accumulate', direction='dir_grass',format = '45degree',accumulation ='acc_grass',
                            stream = 'str_grass_v',threshold = accthresold, overwrite = True)
            grass.run_command('v.to.rast',input = 'str_grass_v',output = 'str_grass_r2',use = 'cat',overwrite = True)
    
            strtemp_array = garray.array(mapname="str_grass_r2")
            acc_array = garray.array(mapname="acc_grass")
            dirarc_array = garray.array(mapname="dir_Arcgis")
    
    #####Correct stream network
            strids = np.unique(strtemp_array)
            strids = strids[strids >= 0] 

        
            for i in range(0,len(strids)):
                strid = strids[i]

                trow,tcol = Getbasinoutlet(strid,strtemp_array,acc_array,dirarc_array,self.ncols,self.nrows)
                nrow,ncol = Nextcell(dirarc_array,trow,tcol)### get the downstream catchment id
                if nrow <= 0 or ncol <=0 or nrow >=self.nrows or ncol >= self.ncols:
                    continue
                nstrid = strtemp_array[nrow,ncol]
        
                rowcol = np.argwhere(strtemp_array==nstrid).astype(int)
                catacc = np.full((len(rowcol),3),-9999)
                catacc[:,0] = rowcol[:,0]
                catacc[:,1] = rowcol[:,1]
                catacc[:,2] = acc_array[rowcol[:,0],rowcol[:,1]]
                catacc = catacc[catacc[:,2].argsort()]
    
                if nrow != catacc[0,0] or ncol != catacc[0,1]:  ### If the stream 1 did not connect to the begining of the downstream stream (2) 
                    nnrow,nncol = Nextcell(dirarc_array,nrow,ncol) ### The last cell of 2 will be changed. 
                    if nnrow <= 0 or nncol <=0 or nnrow >=self.nrows or nncol >= self.ncols:
                        continue
                    nnstrid = strtemp_array[nnrow,nncol]
                    strtemp_array[nrow,ncol] = nnstrid
        ##### end modify stream grid and store new grids
            temparray = garray.array()
            temparray[:,:] = 0
            temparray[:,:] = strtemp_array[:,:]
            temparray.write(mapname="str_grass_rf", overwrite=True)
            grass.run_command('r.null', map='str_grass_rf',setnull=0)
            grass.run_command('r.mapcalc',expression = 'str_grass_r = int(str_grass_rf)',overwrite = True)
             
#        grass.run_command('r.thin',input = 'str_grass_rfn', output = 'str_grass_r',overwrite = True)
        grass.run_command('r.to.vect',  input = 'str_grass_r',output = 'str', type ='line' ,overwrite = True)

        ##### generate catchment without lakes based on 'str_grass_r'        
        grass.run_command('r.stream.basins',direction = 'dir_grass', stream = 'str_grass_r', basins = 'cat1',overwrite = True)

        
################ check connected lakes  and non connected lakes 
        grass.run_command('v.select',ainput = 'Hylake',binput = 'str',output = 'lake_str',overwrite = True)
        grass.run_command('v.out.ogr', input = 'lake_str',output = os.path.join(self.tempfolder, "Connect_lake.shp"),format= 'ESRI_Shapefile',overwrite = True)
        os.system('gdal_rasterize -at -of GTiff -a_nodata -9999 -a Hylak_id -tr  '+ str(self.cellSize) + "  " +str(self.cellSize) +"   " + "\"" +  os.path.join(self.tempfolder, "Connect_lake.shp") +"\""+ "    "+ "\""+os.path.join(self.tempfolder, "cnhylakegdal.tif")+"\"")
        grass.run_command("r.in.gdal", input = os.path.join(self.tempfolder, "cnhylakegdal.tif"), output = 'cnlakeraster_in', overwrite = True)
        grass.run_command('r.mapcalc',expression = 'Connect_Lake = int(cnlakeraster_in)',overwrite = True)    
        grass.run_command('r.mapcalc',expression = 'Nonconnect_Lake = if(isnull(Connect_Lake),alllake,-9)',overwrite = True)
    
#        grass.run_command('v.out.ogr', input = 'finalcat_F',output = os.path.join(self.tempfolder,'finalcat_info1.shp'),format= 'ESRI_Shapefile',overwrite = True,quiet = 'Ture')
        grass.run_command('r.out.gdal', input = 'cat1',output = os.path.join(self.tempfolder,'cat1.tif'),format= 'GTiff',overwrite = True,quiet = 'Ture')    
        grass.run_command('r.out.gdal', input = 'Connect_Lake',output = os.path.join(self.tempfolder,'Connect_Lake.tif'),format= 'GTiff',overwrite = True,quiet = 'Ture')    
        grass.run_command('r.out.gdal', input = 'str_grass_r',output = os.path.join(self.tempfolder,'str_grass_r.tif'),format= 'GTiff',overwrite = True,quiet = 'Ture')    

        PERMANENT.close()
###########################################################################################3

############################################################################################
    def AutomatedWatershedsandLakesFilterToolset(self,Thre_Lake_Area_Connect = 0,Thre_Lake_Area_nonConnect = -1,MaximumLakegrids = 1600):

        tempinfo = Dbf5(self.Path_allLakeply[:-3] + "dbf")
        allLakinfo = tempinfo.to_dataframe()
        allLakinfo.to_csv(self.Path_alllakeinfoinfo,index = None, header=True)
        
        import grass.script as grass
        from grass.script import array as garray
        import grass.script.setup as gsetup
        from grass.pygrass.modules.shortcuts import general as g
        from grass.pygrass.modules.shortcuts import raster as r
        from grass.pygrass.modules import Module
        from grass_session import Session

        os.environ.update(dict(GRASS_COMPRESS_NULLS='1',GRASS_COMPRESSOR='ZSTD',GRASS_VERBOSE='1'))
        PERMANENT = Session()
        PERMANENT.open(gisdb=self.grassdb, location=self.grass_location_geo,create_opts=self.SpRef_in)
        con = sqlite3.connect(self.sqlpath)
        
        VolThreshold =Thre_Lake_Area_Connect ### lake area thresthold for connected lakes 
        NonConLThres = Thre_Lake_Area_nonConnect ### lake area thresthold for non connected lakes 
        nlakegrids = MaximumLakegrids 
    
        temparray = garray.array()
        temparray[:,:] = -9999
        temparray.write(mapname="tempraster", overwrite=True)
        self.ncols = int(temparray.shape[1])
        self.nrows = int(temparray.shape[0])
##### begin processing 

        blid = 1000000    #### begining of new lake id
        bcid = 1          ## begining of new cat id of hydrosheds
        bsid = 2000000    ## begining of new cat id of in inflow of lakes
        blid2 = 3000000
        boid = 4000000
    
        noncnlake_arr = garray.array(mapname="Nonconnect_Lake")
        conlake_arr = garray.array(mapname="Connect_Lake")
        cat1_arr = garray.array(mapname="cat1")
        str_array = garray.array(mapname="str_grass_r")
        acc_array = garray.array(mapname="acc_grass")
        dir_array = garray.array(mapname="dir_Arcgis")
        obs_array = garray.array(mapname="obs")

###### generate selected lakes 
        hylake1 = selectlake2(conlake_arr,VolThreshold,allLakinfo) ### remove lakes with lake area smaller than the VolThreshold from connected lake raster 
        if NonConLThres >= 0:
            Lake1 = selectlake(hylake1,noncnlake_arr,NonConLThres,allLakinfo) ### remove lakes with lake area smaller than the NonConLThres from non-connected lake raster 
        else:
            Lake1 = hylake1
        temparray[:,:] = Lake1[:,:]
        temparray.write(mapname="SelectedLakes", overwrite=True)
        grass.run_command('r.null', map='SelectedLakes',setnull=-9999)

####    
        Pourpoints = GenerPourpoint(cat1_arr,Lake1,str_array,self.nrows,self.ncols,blid,bsid,bcid,acc_array,dir_array)
        temparray[:,:] = Pourpoints[:,:]
        temparray.write(mapname="Pourpoints_1", overwrite=True)
        grass.run_command('r.null', map='Pourpoints_1',setnull=-9999)
        grass.run_command('r.to.vect', input='Pourpoints_1',output='Pourpoints_1_F',type='point', overwrite = True)
        
        grass.run_command('r.stream.basins',direction = 'dir_grass', points = 'Pourpoints_1_F', basins = 'cat2_t',overwrite = True)        
        sqlstat="SELECT cat, value FROM Pourpoints_1_F"
        df_P_1_F = pd.read_sql_query(sqlstat, con)
        df_P_1_F.loc[len(df_P_1_F),'cat'] = '*'
        df_P_1_F.loc[len(df_P_1_F)-1,'value'] = 'NULL'
        df_P_1_F['eq'] = '='
        df_P_1_F.to_csv(os.path.join(self.tempfolder,'rule_cat2.txt'),sep = ' ',columns = ['cat','eq','value'],header = False,index=False)
        grass.run_command('r.reclass', input='cat2_t',output = 'cat2',rules =os.path.join(self.tempfolder,'rule_cat2.txt'), overwrite = True)
        
        
        grass.run_command('v.out.ogr', input = 'Pourpoints_1_F',output = os.path.join(self.tempfolder, "Pourpoints_1_F.shp"),format= 'ESRI_Shapefile',overwrite = True)
#        grass.run_command('r.out.gdal', input = 'cat1',output = os.path.join(self.tempfolder,'cat1.tif'),format= 'GTiff',overwrite = True,quiet = 'Ture')    
    
        cat2_array =  garray.array(mapname="cat2")
        temcat,outlakeids =CE_mcat4lake(cat2_array,Lake1,acc_array,dir_array,bsid,self.nrows,self.ncols,Pourpoints) 
        temcat2 = CE_Lakeerror(acc_array,dir_array,Lake1,temcat,bsid,blid,boid,self.nrows,self.ncols,cat1_arr)
        temparray[:,:] = temcat2[:,:]
        temparray.write(mapname="cat3", overwrite=True)
        grass.run_command('r.null', map='cat3',setnull=-9999)

        grass.run_command('r.out.gdal', input = 'cat2',output = os.path.join(self.tempfolder,'cat2.tif'),format= 'GTiff',overwrite = True,quiet = 'Ture') 
#        grass.run_command('r.out.gdal', input = 'cat3',output = os.path.join(self.tempfolder,'cat3.tif'),format= 'GTiff',overwrite = True,quiet = 'Ture') 
    
        nPourpoints = GenerateFinalPourpoints(acc_array,dir_array,Lake1,temcat2,bsid,blid,boid,self.nrows,self.ncols,cat1_arr,obs_array)
        temparray[:,:] = nPourpoints[:,:]
        temparray.write(mapname="Pourpoints_2", overwrite=True)
        grass.run_command('r.null', map='Pourpoints_2',setnull=-9999)
        grass.run_command('r.to.vect', input='Pourpoints_2',output='Pourpoints_2_F',type='point', overwrite = True)    
        grass.run_command('v.out.ogr', input = 'Pourpoints_2_F',output = os.path.join(self.tempfolder, "Pourpoints_2_F.shp"),format= 'ESRI_Shapefile',overwrite = True)

        ## with new pour points
        grass.run_command('r.stream.basins',direction = 'dir_grass', points = 'Pourpoints_2_F', basins = 'cat3_t',overwrite = True)        
        sqlstat="SELECT cat, value FROM Pourpoints_2_F"
        df_P_1_F = pd.read_sql_query(sqlstat, con)
        df_P_1_F.loc[len(df_P_1_F),'cat'] = '*'
        df_P_1_F.loc[len(df_P_1_F)-1,'value'] = 'NULL'
        df_P_1_F['eq'] = '='
        df_P_1_F.to_csv(os.path.join(self.tempfolder,'rule_cat3.txt'),sep = ' ',columns = ['cat','eq','value'],header = False,index=False)
        grass.run_command('r.reclass', input='cat3_t',output = 'cat3',rules =os.path.join(self.tempfolder,'rule_cat3.txt'), overwrite = True)
        cat3_array =  garray.array(mapname="cat3")
        grass.run_command('r.out.gdal', input = 'cat3',output = os.path.join(self.tempfolder,'cat3.tif'),format= 'GTiff',overwrite = True,quiet = 'Ture') 
                
        outlakeids= check_lakecatchment(cat3_array,Lake1,acc_array,dir_array,bsid,self.nrows,self.ncols)


    
        ### Modify lake flow directions
        ndir = ChangeDIR(dir_array,Lake1,acc_array,self.ncols,self.nrows,outlakeids,nlakegrids,cat3_array)
        temparray[:,:] = ndir[:,:]
        temparray.write(mapname="ndir_Arcgis", overwrite=True)
        grass.run_command('r.null', map='ndir_Arcgis',setnull=-9999)    
        grass.run_command('r.reclass', input='ndir_Arcgis',output = 'ndir_grass',rules =os.path.join(self.RoutingToolPath,'Arcgis2GrassDIR.txt'),overwrite = True)
     
        grass.run_command('r.stream.basins',direction = 'ndir_grass', points = 'Pourpoints_2_F', basins = 'cat4_t',overwrite = True)

        sqlstat="SELECT cat, value FROM Pourpoints_2_F"
        df_P_2_F = pd.read_sql_query(sqlstat, con)
        df_P_2_F.loc[len(df_P_2_F),'cat'] = '*'
        df_P_2_F.loc[len(df_P_2_F)-1,'value'] = 'NULL'
        df_P_2_F['eq'] = '='
        df_P_2_F.to_csv(os.path.join(self.tempfolder,'rule_cat4.txt'),sep = ' ',columns = ['cat','eq','value'],header = False,index=False)
        grass.run_command('r.reclass', input='cat4_t',output = 'cat4',rules =os.path.join(self.tempfolder,'rule_cat4.txt'), overwrite = True)


        grass.run_command('r.out.gdal', input = 'cat4',output = os.path.join(self.tempfolder,'cat4.tif'),format= 'GTiff',overwrite = True,quiet = 'Ture') 
        cat4_array =  garray.array(mapname="cat4")
        rowcols = np.argwhere(cat4_array == 0)
        cat4_array[rowcols[:,0],rowcols[:,1]] = -9999
        finalcat = CE_mcat4lake2(cat4_array,Lake1,acc_array,dir_array,bsid,self.nrows,self.ncols,nPourpoints)
        temparray[:,:] = finalcat[:,:]
        temparray.write(mapname="finalcat", overwrite=True)
        grass.run_command('r.null', map='finalcat',setnull=-9999)    
        grass.run_command('r.to.vect', input='finalcat',output='finalcat_F1',type='area', overwrite = True)    

####   dissolve final catchment polygons    
        grass.run_command('v.db.addcolumn', map= 'finalcat_F1', columns = "Gridcode VARCHAR(40)")
        grass.run_command('v.db.update', map= 'finalcat_F1', column = "Gridcode",qcol = 'value')
#    grass.run_command('v.reclass', input= 'finalcat_F1', column = "Gridcode",output = 'finalcat_F',overwrite = True)
        grass.run_command('v.dissolve', input= 'finalcat_F1', column = "Gridcode",output = 'finalcat_F',overwrite = True)    
#    grass.run_command('v.select',ainput = 'str',binput = 'finalcat_F',output = 'str_finalcat',overwrite = True)
        grass.run_command('v.overlay',ainput = 'str',binput = 'finalcat_F1',operator = 'and',output = 'str_finalcat',overwrite = True)  
        grass.run_command('v.out.ogr', input = 'str_finalcat',output = os.path.join(self.tempfolder,'str_finalcat.shp'),format= 'ESRI_Shapefile',overwrite = True)
        
        grass.run_command('v.out.ogr', input = 'str',output = os.path.join(self.tempfolder,'str.shp'),format= 'ESRI_Shapefile',overwrite = True)    
        grass.run_command('r.to.vect', input='SelectedLakes',output='SelectedLakes_F',type='area', overwrite = True) 
        grass.run_command('v.out.ogr', input = 'str_finalcat',output = os.path.join(self.tempfolder,'str_finalcat.shp'),format= 'ESRI_Shapefile',overwrite = True)
#    grass.run_command('v.db.join', map= 'SelectedLakes_F',column = 'value', other_table = 'result',other_column ='SubId', overwrite = True)
        con.close()
        PERMANENT.close()
                
############################################################################3
    def RoutingNetworkTopologyUpdateToolset_riv(self,projection = 'default'):
        import grass.script as grass
        from grass.script import array as garray
        import grass.script.setup as gsetup
        from grass.pygrass.modules.shortcuts import general as g
        from grass.pygrass.modules.shortcuts import raster as r
        from grass.pygrass.modules import Module
        from grass_session import Session

        QgsApplication.setPrefixPath(self.qgisPP, True)
        Qgs = QgsApplication([],False)
        Qgs.initQgis()
        from qgis import processing
        from processing.core.Processing import Processing
        from processing.tools import dataobjects
           
        feedback = QgsProcessingFeedback()
        Processing.initialize()
        QgsApplication.processingRegistry().addProvider(QgsNativeAlgorithms())
        context = dataobjects.createContext()
        context.setInvalidGeometryCheck(QgsFeatureRequest.GeometryNoCheck)


        os.environ.update(dict(GRASS_COMPRESS_NULLS='1',GRASS_COMPRESSOR='ZSTD',GRASS_VERBOSE='1'))
        PERMANENT = Session()
        PERMANENT.open(gisdb=self.grassdb, location=self.grass_location_geo,create_opts=self.SpRef_in)
        
        con = sqlite3.connect(self.sqlpath)
      
        #### generate new stream raster based on str_grass_r from acc thresthold and finalcat.
         
        finalcat_arr = garray.array(mapname="finalcat")
        str_grass_r_array = garray.array(mapname="str_grass_r")

        self.ncols = int(finalcat_arr.shape[1])
        self.nrows = int(finalcat_arr.shape[0])  
        
        nstrarray = garray.array()
        nstrarray[:,:] = -9999        
        ## loop for each str_grass_r
        
        ## obtain all stream id 
        strids = np.unique(str_grass_r_array)#
        strids = strids[strids>0]
        #obtain all cat id 
        fcatids = np.unique(finalcat_arr)#### cat all catchment idd
        fcatids = fcatids[fcatids>0]
        ###A array store new stream id , old stream id and catchemtn id 
        nstrinfo = np.full((len(strids)*len(fcatids),3),-9999)   ### maximum possible number of new stream segments 
        nstrinfodf = pd.DataFrame(nstrinfo, columns = ['No_Lake_SubId', "Finalcat_SubId","With_Lake_SubId"])
        
        ### assign a unique stream id based on str_grass_r and final cat
        nstrid = 1
        for i in range(0,len(strids)):
            strid = strids[i]
            nstrinfodf.loc[i,'No_Lake_SubId'] = strid
            strmask = str_grass_r_array == strid  ### mask array, true at location of str == strid 
            catsinstr = finalcat_arr[strmask]  ### get all cat id overlay with this stream
            catsinstrids = np.unique(catsinstr)  ### get unique cat id overlay with this stream
            catsinstrids = catsinstrids[catsinstrids>0]
            for j in range(0,len(catsinstrids)):   ### loop for each cat id, and assgin for a new stream id 
                finalcatmask = finalcat_arr == catsinstrids[j]
                mask = np.logical_and(finalcatmask, strmask)   ### build mask for grids belong to current stream and current cat
                nstrarray[mask] = nstrid   ## assgin new stream id to mask region
                nstrinfodf.loc[i,'Finalcat_SubId'] = catsinstrids[j]
                nstrinfodf.loc[i,'With_Lake_SubId'] = nstrid
                nstrid = nstrid + 1
        temparray = garray.array()
        temparray[:,:] = -9999
        temparray[:,:] = nstrarray[:,:]
        temparray.write(mapname="nstr_seg_t", overwrite=True)  #### write new stream id to a grass raster 
        grass.run_command('r.null', map='nstr_seg_t',setnull=-9999)
        grass.run_command('r.mapcalc',expression = 'nstr_seg = int(nstr_seg_t)',overwrite = True)
        grass.run_command('r.out.gdal', input = 'nstr_seg',output =os.path.join(self.tempfolder,'nstr_seg.tif'),format= 'GTiff',overwrite = True)  
        
        ### Generate new catchment based on new stream   
        grass.run_command('r.stream.basins',direction = 'ndir_grass', stream = 'nstr_seg', basins = 'Net_cat',overwrite = True)        
        grass.run_command('r.out.gdal', input = 'Net_cat',output =os.path.join(self.tempfolder,'Net_cat.tif'),format= 'GTiff',overwrite = True)
        grass.run_command('r.to.vect', input='Net_cat',output='Net_cat_F1',type='area', overwrite = True)    ## save to vector 
        grass.run_command('v.db.addcolumn', map= 'Net_cat_F1', columns = "GC_str VARCHAR(40)")
        grass.run_command('v.db.addcolumn', map= 'Net_cat_F1', columns = "Area_m double")        
        grass.run_command('v.db.update', map= 'Net_cat_F1', column = "GC_str",qcol = 'value')
        grass.run_command('v.dissolve', input= 'Net_cat_F1', column = "GC_str",output = 'Net_cat_F',overwrite = True) ### dissolve based on gridcode 
        grass.run_command('v.out.ogr', input = 'Net_cat_F',output = os.path.join(self.tempfolder,'Net_cat_F.shp'),format= 'ESRI_Shapefile',overwrite = True)
        grass.run_command('v.db.addcolumn', map= 'Net_cat_F', columns = "Gridcode INT")        
        grass.run_command('v.db.update', map= 'Net_cat_F', column = "Gridcode",qcol = 'GC_str')
        

        # create a river network shpfile that have river segment based on   'Net_cat_F.shp'
        grass.run_command('r.mapcalc',expression = 'str1 = if(isnull(str_grass_r),null(),1)',overwrite = True) ## a rive 
        grass.run_command('r.to.vect',  input = 'str1',output = 'str1', type ='line' ,overwrite = True)
        grass.run_command('v.overlay',ainput = 'str1',binput = 'Net_cat_F',operator = 'and',output = 'nstr_nfinalcat',overwrite = True)  
        grass.run_command('v.out.ogr', input = 'nstr_nfinalcat',output = os.path.join(self.tempfolder,'nstr_nfinalcat.shp'),format= 'ESRI_Shapefile',overwrite = True)
        processing.run('gdal:dissolve', {'INPUT':os.path.join(self.tempfolder, 'nstr_nfinalcat.shp'),'FIELD':'b_GC_str','OUTPUT':os.path.join(self.tempfolder, "nstr_nfinalcat_F.shp")}) 
        grass.run_command("v.import", input =os.path.join(self.tempfolder, "nstr_nfinalcat_F.shp"), output = 'nstr_nfinalcat_F', overwrite = True)               
  

        
        grass.run_command('v.db.addcolumn', map= 'nstr_nfinalcat_F', columns = "Gridcode INT")
        grass.run_command('v.db.addcolumn', map= 'nstr_nfinalcat_F', columns = "Length_m double")
        
        grass.run_command('v.db.update', map= 'nstr_nfinalcat_F', column = "Gridcode",qcol = 'b_GC_str')
        grass.run_command('v.db.dropcolumn', map= 'nstr_nfinalcat_F', columns = ['b_GC_str'])       
#        grass.run_command('v.out.ogr', input = 'nstr_nfinalcat_F',output = os.path.join(self.tempfolder,'nstr_nfinalcat_F_Final.shp'),format= 'ESRI_Shapefile',overwrite = True)
#        Qgs.exit()       
        PERMANENT.close()
        
        ### Calulate catchment area slope river length under projected coordinates system. 
        if projection != 'default':

            os.system('gdalwarp ' + "\"" + self.Path_dem +"\""+ "    "+ "\""+self.Path_demproj+"\""+ ' -t_srs  ' + "\""+projection+"\"")

            project = Session()
            project.open(gisdb=self.grassdb, location=self.grass_location_pro,create_opts=projection)
            grass.run_command("r.import", input = self.Path_demproj, output = 'dem_proj', overwrite = True)
            grass.run_command('g.region', raster='dem_proj')  
        
            grass.run_command('v.proj', location=self.grass_location_geo,mapset = 'PERMANENT', input = 'nstr_nfinalcat_F',overwrite = True)
            grass.run_command('v.proj', location=self.grass_location_geo,mapset = 'PERMANENT', input = 'Net_cat_F',overwrite = True)
        
            grass.run_command('v.to.db', map= 'Net_cat_F',option = 'area',columns = "Area_m", units = 'meters') 
            grass.run_command('v.to.db', map= 'nstr_nfinalcat_F',option = 'length', columns = "Length_m",units = 'meters')
        
            grass.run_command('r.slope.aspect', elevation= 'dem_proj',slope = 'slope',aspect = 'aspect',precision = 'DCELL',overwrite = True)
            grass.run_command('r.mapcalc',expression = 'tanslopedegree = tan(slope) ',overwrite = True) 
            project.close 
        
            PERMANENT = Session()
            PERMANENT.open(gisdb=self.grassdb, location=self.grass_location_geo,create_opts=self.SpRef_in)
            grass.run_command('g.region', raster='dem')
            grass.run_command('v.proj', location=self.grass_location_pro,mapset = 'PERMANENT', input = 'nstr_nfinalcat_F',overwrite = True)
            grass.run_command('v.proj', location=self.grass_location_pro,mapset = 'PERMANENT', input = 'Net_cat_F',overwrite = True) 
            grass.run_command('r.proj', location=self.grass_location_pro,mapset = 'PERMANENT', input = 'tanslopedegree',overwrite = True) 
            grass.run_command('r.proj', location=self.grass_location_pro,mapset = 'PERMANENT', input = 'slope',overwrite = True) 
            grass.run_command('r.proj', location=self.grass_location_pro,mapset = 'PERMANENT', input = 'aspect',overwrite = True) 

        ### Add attributes to each catchments 
        # read raster arrays 
        Lake1_arr = garray.array(mapname="SelectedLakes")    
        dem_array = garray.array(mapname="dem")
        width_array = garray.array(mapname="width")
        depth_array = garray.array(mapname="depth")
        obs_array = garray.array(mapname="obs")
        slope_array = garray.array(mapname="tanslopedegree")
        aspect_array = garray.array(mapname="aspect")
        slope_deg_array = garray.array(mapname="slope")
        nstr_seg_array = garray.array(mapname="nstr_seg")
        acc_array = garray.array(mapname="acc_grass")
        dir_array = garray.array(mapname="ndir_Arcgis")#ndir_Arcgis
        Q_mean_array = garray.array(mapname="qmean")
        landuse_array = garray.array(mapname="landuse")
        Netcat_array = garray.array(mapname="Net_cat")
        grass.run_command('r.out.gdal', input = 'ndir_Arcgis',output = os.path.join(self.tempfolder,'ndir.tif'),format= 'GTiff',overwrite = True,quiet = 'Ture') 

        grass.run_command('r.out.gdal', input = 'dir_Arcgis',output = os.path.join(self.tempfolder,'dir.tif'),format= 'GTiff',overwrite = True,quiet = 'Ture') 
        grass.run_command('r.out.gdal', input = 'acc_grass',output = os.path.join(self.tempfolder,'acc.tif'),format= 'GTiff',overwrite = True,quiet = 'Ture') 
        ## read landuse and lake infomation data 
        tempinfo = Dbf5(self.Path_allLakeply[:-3] + "dbf")
        allLakinfo = tempinfo.to_dataframe()
        landuseinfo = pd.read_csv(self.Path_Landuseinfo_in,sep=",",low_memory=False)
    ### read length and area
        sqlstat="SELECT Gridcode, Length_m FROM nstr_nfinalcat_F"
        rivleninfo = pd.read_sql_query(sqlstat, con)
        sqlstat="SELECT Gridcode, Area_m FROM Net_cat_F"
        catareainfo = pd.read_sql_query(sqlstat, con)
        
        grass.run_command('r.out.gdal', input = 'obs',output =os.path.join(self.tempfolder,'obs.tif'),format= 'GTiff',overwrite = True)    
        
        allcatid = np.unique(nstr_seg_array)
        allcatid = allcatid[allcatid > 0]
        catinfo2 = np.full((len(allcatid),26),-9999.00000)    
        catinfodf = pd.DataFrame(catinfo2, columns = ['SubId', "DowSubId",'RivSlope','RivLength','BasSlope','BasAspect','BasArea',
                            'BkfWidth','BkfDepth','IsLake','HyLakeId','LakeVol','LakeDepth',
                             'LakeArea','Laketype','IsObs','MeanElev','FloodP_n','Q_Mean','Ch_n','DA','Strahler','Seg_ID','Seg_order'
                             ,'Max_DEM','Min_DEM'])                      
        catinfo= Generatecatinfo_riv(nstr_seg_array,acc_array,dir_array,Lake1_arr,dem_array,
             catinfodf,allcatid,width_array,depth_array,obs_array,slope_array,aspect_array,landuse_array,
             slope_deg_array,Q_mean_array,Netcat_array,landuseinfo,allLakinfo,self.nrows,self.ncols,
             rivleninfo.astype(float),catareainfo.astype(float))
             
        catinfo = Streamorderanddrainagearea(catinfo)         
        catinfo.to_csv(self.Path_finalcatinfo_riv, index = None, header=True)
    
        ### add lake info to selected laeks 
        grass.run_command('db.in.ogr', input=self.Path_alllakeinfoinfo,output = 'alllakeinfo',overwrite = True)
        grass.run_command('v.db.join', map= 'SelectedLakes_F',column = 'value', other_table = 'alllakeinfo',other_column ='Hylak_id', overwrite = True)
        ### add catchment info to all river segment 
        grass.run_command('db.in.ogr', input=self.Path_finalcatinfo_riv,output = 'result_riv',overwrite = True)
        grass.run_command('v.db.join', map= 'nstr_nfinalcat_F',column = 'Gridcode', other_table = 'result_riv',other_column ='SubId', overwrite = True)
        grass.run_command('v.db.dropcolumn', map= 'nstr_nfinalcat_F', columns = ['Length_m','Gridcode'])
        grass.run_command('v.out.ogr', input = 'nstr_nfinalcat_F',output = os.path.join(self.tempfolder,'finalriv_info1.shp'),format= 'ESRI_Shapefile',overwrite = True,quiet = 'Ture')
        
        grass.run_command('v.db.join', map= 'Net_cat_F',column = 'Gridcode', other_table = 'result_riv',other_column ='SubId', overwrite = True)
        grass.run_command('v.db.dropcolumn', map= 'Net_cat_F', columns = ['Area_m','Gridcode','GC_str'])
        grass.run_command('v.out.ogr', input = 'Net_cat_F',output = os.path.join(self.tempfolder,'finalriv_catinfo1.shp'),format= 'ESRI_Shapefile',overwrite = True,quiet = 'Ture')

        PERMANENT.close()
                

        processing.run("native:centroids", {'INPUT':os.path.join(self.tempfolder,'finalriv_catinfo1.shp'),'ALL_PARTS':False,'OUTPUT':os.path.join(self.tempfolder,'Centerpoints.shp')},context = context)
        processing.run("native:addxyfields", {'INPUT':os.path.join(self.tempfolder,'Centerpoints.shp'),'CRS':QgsCoordinateReferenceSystem(self.SpRef_in),'OUTPUT':os.path.join(self.tempfolder,'ctwithxy.shp')},context = context)
        processing.run("native:joinattributestable",{'INPUT':os.path.join(self.tempfolder,'finalriv_catinfo1.shp'),'FIELD':'SubId','INPUT_2':os.path.join(self.tempfolder,'ctwithxy.shp'),'FIELD_2':'SubId',
                          'FIELDS_TO_COPY':['x','y'],'METHOD':0,'DISCARD_NONMATCHING':False,'PREFIX':'centroid_','OUTPUT':os.path.join(self.OutputFolder,'finalriv_info_ply.shp')},context = context)
                          
        processing.run("native:joinattributestable",{'INPUT':os.path.join(self.tempfolder,'finalriv_info1.shp'),'FIELD':'SubId','INPUT_2':os.path.join(self.tempfolder,'ctwithxy.shp'),'FIELD_2':'SubId',
                          'FIELDS_TO_COPY':['x','y'],'METHOD':0,'DISCARD_NONMATCHING':False,'PREFIX':'centroid_','OUTPUT':os.path.join(self.OutputFolder,'finalriv_info.shp')},context = context)
       
        Qgs.exit()  
        
    def RoutingNetworkTopologyUpdateToolset_cat(self,projection = 'default'):
        import grass.script as grass
        from grass.script import array as garray
        import grass.script.setup as gsetup
        from grass.pygrass.modules.shortcuts import general as g
        from grass.pygrass.modules.shortcuts import raster as r
        from grass.pygrass.modules import Module
        from grass_session import Session
        os.environ.update(dict(GRASS_COMPRESS_NULLS='1',GRASS_COMPRESSOR='ZSTD',GRASS_VERBOSE='1'))
        PERMANENT = Session()
        PERMANENT.open(gisdb=self.grassdb, location=self.grass_location_geo,create_opts=self.SpRef_in)
                    
        Netcat_array = garray.array(mapname="Net_cat")
        catinfo = pd.read_csv(self.Path_finalcatinfo_riv)
        lakeids = catinfo['HyLakeId'].values
        lakeids = np.unique(lakeids)
        lakeids = lakeids[lakeids > 0]
        maxsubid = np.max(catinfo['SubId'].values)
        for i in range(0,len(lakeids)):
            lakeid = lakeids[i]
            nlakecatid = maxsubid + 10 + i
            lakeindex = catinfo['HyLakeId'] == lakeid   #### rows in catinfo that has this lake id
            row_lakeindex = np.argwhere(catinfo['HyLakeId'].values == lakeid)   #### rows in catinfo that has this lake id 
            lakecat_info = catinfo[lakeindex]
            
            catscoverlays = catinfo[lakeindex]['SubId'].values  #### catid that covered by this lake
            catscoverlays = np.unique(catscoverlays) 
            #### find lake catchment downstream id 
            downcatid = -1 
            for icat in range(0,len(lakecat_info)):
                if len(np.argwhere(catscoverlays == lakecat_info['DowSubId'].values[icat])) <= 0:
                    downcatid = lakecat_info['DowSubId'].values[icat]
    
            ### change upstream catchment's downstream catchment id  to newlakecatid 
            upcats_to_lakecats = catinfo['DowSubId'].isin(catscoverlays)#### rows that downstream id is the lake catchment
            upcatrows  = np.argwhere(upcats_to_lakecats == True)
            for iupcatrowidx in range(0,len(upcatrows)):
                iupcatrow =upcatrows[iupcatrowidx] 
                catinfo.loc[iupcatrow,'DowSubId'] = nlakecatid

            ## change catchment raster merge lake catchments 
            for j in range(0,len(lakecat_info)):
                jcat = lakecat_info['SubId'].values[j]
                jcatrowcol = np.argwhere(Netcat_array==jcat).astype(int)
                Netcat_array[jcatrowcol[:,0],jcatrowcol[:,1]] = nlakecatid

            #### change lake catchemt infomation 
            for irow in range(0,len(row_lakeindex)):
                irow_idx = row_lakeindex[irow]
                catinfo.loc[irow_idx,'SubId'] = nlakecatid
                catinfo.loc[lakeindex,'DowSubId'] = downcatid
                catinfo.loc[lakeindex,'RivSlope'] = -1.2345
                catinfo.loc[lakeindex,'RivLength'] =0.0
                catinfo.loc[lakeindex,'BasAspect'] = np.average(lakecat_info['BasAspect'].values,weights = lakecat_info['BasArea'].values)
                catinfo.loc[lakeindex,'BasArea'] = np.sum(lakecat_info['BasArea'].values)
                catinfo.loc[lakeindex,'BasSlope'] = np.average(lakecat_info['BasSlope'].values,weights = lakecat_info['BasArea'].values)
                catinfo.loc[lakeindex,'BkfWidth'] = -1.2345
                catinfo.loc[lakeindex,'BkfDepth'] = -1.2345
                catinfo.loc[lakeindex,'MeanElev'] = np.average(lakecat_info['MeanElev'].values,weights = lakecat_info['BasArea'].values)
                catinfo.loc[lakeindex,'IsObs'] = np.max(lakecat_info['IsObs'].values)
                catinfo.loc[lakeindex,'FloodP_n'] = -1.2345
                catinfo.loc[lakeindex,'Q_Mean'] = -1.2345
                catinfo.loc[lakeindex,'Ch_n'] = -1.2345
                catinfo.loc[lakeindex,'DA'] = np.max(lakecat_info['DA'].values)
                catinfo.loc[lakeindex,'Strahler'] =np.max(lakecat_info['Strahler'].values)
                catinfo.loc[lakeindex,'Seg_ID'] = -1.2345
                catinfo.loc[lakeindex,'Seg_order'] = -1.2345
                catinfo.loc[lakeindex,'Max_DEM'] = np.max(lakecat_info['Max_DEM'].values)
                catinfo.loc[lakeindex,'Min_DEM'] = np.min(lakecat_info['Min_DEM'].values)
                
        catinfo.to_csv(self.Path_finalcatinfo_cat, index = None, header=True)
        temparray = garray.array()
        temparray[:,:] = -9999
        temparray[:,:] = Netcat_array[:,:]
        temparray.write(mapname="Cat_Lake_combined", overwrite=True)  #### write new stream id to a grass raster 
        grass.run_command('r.null', map='Cat_Lake_combined',setnull=-9999)
        grass.run_command('r.mapcalc',expression = 'Cat_Lake_combined = int(Cat_Lake_combined)',overwrite = True)
        grass.run_command('r.out.gdal', input = 'Cat_Lake_combined',output = os.path.join(self.tempfolder,'Cat_Lake_combined.tif'),format= 'GTiff',overwrite = True,quiet = 'Ture') 
        grass.run_command('r.to.vect', input='Cat_Lake_combined',output='Cat_Lake_combined_F1',type='area', overwrite = True)    ## save to vector 
        grass.run_command('v.db.addcolumn', map= 'Cat_Lake_combined_F1', columns = "GC VARCHAR(40)")     
        grass.run_command('v.db.update', map= 'Cat_Lake_combined_F1', column = "GC",qcol = 'value')
        grass.run_command('v.dissolve', input= 'Cat_Lake_combined_F1', column = "GC",output = 'Cat_Lake_combined_F',overwrite = True) ### dissolve based on gridcode
        grass.run_command('v.db.addcolumn', map= 'Cat_Lake_combined_F', columns = "Gridcode INT")        
        grass.run_command('v.db.update', map= 'Cat_Lake_combined_F', column = "Gridcode",qcol = 'GC')
        
        grass.run_command('db.in.ogr', input=self.Path_finalcatinfo_cat,output = 'result_cat',overwrite = True)
        grass.run_command('v.db.join', map= 'Cat_Lake_combined_F',column = 'Gridcode', other_table = 'result_cat',other_column ='SubId', overwrite = True)
        grass.run_command('v.db.dropcolumn', map= 'Net_cat_F', columns = ['Area_m','Gridcode','GC'])
        grass.run_command('v.out.ogr', input = 'Cat_Lake_combined_F',output = os.path.join(self.tempfolder,'finalcatinfo_cat1.shp'),format= 'ESRI_Shapefile',overwrite = True,quiet = 'Ture')
        PERMANENT.close()
        
        QgsApplication.setPrefixPath(self.qgisPP, True)
        Qgs = QgsApplication([],False)
        Qgs.initQgis()
        from qgis import processing
        from processing.core.Processing import Processing
        from processing.tools import dataobjects
           
        feedback = QgsProcessingFeedback()
        Processing.initialize()
        QgsApplication.processingRegistry().addProvider(QgsNativeAlgorithms())
        context = dataobjects.createContext()
        context.setInvalidGeometryCheck(QgsFeatureRequest.GeometryNoCheck)
        processing.run("native:centroids", {'INPUT':os.path.join(self.tempfolder,'finalcatinfo_cat1.shp'),'ALL_PARTS':False,'OUTPUT':os.path.join(self.tempfolder,'Centerpoints2.shp')},context = context)
        processing.run("native:addxyfields", {'INPUT':os.path.join(self.tempfolder,'Centerpoints2.shp'),'CRS':QgsCoordinateReferenceSystem(self.SpRef_in),'OUTPUT':os.path.join(self.tempfolder,'ctwithxy2.shp')},context = context)
        processing.run("native:joinattributestable",{'INPUT':os.path.join(self.tempfolder,'finalcatinfo_cat1.shp'),'FIELD':'SubId','INPUT_2':os.path.join(self.tempfolder,'ctwithxy2.shp'),'FIELD_2':'SubId',
                          'FIELDS_TO_COPY':['x','y'],'METHOD':0,'DISCARD_NONMATCHING':False,'PREFIX':'centroid_','OUTPUT':os.path.join(self.OutputFolder,'finalcat_info.shp')},context = context)
        Qgs.exit()
             
###########################################################################3
    def Output_Clean(self,Out = 'Simple',clean = 'True',):
        
        import grass.script as grass
        from grass.script import array as garray
        import grass.script.setup as gsetup
        from grass.pygrass.modules.shortcuts import general as g
        from grass.pygrass.modules.shortcuts import raster as r
        from grass.pygrass.modules import Module
        from grass_session import Session

        os.environ.update(dict(GRASS_COMPRESS_NULLS='1',GRASS_COMPRESSOR='ZSTD',GRASS_VERBOSE='-1'))
        PERMANENT = Session()
        PERMANENT.open(gisdb=self.grassdb, location=self.grass_location_geo,create_opts=self.SpRef_in)
                
        if Out == 'Simple':
#            grass.run_command('v.out.ogr', input = 'finalcat_F',output = os.path.join(self.OutputFolder,'finalcat_info.shp'),format= 'ESRI_Shapefile',overwrite = True,quiet = 'Ture')
            grass.run_command('v.out.ogr', input = 'SelectedLakes_F',output = os.path.join(self.OutputFolder,'SelectedLakes.shp'),format= 'ESRI_Shapefile',overwrite = True,quiet = 'Ture')
#            grass.run_command('v.out.ogr', input = 'nstr_nfinalcat_F',output = os.path.join(self.OutputFolder,'finalriv_info.shp'),format= 'ESRI_Shapefile',overwrite = True,quiet = 'Ture')
#            grass.run_command('v.out.ogr', input = 'Cat_Lake_combined_F',output = os.path.join(self.OutputFolder,'finalcat_info.shp'),format= 'ESRI_Shapefile',overwrite = True,quiet = 'Ture')
            grass.run_command('v.out.ogr', input = 'Hylake',output = os.path.join(self.OutputFolder,'AllLakes.shp'),format= 'ESRI_Shapefile',overwrite = True,quiet = 'Ture')
            grass.run_command('v.out.ogr', input = 'obspoint',output = os.path.join(self.OutputFolder,'obspoint.shp'),format= 'ESRI_Shapefile',overwrite = True,quiet = 'Ture')
        if Out == 'All':
            grass.run_command('r.out.gdal', input = 'SelectedLakes',output = os.path.join(self.OutputFolder,'SelectedLakes.tif'),format= 'GTiff',overwrite = True,quiet = 'Ture')
        if clean == 'True':
            shutil.rmtree(self.grassdb,ignore_errors=True)
            shutil.rmtree(self.tempfolder,ignore_errors=True)


    def GenerateRavenInput(self,Finalcat_NM = 'finalcat_info',lenThres = 1,iscalmanningn = -1):
        
        if not os.path.exists(self.Raveinputsfolder):
            os.makedirs(self.Raveinputsfolder)

        finalcatchpath = os.path.join(self.OutputFolder,Finalcat_NM)
        
        tempinfo = Dbf5( finalcatchpath + ".dbf")#np.genfromtxt(hyinfocsv,delimiter=',')
        ncatinfo = tempinfo.to_dataframe()
        ncatinfo2 = ncatinfo.drop_duplicates('SubId', keep='first')
        Writervhchanl(ncatinfo2,self.Raveinputsfolder,lenThres,iscalmanningn)
        writelake(ncatinfo2,self.Raveinputsfolder)
        

    def selectpolygonsfromroutingproduct(self,Path_shpfile = '#',sub_colnm = 'SubId',down_colnm = 'DowSubId',mostdownid = -1,mostupstreamid = -1):
        
        if mostdownid == -1:
            import grass.script as grass
            from grass.script import array as garray
            import grass.script.setup as gsetup
            from grass.pygrass.modules.shortcuts import general as g
            from grass.pygrass.modules.shortcuts import raster as r
            from grass.pygrass.modules import Module
            from grass_session import Session
            os.environ.update(dict(GRASS_COMPRESS_NULLS='1',GRASS_COMPRESSOR='ZSTD',GRASS_VERBOSE='-1'))
            PERMANENT = Session()
            PERMANENT.open(gisdb=self.grassdb, location=self.grass_location_geo,create_opts=self.SpRef_in)

            finalcat_arr = garray.array(mapname="finalcat")
            acc_array = garray.array(mapname="acc_grass")
            obs_array = garray.array(mapname="obs")
            
            obsids = np.unique(obs_array)
            obsids = obsids[obsids>0]
            obsinfo = np.full((len(obsids),3),-9999)
        
            for i in range(0,len(obsids)):
                rowcol = np.argwhere(obs_array==obsids[i]).astype(int)
                obsinfo[i,0] = obsids[i]
                obsinfo[i,1] = finalcat_arr[rowcol[0,0],rowcol[0,1]]
                obsinfo[i,2] = acc_array[rowcol[0,0],rowcol[0,1]]
            
            obsinfo = obsinfo[obsinfo[:,2].argsort()].astype(int)
            mostdownid = obsinfo[len(obsinfo) - 1,1]

        QgsApplication.setPrefixPath(self.qgisPP, True)
        Qgs = QgsApplication([],False)
        Qgs.initQgis()
        from qgis import processing
        from processing.core.Processing import Processing   
        feedback = QgsProcessingFeedback()
        Processing.initialize()
        QgsApplication.processingRegistry().addProvider(QgsNativeAlgorithms())
        OutHyID = mostdownid
        OutHyID2 = mostupstreamid
        
        if Path_shpfile == '#':
            Path_shpfile = os.path.join(self.tempfolder,'finalcat_info2.shp')
        hyinfocsv = Path_shpfile[:-3] + "dbf"
        tempinfo = Dbf5(hyinfocsv)
        hyshdinfo2 = tempinfo.to_dataframe().drop_duplicates(sub_colnm, keep='first')
        hyshdinfo =  hyshdinfo2[[sub_colnm,down_colnm]].astype('float').values
    
        HydroBasins1 = Defcat(hyshdinfo,OutHyID) ### return fid of polygons that needs to be select 
        if OutHyID2 > 0:
            HydroBasins2 = Defcat(hyshdinfo,self.OutHyID2)            
    ###  exculde the Ids in HydroBasins2 from HydroBasins1
            for i in range(len(HydroBasins2)):
                rows =np.argwhere(HydroBasins1 == HydroBasins2[i])
                HydroBasins1 = np.delete(HydroBasins1, rows)
            HydroBasins = HydroBasins1            
        else:
            HydroBasins = HydroBasins1
    ### Load HydroSHED Layers 
        hyshedl12 = QgsVectorLayer(Path_shpfile, "")
        
        where_clause = '"SubId" IN'+ " ("
        for i in range(0,len(HydroBasins)):
            if i == 0:
                where_clause = where_clause + str(HydroBasins[i])
            else:
                where_clause = where_clause + "," + str(HydroBasins[i])
        where_clause = where_clause + ")"
    
        req = QgsFeatureRequest().setFlags( QgsFeatureRequest.NoGeometry )
        req.setFilterExpression(where_clause)
        it = hyshedl12.getFeatures( req )
        
        ### obtain all feature id of selected polygons
        selectedFeatureID = []
    
        for feature in it:
            selectedFeatureID.append(feature.id())
        
        hyshedl12.select(selectedFeatureID)   ### select with polygon id
        
        # Save selected polygons to output 
        _writer = QgsVectorFileWriter.writeAsVectorFormat(hyshedl12, os.path.join(self.OutputFolder,'finalcat_info.shp'), "UTF-8", hyshedl12.crs(), "ESRI Shapefile", onlySelected=True)
        del hyshedl12
        Qgs.exit()
        return 

        