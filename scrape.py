import requests
import json
import argparse
import sys
from bs4 import BeautifulSoup


def handle_person_keys(sport_row_header):
    person_keys_arizona = ['sport', 'name',
                           'position', 'room', 'phone', 'email']
    person_keys_seattle = ['sport', 'name', 'position', 'email', 'phone']
    person_keys_arkansas = ['sport', 'name', 'position', 'phone', 'email']

    sport_row = sport_row_header.parent
    # sport name is on the second level of row's children
    # for Arizona and Seattle
    if sport_row.name == 'td':
        # Arizona's sport name td has neighbors at the same level
        next_sibling = sport_row.find_next_sibling('td')
        if next_sibling and next_sibling.name:
            person_keys = person_keys_arizona
        else:
            # Arkansas's sport name td has no other elements at the same level
            person_keys = person_keys_arkansas
        # tr is parent on td; this is required step to move to the next row
        sport_row = sport_row.parent
    else:
        # sport name is on the first level of row's children
        # for Arizona and Seattle
        person_keys = person_keys_seattle
    return sport_row, person_keys


def prepare_output(sport_row_header):
    sport_row, person_keys = handle_person_keys(sport_row_header)
    current_person_raw = sport_row.find_next_sibling('tr')
    # handle case when sport name is invalid, for example "name"
    if not current_person_raw:
        return None

    current_person_info = current_person_raw.find_all(['td', 'th'])
    output = []
    while True:
        current_person = {}
        i = 0
        # current_person["sport"] = sport
        current_person[person_keys[i]] = sport_row_header.text
        i += 1
        for item in current_person_info:
            # take a phone or email from href if exists
            value = item.select_one(
                "a[href^='mailto:']") or item.select_one("a[href^='tel:']")
            if value is None:
                # take text if item has neither mail nor phone in href
                current_person[person_keys[i]] = item.text.strip()
            else:
                # get rid of 'mailto' or 'tel' and take only email or phone
                _, value = value['href'].split(':')
                # replace unicode representation of hyphen and space characters
                value = value.replace('\u2010', '-').replace('%20', '')
                current_person[person_keys[i]] = value
            i += 1
        output.append(current_person)
        current_person_raw = current_person_raw.find_next_sibling('tr')
        # first condition is to break loop on the end of table (specified
        # sport is last sport in table)
        # second condition is for Arizona's to break loop
        # when next sport encounters
        if not current_person_raw or not current_person_raw.find(['a', 'img']):
            break
        current_person_info = current_person_raw.find_all(['td', 'th'])
    return output


def handle_command_line_arguments(
        soup, html_element, html_element_id, html_element_class,
        html_element_index, sport):
    sport_row_header = None
    # cases when html-element is specified
    if html_element:
        all_specified_elements = soup.find_all(html_element)
        # subcase when also html-element-id is specified
        if html_element_id:
            sport_row_header = handle_element_and_id(
                all_specified_elements, html_element_id, sport)
        # subcase when also html-element-class is specified
        elif html_element_class:
            sport_row_header = handle_element_and_class(
                all_specified_elements, html_element_class, sport)
        # subcase when also html-element-index is specified
        elif html_element_index:
            sport_row_header = handle_element_and_index(
                all_specified_elements, html_element_index, sport)
        # case when only html-element is specified
        else:
            sport_row_header = find_sport_row_header_in_all_specified_elements(
                all_specified_elements, sport)
    # cases when only html-element-id is specified
    elif html_element_id:
        sport_row_header = handle_only_id(soup, html_element_id, sport)
    # cases when only html-element-class is specified
    elif html_element_class:
        sport_row_header = handle_only_class(soup, html_element_class, sport)
    # case when only required arguments are specified
    else:
        sport_row_header = find_sport_row_header_in_all_specified_elements(
            soup, sport)
    return sport_row_header


def find_sport_row_header_in_all_specified_elements(
        all_specified_elements, sport):
    # example is case when specified html-element has multiple apperances
    # on page, e.g."tr"
    if isinstance(all_specified_elements, list):
        for specified_element in all_specified_elements:
            # case when specified_element is one which contains specified
            # sport on the same level
            if (len(specified_element.find_all(recursive=False)) == 0 and
                    specified_element.name in ['center', 'th', 'strong']
                    and specified_element.text.lower() == sport):
                return specified_element
            # case when specified sport is possibly
            # inside the specified_element
            sport_row_header = specified_element.find(
                ['center', 'th', 'strong'],
                text=lambda x: x and x.lower() == sport)
            # sport found
            if sport_row_header:
                return sport_row_header
    # example is case when only required arguments are specified
    else:
        if (len(all_specified_elements.find_all(recursive=False)) == 0
                and all_specified_elements.text.lower() == sport):
            return all_specified_elements
        else:
            return all_specified_elements.find(
                ['center', 'th', 'strong'],
                text=lambda x: x and x.lower() == sport)
    return None


def handle_element_and_id(all_specified_elements, html_element_id, sport):
    element_id = None
    for specified_element in all_specified_elements:
        # specified element is one with specified id
        if html_element_id == specified_element.get('id'):
            return find_sport_row_header_in_all_specified_elements(
                specified_element, sport)
        else:
            # child of the specified element has specified id
            element_id = specified_element.find(id=html_element_id)
            # html-element-id is unique per page
            if element_id:
                return find_sport_row_header_in_all_specified_elements(
                    element_id, sport)

    return None


def handle_element_and_class(
        all_specified_elements, html_element_class, sport):
    for specified_element in all_specified_elements:
        # specified element is one which contains specified class
        specified_element_classes = specified_element.get('class')
        if (specified_element_classes is not None
                and html_element_class in specified_element_classes):
            sport_row_header = find_sport_row_header_in_all_specified_elements(
                specified_element, sport)
            if sport_row_header:
                return sport_row_header
        else:
            # children which contains specified class
            # for current specified element
            all_spec_elements = specified_element.find_all(
                class_=html_element_class)
            if all_spec_elements:
                sport_row_header = find_sport_row_header_in_all_specified_elements(
                    all_spec_elements, sport)
                # specified class possibly can have multiple appereance
                # and because of that we break loop only if sport is found
                if sport_row_header:
                    return sport_row_header
    return None


def handle_element_and_index(
        all_specified_elements, html_element_index, sport):
    for specified_element in all_specified_elements:
        # array numeration
        i = 0
        # only direct children of specified element
        children = specified_element.find_all(recursive=False)
        for child in children:
            if i == int(args.html_element_index):
                return find_sport_row_header_in_all_specified_elements(
                    child, sport)
            i += 1
    # case when number is invalid
    return None


def handle_only_id(soup, html_element_id, sport):
    element_id = soup.find(id=html_element_id)
    if element_id:
        return find_sport_row_header_in_all_specified_elements(
            element_id, sport)
    return None


def handle_only_class(soup, html_element_class, sport):
    all_spec_elements = soup.find_all(class_=html_element_class)
    if all_spec_elements:
        return find_sport_row_header_in_all_specified_elements(
            all_spec_elements,
            sport)
    return None


parser = argparse.ArgumentParser()
# three group of arguments, required arguments are first group...
required = parser.add_argument_group('required arguments')
required.add_argument(
    '--url', help="The Staff Directory page URL to be scraped", required=True)
required.add_argument(
    '--sport',
    help="The sport name to be filtered (case insensitive, e.g. 'volleyball')",
    required=True)

# ...optional arguments are second group
optional = parser.add_argument_group('optional arguments')
optional.add_argument(
    '--html-element',
    help="The name of the HTML element to be " +
    "searched for (e.g. 'tr'' or 'table')")

# ... and optional mutually exclusive arguments are third group
mutually_exclusive = optional.add_mutually_exclusive_group()
mutually_exclusive.add_argument(
    '--html-element-id',
    help="Id of the specified HTML element to be searched for (e.g. 'Table1')")
mutually_exclusive.add_argument(
    '--html-element-index',
    help="Index of the specified HTML element to be searched for (e.g. '1')")
mutually_exclusive.add_argument(
    '--html-element-class',
    help="Style class of the specified HTML element to be " +
    "searched for (e.g. 'sport-name')")

args = parser.parse_args()
sport = args.sport.lower()
# Validation for dependency between html-element and html-element-index
if args.html_element_index and not args.html_element:
    print("html-element-index cannot be specified without an html-element")
    sys.exit(1)

# for astateredwolves's .aspx page
headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64)'}
# get specified url
try:
    r = requests.get(args.url, headers=headers)
except:
    print(f'Page {args.url} not found. Please check url and try again.')
    sys.exit(1)

# parse specified page
soup = BeautifulSoup(r.text, 'lxml')
all_soups = [soup]
# used lambda instead of regex for better performance
sport_row_header = handle_command_line_arguments(
    soup, args.html_element, args.html_element_id, args.html_element_class,
    args.html_element_index, sport)

# Sport found inside of specified page, no need for iframes
if sport_row_header:
    output = prepare_output(sport_row_header)
    if not output:
        print(
            f'There is no staff for {args.sport}. Please check ' +
            'your specified parameters and try again.')
        sys.exit(1)
    # convert python dictionary "output" to string formatted as JSON
    print(json.dumps(output, indent=4))
# Sport not found inside of specified page, search continues in iframes
else:
    all_soups.pop()
    # find all iframes
    iframes = soup.find_all('iframe')
    for iframe in iframes:
        # get current iframe
        try:
            r = requests.get(iframe.attrs['src'], headers=headers)
        except:
            # missing schema, page not found, ...
            continue
        # parse current frame
        soup = BeautifulSoup(r.text, 'lxml')
        all_soups.append(soup)

    # there is no embedded iframes inside main page
    if len(all_soups) == 0:
        print(
            f'There is no staff for {args.sport}. Please check ' +
            'your specified parameters and try again.')
        sys.exit(1)

    # search one by one parsed iframe
    for soup in all_soups:
        sport_row_header = handle_command_line_arguments(
            soup, args.html_element, args.html_element_id, args.
            html_element_class, args.html_element_index, sport)
        # move to the next parsed iframe if specified sport
        # isn't in current iframe
        if not sport_row_header:
            continue
        # if execution comes here it means that current
        # iframe contains specified sport
        output = prepare_output(sport_row_header)
        if not output:
            print(
                f'There is no staff for {args.sport}. Please check ' +
                'your specified parameters and try again.')
            sys.exit(1)
        # convert python dictionary "output" to string formatted as JSON
        print(json.dumps(output, indent=4))
        break

    # case when specified sport is not in iframes
    if not sport_row_header:
        print(
            f'There is no staff for {args.sport}. Please check your ' +
            'specified parameters and try again.')
