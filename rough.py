import csv

with open('data.csv', 'r') as csv_file:
    csv_reader = csv.reader(csv_file)
    data = list(csv_reader)
    headers = data[0]
    data = data[1:]

def match_rows(speciality = None, city = None, state = None, zip_code = None):
    for row in data:
        # ['2', 'B', 'Vision', 'Trenton', 'HD', '97654', 'white 645']
        if (speciality == row[2] or not speciality) and (city == row[3] or not city) and (state == row[4] or not state) and (zip_code == row[5] or not zip_code):
            return row

##
##print('Input blank of None.')
##speciality = input("Enter speciality: ")
##city = input("Enter city: ")
##state = input("Enter state: ")
##zip_code = input("Enter zip code: ")
#print(speciality, city, state, zip_code)
print(match_rows(speciality = speciality, city = city, state = state, zip_code = zip_code))
