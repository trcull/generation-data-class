import csv


class MyDataMunger:
    def do_it_all(self, input_file_path, output_file_path):
        with open(input_file_path) as inputcsv:
            reader = csv.reader(inputcsv)
            with open(output_file_path, 'w', newline='') as outputcsv:
                writer = csv.writer(outputcsv)
                for row in reader:
                    self.do_this_row(row, writer)

    def do_this_row(self, row, writer):
        to_write = self.remove_column(row)
        writer.writerow(to_write)

    def remove_column(self, row):
        return [row[0],row[1],row[2],row[3],row[4],row[5],row[7],row[8]]

if __name__ == '__main__':
    print("starting...")
    munger = MyDataMunger()
    munger.do_it_all('./class-event-data.csv', './class-event-data-remove-row-output.csv')
    print("...done")
