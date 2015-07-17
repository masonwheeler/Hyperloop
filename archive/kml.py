from pykml.factory import KML_ElementMaker as KML
from lxml import etree
from pykml import parser

def polygoncoord_to_kmlcoordstring(polygoncoord):
    xCoord, yCoord = map(str,polygoncoord)
    KMLCoordstring = ''.join(['\n',
                              '          ',
                              yCoord,
                              ',',
                              xCoord
                              '\n',
                              '          '])
    return KMLCoordstring

def polygon_to_kmlpolygon(polygon):
    KMLCoordstringList = map(polygoncoord_to_kmlcoordstring,polygon)
    KMLCoordstring = ''.join(KMLCoordstringList)
    KMLPolygon = KML.kml(
        KML.Placemark(
            KML.Polygon(
                KML.outerBoundaryIs(
                    KML.LinearRing(
                        KML.coordinates(
                            KMLCoordstring
                        )
                    )
                )
            )
        )
    )
    return KMLPolygon

