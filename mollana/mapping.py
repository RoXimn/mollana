# ******************************************************************************
# Copyright (c) 2025. All rights reserved.
#
# This work is licensed under the Creative Commons Attribution 4.0 International License.
# To view a copy of this license, visit # http://creativecommons.org/licenses/by/4.0/.
#
# Author:      RoXimn <roximn@rixir.org>
# ******************************************************************************
import csv
from itertools import chain
from collections import defaultdict
from pathlib import Path

from symspellpy import SymSpell, Verbosity

from tafseer import tafseerUrduRm2Rm


# ******************************************************************************
def dictLookup(word: str, *, dictionary: SymSpell, distance: int) -> list:
    suggestions = dictionary.lookup(word, Verbosity.CLOSEST,
                                    max_edit_distance=distance,
                                    include_unknown=False)
    s0 = list(filter(lambda item: item.distance == 0, suggestions))
    if distance <= 0:
        return [s0, [], []]
    else:
        s1 = list(filter(lambda item: item.distance == 1, suggestions))
        if distance == 1:
            return [s0, s1, []]
        else:
            s2 = list(filter(lambda item: item.distance == 2, suggestions))
            return [s0, s1, s2]


# ******************************************************************************
def getSortedSuggestions(suggestions, index, atmost = -1):
    # Flatten all the suggestions for each permutation to a single list
    matches = chain.from_iterable([s[index] for s in suggestions])
    # Remove duplicates
    matches = list({match.term: match for match in matches}.values())
    # Sort with decreasing count
    matches = sorted(matches, key=lambda item: item.count, reverse=True)
    if atmost >= 0:
        matches = matches[:atmost]
    return matches


# ******************************************************************************
def processRomanToken(token, urDict: SymSpell, deromanizerMapping: dict) -> list:
    if not token:
        return [(), (), ()]

    rmWords = tafseerUrduRm2Rm(token)
    if len(rmWords) == 0:
        return [(), (), ()]

    # print(f"{token} -> [{len(rmWords)}]{rmWords}")
    suggestionsList = [dictLookup(word, dictionary=urDict, distance=1)
                       for word in rmWords]
    s0 = getSortedSuggestions(suggestionsList, 0)
    s1 = getSortedSuggestions(suggestionsList, 1)
    s2 = getSortedSuggestions(suggestionsList, 2)
    if s0:
        s0 = [(wd, sg.term, fr) for sg in s0
               for (wd, fr) in deromanizerMapping.get(sg.term)]
        s0 = sorted(s0, key=lambda item: item[2], reverse=True)
        # print(f"{token} -> 0:[{len(lst):2d}] {lst}")
    if s1:
        s1 = [(wd, sg.term, fr) for sg in s1
               for (wd, fr) in deromanizerMapping.get(sg.term)]
        s1 = sorted(s1, key=lambda item: item[2], reverse=True)
        # print(f"{token} -> 1:[{len(lst):2d}] {lst}")
        if s2:
            s2 = [(wd, sg.term, fr) for sg in s2
                   for (wd, fr) in deromanizerMapping.get(sg.term)]
            s2 = sorted(s2, key=lambda item: item[2], reverse=True)
            # print(f"{token} -> 2:[{len(lst):2d}] {lst}")

    return [s0, s1, s2]


# ******************************************************************************
def loadDictionaries(dictPath: str, csvPath: str) -> tuple[SymSpell, dict]:
    symSpellDict = SymSpell()
    success = symSpellDict.load_dictionary(dictPath,
                                   term_index=0, count_index=1,
                                   separator="$", encoding='utf8')
    if not success:
        raise FileNotFoundError

    if not Path(csvPath).exists():
        raise FileNotFoundError

    wordsList: list = []
    with open(csvPath, mode='r', newline='', encoding='utf-8') as file:
        csvReader = csv.reader(file)
        for row in csvReader:
            wordsList.append([int(row[0]), row[1], row[2]])

    mapping = defaultdict(set)
    for f, w, r in wordsList:
        mapping[r].add((w, f))

    return symSpellDict, mapping


# ******************************************************************************
if __name__ == '__main__':
    RomanUrduDict, DeromanizerMapping = loadDictionaries("RomanizedUrduWords150k.dict",
                                                        "RomanizedUrduWords150k.csv")
    word = 'JNORY'
    u0, u1, u2 = processRomanToken(word, RomanUrduDict, DeromanizerMapping)
    print(f"{word} -> 0:[{len(u0):2d}] {u0}")
    print(f"{word} -> 1:[{len(u1):2d}] {u1}")
    print(f"{word} -> 2:[{len(u2):2d}] {u2}")
