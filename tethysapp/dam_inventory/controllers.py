from django.shortcuts import render, reverse, redirect
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from tethys_sdk.gizmos import MapView, Button, TextInput, DatePicker, SelectInput, DataTableView, MVDraw, MVLegendClass, MVLegendGeoServerImageClass, MVLegendImageClass, MVView, MVLayer, EMView, EMLayer, ESRIMap 

from .model import add_new_dam, get_all_dams

###########################################################################
@login_required()
def home(request):
    """
    Controller for the app home page.
    """
    # Get list of dams and create dams MVLayer:
    dams = get_all_dams()
    features = []
    lat_list = []
    lng_list = []

    # Define a GeoJSON Features
    for dam in dams:
        dam_location = dam.pop('location')
        lat_list.append(dam_location['coordinates'][1])
        lng_list.append(dam_location['coordinates'][0])

        dam_feature = {
            'type': 'Feature',
            'geometry': {
                'type': dam_location['type'],
                'coordinates': dam_location['coordinates'],
            }
        }

        features.append(dam_feature)

    # Define GeoJSON FeatureCollection
    dams_feature_collection = {
        'type': 'FeatureCollection',
        'crs': {
            'type': 'name',
            'properties': {
                'name': 'EPSG:4326'
            }
        },
        'features': features
    }

    # Create a Map View Layer
    dams_layer = MVLayer(
        source='GeoJSON',
        options=dams_feature_collection,
        legend_title='Dams',
        layer_options={
            'style': {
                'image': {
                    'circle': {
                        'radius': 10,
                        'fill': {'color':  '#d84e1f'},
                        'stroke': {'color': '#ffffff', 'width': 1},
                    }
                }
            }
        }
    )

    # Define view centered on dam locations
    try:
        view_center = [sum(lng_list) / float(len(lng_list)), sum(lat_list) / float(len(lat_list))]
    except ZeroDivisionError:
        view_center = [-98.6, 39.8]
        
    view_center = [-105.6, 39.0]
    view_options = MVView(
        projection='EPSG:4326',
        center=view_center,
        zoom=5.5,
        maxZoom=18,
        minZoom=5
    )

    dam_inventory_map = MapView(
        height='100%',
        width='100%',
        layers=[dams_layer],
         basemap=['OpenStreetMap',
            {'OpenStreetMap': {'url': 'http://tile.stamen.com/watercolor/{z}/{x}/{y}.jpg',
                               'label': 'Watercolor'}
             }],
        view=view_options
    )

    add_dam_button = Button(
        display_text='Add Dam',
        name='add-dam-button',
        icon='glyphicon glyphicon-plus',
        style='success',
        href=reverse('dam_inventory:add_dam')
    )
    
    #ESRI Map Gizmo
    esri_map_view = EMView(center=[-100, 40], zoom=4)
    esri_layer = EMLayer(type='FeatureLayer',
                         url='http://geoserver.byu.edu/arcgis/rest/services/gaugeviewer/AHPS_gauges/MapServer/0')

    vector_tile = EMLayer(type='ImageryLayer',
                          url='https://sampleserver6.arcgisonline.com/arcgis/rest/services/NLCDLandCover2001/ImageServer')

    esri_map = ESRIMap(height='650px', width='100%', basemap='topo', view=esri_map_view,
                       layers=[vector_tile, esri_layer])
                       
    ##### WMS Layer Testing - Ryan
    usdm_legend = MVLegendImageClass(value='Drought Category',
                             image_url='http://ndmc-001.unl.edu:8080/cgi-bin/mapserv.exe?map=/ms4w/apps/usdm/service/usdm_current_wms.map&version=1.3.0&service=WMS&request=GetLegendGraphic&sld_version=1.1.0&layer=usdm_current&format=image/png&STYLE=default')
    usdm_current = MVLayer(
            source='ImageWMS',
            options={'url': 'http://ndmc-001.unl.edu:8080/cgi-bin/mapserv.exe?map=/ms4w/apps/usdm/service/usdm_current_wms.map&',
                     'params': {'LAYERS':'usdm_current','FORMAT':'image/png'},
                   'serverType': 'geoserver'},
            layer_options={'opacity':0.5},
            legend_title='USDM',
            legend_classes=[usdm_legend],
            legend_extent=[-126, 24.5, -66.2, 49])
            
#    usdm_current = MVLayer(
#            source='KML',
#            options={'url': 'http://ndmc-001.unl.edu:8080/cgi-bin/mapserv.exe?map=/ms4w/apps/usdm/service/usdm_current_wms.map&',
#                     'params': {'LAYERS':'usdm_current','FORMAT':'application/vnd.google-earth.kml+xml'}},
#            layer_options={'opacity':0.5},
#            legend_title='USDM',
#            legend_extent=[-126, 24.5, -66.2, 49])

    ww_legend = MVLegendImageClass(value='Current Streamflow',
                             image_url='https://edcintl.cr.usgs.gov/geoserver/qdriwaterwatchshapefile/ows?service=WMS&request=GetLegendGraphic&format=image%2Fpng&width=20&height=20&layer=water_watch_today')   
    water_watch = MVLayer(
            source='ImageWMS',
            options={'url': 'https://edcintl.cr.usgs.gov/geoserver/qdriwaterwatchshapefile/wms?',
                     'params': {'LAYERS': 'water_watch_today'},
                   'serverType': 'geoserver'},
            layer_options={'opacity':0.5},
            legend_title='USGS Water Watch',
            legend_classes=[ww_legend],
            legend_extent=[-126, 24.5, -66.2, 49])

    prec7_legend = MVLegendImageClass(value='7-day Precip',
                         image_url='https://vegdri.cr.usgs.gov/wms.php?service=WMS&request=GetLegendGraphic&format=image%2Fpng&width=20&height=20&LAYER=PRECIP_TP7')   
    precip7day = MVLayer(
            source='ImageWMS',
            options={'url': 'https://vegdri.cr.usgs.gov/wms.php?',
                     'params': {'LAYERS': 'PRECIP_TP7'},
                   'serverType': 'geoserver'},
            layer_options={'visible':False,'opacity':0.5},
            legend_title='7-day Precip',
            legend_classes=[prec7_legend],
            legend_extent=[-126, 24.5, -66.2, 49])
            
    vdri_legend = MVLegendImageClass(value='VegDRI Cat',
                     image_url='https://vegdri.cr.usgs.gov/wms.php?service=WMS&request=GetLegendGraphic&format=image%2Fpng&width=20&height=20&LAYER=DROUGHT_VDRI_EMODIS_1')   
    vegdri = MVLayer(
            source='ImageWMS',
            options={'url': 'https://vegdri.cr.usgs.gov/wms.php?',
                     'params': {'LAYERS': 'DROUGHT_VDRI_EMODIS_1'},
                   'serverType': 'geoserver'},
            layer_options={'visible':False,'opacity':0.5},
            legend_title='VegDRI',
            legend_classes=[vdri_legend],
            legend_extent=[-126, 24.5, -66.2, 49])
            # historical layers https://edcintl.cr.usgs.gov/geoserver/qdrivegdriemodis/wms?', 'params': {'LAYERS': 'qdrivegdriemodis_pd_1-sevenday-53-2017_mm_data'

    qdri_legend = MVLegendImageClass(value='QuickDRI Cat',
                     image_url='https://vegdri.cr.usgs.gov/wms.php?service=WMS&request=GetLegendGraphic&format=image%2Fpng&width=20&height=20&LAYER=DROUGHT_QDRI_EMODIS_1')   
    quickdri = MVLayer(
            source='ImageWMS',
            options={'url': 'https://vegdri.cr.usgs.gov/wms.php?',
                     'params': {'LAYERS': 'DROUGHT_QDRI_EMODIS_1'},
                   'serverType': 'geoserver'},
            layer_options={'visible':False,'opacity':0.5},
            legend_title='QuickDRI',
            legend_classes=[qdri_legend],
            legend_extent=[-126, 24.5, -66.2, 49])
            # historical layers: https://edcintl.cr.usgs.gov/geoserver/qdriquickdriraster/wms?', 'params': {'LAYERS': 'qdriquickdriraster_pd_1-sevenday-53-2017_mm_data'
    
    # USGS Rest server for HUC watersheds        
    watersheds = MVLayer(
        source='TileArcGISRest',
        options={'url': 'https://services.nationalmap.gov/arcgis/rest/services/wbd/MapServer'},
        legend_title='HUC Watersheds',
        layer_options={'visible':True,'opacity':0.4},
        legend_extent=[-112, 36.3, -98.5, 41.66])
    
#    # SWSI Rest server        
#    swsi = MVLayer(
#        source='TileArcGISRest',
#        options={'url': 'https://www.coloradodnr.info/Geocortex/Essentials/GCE4/REST/sites/DWR_HydroBase/map/mapservices/109/GeoREST/MapServer',
#                 'params': {'FORMAT': 'png8'}},
#        legend_title='SWSI',
#        layer_options={'visible':True,'opacity':0.4},
#        legend_extent=[-112, 36.3, -98.5, 41.66])
        
    # Define map view options
    map_view_options = MapView(
            height='630px',
            width='70%',
            controls=['ZoomSlider', 'Rotate', 'FullScreen',
                      {'MousePosition': {'projection': 'EPSG:4326'}},
                      {'ZoomToExtent': {'projection': 'EPSG:4326', 'extent': [-130, 22, -65, 54]}}],
            layers=[water_watch,usdm_current,precip7day,vegdri,quickdri,watersheds],
            view=view_options,
            basemap='OpenStreetMap',
            legend=True
        )

    context = {
        'dam_inventory_map': dam_inventory_map,
        'add_dam_button': add_dam_button,
        'esri_map':esri_map,
        'map_view_options':map_view_options,
    }

    return render(request, 'dam_inventory/home.html', context)
############################## Drought Map Main ############################################
@login_required()
def drought_map(request):
    """
    Controller for the app drought map page.
    """
           
    view_center = [-105.6, 39.0]
    view_options = MVView(
        projection='EPSG:4326',
        center=view_center,
        zoom=7.0,
        maxZoom=12,
        minZoom=5
    )

    # TIGER state/county mapserver
    tiger_boundaries = MVLayer(
        source='TileArcGISRest',
        options={'url': 'https://tigerweb.geo.census.gov/arcgis/rest/services/TIGERweb/State_County/MapServer'},
        legend_title='State Boundaries',
        layer_options={'visible':True,'opacity':0.8},
        legend_extent=[-112, 36.3, -98.5, 41.66])    
    
    ##### WMS Layers - Ryan
    usdm_legend = MVLegendImageClass(value='Drought Category',
                             image_url='http://ndmc-001.unl.edu:8080/cgi-bin/mapserv.exe?map=/ms4w/apps/usdm/service/usdm_current_wms.map&version=1.3.0&service=WMS&request=GetLegendGraphic&sld_version=1.1.0&layer=usdm_current&format=image/png&STYLE=default')
    usdm_current = MVLayer(
            source='ImageWMS',
            options={'url': 'http://ndmc-001.unl.edu:8080/cgi-bin/mapserv.exe?map=/ms4w/apps/usdm/service/usdm_current_wms.map&',
                     'params': {'LAYERS':'usdm_current','FORMAT':'image/png'},
                   'serverType': 'geoserver'},
            layer_options={'opacity':0.5},
            legend_title='USDM',
            legend_classes=[usdm_legend],
            legend_extent=[-126, 24.5, -66.2, 49])
            
    usdm_kml = MVLayer(
        source='KML',
        options={'url': '/static/tethys_gizmos/data/usdm_current.kml'},
        layer_options={'visible':False,'opacity':0.5},
        legend_title='USDM',
        legend_classes=[usdm_legend],
        legend_extent=[-126, 24.5, -66.2, 49])

    ww_legend = MVLegendImageClass(value='Current Streamflow',
                             image_url='https://edcintl.cr.usgs.gov/geoserver/qdriwaterwatchshapefile/ows?service=WMS&request=GetLegendGraphic&format=image%2Fpng&width=20&height=20&layer=water_watch_today')   
    water_watch = MVLayer(
            source='ImageWMS',
            options={'url': 'https://edcintl.cr.usgs.gov/geoserver/qdriwaterwatchshapefile/wms?',
                     'params': {'LAYERS': 'water_watch_today'},
                   'serverType': 'geoserver'},
            layer_options={'opacity':0.5},
            legend_title='USGS Water Watch',
            legend_classes=[ww_legend],
            legend_extent=[-126, 24.5, -66.2, 49])

    prec7_legend = MVLegendImageClass(value='7-day Precip Total',
                         image_url='https://vegdri.cr.usgs.gov/wms.php?service=WMS&request=GetLegendGraphic&format=image%2Fpng&width=20&height=20&LAYER=PRECIP_TP7')   
    precip7day = MVLayer(
            source='ImageWMS',
            options={'url': 'https://vegdri.cr.usgs.gov/wms.php?',
                     'params': {'LAYERS': 'PRECIP_TP7'},
                   'serverType': 'geoserver'},
            layer_options={'visible':False,'opacity':0.5},
            legend_title='7-day Precip',
            legend_classes=[prec7_legend],
            legend_extent=[-126, 24.5, -66.2, 49])
            
    vdri_legend = MVLegendImageClass(value='VegDRI Cat',
                     image_url='https://vegdri.cr.usgs.gov/wms.php?service=WMS&request=GetLegendGraphic&format=image%2Fpng&width=20&height=20&LAYER=DROUGHT_VDRI_EMODIS_1')   
    vegdri = MVLayer(
            source='ImageWMS',
            options={'url': 'https://vegdri.cr.usgs.gov/wms.php?',
                     'params': {'LAYERS': 'DROUGHT_VDRI_EMODIS_1'},
                   'serverType': 'geoserver'},
            layer_options={'visible':False,'opacity':0.5},
            legend_title='VegDRI',
            legend_classes=[vdri_legend],
            legend_extent=[-126, 24.5, -66.2, 49])
            # historical layers https://edcintl.cr.usgs.gov/geoserver/qdrivegdriemodis/wms?', 'params': {'LAYERS': 'qdrivegdriemodis_pd_1-sevenday-53-2017_mm_data'

    qdri_legend = MVLegendImageClass(value='QuickDRI Cat',
                     image_url='https://vegdri.cr.usgs.gov/wms.php?service=WMS&request=GetLegendGraphic&format=image%2Fpng&width=20&height=20&LAYER=DROUGHT_QDRI_EMODIS_1')   
    quickdri = MVLayer(
            source='ImageWMS',
            options={'url': 'https://vegdri.cr.usgs.gov/wms.php?',
                     'params': {'LAYERS': 'DROUGHT_QDRI_EMODIS_1'},
                   'serverType': 'geoserver'},
            layer_options={'visible':False,'opacity':0.5},
            legend_title='QuickDRI',
            legend_classes=[qdri_legend],
            legend_extent=[-126, 24.5, -66.2, 49])
            # historical layers: https://edcintl.cr.usgs.gov/geoserver/qdriquickdriraster/wms?', 'params': {'LAYERS': 'qdriquickdriraster_pd_1-sevenday-53-2017_mm_data'
    
    # USGS Rest server for HUC watersheds        
    watersheds = MVLayer(
        source='TileArcGISRest',
        options={'url': 'https://services.nationalmap.gov/arcgis/rest/services/wbd/MapServer'},
        legend_title='HUC Watersheds',
        layer_options={'visible':False,'opacity':0.4},
        legend_extent=[-112, 36.3, -98.5, 41.66])

    # Define SWSI KML Layer
    SWSI_kml = MVLayer(
        source='KML',
        options={'url': '/static/tethys_gizmos/data/SWSI_2017Dec.kml'},
        legend_title='SWSI',
        layer_options={'visible':False,'opacity':0.7},
        feature_selection=True,
        legend_extent=[-110, 36, -101.5, 41.6])
    
    # NOAA Rest server for NWM streamflow      
    nwm_stream = MVLayer(
        source='TileArcGISRest',
        options={'url': 'https://mapservice.nohrsc.noaa.gov/arcgis/rest/services/national_water_model/NWM_Stream_Analysis/MapServer',
                'params': {'LAYERS': 'show:1,2,3,4,5,12'}},
        legend_title='NWM Streamflow',
        layer_options={'visible':False,'opacity':1.0},
        legend_extent=[-112, 36.3, -98.5, 41.66])
    nwm_stream_anom = MVLayer(
        source='TileArcGISRest',
        options={'url': 'https://mapservice.nohrsc.noaa.gov/arcgis/rest/services/national_water_model/NWM_Stream_Analysis/MapServer',
                'params': {'LAYERS': 'show:7,8,9,10,11,12'}},
        legend_title='NWM Flow Anomoly',
        layer_options={'visible':True,'opacity':1.0},
        legend_extent=[-112, 36.3, -98.5, 41.66])
        
    # NOAA NOHRSC snow products
    snodas_swe = MVLayer(
        source='TileArcGISRest',
        options={'url': 'https://idpgis.ncep.noaa.gov/arcgis/rest/services/NWS_Observations/NOHRSC_Snow_Analysis/MapServer',
                'params': {'LAYERS': 'show:7'}},
        legend_title='SNODAS Model SWE (in)',
        layer_options={'visible':True,'opacity':0.7},
        legend_extent=[-112, 36.3, -98.5, 41.66])

    # NOAA Rest server for NWM soil moisture
    nwm_soil_legend = MVLegendGeoServerImageClass(value='test', style='green', layer='rivers',
                         geoserver_url='https://mapservice.nohrsc.noaa.gov/arcgis/rest/services/national_water_model/NWM_Land_Analysis/MapServer/legend?f=pjson')   
    nwm_soil = MVLayer(
        source='TileArcGISRest',
        options={'url': 'https://mapservice.nohrsc.noaa.gov/arcgis/rest/services/national_water_model/NWM_Land_Analysis/MapServer'},
        legend_title='NWM Soil Moisture',
        layer_options={'visible':False,'opacity':0.5},
        legend_classes=[nwm_soil_legend],
        legend_extent=[-112, 36.3, -98.5, 41.66])
        
#    SWSI_json = MVLayer(
#        source='GeoJSON',
#        options={'url': '/static/tethys_gizmos/data/SWSI_2017Dec.geojson', 'featureProjection': 'EPSG:3857'},
#        legend_title='SWSI',
#        layer_options={'visible':True,'opacity':0.4},
#        feature_selection=True,
#        legend_extent=[-110, 36, -101.5, 41.6])  
        
    # Define map view options
    drought_map_view_options = MapView(
            height='630px',
            width='100%',
            controls=['ZoomSlider', 'Rotate', 'FullScreen',
                      {'MousePosition': {'projection': 'EPSG:4326'}},
                      {'ZoomToExtent': {'projection': 'EPSG:4326', 'extent': [-130, 22, -65, 54]}}],
            layers=[tiger_boundaries,nwm_stream,nwm_stream_anom,nwm_soil,snodas_swe,water_watch,SWSI_kml,usdm_kml,precip7day,vegdri,quickdri,watersheds],
            view=view_options,
            basemap='OpenStreetMap',
            legend=True
        )

    context = {
        'drought_map_view_options':drought_map_view_options,
    }

    return render(request, 'dam_inventory/drought.html', context)
##################### End Drought Main Map #############################################
##################### Start Drought Map - Forecast #############################################
@login_required()
def drought_map_forecast(request):
    """
    Controller for the app drought map page.
    """
           
    view_center = [-105.6, 39.0]
    view_options = MVView(
        projection='EPSG:4326',
        center=view_center,
        zoom=7.0,
        maxZoom=12,
        minZoom=5
    )

    # TIGER state/county mapserver
    tiger_boundaries = MVLayer(
        source='TileArcGISRest',
        options={'url': 'https://tigerweb.geo.census.gov/arcgis/rest/services/TIGERweb/State_County/MapServer'},
        legend_title='State Boundaries',
        layer_options={'visible':True,'opacity':0.8},
        legend_extent=[-112, 36.3, -98.5, 41.66])    
    
    # USGS Rest server for HUC watersheds        
    watersheds = MVLayer(
        source='TileArcGISRest',
        options={'url': 'https://services.nationalmap.gov/arcgis/rest/services/wbd/MapServer'},
        legend_title='HUC Watersheds',
        layer_options={'visible':False,'opacity':0.4},
        legend_extent=[-112, 36.3, -98.5, 41.66])

    # NOAA Rest server for NWM streamflow      
    nwm_stream = MVLayer(
        source='TileArcGISRest',
        options={'url': 'https://mapservice.nohrsc.noaa.gov/arcgis/rest/services/national_water_model/NWM_Stream_Analysis/MapServer',
                'params': {'LAYERS': 'show:1,2,3,4,5,12'}},
        legend_title='NWM Streamflow',
        layer_options={'visible':False,'opacity':1.0},
        legend_classes=[
            MVLegendClass('line', '> 1.25M', stroke='rgba(75,0,115,0.9)'),
            MVLegendClass('line', '500K - 1.25M', stroke='rgba(176,28,232,0.9)'),
            MVLegendClass('line', '100K - 500K', stroke='rgba(246,82,213,0.9)'),
            MVLegendClass('line', '50K - 100K', stroke='rgba(254,7,7,0.9)'),
            MVLegendClass('line', '25K - 50K', stroke='rgba(252,138,23,0.9)'),
            MVLegendClass('line', '10K - 25K', stroke='rgba(45,108,183,0.9)'),
            MVLegendClass('line', '5K - 10K', stroke='rgba(27,127,254,0.9)'),
            MVLegendClass('line', '2.5K - 5K', stroke='rgba(79,169,195,0.9)'),
            MVLegendClass('line', '250 - 2.5K', stroke='rgba(122,219,250,0.9)'),
            MVLegendClass('line', '0 - 250', stroke='rgba(206,222,251,0.9)'),
            MVLegendClass('line', 'No Data', stroke='rgba(195,199,201,0.9)')],
        legend_extent=[-112, 36.3, -98.5, 41.66])
    nwm_stream_anom = MVLayer(
        source='TileArcGISRest',
        options={'url': 'https://mapservice.nohrsc.noaa.gov/arcgis/rest/services/national_water_model/NWM_Stream_Analysis/MapServer',
                'params': {'LAYERS': 'show:7,8,9,10,11,12'}},
        legend_title='NWM Flow Anomoly',
        layer_options={'visible':True,'opacity':1.0},
        legend_classes=[
            MVLegendClass('line', 'High', stroke='rgba(176,28,232,0.9)'),
            MVLegendClass('line', '', stroke='rgba(61,46,231,0.9)'),
            MVLegendClass('line', '', stroke='rgba(52,231,181,0.9)'),
            MVLegendClass('line', 'Moderate', stroke='rgba(102,218,148,0.9)'),
            MVLegendClass('line', '', stroke='rgba(241,156,77,0.9)'),
            MVLegendClass('line', '', stroke='rgba(175,62,44,0.9)'),
            MVLegendClass('line', 'Low', stroke='rgba(241,42,90,0.9)'),
            MVLegendClass('line', 'No Data', stroke='rgba(195,199,201,0.9)')],
        legend_extent=[-112, 36.3, -98.5, 41.66])

    # NOAA Rest server for NWM soil moisture
    nwm_soil_legend = MVLegendGeoServerImageClass(value='test', style='green', layer='NWM_Land_Analysis',
                         geoserver_url='https://mapservice.nohrsc.noaa.gov/arcgis/rest/services/national_water_model/NWM_Land_Analysis/MapServer/legend?f=pjson')   
    nwm_soil = MVLayer(
        source='TileArcGISRest',
        options={'url': 'https://mapservice.nohrsc.noaa.gov/arcgis/rest/services/national_water_model/NWM_Land_Analysis/MapServer'},
        legend_title='NWM Soil Moisture (%)',
        layer_options={'visible':True,'opacity':0.5},
        legend_classes=[
            MVLegendClass('polygon', '0.95 - 1.0', fill='rgba(49,56,148,0.5)'),
            MVLegendClass('polygon', '0.85 - 0.95', fill='rgba(97,108,181,0.5)'),
            MVLegendClass('polygon', '0.75 - 0.85', fill='rgba(145,180,216,0.5)'),
            MVLegendClass('polygon', '0.65 - 0.75', fill='rgba(189,225,225,0.5)'),
            MVLegendClass('polygon', '0.55 - 0.65', fill='rgba(223,240,209,0.5)'),
            MVLegendClass('polygon', '0.45 - 0.55', fill='rgba(225,255,191,0.5)'),
            MVLegendClass('polygon', '0.35 - 0.45', fill='rgba(255,222,150,0.5)'),
            MVLegendClass('polygon', '0.25 - 0.35', fill='rgba(255,188,112,0.5)'),
            MVLegendClass('polygon', '0.15 - 0.25', fill='rgba(235,141,81,0.5)'),
            MVLegendClass('polygon', '0.05 - 0.15', fill='rgba(201,77,58,0.5)'),
            MVLegendClass('polygon', '0 - 0.05', fill='rgba(166,0,38,0.5)')],
        legend_extent=[-112, 36.3, -98.5, 41.66])
        
    # NCEP Climate Outlook MapServer
    ncep_month_outlook = MVLayer(
        source='TileArcGISRest',
        options={'url': 'https://idpgis.ncep.noaa.gov/arcgis/rest/services/NWS_Climate_Outlooks/cpc_drought_outlk/MapServer',
                'params': {'LAYERS': 'show:0'}},
        legend_title='NCEP Monthly Drought Outlook',
        layer_options={'visible':False,'opacity':0.7},
        legend_classes=[
            MVLegendClass('polygon', 'Persistence', fill='rgba(155,113,73,0.7)'),
            MVLegendClass('polygon', 'Improvement', fill='rgba(226,213,192,0.7)'),
            MVLegendClass('polygon', 'Removal', fill='rgba(178,173,105,0.7)'),
            MVLegendClass('polygon', 'Development', fill='rgba(255,222,100,0.7)')],
        legend_extent=[-112, 36.3, -98.5, 41.66])
    ncep_seas_outlook = MVLayer(
        source='TileArcGISRest',
        options={'url': 'https://idpgis.ncep.noaa.gov/arcgis/rest/services/NWS_Climate_Outlooks/cpc_drought_outlk/MapServer',
                'params': {'LAYERS': 'show:1'}},
        legend_title='NCEP Seasonal Drought Outlook',
        layer_options={'visible':False,'opacity':0.7},
        legend_classes=[
            MVLegendClass('polygon', 'Persistence', fill='rgba(155,113,73,0.7)'),
            MVLegendClass('polygon', 'Improvement', fill='rgba(226,213,192,0.7)'),
            MVLegendClass('polygon', 'Removal', fill='rgba(178,173,105,0.7)'),
            MVLegendClass('polygon', 'Development', fill='rgba(255,222,100,0.7)')],
        legend_extent=[-112, 36.3, -98.5, 41.66])


    # Define map view options
    drought_fx_map_view_options = MapView(
            height='630px',
            width='100%',
            controls=['ZoomSlider', 'Rotate', 'FullScreen',
                      {'MousePosition': {'projection': 'EPSG:4326'}},
                      {'ZoomToExtent': {'projection': 'EPSG:4326', 'extent': [-112, 36.3, -98.5, 41.66]}}],
            layers=[tiger_boundaries,nwm_stream_anom,nwm_stream,nwm_soil,ncep_month_outlook,ncep_seas_outlook,watersheds],
            view=view_options,
            basemap='OpenStreetMap',
            legend=True
        )

    context = {
        'drought_fx_map_view_options':drought_fx_map_view_options,
    }

    return render(request, 'dam_inventory/drought_fx.html', context)
########################### End drought_fx map #######################################
########################## Start drought_index amp#########################################
@login_required()
def drought_index_map(request):
    """
    Controller for the app drought map page.
    """
           
    view_center = [-105.6, 39.0]
    view_options = MVView(
        projection='EPSG:4326',
        center=view_center,
        zoom=7.0,
        maxZoom=12,
        minZoom=5
    )

    # TIGER state/county mapserver
    tiger_boundaries = MVLayer(
        source='TileArcGISRest',
        options={'url': 'https://tigerweb.geo.census.gov/arcgis/rest/services/TIGERweb/State_County/MapServer'},
        legend_title='State Boundaries',
        layer_options={'visible':True,'opacity':0.8},
        legend_extent=[-112, 36.3, -98.5, 41.66]) 
        
    # USGS Rest server for HUC watersheds        
    watersheds = MVLayer(
        source='TileArcGISRest',
        options={'url': 'https://services.nationalmap.gov/arcgis/rest/services/wbd/MapServer'},
        legend_title='HUC Watersheds',
        layer_options={'visible':False,'opacity':0.4},
        legend_extent=[-112, 36.3, -98.5, 41.66])
    
    ##### WMS Layers - Ryan
    usdm_legend = MVLegendImageClass(value='Drought Category',
                             image_url='http://ndmc-001.unl.edu:8080/cgi-bin/mapserv.exe?map=/ms4w/apps/usdm/service/usdm_current_wms.map&version=1.3.0&service=WMS&request=GetLegendGraphic&sld_version=1.1.0&layer=usdm_current&format=image/png&STYLE=default')
    usdm_current = MVLayer(
            source='ImageWMS',
            options={'url': 'http://ndmc-001.unl.edu:8080/cgi-bin/mapserv.exe?map=/ms4w/apps/usdm/service/usdm_current_wms.map&',
                     'params': {'LAYERS':'usdm_current','FORMAT':'image/png'},
                   'serverType': 'geoserver'},
            layer_options={'opacity':0.5},
            legend_title='USDM',
            legend_classes=[usdm_legend],
            legend_extent=[-126, 24.5, -66.2, 49])
            
    usdm_kml = MVLayer(
        source='KML',
        options={'url': '/static/tethys_gizmos/data/usdm_current.kml'},
        layer_options={'visible':True,'opacity':0.5},
        legend_title='USDM',
        legend_classes=[usdm_legend],
        legend_extent=[-126, 24.5, -66.2, 49])
            
    vdri_legend = MVLegendImageClass(value='VegDRI Cat',
                     image_url='https://vegdri.cr.usgs.gov/wms.php?service=WMS&request=GetLegendGraphic&format=image%2Fpng&width=20&height=20&LAYER=DROUGHT_VDRI_EMODIS_1')   
    vegdri = MVLayer(
            source='ImageWMS',
            options={'url': 'https://vegdri.cr.usgs.gov/wms.php?',
                     'params': {'LAYERS': 'DROUGHT_VDRI_EMODIS_1'},
                   'serverType': 'geoserver'},
            layer_options={'visible':False,'opacity':0.5},
            legend_title='VegDRI',
            legend_classes=[vdri_legend],
            legend_extent=[-126, 24.5, -66.2, 49])
            # historical layers https://edcintl.cr.usgs.gov/geoserver/qdrivegdriemodis/wms?', 'params': {'LAYERS': 'qdrivegdriemodis_pd_1-sevenday-53-2017_mm_data'

    qdri_legend = MVLegendImageClass(value='QuickDRI Cat',
                     image_url='https://vegdri.cr.usgs.gov/wms.php?service=WMS&request=GetLegendGraphic&format=image%2Fpng&width=20&height=20&LAYER=DROUGHT_QDRI_EMODIS_1')   
    quickdri = MVLayer(
            source='ImageWMS',
            options={'url': 'https://vegdri.cr.usgs.gov/wms.php?',
                     'params': {'LAYERS': 'DROUGHT_QDRI_EMODIS_1'},
                   'serverType': 'geoserver'},
            layer_options={'visible':False,'opacity':0.5},
            legend_title='QuickDRI',
            legend_classes=[qdri_legend],
            legend_extent=[-126, 24.5, -66.2, 49])
            # historical layers: https://edcintl.cr.usgs.gov/geoserver/qdriquickdriraster/wms?', 'params': {'LAYERS': 'qdriquickdriraster_pd_1-sevenday-53-2017_mm_data'

    # Define SWSI KML Layer
    SWSI_kml = MVLayer(
        source='KML',
        options={'url': '/static/tethys_gizmos/data/SWSI_2017Dec.kml'},
        legend_title='SWSI',
        layer_options={'visible':True,'opacity':0.7},
        feature_selection=True,
        legend_extent=[-110, 36, -101.5, 41.6])
    
        
    # Define map view options
    drought_index_map_view_options = MapView(
            height='630px',
            width='100%',
            controls=['ZoomSlider', 'Rotate', 'FullScreen',
                      {'MousePosition': {'projection': 'EPSG:4326'}},
                      {'ZoomToExtent': {'projection': 'EPSG:4326', 'extent': [-130, 22, -65, 54]}}],
            layers=[tiger_boundaries,SWSI_kml,usdm_kml,vegdri,quickdri,watersheds],
            view=view_options,
            basemap='OpenStreetMap',
            legend=True
        )

    context = {
        'drought_index_map_view_options':drought_index_map_view_options,
    }

    return render(request, 'dam_inventory/drought_index.html', context)
########################### End drought_index map #######################################
######################## Start Drought Precip Map Main ###################################
@login_required()
def drought_prec_map(request):
    """
    Controller for the app drought map page.
    """
           
    view_center = [-105.6, 39.0]
    view_options = MVView(
        projection='EPSG:4326',
        center=view_center,
        zoom=7.0,
        maxZoom=12,
        minZoom=5
    )

    # TIGER state/county mapserver
    tiger_boundaries = MVLayer(
        source='TileArcGISRest',
        options={'url': 'https://tigerweb.geo.census.gov/arcgis/rest/services/TIGERweb/State_County/MapServer'},
        legend_title='State Boundaries',
        layer_options={'visible':True,'opacity':0.8},
        legend_extent=[-112, 36.3, -98.5, 41.66])    
        
    # USGS Rest server for HUC watersheds        
    watersheds = MVLayer(
        source='TileArcGISRest',
        options={'url': 'https://services.nationalmap.gov/arcgis/rest/services/wbd/MapServer'},
        legend_title='HUC Watersheds',
        layer_options={'visible':False,'opacity':0.4},
        legend_extent=[-112, 36.3, -98.5, 41.66])
    
    ww_legend = MVLegendImageClass(value='Current Streamflow',
                             image_url='https://edcintl.cr.usgs.gov/geoserver/qdriwaterwatchshapefile/ows?service=WMS&request=GetLegendGraphic&format=image%2Fpng&width=20&height=20&layer=water_watch_today')   
    water_watch = MVLayer(
            source='ImageWMS',
            options={'url': 'https://edcintl.cr.usgs.gov/geoserver/qdriwaterwatchshapefile/wms?',
                     'params': {'LAYERS': 'water_watch_today'},
                   'serverType': 'geoserver'},
            layer_options={'visible':True,'opacity':0.5},
            legend_title='USGS Water Watch',
            legend_classes=[ww_legend],
            legend_extent=[-126, 24.5, -66.2, 49])

    prec7_legend = MVLegendImageClass(value='7-day Precip Total',
                         image_url='https://vegdri.cr.usgs.gov/wms.php?service=WMS&request=GetLegendGraphic&format=image%2Fpng&width=20&height=20&LAYER=PRECIP_TP7')   
    precip7day = MVLayer(
            source='ImageWMS',
            options={'url': 'https://vegdri.cr.usgs.gov/wms.php?',
                     'params': {'LAYERS': 'PRECIP_TP7'},
                   'serverType': 'geoserver'},
            layer_options={'visible':True,'opacity':0.5},
            legend_title='7-day Precip',
            legend_classes=[prec7_legend],
            legend_extent=[-126, 24.5, -66.2, 49])
               
    # NOAA NOHRSC snow products
    snodas_swe = MVLayer(
        source='TileArcGISRest',
        options={'url': 'https://idpgis.ncep.noaa.gov/arcgis/rest/services/NWS_Observations/NOHRSC_Snow_Analysis/MapServer',
                'params': {'LAYERS': 'show:7'}},
        legend_title='SNODAS Model SWE',
        layer_options={'visible':True,'opacity':0.7},
        legend_classes=[
            MVLegendClass('polygon', '0.04', fill='rgba(144,175,180,0.7)'),
            MVLegendClass('polygon', '0.20', fill='rgba(128,165,192,0.7)'),
            MVLegendClass('polygon', '0.39', fill='rgba(95,126,181,0.7)'),
            MVLegendClass('polygon', '0.78', fill='rgba(69,73,171,0.7)'),
            MVLegendClass('polygon', '2.00', fill='rgba(71,46,167,0.7)'),
            MVLegendClass('polygon', '3.90', fill='rgba(79,20,144,0.7)'),
            MVLegendClass('polygon', '5.90', fill='rgba(135,33,164,0.7)'),
            MVLegendClass('polygon', '9.80', fill='rgba(155,53,148,0.7)'),
            MVLegendClass('polygon', '20', fill='rgba(189,88,154,0.7)'),
            MVLegendClass('polygon', '30', fill='rgba(189,115,144,0.7)'),
            MVLegendClass('polygon', '39', fill='rgba(195,142,150,0.7)'),
            MVLegendClass('polygon', '79', fill='rgba(179,158,153,0.7)')],
        legend_extent=[-112, 36.3, -98.5, 41.66])
        
    # Define map view options
    drought_prec_map_view_options = MapView(
            height='630px',
            width='100%',
            controls=['ZoomSlider', 'Rotate', 'FullScreen', 'ScaleLine', 'WMSLegend',
                      {'MousePosition': {'projection': 'EPSG:4326'}},
                      {'ZoomToExtent': {'projection': 'EPSG:4326', 'extent': [-130, 22, -65, 54]}}],
            layers=[tiger_boundaries,water_watch,snodas_swe,precip7day,watersheds],
            view=view_options,
            basemap='OpenStreetMap',
            legend=True
        )

    context = {
        'drought_prec_map_view_options':drought_prec_map_view_options,
    }

    return render(request, 'dam_inventory/drought_prec.html', context)
##################### End Drought Precip Map #############################################
#########################################################################################
@login_required()
def drought_4pane(request):
    return render(request, 'dam_inventory/drought_4pane.html')
#########################################################################################
@login_required()
def add_dam(request):
    """
    Controller for the Add Dam page.
    """
    # Default Values
    location = ''
    name = ''
    owner = 'Reclamation'
    river = ''
    date_built = ''

    # Errors
    location_error = ''
    name_error = ''
    owner_error = ''
    river_error = ''
    date_error = ''

    # Handle form submission
    if request.POST and 'add-button' in request.POST:
        # Get values
        has_errors = False
        location = request.POST.get('geometry', None)
        name = request.POST.get('name', None)
        owner = request.POST.get('owner', None)
        river = request.POST.get('river', None)
        date_built = request.POST.get('date-built', None)

        # Validate
        if not location:
            has_errors = True
            location_error = 'Location is required.'

        if not name:
            has_errors = True
            name_error = 'Name is required.'

        if not owner:
            has_errors = True
            owner_error = 'Owner is required.'

        if not river:
            has_errors = True
            river_error = 'River is required.'

        if not date_built:
            has_errors = True
            date_error = 'Date Built is required.'

        if not has_errors:
            add_new_dam(location=location, name=name, owner=owner, river=river, date_built=date_built)
            return redirect(reverse('dam_inventory:home'))

        messages.error(request, "Please fix errors.")

    # Define form gizmos
    initial_view = MVView(
        projection='EPSG:4326',
        center=[-98.6, 39.8],
        zoom=3.5
    )

    drawing_options = MVDraw(
        controls=['Modify', 'Delete', 'Move', 'Point'],
        initial='Point',
        output_format='GeoJSON',
        point_color='#FF0000'
    )

    location_input = MapView(
        height='300px',
        width='100%',
        basemap='OpenStreetMap',
        draw=drawing_options,
        view=initial_view
    )

    name_input = TextInput(
        display_text='Name',
        name='name',
        initial=name,
        error=name_error
    )

    owner_input = SelectInput(
        display_text='Owner',
        name='owner',
        multiple=False,
        options=[('Reclamation', 'Reclamation'), ('Army Corp', 'Army Corp'), ('Other', 'Other')],
        initial=owner,
        error=owner_error
    )

    river_input = TextInput(
        display_text='River',
        name='river',
        placeholder='e.g.: Mississippi River',
        initial=river,
        error=river_error
    )

    date_built = DatePicker(
        name='date-built',
        display_text='Date Built',
        autoclose=True,
        format='MM d, yyyy',
        start_view='decade',
        today_button=True,
        initial=date_built,
        error=date_error
    )

    add_button = Button(
        display_text='Add',
        name='add-button',
        icon='glyphicon glyphicon-plus',
        style='success',
        attributes={'form': 'add-dam-form'},
        submit=True
    )

    cancel_button = Button(
        display_text='Cancel',
        name='cancel-button',
        href=reverse('dam_inventory:home')
    )

    context = {
        'location_input': location_input,
        'location_error': location_error,
        'name_input': name_input,
        'owner_input': owner_input,
        'river_input': river_input,
        'date_built_input': date_built,
        'add_button': add_button,
        'cancel_button': cancel_button,
    }

    return render(request, 'dam_inventory/add_dam.html', context)


@login_required()
def list_dams(request):
    """
    Show all dams in a table view.
    """
    dams = get_all_dams()
    table_rows = []

    for dam in dams:
        table_rows.append(
            (
                dam['name'], dam['owner'],
                dam['river'], dam['date_built']
            )
        )

    dams_table = DataTableView(
        column_names=('Name', 'Owner', 'River', 'Date Built'),
        rows=table_rows,
        searching=False,
        orderClasses=False,
        lengthMenu=[ [10, 25, 50, -1], [10, 25, 50, "All"] ],
    )

    context = {
        'dams_table': dams_table
    }

    return render(request, 'dam_inventory/list_dams.html', context)
