import os
import shutil

import pandas as pd
import pytest
from simpledbf import Dbf5

from ToolboxClass import LRRT


def Dbf_To_Dataframe(file_path):
    """Transfer an input dbf file to dataframe

    Parameters
    ----------
    file_path   : string
    Full path to a shapefile

    Returns:
    -------
    dataframe   : datafame
    a pandas dataframe of attribute table of input shapefile
    """
    tempinfo = Dbf5(file_path[:-3] + "dbf")
    dataframe = tempinfo.to_dataframe()
    return dataframe


def test_Select_Routing_product_based_SubId():
    """test function that will:

    Function that used to obtain the region of interest from routing
    product based on given SubId

    """

    ###Floder where store the inputs for tests function
    Routing_Product_Folder = "./testdata/Routing_product_V2/"
    ###Folder where store the expected resuts
    Expect_Result_Folder = os.path.join("./testdata", "02LE024")
    ###Folder where the output will be generated
    Output_Folder = os.path.join("./testdata", "test_out10")

    ###Define path of input dataset

    ###The lake polygons
    Path_Con_Lake_ply = os.path.join(
        Routing_Product_Folder, "Con_Lake_Ply.shp"
    )  ### Connected lake polygons
    Path_NonCon_Lake_ply = os.path.join(
        Routing_Product_Folder, "Non_Con_Lake_Ply.shp"
    )  ### None connected lake polygons
    ###product that need futher process
    Path_final_riv_ply = os.path.join(
        Routing_Product_Folder, "finalriv_info_ply.shp"
    )  ### River polyline
    Path_final_riv = os.path.join(
        Routing_Product_Folder, "finalriv_info.shp"
    )  ### Catchment polygons
    ###product that do not need need futher process
    Path_final_cat_ply = os.path.join(
        Routing_Product_Folder, "finalcat_info.shp"
    )  ### catchment polygons
    Path_final_cat_riv = os.path.join(
        Routing_Product_Folder, "finalcat_info_riv.shp"
    )  ### CRiver polyline

    ###Generate test resuts
    RTtool = LRRT()
    ### extract product that do not need further process
    RTtool.Select_Routing_product_based_SubId(
        OutputFolder=Output_Folder,
        Path_Catchment_Polygon=Path_final_cat_ply,
        Path_River_Polyline=Path_final_cat_riv,
        Path_Con_Lake_ply=Path_Con_Lake_ply,
        Path_NonCon_Lake_ply=Path_NonCon_Lake_ply,
        mostdownid=1024,
    )
    ### extract product that need further process
    subids = RTtool.Select_Routing_product_based_SubId(
        OutputFolder=Output_Folder,
        Path_Catchment_Polygon=Path_final_riv_ply,
        Path_River_Polyline=Path_final_riv,
        mostdownid=1024,
    )

    """Evaluate extracted shapefiles by comparing attribute table
    following shapefiles will be generated by above two commands 
    
    'finalcat_info.shp' is the catchment polygons that do not need further process 
    'finalcat_info_riv.shp' is the river network polyline that do not need further process 
    
    'finalriv_info_ply.shp' is the catchment polygons that need further process 
    'finalriv_info.shp' is the river network polylin that need further process 
    
    'Con_Lake_Ply.shp' is the connected lake polygons 
    'Non_Con_Lake_Ply.shp' is non-connected lake polygons 
    """

    ### transfer resulted catchment polygon that do not need further process into pandas dataframe:Result_Finalcat_info
    Result_Finalcat_info = Dbf_To_Dataframe(
        os.path.join(Output_Folder, "finalcat_info.shp")
    )
    ### transfer resulted river network polyline that do not need further process into pandas dataframe:Result_Finalcat_riv_info
    Result_Finalcat_riv_info = Dbf_To_Dataframe(
        os.path.join(Output_Folder, "finalcat_info_riv.shp")
    )
    ### transfer resulted catchment polygon that need further process into pandas dataframe:Result_Finalriv_info_ply
    Result_Finalriv_info_ply = Dbf_To_Dataframe(
        os.path.join(Output_Folder, "finalriv_info_ply.shp")
    )
    ### transfer resulted river network polyline that need further process into pandas dataframe:Result_Finalcat_riv_info
    Result_Finalriv_info = Dbf_To_Dataframe(
        os.path.join(Output_Folder, "finalriv_info.shp")
    )
    ### transfer resulted connected lake polygon into pandas dataframe Result_Con_Lake_Ply
    Result_Con_Lake_Ply = Dbf_To_Dataframe(
        os.path.join(Output_Folder, "Con_Lake_Ply.shp")
    )
    ### transfer resulted non-connected lake polygon into pandas dataframe Result_Non_Con_Lake_Ply
    Result_Non_Con_Lake_Ply = Dbf_To_Dataframe(
        os.path.join(Output_Folder, "Non_Con_Lake_Ply.shp")
    )

    ### transfer Expect catchment polygon that do not need further process into pandas dataframe:Expect_Finalcat_info
    Expect_Finalcat_info = Dbf_To_Dataframe(
        os.path.join(Expect_Result_Folder, "finalcat_info.shp")
    )
    ### transfer Expect river network polyline that do not need further process into pandas dataframe:Expect_Finalcat_riv_info
    Expect_Finalcat_riv_info = Dbf_To_Dataframe(
        os.path.join(Expect_Result_Folder, "finalcat_info_riv.shp")
    )
    ### transfer Expect catchment polygon that need further process into pandas dataframe:Expect_Finalriv_info_ply
    Expect_Finalriv_info_ply = Dbf_To_Dataframe(
        os.path.join(Expect_Result_Folder, "finalriv_info_ply.shp")
    )
    ### transfer Expect river network polyline that need further process into pandas dataframe:Expect_Finalriv_info
    Expect_Finalriv_info = Dbf_To_Dataframe(
        os.path.join(Expect_Result_Folder, "finalriv_info.shp")
    )
    ### transfer Expect connected lake polygon into pandas dataframe Expect_Con_Lake_Ply
    Expect_Con_Lake_Ply = Dbf_To_Dataframe(
        os.path.join(Expect_Result_Folder, "Con_Lake_Ply.shp")
    )
    ### transfer Expect non-connected lake polygon into pandas dataframe Expect_Non_Con_Lake_Ply
    Expect_Non_Con_Lake_Ply = Dbf_To_Dataframe(
        os.path.join(Expect_Result_Folder, "Non_Con_Lake_Ply.shp")
    )

    ### compare two pd dataframe Result_Finalcat_info and  Expect_Finalcat_info
    assert Result_Finalcat_info.equals(Expect_Finalcat_info)
    ### compare two pd dataframe Result_Finalcat_riv_info and  Expect_Finalcat_riv_info
    assert Result_Finalcat_riv_info.equals(Expect_Finalcat_riv_info)
    ### compare two pd dataframe Result_Finalriv_info_ply and  Expect_Finalriv_info_ply
    assert Result_Finalriv_info_ply.equals(Expect_Finalriv_info_ply)
    ### compare two pd dataframe Result_Finalriv_info and  Expect_Finalriv_info
    assert Result_Finalriv_info.equals(Expect_Finalriv_info)
    ### compare two pd dataframe Result_Con_Lake_Ply and  Expect_Con_Lake_Ply
    assert Result_Con_Lake_Ply.equals(Expect_Con_Lake_Ply)
    ### compare two pd dataframe Result_Non_Con_Lake_Ply and  Expect_Non_Con_Lake_Ply
    assert Result_Non_Con_Lake_Ply.equals(Expect_Non_Con_Lake_Ply)

    shutil.rmtree(Output_Folder)
