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
        writer.writerow(row)


if __name__ == '__main__':
    munger = MyDataMunger()
    munger.do_it_all('./class-event-data.csv', './class-event-data-output.csv')
