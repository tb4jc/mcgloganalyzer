'''
Created on 10.02.2016

@author: tburri
'''
from pathlib import Path
import time

class KmlWriter():
    '''
    classdocs
    '''


    def __init__(self, filename):
        '''
        Constructor
        '''
        self.kmlFilePath = Path(filename)
        try:
            self.kmlFile = Path(filename).open('w')
            self.kmlFile.write('''<?xml version="1.0" encoding="UTF-8"?>
<kml xmlns="http://www.opengis.net/kml/2.2">
    <Document>
        <Style id="iconRed"><IconStyle><Icon><href>http://maps.google.com/mapfiles/kml/paddle/red-circle.png</href></Icon></IconStyle></Style>
        <Style id="iconPurpleStar"><IconStyle><Icon><href>http://maps.google.com/mapfiles/kml/paddle/purple-stars.png</href></Icon></IconStyle></Style>
        <Style id="iconPinkStar"><IconStyle><Icon><href>http://maps.google.com/mapfiles/kml/paddle/pink-stars.png</href></Icon></IconStyle></Style>
        <Style id="iconRedStar"><IconStyle><Icon><href>http://maps.google.com/mapfiles/kml/paddle/red-stars.png</href></Icon></IconStyle></Style>
        <Style id="iconYellowStar"><IconStyle><Icon><href>http://maps.google.com/mapfiles/kml/paddle/ylw-stars.png</href></Icon></IconStyle></Style>
        <Style id="iconGreen"><IconStyle><Icon><href>http://maps.google.com/mapfiles/kml/paddle/grn-circle.png</href></Icon></IconStyle></Style>''')
        except BaseException:
            print("KmlWriter failed to open file")
        
    def addPlacemark(self, statusLine, comType, comResult):
        # 04.02.2016 06:35:39 yes  11  48.80893  3.07987  0.00  0.00  3  -69 
        statLineSplit = statusLine.split(';')
        dateTime = statLineSplit[0]
        fix = statLineSplit[1]
        sats =  statLineSplit[2]
        lat = statLineSplit[3]
        long =  statLineSplit[4]
        if lat=="nan" or long=="nan":
            return
        speed =  statLineSplit[5]
        heading =  statLineSplit[6]
        conStatus =  statLineSplit[7]
        rssi =  statLineSplit[8]
        #altitudeRssi = 113+int(rssi)
        iconType = "#iconGreen" if comResult else "#iconRed"
        newPlacemark = '''    <Placemark>
        <name></name>
        <description>%s result\nTimestamp: %s\nlong: %s\nlat: %s\nspeed: %s\nheading: %s\nconStatus: %s\nrssi: %s</description>
        <styleUrl>%s</styleUrl>
        <Point>
            <altitudeMode>relativeToGround</altitudeMode>
            <coordinates>%s,%s,0</coordinates>
        </Point>
    </Placemark>\n''' % (comType, dateTime, long, lat, speed, heading, conStatus, rssi, iconType, long, lat)
        self.kmlFile.write(newPlacemark)

    def addPlacemarkPpp(self, statusLine, resultType, result):
        statLineSplit = statusLine.split(';')
        dateTime = statLineSplit[0]
        fix = statLineSplit[1]
        sats =  statLineSplit[2]
        lat = statLineSplit[3]
        long =  statLineSplit[4]
        if lat=="nan" or long=="nan":
            return
        speed =  statLineSplit[5]
        heading =  statLineSplit[6]
        conStatus =  statLineSplit[7]
        rssi =  statLineSplit[8]
        if resultType == 1: iconType = "#iconPinkStar"
        elif resultType == 2: iconType = "#iconPurpleStar"
        elif resultType == 4: iconType = "#iconYellowStar"
        else: iconType = "#iconRedStar"
        newPlacemark = '''    <Placemark>
        <name></name>
        <description>%s\nTimestamp: %s\nlong: %s\nlat: %s\nspeed: %s\nheading: %s\nconStatus: %s\nrssi: %s</description>
        <styleUrl>%s</styleUrl>
        <Point>
            <altitudeMode>relativeToGround</altitudeMode>
            <coordinates>%s,%s,0</coordinates>
        </Point>
    </Placemark>\n''' % (result, dateTime, long, lat, speed, heading, conStatus, rssi, iconType, long, lat)
        self.kmlFile.write(newPlacemark)

    def finishFile(self):
        self.kmlFile.write("\n    </Document>\n</kml>\n")
        self.kmlFile.close()

if __name__ == '__main__':
    kmlWriter = KmlWriter('exmample.kml')
    kmlWriter.addPlacemark("04.02.2016 06:37:01;yes;11;48.80893;3.07986;0.00;0.00;3;-69;FSFR;2", "FTP", False)
    kmlWriter.finishFile()
