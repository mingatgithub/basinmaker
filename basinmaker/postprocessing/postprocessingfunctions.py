def combine_catchments_covered_by_the_same_lake(
    OutputFolder="#",
    Path_final_rivply="#",
    Path_final_riv="#",
    qgis_prefix_path="#",
    gis_platform="qgis",
):

    if gis_platform == "qgis":
        assert (
            qgis_prefix_path != "#"
        ), "qgis prefix path is needed, when gis_platform = qgis"
        from postprocessing.combine import (
            combine_catchments_covered_by_the_same_lake_qgis,
        )

        combine_catchments_covered_by_the_same_lake_qgis(
            OutputFolder=OutputFolder,
            Path_final_rivply=Path_final_rivply,
            Path_final_riv=Path_final_riv,
            qgis_prefix_path=qgis_prefix_path,
        )


def simplify_routing_structure_by_filter_lakes(
    Path_final_riv_ply="#",
    Path_final_riv="#",
    Path_Con_Lake_ply="#",
    Path_NonCon_Lake_ply="#",
    Thres_Area_Conn_Lakes=-1,
    Thres_Area_Non_Conn_Lakes=-1,
    Selection_Method="ByArea",
    Selected_Lake_List_in=[],
    OutputFolder="#",
    qgis_prefix_path="#",
    gis_platform="qgis",
):

    if gis_platform == "qgis":
        assert (
            qgis_prefix_path != "#"
        ), "qgis prefix path is needed, when gis_platform = qgis"
        from postprocessing.selectlake import (
            simplify_routing_structure_by_filter_lakes_qgis,
        )

        simplify_routing_structure_by_filter_lakes_qgis(
            Path_final_riv_ply=Path_final_riv_ply,
            Path_final_riv=Path_final_riv,
            Path_Con_Lake_ply=Path_Con_Lake_ply,
            Path_NonCon_Lake_ply=Path_NonCon_Lake_ply,
            Thres_Area_Conn_Lakes=Thres_Area_Conn_Lakes,
            Thres_Area_Non_Conn_Lakes=Thres_Area_Non_Conn_Lakes,
            Selection_Method=Selection_Method,
            Selected_Lake_List_in=Selected_Lake_List_in,
            OutputFolder=OutputFolder,
            qgis_prefix_path=qgis_prefix_path,
            gis_platform=gis_platform,
        )


def simplify_routing_structure_by_drainage_area(
    Path_final_riv_ply="#",
    Path_final_riv="#",
    Path_Con_Lake_ply="#",
    Path_NonCon_Lake_ply="#",
    Area_Min=-1,
    OutputFolder="#",
    qgis_prefix_path="#",
    gis_platform="qgis",
):

    if gis_platform == "qgis":
        assert (
            qgis_prefix_path != "#"
        ), "qgis prefix path is needed, when gis_platform = qgis"
        from postprocessing.increaseda import (
            simplify_routing_structure_by_drainage_area_qgis,
        )

        simplify_routing_structure_by_drainage_area_qgis(
            Path_final_riv_ply=Path_final_riv_ply,
            Path_final_riv=Path_final_riv,
            Path_Con_Lake_ply=Path_Con_Lake_ply,
            Path_NonCon_Lake_ply=Path_NonCon_Lake_ply,
            Area_Min=Area_Min,
            OutputFolder=OutputFolder,
            qgis_prefix_path=qgis_prefix_path,
        )


def select_part_of_routing_product(
    Path_Points,
    Gauge_NMS,
    OutputFolder,
    Path_Catchment_Polygon="#",
    Path_River_Polyline="#",
    Path_Con_Lake_ply="#",
    Path_NonCon_Lake_ply="#",
    qgis_prefix_path="#",
    gis_platform = 'qgis'
):

    if gis_platform == 'qgis':
        from postprocessing.selectprod import (
            Locate_subid_needsbyuser_qgis,Select_Routing_product_based_SubId_qgis
        )

        subids = Locate_subid_needsbyuser_qgis(
            Path_Points=Path_Points, Gauge_NMS=Gauge_NMS, Path_products=Path_Catchment_Polygon,qgis_prefix_path=qgis_prefix_path
        )    
        if len(subids) > 1:
            for i in range(0,len(subids)):
                subid = subids[i]
                OutputFolder_i = os.path.join(OutputFolder,'SubId_'+str(subid))
                Select_Routing_product_based_SubId_qgis(
                    OutputFolder = OutputFolder_i,
                    Path_Catchment_Polygon=Path_Catchment_Polygon,
                    Path_River_Polyline=Path_River_Polyline,
                    Path_Con_Lake_ply=Path_Con_Lake_ply,
                    Path_NonCon_Lake_ply=Path_NonCon_Lake_ply,
                    mostdownid=subid,
                    qgis_prefix_path = qgis_prefix_path,
                )             
        else:
            Select_Routing_product_based_SubId_qgis(
                OutputFolder = OutputFolder,
                Path_Catchment_Polygon=Path_Catchment_Polygon,
                Path_River_Polyline=Path_River_Polyline,
                Path_Con_Lake_ply=Path_Con_Lake_ply,
                Path_NonCon_Lake_ply=Path_NonCon_Lake_ply,
                mostdownid=subids,
                qgis_prefix_path = qgis_prefix_path,
            )
        
    return 



def generate_hrus(
    Path_Subbasin_Ply,
    Landuse_info,
    Soil_info,
    Veg_info,
    Sub_Lake_ID="HyLakeId",
    Sub_ID="SubId",
    Path_Connect_Lake_ply="#",
    Path_Non_Connect_Lake_ply="#",
    Lake_Id="Hylak_id",
    Path_Landuse_Ply="#",
    Landuse_ID="Landuse_ID",
    Path_Soil_Ply="#",
    Soil_ID="Soil_ID",
    Path_Veg_Ply="#",
    Veg_ID="Veg_ID",
    Path_Other_Ply_1="#",
    Other_Ply_ID_1="O_ID_1",
    Path_Other_Ply_2="#",
    Other_Ply_ID_2="O_ID_2",
    DEM="#",
    Project_crs="EPSG:3573",
    OutputFolder="#",
    qgis_prefix_path='#',
    gis_platform='qgis',
):

    if gis_platform == 'qgis':
        from postprocessing.hru import (
            GenerateHRUS_qgis
        )
        GenerateHRUS_qgis(
            Path_Subbasin_Ply=Path_Subbasin_Ply,
            Landuse_info=Landuse_info,
            Soil_info=Soil_info,
            Veg_info=Veg_info,
            Sub_Lake_ID=Sub_Lake_ID,
            Sub_ID=Sub_ID,
            Path_Connect_Lake_ply=Path_Connect_Lake_ply,
            Path_Non_Connect_Lake_ply=Path_Non_Connect_Lake_ply,
            Lake_Id=Lake_Id,
            Path_Landuse_Ply=Path_Landuse_Ply,
            Landuse_ID=Landuse_ID,
            Path_Soil_Ply=Path_Soil_Ply,
            Soil_ID=Soil_ID,
            Path_Veg_Ply=Path_Veg_Ply,
            Veg_ID=Veg_ID,
            Path_Other_Ply_1=Path_Other_Ply_1,
            Other_Ply_ID_1=Other_Ply_ID_1,
            Path_Other_Ply_2=Path_Other_Ply_2,
            Other_Ply_ID_2=Other_Ply_ID_2,
            DEM=DEM,
            Project_crs=Project_crs,
            OutputFolder=OutputFolder,
            qgis_prefix_path=qgis_prefix_path,
        )        
        
    return 
    
    