# ******************************************************************************
import re
import itertools


# ******************************************************************************
def permuteFirstOccurrence(token: str, mapping: dict) -> list[str]:
    # Initialize with a value larger than any possible index
    minIndex = len(token)
    leftMostKey = ''

    for substr in mapping.keys():
        index = token.find(substr)
        if index != -1 and index < minIndex:
            minIndex = index
            leftMostKey = substr

    if leftMostKey:
        # print(f'Found "{leftMostKey}" at index {minIndex} in "{text}"')
        substitutions = mapping[leftMostKey]
        return [token.replace(leftMostKey, substr, 1) for substr in substitutions]

    return []


# ******************************************************************************
def permuteAllOccurrences(tokenList: list[str], mapping: dict) -> list[str]:
    outList = []
    for token in tokenList:
        completedWords = []
        processedWords = [token]
        while processedWords:
            word = processedWords.pop(0)
            replacedVowels = permuteFirstOccurrence(word, mapping)
            if replacedVowels:
                processedWords.extend(replacedVowels)
            else:
                completedWords.append(word)
        outList.extend(completedWords)
    return outList


# ******************************************************************************
def permuteEnding(text: str, mapping: dict) -> list[str]:
    """
    Checks if the input text ends with any key in the mapping.
    If so, replaces that suffix with all corresponding substitutions.
    """
    for key, substitutions in mapping.items():
        if text.endswith(key):
            # Calculate where the suffix starts to replace only the end
            prefix = text[:-len(key)]
            return [prefix + sub for sub in substitutions]

    # Return empty list if no matching suffix is found
    return []


# ******************************************************************************
def permuteAllEndings(tokenList: list[str], mapping: dict) -> list[str]:
    outList = []
    for token in tokenList:
        completedWords = []
        processedWords = [token]
        while processedWords:
            word = processedWords.pop(0)
            replacedVowels = permuteEnding(word, mapping)
            if replacedVowels:
                processedWords.extend(replacedVowels)
            else:
                completedWords.append(word)
        outList.extend(completedWords)
    return outList


# ******************************************************************************
def replaceEnding(token: str, mapping: dict, n: int) -> str:
    if len(token) >= n and token[-n:] in mapping:
        return token[:-n] + mapping[token[-n:]]
    else:
        return token


# ******************************************************************************
def findVowelCombos(word):
    # Convert list to set for O(1) average lookup performance
    VowelPatterns = ["a", "aa", "ai", "au", "ay",
                     "e", "ee", "ei", "ey",
                     "i", "ie",
                     "o", "oo", "ou",
                     "u"]
    vowelsSet = set(VowelPatterns)
    validCombos = []

    #  -------------------------------------------------------------------------
    def findCombinations(remaining, currentPath):
        # Base case: if no characters are left, we found a valid breakdown
        if not remaining:
            validCombos.append(list(currentPath))
            return

        # Check 1-character substring
        chunk1 = remaining[:1]
        if chunk1 in vowelsSet:
            currentPath.append(chunk1)
            findCombinations(remaining[1:], currentPath)
            currentPath.pop()  # Backtrack

        # Check 2-character substring
        if len(remaining) >= 2:
            chunk2 = remaining[:2]
            if chunk2 in vowelsSet:
                currentPath.append(chunk2)
                findCombinations(remaining[2:], currentPath)
                currentPath.pop()  # Backtrack

    findCombinations(word, [])
    return validCombos


# ******************************************************************************
def concatenateCombos(subStrings, charset):
    """
    Concatenates a list of strings using all combinations of single characters
    from a given set as separators.

    Args:
        subStrings: A list of strings to concatenate.
        charset: A set of single-character strings to use as separators.

    Returns:
        A list of all possible concatenated strings.
    """
    if not subStrings:
        return []
    if len(subStrings) == 1:
        return subStrings

    separatorCount = len(subStrings) - 1
    # Generate all combinations of separators with replacement
    separatorCombos = itertools.product(charset, repeat=separatorCount)

    results = []
    for combo in separatorCombos:
        combinedString = ""
        for i in range(len(subStrings) - 1):
            combinedString += subStrings[i] + combo[i]
        combinedString += subStrings[-1]
        results.append(combinedString)
    return results

# ******************************************************************************
def permuteConsecutiveVowels(inList: list[str]) -> list[str]:
    """Process two or more consecutive vowels"""
    reVowels = r"[aeiou]{2,}"
    outList = []

    for token in inList:
        # print(f'processing "{w}"')
        matched = False
        wordOutput = []
        matches = re.finditer(reVowels, token)
        for match in matches:
            matched = True
            comboOutput = []
            combos = findVowelCombos(match.group())
            for combo in combos:
                if len(combo) == 1:
                    comboOutput.extend(combo)
                else:
                    comboOutput.extend(concatenateCombos(combo, ["A", "Y"]))
            # print(f'"{w}" -> {comboOutput}')
            for o in comboOutput:
                s, e = match.span()
                # print(f"-> {token[:s]}{o}{token[e:]}")
                wordOutput.append(f"{token[:s]}{o}{token[e:]}")

        outList.extend(wordOutput if matched else [token])

    return outList

# ******************************************************************************
def tafseerUrduRm2Rm(word: str) -> set[str]:
    # Step 00 ------------------------------------------------------------------
    word = word.strip().lower()

    # Step 01 ------------------------------------------------------------------
    # print(f' 1. "{word}" -> ', end='')
    token = "".join(char if char in 'aeiouyh' else char.upper() for char in word)
    # print(f'"{token}"')

    # Step 02 ------------------------------------------------------------------
    # print(f' 2. "{token}" -> ', end='')
    token = re.sub(r'([A-Z])\1+', r'\1', token)
    # print(f'"{token}"')

    # Step 03 ------------------------------------------------------------------
    # print(f' 3. "{token}" -> ', end='')
    token = ('A' if token[0] in 'aeiou' else '') + token
    # print(f'"{token}"')

    # Step 04 ------------------------------------------------------------------
    hVowelCombos = {
        'ehe': ['eHe', 'H'],
        'eh': ['eH', 'H'],
        'oh': ['oH', 'H'],
        'h': ['H'],
    }
    # print(f' 4. "{token}" -> ', end='')
    tokenList = permuteAllOccurrences([token], hVowelCombos)
    # print(f'{tokenList}')

    # Step 05 ------------------------------------------------------------------
    yehEndings = {
        'ey': 'Y',
        'ay': "E",
    }
    # print(f' 5. {tokenList} -> ', end='')
    tokenList = [replaceEnding(token, yehEndings, 2) for token in tokenList]
    # print(f'{tokenList}')

    # Step 06 ------------------------------------------------------------------
    yVowelCombos = {
        'ey': ['Y', 'eY'],
        'ay': ['Y', 'aY'],
    }
    # print(f' 6. {tokenList} -> ', end='')
    tokenList = permuteAllOccurrences(tokenList, yVowelCombos)
    # print(f'{tokenList}')

    # Step 07 ------------------------------------------------------------------
    # print(f' 7. {tokenList} -> ', end='')
    tokenList = [w.replace('y', 'Y') for w in tokenList]
    # print(f'{tokenList}')

    # Step 08 ------------------------------------------------------------------
    iEndings = {
        'ai': ['E', 'aYi', 'aAi'],
        'ei': ['E', 'eYi', 'eAi'],
    }
    # print(f' 8. {tokenList} -> ', end='')
    tokenList = permuteAllEndings(tokenList, iEndings)
    # print(f'{tokenList}')

    # Step 09 ------------------------------------------------------------------
    # print(f' 9. {tokenList} -> ', end='')
    tokenList = permuteConsecutiveVowels(tokenList)
    # print(f'{tokenList}')

    # Step 10 ------------------------------------------------------------------
    DoubleVowels = {
        'aa': ['A'],
        'ai': ['Y'],
        'ei': ['Y'],
        'ee': ['Y'],
        'ie': ['Y'],
        'oo': ['O'],
        'au': ['O'],
        'ou': ['O'],
    }
    # print(f'10. {tokenList} -> ', end='')
    tokenList = permuteAllOccurrences(tokenList, DoubleVowels)
    # print(f'{tokenList}')

    # Step 11 ------------------------------------------------------------------
    VowelEndings = {
        'e': 'E',
        'a': 'AH',
        'i': 'Y',
        'u': 'O'
    }
    # print(f'11. {tokenList} -> ', end='')
    tokenList = permuteAllEndings(tokenList, VowelEndings)
    # print(f'{tokenList}')

    # Step 12 ------------------------------------------------------------------
    VowelReplacements = {
        'a': ('', 'A'),
        'i': ('', 'Y'),
        'u': ('', 'O'),
        'e': ('E',),
        'o': ('O',),
    }
    # print(f'12. {tokenList} -> ', end='')
    tokenList = permuteAllOccurrences(tokenList, VowelReplacements)
    # print(f'{tokenList}')

    return {w for w in tokenList}


# ******************************************************************************
Urdu2RomanEncodingMap = {
    '\u0627': 'A',
    '\u0639': 'A',
    '\u0622': 'AA',
    '\u0623': 'A',
    '\u0628': 'B',
    '\u067E': 'P',
    '\u062a': 'T',
    '\u0637': 'T',
    '\u0679': 'T',
    '\u06C3': 'T',
    '\u062c': 'J',
    '\u062b': 'S',
    '\u0633': 'S',
    '\u0635': 'S',
    '\u0686': 'CH',
    '\u062d': 'H',
    '\u06c1': 'H',
    '\u06c2': 'H',
    '\u06be': 'H',
    '\u0647': 'H',
    '\u062e': 'KH',
    '\u062f': 'D',
    '\u0688': 'D',
    '\u0630': 'Z',
    '\u0632': 'Z',
    '\u0636': 'Z',
    '\u0638': 'Z',
    '\u0698': 'Z',
    '\u0631': 'R',
    '\u0691': 'R',
    '\u0634': 'SH',
    '\u063a': 'GH',
    '\u0641': 'F',
    '\u06A9': 'K',
    '\u0642': 'Q',
    '\u06af': 'G',
    '\u0644': 'L',
    '\u0645': 'M',
    '\u0646': 'N',
    '\u06ba': 'N',
    '\u0648': 'O',
    '\u0624': 'O',
    '\u06CC': 'Y',
    '\u0621': 'Y',
    '\u0626': 'Y',
    '\u064A': 'Y',
    '\u06d2': 'E',
}


# ******************************************************************************
def tafseerUrduAr2Rm(word: str) -> tuple[str, int]:
    """Convert arabic script Urdu word to roman script"""
    assert isinstance(word, str), type(word)

    # Split all spaced tokens
    tokens = word.strip().split(' ')
    if not tokens:
        return '', -1

    # for each token
    #   translate each character to its roman equivalent,
    #   leave any other character unchanged
    romanizedTokens = []
    undefCount = 0

    for token in tokens:
        romanizedToken = ''

        # Treat Wow at beginning as consonant
        if token.startswith('\u0648'):
            token = token[1:]
            romanizedToken = 'W'

        for char in token:
            if char in Urdu2RomanEncodingMap:
                romanizedToken = romanizedToken + Urdu2RomanEncodingMap[char]
            else:
                print(f"'{char}' U+[{ord(char):04X}] in {token}[{word}] has undefined romanization")
                romanizedToken = romanizedToken + char
                undefCount += 11
        romanizedTokens.append(romanizedToken)

    return ' '.join(romanizedTokens), undefCount


# ******************************************************************************
# Single Character Mapping
Roman2UrduEncodingMap01 = {
    'A': ['\u0627', '\u0639'],
    'B': ['\u0628'],
    'P': ['\u067E'],
    'T': ['\u062a', '\u0637', '\u0679', '\u06c3'],
    'J': ['\u062c'],
    'S': ['\u062b', '\u0633', '\u0635'],
    'H': ['\u062d', '\u06c1', '\u06be'],
    'D': ['\u062f', '\u0688'],
    'Z': ['\u0630', '\u0632', '\u0636', '\u0638', '\u0698'],
    'R': ['\u0631', '\u0691'],
    'F': ['\u0641'],
    'K': ['\u06A9', '\u0642', '\u0643'],
    'G': ['\u06af'],
    'L': ['\u0644'],
    'M': ['\u0645'],
    'N': ['\u0646', '\u06ba'],
    'V': ['\u0648'],
    'W': ['\u0648'],
    'O': ['\u0648'],
    'Y': ['\u06CC', '\u0621'],
    'E': ['\u06d2'],
}

# Double Character Mapping
Roman2UrduEncodingMap02 = {
    'CH': ['\u0686', '\u0686\u06be'],
    'KH': ['\u062e', '\u06a9\u06be', '\u06a9\u06c1', '\u0642\u06c1'],
    'SH': ['\u0634'],
    'GH': ['\u063a'],
}

# ******************************************************************************
def roximnUrduRm2Ar(word: str) -> set[str]:
    """Convert a roman script Urdu word to arabic script,
    with permutations of all possible corresponding alphabets having multiple
    representations.
    """
    assert isinstance(word, str), type(word)

    # Trim extra space
    token = word.strip().upper()
    if not token:
        return {''}

    if token.startswith('AA') :
        token = '\u0622' + token[2:]

    # Process double character representations before single character ones
    arabizedTokens = permuteAllOccurrences(
        tokenList=permuteAllOccurrences(
            tokenList=[token],
            mapping=Roman2UrduEncodingMap02),
        mapping=Roman2UrduEncodingMap01)

    # Replace Hamza followed by Choti-ye and Bari-ye to joining Hamza over yeh
    # at the end of the words
    for i, permutedToken in enumerate(arabizedTokens):
        if permutedToken.endswith('\u0621\u06cc') :
            arabizedTokens[i] = permutedToken[:-2] + '\u0626\u06cc'
        elif permutedToken.endswith('\u0621\u06d2') :
            arabizedTokens[i] = permutedToken[:-2] + '\u0626\u06d2'

    return {w for w in arabizedTokens}


# ******************************************************************************
if __name__ == '__main__':
    for word in ('bhai', 'bukhar', 'hai', 'bhayi', 'shohrat'):
        processedWords = tafseerUrduRm2Rm(word)
        print(f'{word} -> {[w.lower() for w in processedWords]}')
        arabizedWords = {x for w in processedWords for x in roximnUrduRm2Ar(w)}
        print(f'{len(arabizedWords)}: {arabizedWords}')
