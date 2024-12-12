import csv

filename = 'phone_book.csv'


with open(filename, 'w', newline='',encoding="utf8") as csvfile:
    writer = csv.writer(csvfile)
    writer.writerow(['Name', ' Phone'])
    writer.writerow(['Anna',870712345])
    writer.writerow(['Ivan',874701010])
    writer.writerow(['Tomirsis',870100035])
    writer.writerow(['Ayan',877755555])
    print("CSV файл успешно создан.")