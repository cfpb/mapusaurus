import csv

def read_file(filename):
    with open(filename, encoding='utf-8') as institutionscsv:
        institution_reader = csv.reader(institutionscsv, delimiter='\t')
        for row in institution_reader:
            print(row)



if __name__ == "__main__":
    read_file('/vagrant/data/HMDA/2012/institutionrecords.txt')
