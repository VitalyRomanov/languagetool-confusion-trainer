from subprocess import Popen, PIPE, run, call
from os import popen, path, mkdir
import sys

PAIRS_PATH = "/home/ltv/data/languagetool/languagetool-development/filtered_popular_pairs.txt"
PAIRS_TEXT_PATH = "/home/ltv/data/languagetool/pair_data"

pairs = open(PAIRS_PATH, "r").read().split("\n")

def split(x):
    a = x.split("; ")
    return tuple(a[:2])

pairs = list(map(split, pairs))

c_pair = 0
if path.isfile("state"):
    with open("state", "r") as state:
        c_pair = int(state.read().strip())
    print("Restoring from %dth pair" % c_pair)

while c_pair < len(pairs):
    pair = pairs[c_pair]

    file_path = path.join(PAIRS_TEXT_PATH, "%s_%s.txt" % (pair[0], pair[1]))
    tokens = "%s %s" % (pair[0], pair[1])

    # some files do not exist because on of the words in the pair is too rare
    if path.isfile(file_path):

        command_line = "java -cp /home/ltv/data/languagetool/languagetool/languagetool-dev/target/languagetool-dev-4.3-SNAPSHOT-jar-with-dependencies.jar:/home/ltv/data/languagetool/languagetool/languagetool-standalone/target/LanguageTool-4.3-SNAPSHOT/LanguageTool-4.3-SNAPSHOT/languagetool.jar org.languagetool.dev.bigdata.ConfusionRuleEvaluator %s %s ru /home/ltv/Documents/lt_index ~/data/languagetool/pair_data/%s_%s.txt" % (pair[0], pair[1], pair[0], pair[1])

        try:
            gradlew_output = popen(command_line).read().split("\n")[-22:]
            print(gradlew_output)
            sys.exit()
            # get_scores(gradlew_output)
        except:
            pass

    c_pair += 1
    print("\n\nProcessed %d/%d pairs" % (c_pair, len(pairs)))

    # with open("state", "w") as state:
    #     state.write("%d" % c_pair)

