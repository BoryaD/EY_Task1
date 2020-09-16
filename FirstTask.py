import datetime
import time
import random
import string
import os
import sqlite3


class StringManager:

    __cursor = None
    __conn = None

    def __init__(self, number_of_files, filenames):
        self._len_of_strings = 10
        self._delim = '||'
        self._date_delim = "."
        self._russian_alphabet = 'абвгдеёжзийклмнопрстуфхцчшщъыьэюяАБВГДЕЁЖЗИЙКЛМНОПРСТУФХЦЧШЩЪЫЬЭЮЯ'
        self._int_random_from = 1
        self._int_random_to = 1_000_000
        self._float_random_from = 1
        self._float_random_to = 20
        today = datetime.date.today()
        self.today_sec = time.mktime(today.timetuple())
        five_years_ago = today.replace(year=today.year - 5)
        self._five_years_ago_sec = time.mktime(five_years_ago.timetuple())
        self._number_of_files = number_of_files
        self._filenames = []
        self._res_filename = filenames + '_concat.txt'

        for i in range(1, self._number_of_files + 1):
            self._filenames.append(f'{filenames}{i}.txt')

    def create_string(self):

        """Function that create and return string. Temple: date (last 5 years)||10 eng symb||10 rus symb||
        int(from 1 to 1_000_000||float (from 1 to 20, 8 digits after )||"""

        # convert two date to secs and random int between to sec and convert to date
        date_sec = random.randint(self._five_years_ago_sec, self.today_sec)
        date = datetime.datetime.fromtimestamp(date_sec)
        date_str = str(date.day) + self._date_delim + str(date.month) + self._date_delim + str(date.year) + self._delim
        # random chars from string
        letters = string.ascii_letters
        eng_str = ''.join(random.choice(letters) for i in range(self._len_of_strings)) + self._delim
        # random chars from string
        rus_str = ''.join(random.choice(self._russian_alphabet) for i in range(self._len_of_strings)) + self._delim
        # random int
        int_str = str(random.randint(self._int_random_from, self._int_random_to)) + self._delim
        # random float
        float_str = str(round(random.uniform(self._float_random_from, self._float_random_to), 8)) + self._delim

        return date_str + eng_str + rus_str + int_str + float_str

    def generate_random_strings(self, number_of_strings):
        """create big string with specified amount of little strings"""
        return ''.join(self.create_string() + '\n' for i in range(number_of_strings))[:-1:]

    def write_to_files(self, texts):
        """"create files and write text to files"""
        for i in range(len(self._filenames)):
            with open(self._filenames[i], "w") as f:
                f.write(texts[i])
                f.close()

    def delete_str_from_files(self, substr):
        """Delete from all files string that contains specified substrings"""
        # read all strings from file to list and try to find substring.

        deleted_string_counter = 0
        for filename in self._filenames:
            new_text = ''
            with open(filename, "r+") as f:
                #  If we finds substr, delete from list.
                rw_flag = False
                lines = f.readlines()
                for line in lines:
                    if substr in line:
                        deleted_string_counter += 1
                        rw_flag = True
                    else:
                        new_text += line
                #  If we delete some strings from list, close file and open again to rewrite.
                #  If we don't delete strings, do nothing, just close file
                if rw_flag:
                    f.close()
                    with open(filename, "w") as file:
                        if new_text:
                            if new_text[-1] == '\n':
                                new_text = new_text[:-1]
                        file.write(new_text)
                f.close()
        print(f'Count of deleted strings is {deleted_string_counter}')

    def concat_files(self):
        """concat all files"""
        text = ''
        # open files, save string to variable, than open new file and write to file this variable
        for filename in self._filenames:
            with open(filename, "r+") as f:
                text += f.read() + '\n'
        with open(self._res_filename, "w") as file:
            file.write(text[:-1])

    @staticmethod
    def get_cursor_to_db():
        """This singletone just open conection to database if it's close, and return handler"""
        if StringManager.__cursor is None:
            conn = sqlite3.connect("strings.db")
            StringManager.__cursor = conn.cursor()
            StringManager.__conn = conn
        return StringManager.__cursor, StringManager.__conn

    def save_to_db(self):
        """save all files to db"""
        cursor, conn = StringManager.get_cursor_to_db()
        # crate database if it's not exist
        cursor.execute('''CREATE TABLE IF NOT EXISTS strings(id INTEGER PRIMARY KEY, 
         date_rand text, eng_chars text, rus_chars text, numbers numeric, floats REAL )''')
        # open files and write every value to column in table.
        with open(self._res_filename, "r") as file:
            lines = file.readlines()
            for i in range(len(lines)):
                arr_str = lines[i].split('||')
                # open files and write every value to column in table.
                cursor.execute('''INSERT INTO strings (date_rand, eng_chars, rus_chars, numbers, floats)
                VALUES(?,?,?,?,?)''', arr_str[:-1])
                conn.commit()
                print(f'{i} out of {len(lines)} writes ready')

    @staticmethod
    def count_average_and_median():
        """return median of floats and sum of int """
        cursor, conn = StringManager.get_cursor_to_db()
        # nested sql-query to return median of float values
        cursor.execute(
            '''SELECT floats FROM strings ORDER BY floats LIMIT 1 OFFSET (SELECT COUNT(*) FROM strings) / 2 ''')
        median = cursor.fetchall()[0][0]
        # sql-query to return sum of field that contains ints
        cursor.execute(
            '''SELECT sum(numbers) FROM strings ''')
        sum_ = cursor.fetchall()[0][0]
        print(f'Sum of numbers is {sum_}, median of floats is {median}')
        return median, sum_


def main():
    # create directory if not exist
    if not os.path.exists('files'):
        os.mkdir('files')

    # create object if our class that takes count of files and path to save files
    str_worker = StringManager(100, 'files//file')

    # create 100 strings 100 times
    texts = []
    [texts.append(str_worker.generate_random_strings(100)) for i in range(100)]

    # create and write 100 files that contains 100 strings
    # str_worker.write_to_files(texts)
    # delete from all files strings that contains substring 'S'
    # str_worker.delete_str_from_files('S')
    # concatinate all files to one file
    # str_worker.concat_files()
    # save all strings from concatinated file to database
    # str_worker.save_to_db()
    # function return with nested sql-query (does not support stored procedure)
    str_worker.count_average_and_median()


if __name__ == '__main__':
    main()
