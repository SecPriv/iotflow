from androguard.misc import AnalyzeAPK
import argparse
import os
import json


def setupArgparse():
    parser = argparse.ArgumentParser(description='Get package stats')
    parser.add_argument('-a', "--apk", type=str, help='The apk to analyze', required=True)
    parser.add_argument('-o', "--output", type=str, help='Output directory', required=True)

    return parser.parse_args()



def getStringAndClases(apkFilePath):
    apk, dalvik, analysis = AnalyzeAPK(apkFilePath)
    stringValues = set()
    for s in analysis.get_strings():
        stringValues.add(s.get_value())
        stringValues.add(s.get_orig_value())



    classes = analysis.get_classes()
    classNames = set()
    for c in classes:
        classNames.add(c.name)

    return stringValues, classNames




def saveToFile(outputfile, data):
    with open(outputfile, 'w') as f:
        json.dump(data, f)


def directoryExistsOrCreate(directory):
    if not os.path.exists(directory):
        os.makedirs(directory)


if __name__ == "__main__":
    args = setupArgparse()
    splittedPath = os.path.split(args.apk)
    filename = splittedPath[1]
    outputfile = args.output + filename.replace(".apk", "")

    directoryExistsOrCreate(args.output + "permissions/")

    apk, _,_ = AnalyzeAPK(args.apk)

    saveToFile(args.output + "permissions/" +filename.replace(".apk", ".json"),apk.get_permissions() )
