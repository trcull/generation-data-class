import csv
import requests
import json
import os

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
        to_write = [row[0],row[1],row[2],row[3],row[4],row[5],row[7],row[8], "wrong_type_flag", "score", "tags", "possible_languages", "maybe_curses"]
        writer.writerow(to_write)

    def do_this_row(self, row, writer, row_num):
        to_write = row
        to_write = self.remove_column(to_write)
        to_write = self.insert_disclaimer(to_write)
        to_write = self.check_event_type(to_write)
        to_write = self.assign_score(to_write)
        to_write = self.ml_awesomeness(to_write, row_num)

        writer.writerow(to_write)

    def call_monkeymind(self, service, description):
        base_url = "https://api.monkeylearn.com/v3/classifiers/"
        # don't forget to do "export MONKEYMIND_API_KEY=xxxxxx" on the command line before running this.
        headers = {
            'Content-Type': 'application/json',
            'Authorization': 'Token {}'.format(os.environ['MONKEYMIND_API_KEY'])
        }
        a_request = {
            'data':
                [description]
        }
        http_response = requests.post((base_url + service), data=json.dumps(a_request), headers=headers)
        if http_response.status_code != 200:
            print("Error from Monkeymind: {}, {}".format(http_response.status_code, http_response.text))
            raise Exception("oops, that failed")

            # we are expecting a response like this:
            # [
            #   {
            #     "text": "Harvard University is a private Ivy League research university in Cambridge, Massachusetts, established in 1636, whose history, influence, and wealth have made it one of the world's most prestigious universities.",
            #     "external_id": null,
            #     "error": false,
            #     "classifications": [
            #       {
            #         "tag_name": "Education",
            #         "tag_id": 54974261,
            #         "confidence": 0.13
            #       }
            #     ]
            #   }
            # ]
        the_json = http_response.json()

        #let's dig down to the "classifications" part and only return that
        return the_json[0]['classifications']


    def ml_awesomeness(self, row, row_num):
        # Avoid actually calling this stuff 1,000 times because that will take forever.  No other reason, though.
        if row_num < 5:
            description = row[7]
            print(row_num)

            #see: https://app.monkeylearn.com/main/classifiers/cl_o46qggZq/tab/api/
            tags = self.call_monkeymind('cl_o46qggZq/classify/',description)
            print(tags)
            tags_str = ""
            #build up a slash-separated string of tags
            for tag in tags:
                if len(tags_str) > 0:
                    tags_str = tags_str + "/" + tag['tag_name']
                else:
                    tags_str = tag['tag_name']
            row.append(tags_str)

            #see: https://app.monkeylearn.com/main/classifiers/cl_Vay9jh28/tab/api/
            languages = self.call_monkeymind('cl_Vay9jh28/classify/',description)
            print(languages)
            language_str = ""
            #build up a slash-separated string of tags
            for language in languages:
                if len(language_str) > 0:
                    language_str = language_str + "/" + language['tag_name']
                else:
                    language_str = language['tag_name']

            #see: https://app.monkeylearn.com/main/classifiers/cl_KFXhoTdt/tab/api/
            issues = self.call_monkeymind('cl_KFXhoTdt/classify/',description)
            print(issues)
            is_cursey = 'no'
            for issue in issues:
                if language['tag_name'] == 'profanity':
                    is_cursey = 'yes'
            row.append(is_cursey)

        else:
            row.append('unk')
            row.append('unk')
            row.append('unk')

        return row

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
    munger.do_it_all('./class-event-data.csv', './class-event-data-ml-awesome-output.csv')
    print("...done")
