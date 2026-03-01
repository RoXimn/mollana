# ******************************************************************************
# Copyright (c) 202. All rights reserved.
#
# This work is licensed under the Creative Commons Attribution 4.0 International License.
# To view a copy of this license, visit # http://creativecommons.org/licenses/by/4.0/.
#
# Author:      RoXimn <roximn@rixir.org>
# ******************************************************************************
"""Collection of miscellaneous helper functions.

This module contains assorted helper functions which do not yet have a
separate module.
"""
# ******************************************************************************
import re
from unittest import result

import unicodedata
import string
import xml.etree.ElementTree as ET

from fast_langdetect import detect


# ******************************************************************************
MinimumValidChars: str = "-_.()" + string.ascii_letters + string.digits
"""Set of characters which can be universally used in names and titles."""
FilenameCharLimit: int = 255
"""Upper limit to filename length."""

# ******************************************************************************
def tms(x: int | float) -> int:
    """Convert seconds to milliseconds (int)"""
    return int(x * 1000)


# ******************************************************************************
def hmsTimestamp(milliseconds: int, srtFormat: bool = False,
                 shorten: bool = False, useDays: bool = False,
                 fixedPrecision: bool = False) -> str:
    """
    Converts milliseconds to timestamp format (HH:MM:SS,ms).

    Args:
      milliseconds (int): An integer representing the time in milliseconds.
      srtFormat (bool): Use comma for millisecond seperator
      shorten (bool): Skip leading empty values.
      useDays (bool): Resolve hours into days
      fixedPrecision (bool): Use fixed precision for milliseconds

    Returns:
      Timestamp formated as (HH:MM:SS.ms) by default. Alternatively, (HH:MM:SS,ms).
    """
    seconds, milliseconds = divmod(int(milliseconds), 1000)
    minutes, seconds = divmod(seconds, 60)
    hours, minutes = divmod(minutes, 60)

    if srtFormat:
        return f"{hours:02}:{minutes:02}:{seconds:02},{milliseconds:03}"

    if useDays:
        days, hours = divmod(hours, 24)
    else:
        days = 0

    if shorten:
        timestamp = ''
        if days:
            timestamp += f"{days}d "
        if hours:
            timestamp += f"{hours}:{minutes}:"
        elif minutes:
            timestamp += f"{minutes}:"

        if fixedPrecision:
            timestamp += f"{seconds + milliseconds / 1000.0:.3f}"
        else:
            timestamp += f"{round(seconds + milliseconds / 1000.0, 3)}"

    elif useDays:
        timestamp = f"{days}d {hours:02}:{minutes:02}:{seconds:02}.{milliseconds:03}"
    else:
        timestamp = f"{hours:02}:{minutes:02}:{seconds:02}.{milliseconds:03}"

    return timestamp


# ******************************************************************************
def isValidProjectName(name: str) -> bool:
    """Check the given name is valid to be used as a filename

    The name should be non-zero length of ascii upper(A-Z) and lower case(a-z)
    characters, digits (0-9), and `Space` character, in any order. The validation
    is done *after* stripping any leading or trailing whitespace from the given
    string.

    Args:
        name (str): the name to be validated. Validation is done *after*
            stripping any leading or trailing whitespace.

    Returns:
        bool: True if valid, False otherwise.
    """
    assert isinstance(name, str)
    return bool(re.search('^[A-Za-z0-9 _-]+$', name.strip()))


# ******************************************************************************
def slugify(name: str, whitelist: str = MinimumValidChars, replace: str = ' ') -> str:
    """Reduce given string to acceptable set of characters

    .. note::

        A *slug* is a short label for something, containing only letters, numbers,
        underscores or hyphens (as in `Django` docs).

    The characters matching the `replace` string characters are replaced,
    followed by *decomposed normalization* to `ASCII` characters,
    then the whitelisted characters are filtered
    and lastly the name length is truncated to :py:const:`~rekhtanavees.misc.FilenameCharLimit`.

    Args:
        name (str): the string to *slugify*.
        whitelist (str): the set of allowed characters
        replace (str): the characters to be replaced with *hyphen*
    """
    # replace spaces
    for r in replace:
        name = name.replace(r, '-')

    # keep only valid ascii chars
    slug = unicodedata.normalize('NFKD', name).encode('ASCII', 'ignore').decode()

    # keep only whitelisted chars
    slug = ''.join(c for c in slug if c in whitelist)

    # Truncate to maximum allowed characters
    return slug[:FilenameCharLimit]

# ******************************************************************************
def extractUrduText(xmlInputPath, txtOutputPath):
    """
    Parses an XML file and extracts text from <body> tags
    identified as Urdu using fast-langdetect.
    """
    try:
        # Parse the XML file
        tree = ET.parse(xmlInputPath)
        root = tree.getroot()

        urduSentences = []

        # root.iter() visits every node in the XML tree recursively
        for elem in root.iter():
            # Check if the element contains text
            if elem.text and elem.text.strip():
                cleanText = elem.text.strip()

                # Use fast-langdetect to identify the language
                # Returns 'ur' for Urdu
                result = detect(cleanText, model='full')

                if result:
                    for lang in result:
                        if lang.get('lang') == 'ur':
                            urduSentences.append(cleanText)

        # Write to a UTF-8 encoded text file
        with open(txtOutputPath, 'w', encoding='utf-8') as f:
            for line in urduSentences:
                f.write(line + '\n')

        print(f"Successfully extracted {len(urduSentences)} Urdu entries to {txtOutputPath}")

    except ET.ParseError as e:
        print(f"Error parsing XML: {e}")
    except Exception as e:
        print(f"An error occurred: {e}")


# Usage
if __name__ == "__main__":
    extractUrduText("0001.xml", "0001.txt")

# ******************************************************************************
