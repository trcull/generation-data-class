import csv


class MyDataMunger:
    def do_it_all(self, input_file_path, output_file_path):
        with open(input_file_path) as inputcsv:
            reader = csv.reader(inputcsv)
            with open(output_file_path, 'w', newline='') as outputcsv:
                writer = csv.writer(outputcsv)
                row_num = 0
                for row in reader:
                    if row_num == 0:
                        self.do_this_header(row, writer)
                    else:
                        self.do_this_row(row, writer, row_num)
                    row_num = row_num + 1

    def do_this_header(self, row, writer):
        #don't forget we have to trim the second "city" column from the header, too.
        to_write = [row[0],row[1],row[2],row[3],row[4],row[5],row[7],row[8], "wrong_type_flag", "score"]
        writer.writerow(to_write)

    def do_this_row(self, row, writer, row_num):
        to_write = row
        to_write = self.remove_column(to_write)
        to_write = self.insert_disclaimer(to_write)
        to_write = self.check_event_type(to_write)
        to_write = self.assign_score(to_write)

        writer.writerow(to_write)


    def assign_score(self, row):
        event_type = row[1]
        description = row[7].lower()
        #default to a zero score
        row.append(0)

        #is it a letter writing party that mentions Vote Forward?
        if 'letter-writing' == event_type and ('vote forward' in description or 'votefwd' in description):
            row[9] = row[9] + 5

        #is it just a DNC convention watch party that doesn't actually contact voters?
        if 'watch party' in description or 'dnc convention' in description:
            row[9] = row[9] - 1

        #do they mention Zoom, but not include a link to Zoom? (which confuses people to no end)
        if 'zoom' in description and 'zoom.us/' not in description:
            row[9] = row[9] - 2

        #we love Georgia.  Does this have to do with Georgia?
        if 'georgia' in description or ' ga ' in description:
            row[9] = row[9] + 3

        #AOC.  Need we say more?
        if ' aoc ' in description:
            row[9] = row[9] + 100

        return row


    ALL_EVENT_TYPES = [
        ['canvassing',           'canvass','knock doors'],
        ['fundraiser',           'raise money','fundraise'],
        ['house-party',          'house party'],
        ['letter-writing',       'write letters','letter writing'],
        ['other'                  ],
        ['phonebank',            'call voters', 'phone bank'],
        ['training',             'training'],
        ['voter-registration',   'register voters', 'voter registration'],
    ]

    def check_event_type(self, row):
        listed_event_type = row[1]
        description = row[7]

        row.append('not flagged')
        for event_type in self.ALL_EVENT_TYPES:
            if listed_event_type == event_type[0]:
                pass #do nothing, we expect there to be these words in the description
            else:
                #check the description to make sure there aren't any words in it that imply the event type is this one
                for words in event_type[1:]:
                    if words in description:
                        row[8] = 'flagged'
        return row


    def insert_disclaimer(self, row):
        if "swingleft.org/community-agreements" not in row[7]:
            row[7] = row[7] + "\n\nBy clicking RSVP, you agree to Swing Left's Community Agreements (https://swingleft.org/community-agreements)."
        return row

    def remove_column(self, row):
        return [row[0],row[1],row[2],row[3],row[4],row[5],row[7],row[8]]

if __name__ == '__main__':
    print("starting...")
    munger = MyDataMunger()
    munger.do_it_all('./class-event-data.csv', './class-event-data-event-score-output.csv')
    print("...done")
