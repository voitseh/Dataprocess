# Import necessary libraries
import os, sys, shutil, glob, argparse
import numpy as np
import json
import argparse
from Utils import common
from PIL import Image
from lxml import etree

###########################################################
##########        JSON to VOC Conversion        ##########
###########################################################

# This script is run from  console terminal
# Sample: python json_to_pascalVoc.py --json "datasets/JSON_AFW/" --images "datasets/AFW/"

ap = argparse.ArgumentParser()
ap.add_argument("--json", required = True, help = "Type json folder path to receive annotations from")
ap.add_argument("--images", required = True, help = "Type images folder path to receive images from")
namespace = ap.parse_args(sys.argv[1:])

class JsonToPascalVoc():
   
    def to_pasvoc_xml(self,args):
        annotation = etree.Element('annotation')
        filename = etree.Element('filename')
        f = args['fname'].split("/")
        filename.text = f[-1]
        annotation.append(filename)
        folder = etree.Element('folder')
        folder.text = "/".join(f[:-1])
        annotation.append(folder)
        for i in range(len(args['coords'])):
            object = etree.Element('object')
            annotation.append(object)
            name = etree.Element('name')
            name.text = args['labels'][i]
            object.append(name)
            if args['genders'] != []:
                name = etree.Element('gender')
                name.text = str(args['genders'][i])
                object.append(name)
                name = etree.Element('age')
                name.text = str(args['ages'][i])
                object.append(name)
            
            bndbox = etree.Element('bndbox')
            object.append(bndbox)
            xmax = etree.Element('xmax')
            xmax.text = str(args['coords'][i][2])
            bndbox.append(xmax)
            xmin = etree.Element('xmin')
            xmin.text = str(args['coords'][i][0])
            bndbox.append(xmin)
            ymax = etree.Element('ymax')
            ymax.text = str(args['coords'][i][3])
            bndbox.append(ymax)
            ymin = etree.Element('ymin')
            ymin.text = str(args['coords'][i][1])
            bndbox.append(ymin)
            difficult = etree.Element('difficult')
            difficult.text = '0'
            object.append(difficult)
            occluded = etree.Element('occluded')
            occluded.text = '0'
            object.append(occluded)
            pose = etree.Element('pose')
            pose.text = 'Unspecified'
            object.append(pose)
            truncated = etree.Element('truncated')
            truncated.text = '1'
            object.append(truncated)
        img_size = etree.Element('size')
        annotation.append(img_size)
        depth = etree.Element('depth')
        depth.text = '3'
        img_size.append(depth)
        height = etree.Element('height')
        height.text = str(args['h'])
        img_size.append(height)
        width = etree.Element('width')
        width.text = str(args['w'])
        img_size.append(width)

        return annotation

    def parse_json_ann(self, filename):
        """
        Definition: Parses json annotation file to extract bounding box coordintates.

        Returns: all_clases - contains a list of clases
                     all_coords - contains a list of bdn_bxs
        """
        lfile = open(filename)
        classes = []
        bdn_bxs = []
        genders = []
        ages = []
        f= open(filename)
        for line in f:
            line = line.replace("'", '"')
            line = line.replace("nan", 'null')
            my_dict = json.loads(line)
            for obj in my_dict["objects"]:
                classes.append(obj["class_name"])
                bdn_bxs.append(obj["bounding_box"])
                if "gender" in obj:
                    genders.append(obj["gender"])
                    ages.append(obj["age"])
        return  classes,bdn_bxs,genders,ages
    
    def voc(self, label=None):
        voc_annotations_dir = 'datasets/VOC_{}{}'.format(namespace.images.split("/")[1],"/single/")
        common.make_directory(voc_annotations_dir)
        print ("Convert json to voc")
        # Iterate through json annotations data
        for f in os.listdir(str(namespace.json)):
            fname = os.path.join( str(namespace.json) , f)
            if os.path.isfile(fname):
                fname = os.path.join(namespace.images , f).split(".json")[0] + ".jpg"
                if os.path.isfile(fname):
                    img = Image.open(fname)
                    w, h = img.size
                    img.close()
                    labels, coords, genders, ages = self.parse_json_ann(os.path.join(str(namespace.json) + f))
                    to_pasvoc_xml_args = {'fname':fname, 'labels':labels, 'coords':coords, 'genders':genders, 'ages':ages, 'w':w, 'h':h}
                    annotation = self.to_pasvoc_xml(to_pasvoc_xml_args)
                    et = etree.ElementTree(annotation)
                    et.write('{0}{1}{2}'.format(voc_annotations_dir, f.split(".json")[0], ".xml"), pretty_print=True)
                    
def main():
    voc = JsonToPascalVoc()
    voc.voc()
if __name__ == '__main__':
    main()