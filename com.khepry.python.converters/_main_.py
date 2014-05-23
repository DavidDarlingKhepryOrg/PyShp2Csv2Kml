# -*- coding: utf-8 -*-

import csv
import ogr
import os
import sys


# ----------------------------------------------------------------------------
# define the mainline method
# ----------------------------------------------------------------------------

def main(argv):

    if len(sys.argv) > 1:
        shpFile = sys.argv[1]
    else:
        print ("ShapeFile path is required!")
        
        # override the following two lines for testing purposes only!        
        # exit()
        shpFile = r'~/Documents/fracking/data/North-Dakota/Wells.shp'
    
    if len(sys.argv) > 2:
        csvFile = sys.argv[2]
    else:
        csvFile = shpFile.replace('.shp','.csv')
        print ("csvFile = %s" % csvFile)
    
    if len(sys.argv) > 3:
        kmlFile = sys.argv[3]
    else:
        kmlFile = csvFile.replace('.csv','.kml')
        print ("kmlFile = %s" % kmlFile)
        
    maxRecords = 0
        
    
    # expand any leading tilde
    # to the user's home path
    shpFile = os.path.expanduser(shpFile);
    csvFile = os.path.expanduser(csvFile);
    kmlFile = os.path.expanduser(kmlFile);
    
    # convert from shape to csv
    # shp2csv(shpFile, csvFile, maxRecords)
    
    # convert from csv to kml
    # csv2kml(csvFile, kmlFile, maxRecords)
    
    # convert from shp to kml
    # shp2kml(shpFile, kmlFile, maxRecords)
    
    # convert from shp to kml and csv
    shp2kmlcsv(shpFile, kmlFile, csvFile, maxRecords)


# ----------------------------------------------------------------------------
# define the CSV to KML method
# ----------------------------------------------------------------------------

def csv2kml(csvFile, kmlFile, maxRecords):
    
    print ("")
    print ("========================")
    print ("CSV to KML conversion...")
    print ("------------------------")
    
    ogr.UseExceptions()
    
    csvreader=csv.reader(open(csvFile,'rb'))
    headers=csvreader.next()
    
    kmlDs = ogr.GetDriverByName('KML').CreateDataSource(kmlFile)
    kmlLyr = kmlDs.CreateLayer(os.path.splitext(os.path.basename(kmlFile))[0])
    
    for field in headers[:-1]: #skip kmlgeometry (assumed to be in last column)
        field_def = ogr.FieldDefn(field)
        kmlLyr.CreateField(field_def)
    
    rows = 0
    for rec in csvreader:
        feat = ogr.Feature(kmlLyr.GetLayerDefn())
        for i,field in enumerate(headers[:-1]): #skip kmlgeometry
            feat.SetField(field, rec[i])
        feat.SetGeometry(ogr.CreateGeometryFromGML(rec[-1]))
        kmlLyr.CreateFeature(feat)
        rows += 1
        if rows % 1000 == 0:
            print ("Rows: {:,}".format(rows))
        if maxRecords > 0 and rows >= maxRecords:
            break
    
    #clean up
    del kmlLyr,kmlDs

    print ("------------")
    print ("Rows: {:,}".format(rows))
    print ("")


# ----------------------------------------------------------------------------
# define the SHP to CSV method
# ----------------------------------------------------------------------------

def shp2csv(shpFile, csvFile, maxRecords):
    
    print ("")
    print ("========================")
    print ("SHP to CSV conversion...")
    print ("------------------------")
    
    #Open files
    csvfile=open(csvFile,'wb')
    shpDs=ogr.Open(shpFile)
    shpLayer=shpDs.GetLayer()
    
    #Get field names
    shpDfn=shpLayer.GetLayerDefn()
    nfields=shpDfn.GetFieldCount()
    
    headers=[]
    for i in range(nfields):
        headers.append(shpDfn.GetFieldDefn(i).GetName())
    headers.append('kmlgeometry')
    
    csvwriter = csv.DictWriter(csvfile, headers)
    try:csvwriter.writeheader() #python 2.7+
    except:csvfile.write(','.join(headers)+'\n')
    
    # Write attributes and kml geometry out to csv
    rows = 0
    for shpFeat in shpLayer:
        attributes=shpFeat.items()
        shpGeom=shpFeat.GetGeometryRef()
        attributes['kmlgeometry']=shpGeom.ExportToKML()
        csvwriter.writerow(attributes)
        rows += 1
        if rows % 1000 == 0:
            print ("Rows: {:,}".format(rows))
        if maxRecords > 0 and rows >= maxRecords:
            break
    
    #clean up
    del csvwriter,shpLayer,shpDs
    csvfile.close()

    print ("------------")
    print ("Rows: {:,}".format(rows))
    print ("")


# ----------------------------------------------------------------------------
# define the SHP to KML method
# ----------------------------------------------------------------------------

def shp2kml(shpFile, kmlFile, maxRecords):
    
    print ("")
    print ("========================")
    print ("SHP to KML conversion...")
    print ("------------------------")
    
    #Open files
    shpDs=ogr.Open(shpFile)
    shpLayer=shpDs.GetLayer()
    
    kmlDs = ogr.GetDriverByName('KML').CreateDataSource(kmlFile)
    kmlLayer = kmlDs.CreateLayer(os.path.splitext(os.path.basename(kmlFile))[0])
    
    #Get field names
    shpDfn=shpLayer.GetLayerDefn()
    nfields=shpDfn.GetFieldCount()
    headers=[]
    for i in range(nfields):
        headers.append(shpDfn.GetFieldDefn(i).GetName())
        field = shpDfn.GetFieldDefn(i).GetName()
        field_def = ogr.FieldDefn(field)
        kmlLayer.CreateField(field_def)
    headers.append('kmlgeometry')
   
    # Write attributes and kml out to csv
    rows = 0
    for shpFeat in shpLayer:
        attributes=shpFeat.items()
        shpGeom=shpFeat.GetGeometryRef()
        attributes['kmlgeometry']=shpGeom.ExportToKML()
        # print (attributes)
        kmlFeat = ogr.Feature(kmlLayer.GetLayerDefn())
        for field in headers[:-1]: #skip kmlgeometry (assumed to be in last column)
            kmlFeat.SetField(field, attributes[field])
        kmlFeat.SetGeometry(ogr.CreateGeometryFromGML(attributes['kmlgeometry']))
        kmlLayer.CreateFeature(kmlFeat)
        rows += 1
        if rows % 1000 == 0:
            print ("Rows: {:,}".format(rows))
        if maxRecords > 0 and rows >= maxRecords:
            break
    
    #clean up
    del shpLayer,shpDs,kmlLayer,kmlDs

    print ("------------")
    print ("Rows: {:,}".format(rows))
    print ("")


# ----------------------------------------------------------------------------
# define the SHP to KML method
# ----------------------------------------------------------------------------

def shp2kmlcsv(shpFile, kmlFile, csvFile, maxRecords):
    
    print ("")
    print ("================================")
    print ("SHP to KML and CSV conversion...")
    print ("--------------------------------")
    
    #Open files
    csvfile=open(csvFile,'wb')
    shpDs=ogr.Open(shpFile)
    shpLayer=shpDs.GetLayer()
    
    kmlDs = ogr.GetDriverByName('KML').CreateDataSource(kmlFile)
    kmlLayer = kmlDs.CreateLayer(os.path.splitext(os.path.basename(kmlFile))[0])
    
    #Get field names
    shpDfn=shpLayer.GetLayerDefn()
    nfields=shpDfn.GetFieldCount()
    headers=[]
    for i in range(nfields):
        headers.append(shpDfn.GetFieldDefn(i).GetName())
        field = shpDfn.GetFieldDefn(i).GetName()
        field_def = ogr.FieldDefn(field)
        kmlLayer.CreateField(field_def)
    headers.append('kmlgeometry')
    
    csvwriter = csv.DictWriter(csvfile, headers)
    try:csvwriter.writeheader() #python 2.7+
    except:csvfile.write(','.join(headers)+'\n')
   
    # Write attributes and kml out to csv
    rows = 0
    for shpFeat in shpLayer:
        attributes=shpFeat.items()
        shpGeom=shpFeat.GetGeometryRef()
        attributes['kmlgeometry']=shpGeom.ExportToKML()
        csvwriter.writerow(attributes)
        kmlFeat = ogr.Feature(kmlLayer.GetLayerDefn())
        for field in headers[:-1]: #skip kmlgeometry (assumed to be in last column)
            kmlFeat.SetField(field, attributes[field])
        kmlFeat.SetGeometry(ogr.CreateGeometryFromGML(attributes['kmlgeometry']))
        kmlLayer.CreateFeature(kmlFeat)
        rows += 1
        if rows % 1000 == 0:
            print ("Rows: {:,}".format(rows))
        if maxRecords > 0 and rows >= maxRecords:
            break
    
    #clean up
    del csvwriter,shpLayer,shpDs,kmlLayer,kmlDs
    csvfile.close()

    print ("------------")
    print ("Rows: {:,}".format(rows))
    print ("")
    
    
# ============================================================================
# execute the mainline processing routine
# ============================================================================

if (__name__ == "__main__"):
    retval = main(sys.argv[1:])
