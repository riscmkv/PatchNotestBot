import re
import argparse
import random
import glob
import os
from datetime import datetime
import EZTwitterPy.EZTwitterPy as ez

newline_chars = "\r\n"

def choose_random_from_list(lst):
    random.seed(datetime.now())
    return lst[random.randint(0, len(lst)-1)]

class Change:
    string = None
    args = None

    def __init__(self, string, args):
        self.string = string
        self.args = args

    def __str__(self):
        return "string: " + self.string + " " + str(self.args)

    def __repr__(self):
        return "{ string: " + self.string + " args: " + str(self.args) + " }"

class Tweet:
    message = None
    fname = None
    media = None

    def __init__(self, message, fname, media):
        self.message = message
        self.fname = fname
        self.media = media

def line_remove_comment(line):
    line = line.strip()
    comment = re.search('\s*#.*', line)
    if comment:
        line = line.replace(comment.group(0), "")
    return line


def line_remove_arg(line):
    line = line.strip()
    line = line_remove_comment(line)
    arg = re.search('\s--.*', line)
    if arg:
        line = line.replace(arg.group(0), "")
    return line


def line_get_string(line):
    line = line.strip()
    line = line_remove_comment(line)
    line = line_remove_arg(line)
    return line


def line_get_args(line):
    line = line.strip()
    line = line_remove_comment(line)
    args = re.findall("--[^--]*", line)
    arg_dict = {}

    for arg in args:
        arg = arg.replace('-', '')
        arg = arg.replace(' ', '')

        arg_pair = re.findall("[^=]+", arg)
        if(len(arg_pair) == 2):
            arg_dict[arg_pair[0]] = arg_pair[1]
        else:
            arg_dict[arg_pair[0]] = None

    return arg_dict


def gen_change_list(changes_path):
    f = open(changes_path, 'r')

    change_list = []

    for line in f:
        string = line_get_string(line)
        if string:
            change_list.append(Change(string, line_get_args(line)))

    return change_list

def pick_n_strings(change_list, n_changes=3):
    strings_chosen = []
    exclusive_groups = []
    n_chosen = 0
    while n_chosen < n_changes:
        potential_change = choose_random_from_list(change_list)

        # Check if we have an exclusive groups
        if 'exclusive_group' in potential_change.args:
            if potential_change.args['exclusive_group'] in exclusive_groups:
                continue

        # Add the string to the strings_chosen, append the exclusive_group
        # if applicable
        if not (potential_change.string in strings_chosen):
            strings_chosen.append(potential_change.string)
            n_chosen += 1

            if 'exclusive_group' in potential_change.args:
                exclusive_groups.append(potential_change.args['exclusive_group'])

    return strings_chosen

def gen_message(n_changes, char_limit=280, sw_name=None):
    if sw_name:
        message = "Changes added in latest " + sw_name + " update:\n"
    else:
        message = "Changes added in latest update:\n"

    for n in range(len(n_changes)):
        potential_addition = " - " + n_changes[n] + '\n'
        if len(message) + len(potential_addition) >= char_limit:
            break
        else:
            message = message + potential_addition

    return message


def gen_tweet(sw_type="video_games"):
    pwd = os.getcwd()
    titles = glob.glob(pwd + "/resources/" + sw_type + "/*")
    titles.remove(pwd + "/resources/" + sw_type + "/changes.txt")
    title_img = choose_random_from_list(titles)
    title_name = title_img.split("/")[-1].split(".")[0]

    changes = gen_change_list(pwd + "/resources/" + sw_type + "/changes.txt")
    pick_n = pick_n_strings(changes)
    message = gen_message(pick_n, sw_name=title_name)

    #message, fname, media
    return Tweet(message, title_img, title_name)

def do_tweet(sw_type="video_games"):
    tweet = gen_tweet(sw_type)
    print(tweet.message)
    print(tweet.fname)
    ez.post_tweet(tweet.message, media_fname=tweet.fname)

def unit_test():
    print("Testing line_remove_comment()... you should not see any #-starting strings:")
    print(line_remove_comment("#hello world this entire thing is a comment"))
    print(line_remove_comment("\n \n hello world  #This is a comment #within a comment \n"))
    print(line_remove_comment("\n This line has no comments!"))
    print(line_remove_comment(""))
    print("")

    print("Testing line_remove_arg()... you should not see any strings containing --:")
    print(line_remove_arg("\n\n hello world --arg=This_is_an_arg"))
    print(line_remove_arg(""))
    print(line_remove_arg("hello world --arg=arg #This has a comment too!"))
    print("")

    print("Testing line_get_args()...")
    print(line_get_args("hello world --arg=string"))
    print(line_get_args("hello world 2 --arg1=string1 --arg2=string2 --arg3"))
    print(line_get_args(""))
    print(line_get_args("hello world"))

    change_list = gen_change_list('./resources/video_games/changes.txt')
    print("testing gen_Change_list()...")
    print(change_list)
    print(" ")

    pick_n = pick_n_strings(change_list)
    print("testing pick_n_strings()...")
    print(pick_n)
    print(" ")

    message = gen_message(pick_n)
    print("testing gen_message()...")
    print(message)
    print(" ")

    print("testing gen_tweet()...")
    print(gen_tweet())
    print(" ")


def main():
    parser = argparse.ArgumentParser(description="A bot to post randomly generated patchnotes to twitter!")
    parser.add_argument('--unit-test', dest='unit_test', type=bool,
                        help='Run unit tests')
    args = parser.parse_args()

    if args.unit_test:
        unit_test()
    else:
        do_tweet()


if __name__ == "__main__":
    main()