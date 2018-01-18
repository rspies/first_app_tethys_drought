$(function()
{
    var layer = new ol.layer.Tile({
        source: new ol.source.OSM()
      });
      var london = ol.proj.transform([-0.12755, 51.507222], 'EPSG:4326', 'EPSG:3857');
      var view = new ol.View({
        center: [-201694.22, 6880651.07],
        zoom: 6
      });
      // create two maps
      var map1 = new ol.Map({
        target: 'map1',
        layers: [layer]
      });
      var map2 = new ol.Map({
        target: 'map2',
        layers: [layer],
        view: view
      });
      // and bind the view properties so they effectively share a view
      map1.bindTo('view', map2);
});