from basinmaker.func.grassgis import *
from basinmaker.func.qgis import *
from basinmaker.func.pdtable import *
from basinmaker.func.rarray import *
from basinmaker.utilities.utilities import *
import os
from processing.core.Processing import Processing
from processing.tools import dataobjects
from qgis import processing

def obtain_polygon_boundary(grassdb, qgis_prefix_path, ply_path, output,ply_name):
    QgsApplication.setPrefixPath(qgis_prefix_path, True)
    Qgs = QgsApplication([], False)
    Qgs.initQgis()

    feedback = QgsProcessingFeedback()
    Processing.initialize()
    QgsApplication.processingRegistry().addProvider(QgsNativeAlgorithms())
    context = dataobjects.createContext()
    context.setInvalidGeometryCheck(QgsFeatureRequest.GeometryNoCheck)

    # obtain lake boundary lines
    qgis_vector_polygon_stro_lines(
            processing,
            context,
            INPUT=ply_path,
            OUTPUT=output,
        )
    qgis_vector_reproject_layers(
        processing,
        context,
        INPUT=output,
        TARGET_CRS=GEO_EPSG_CRS_AUTHID,
        OUTPUT=os.path.join(grassdb, ply_name + ".shp")
        )
    Qgs.exit()


def reproject_clip_vectors_by_polygon(
    grassdb, grass_location, qgis_prefix_path, mask, path_polygon, ply_name
):

    QgsApplication.setPrefixPath(qgis_prefix_path, True)
    Qgs = QgsApplication([], False)
    Qgs.initQgis()
    from processing.core.Processing import Processing
    from processing.tools import dataobjects
    from qgis import processing

    feedback = QgsProcessingFeedback()
    Processing.initialize()
    QgsApplication.processingRegistry().addProvider(QgsNativeAlgorithms())
    context = dataobjects.createContext()
    context.setInvalidGeometryCheck(QgsFeatureRequest.GeometryNoCheck)

    # extract lake for target location first
    try:
        qgis_vector_ectract_by_location(
            processing,
            context,
            INPUT=path_polygon,
            INTERSECT=mask,
            OUTPUT=os.path.join(grassdb, ply_name + "_temp.shp"),
        )
        if ply_name == 'kc_zone':
            processing.run("native:clip", {
                           'INPUT':os.path.join(grassdb, ply_name + "_project.shp"),
                           'OVERLAY':mask,
                           'OUTPUT':os.path.join(grassdb, ply_name + "_clip.shp")})

    except:
        print("Need fix lake boundary geometry to speed up")
        qgis_vector_fix_geometries(
            processing,
            context,
            INPUT=os.path.join(grassdb, ply_name + "_project.shp"),
            OUTPUT=os.path.join(grassdb, ply_name + "_fixgeo.shp"),
        )
        qgis_vector_fix_geometries(
            processing,
            context,
            INPUT=mask,
            OUTPUT=os.path.join(grassdb, "mask_fixgeo.shp"),
        )
        
        qgis_vector_ectract_by_location(
            processing,
            context,
            INPUT=os.path.join(grassdb, ply_name + "_fixgeo.shp"),
            INTERSECT=os.path.join(grassdb, "mask_fixgeo.shp"),
            OUTPUT=os.path.join(grassdb, ply_name + ".shp"),
        )

        if ply_name == 'kc_zone':
            processing.run("native:clip", {
                           'INPUT':os.path.join(grassdb, ply_name + "_fixgeo.shp"),
                           'OVERLAY':os.path.join(grassdb, "mask_fixgeo.shp"),
                           'OUTPUT':os.path.join(grassdb, ply_name + "_clip.shp")})
            

    # crs_id = qgis_vector_return_crs_id(
    #     processing, context, mask, Input_Is_Feature_In_Mem=False
    # )
    crs_id = GEO_EPSG_CRS_AUTHID

    qgis_vector_reproject_layers(
        processing,
        context,
        INPUT=os.path.join(grassdb, ply_name + "_temp.shp"),
        TARGET_CRS=crs_id,
        OUTPUT=os.path.join(grassdb, ply_name + ".shp"),
    )
    # lake polygon sometime has error in geometry
                       
    Qgs.exit()
