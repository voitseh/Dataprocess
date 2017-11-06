import sys
from scipy.io import loadmat
from datetime import datetime
from Parser import *
from Utils import common

###########################################################
#####   IMDB-WIKI to JSON_INDB_WIKI Convector    ##########
###########################################################
#This script is run from console terminal
#Sample: C:\Users\User>python imdb_wiki_to_json.py

dataset_archive = "wiki_crop.tar"
imgs_and_anns_subfolder = "wiki_crop/"
imgs_and_anns_destination = 'datasets/IMDB-WIKI/'
json_dir = 'datasets/JSON_IMDB-WIKI/'
annotations_file = 'datasets/IMDB-WIKI/wiki_crop/wiki.mat'
directories = [imgs_and_anns_destination, json_dir]
db = "wiki"
subdir_count = 100
subdir = []

ap = argparse.ArgumentParser()
ap.add_argument("--subfolder", default=imgs_and_anns_subfolder, required = False, help = "Images and annotations subfolder to extract from")
namespace = ap.parse_args(sys.argv[1:])

def calc_age(taken, dob):
    birth = datetime.fromordinal(max(int(dob) - 366, 1))
    # assume the photo was taken in the middle of the year
    result = taken - birth.year
    return result if birth.month < 7 else (result -1) 
        
def imgs_to_single_folder():
    #Copy images to single folder
    for i in range(subdir_count):
        subdir.append('{0}{1}{2}{3}{4}'.format(imgs_and_anns_destination, imgs_and_anns_subfolder, "0", str(i), "/")) if i < 10 else  subdir.append('{0}{1}{2}{3}'.format(imgs_and_anns_destination,imgs_and_anns_subfolder, str(i), "/"))
        common.copy_files(subdir[i], imgs_and_anns_destination)

class ImdbWikiToJson(Parser):
    
    def __init__(self):
        self.objects = []   
        self.object_info = {}
        self.coords = []
        common.make_directories(directories)
        extract_archive(dataset_archive, imgs_and_anns_destination)
        imgs_to_single_folder()
        # remove old folders
        for i in range(subdir_count):
            common.remove_directory(subdir[i])

        super(ImdbWikiToJson, self).__init__()
    
    def parse(self):
        """
            Definition: Make annotations directory for wiki annotations and populate it with separate ann files.
            Returns: None
        """
        meta = loadmat(annotations_file)
        full_path = meta[db][0, 0]["full_path"][0]
        dob = meta[db][0, 0]["dob"][0]  # Matlab serial date number
        gender = meta[db][0, 0]["gender"][0]
        name = meta[db][0, 0]["name"][0]
        face_location = meta[db][0, 0]["face_location"][0]
        photo_taken = meta[db][0, 0]["photo_taken"][0]  # year
        face_score = meta[db][0, 0]["face_score"][0]
        second_face_score = meta[db][0, 0]["second_face_score"][0]
        age = [calc_age(photo_taken[i], dob[i]) for i in range(len(dob))]
        ind = -1
        
        for i in range(len(dob)):
            self.object_info['filename'] = str(full_path[i]).split("/")[1].split("'")[0]
            self.object_info['objects'] = []
            self.face_info = {'class_name':'face'}
            for row in face_location[i]:
                for j in row:
                    self.coords.append(int(j))
                self.face_info['bounding_box'] = self.coords
                self.coords = []

            self.face_info['gender'] = gender[i]
            self.face_info['age'] = age[i]
            self.object_info['objects'].append(self.face_info)
                
            self.objects.append(self.object_info.copy())
                
        for i in self.objects:
            file = os.path.join(json_dir, i["filename"].split('.')[0])
            with open("{}.json".format(file), "wt") as out_file:
                out_file.write(str(i))
    
def main():
    imdb_wiki = ImdbWikiToJson()
    imdb_wiki.parse()

if __name__ == '__main__':
    main()