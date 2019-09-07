import csv

with open('nasdaq_index_companies.csv') as csv_file:
  csv_reader = csv.reader(csv_file, delimiter=',')
  results = []
  for row in csv_reader:
    results.append(row[1])
  print(results)