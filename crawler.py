import requests
import feedparser
import re
import csv

from bs4 import BeautifulSoup


class Holding(object):
    """
    POPO (is that a thing? it should be a thing) which can return itself as an array, and a method for the headers
    of the output file
    """
    def __init__(self, name_of_issuer, title_of_class, cusip, value, ssh_prnamt, ssh_prnamt_type, investment_discretion,
                 other_manager, voting_authority_sole, voting_authority_shared, voting_authority_none):
        self.nameOfIssuer = name_of_issuer
        self.titleOfClass = title_of_class
        self.cusip = cusip
        self.value = value
        self.sshPrnamt = ssh_prnamt
        self.sshPrnamtType = ssh_prnamt_type
        self.investmentDiscretion = investment_discretion
        self.otherManager = other_manager
        self.votingAuthoritySole = voting_authority_sole
        self.votingAuthorityShared = voting_authority_shared
        self.votingAuthorityNone = voting_authority_none

    @staticmethod
    def get_headers():
        return [
            'nameOfIssuer',
            'titleOfClass',
            'cusip',
            'value',
            'sshPrnamt',
            'sshPrnamtType',
            'investmentDiscretion',
            'otherManager',
            'votingAuthoritySole',
            'votingAuthorityShared',
            'votingAuthorityNone'
        ]

    def to_array(self):
        return [
            self.nameOfIssuer,
            self.titleOfClass,
            self.cusip,
            self.value,
            self.sshPrnamt,
            self.sshPrnamtType,
            self.investmentDiscretion,
            self.otherManager,
            self.votingAuthoritySole,
            self.votingAuthorityShared,
            self.votingAuthorityNone
        ]


def _file_to_holding_array(path):
    """
    used for testing mostly, given a tsv file name, convert it into an array of Holding objects
    :param path:
    :return:
    """
    to_return = []

    with open(path, 'r', newline='') as handle:
        tsvreader = csv.reader(handle, delimiter='\t')

        for row in tsvreader:
            holding = Holding(*row)
            to_return.append(holding)

    return to_return[1:]  # ignore the first line because it is the headers row


def _get_string_or_empty_string(elem, *args):
    """
    helper method for getting the string contents of a BeautifulSoup Tag's subtag, or nth subtag
    :param elem:
    :param args:
    :return:
    """
    for arg in args:
        if elem is None:
            return ''

        elem = getattr(elem, arg, None)

    return getattr(elem, 'string', None) or ''


def generate_report_for_ticker(ticker, output_path):
    """
    interface for downloading, processing and writing the 13f report to the specified output file
    :param ticker:
    :param output_path:
    :return:
    """
    doc = find_13f_report(ticker)

    holding_array = parse_13f_doc(doc)

    write_holding_array_to_file(holding_array, output_path)

    return holding_array


def write_holding_array_to_file(holding_array, output_path):
    """
    given an array of Holding objects, write the tsv to the provided output file
    :param holding_array:
    :param output_path:
    :return:
    """
    with open(output_path, 'w', newline='') as output_handle:
        tsvout = csv.writer(output_handle, delimiter='\t')

        tsvout.writerow(Holding.get_headers())

        for holding in holding_array:
            tsvout.writerow(holding.to_array())


def parse_13f_doc(report_13f):
    """
    given the downloaded 13f report, create and return a Holding object for each info table entry

    :param report_13f:
    :return:
    """
    to_return = []

    xml_soup = BeautifulSoup(report_13f, 'xml')

    for info_table_elem in xml_soup.find_all('infoTable'):
        info_table_holding = Holding(
            _get_string_or_empty_string(info_table_elem, 'nameOfIssuer'),
            _get_string_or_empty_string(info_table_elem, 'titleOfClass'),
            _get_string_or_empty_string(info_table_elem, 'cusip'),
            _get_string_or_empty_string(info_table_elem, 'value'),
            _get_string_or_empty_string(info_table_elem, 'shrsOrPrnAmt', 'sshPrnamt'),
            _get_string_or_empty_string(info_table_elem, 'shrsOrPrnAmt', 'sshPrnamtType'),
            _get_string_or_empty_string(info_table_elem, 'investmentDiscretion'),
            _get_string_or_empty_string(info_table_elem, 'otherManager'),

            _get_string_or_empty_string(info_table_elem, 'votingAuthority', 'Sole'),
            _get_string_or_empty_string(info_table_elem, 'votingAuthority', 'Shared'),
            _get_string_or_empty_string(info_table_elem, 'votingAuthority', 'None')
        )

        to_return.append(info_table_holding)

    return to_return


def find_13f_report(ticker):
    """
    to retrieve the 13f report,
     1. find the company's latest 13f filing
     2. parse the filing page for the complete submission text file link
     3. download the complete submission text file

    :param ticker:
    :return:
    """
    edgar_search_rss_url = \
        'https://www.sec.gov/cgi-bin/browse-edgar' \
        '?action=getcompany&CIK={}&type=13f%&dateb=&owner=exclude&start=0&count=50&output=atom' \
            .format(ticker)

    edgar_search_rss_request = requests.get(edgar_search_rss_url)

    if not edgar_search_rss_request.ok:
        raise ValueError('failed to download rss feed for ticker or cik at: {}'.format(edgar_search_rss_url))

    target_rss = feedparser.parse(edgar_search_rss_request.text)

    if len(target_rss['entries']) == 0:
        raise ValueError('no filings for ticker or cik')

    target_entry = None

    for entry in target_rss['entries']:
        if entry['filing-type'] == '13F-HR':
            target_entry = entry

            break

    if target_entry is None:
        raise ValueError('failed to find a 13F-HR filing in the company\'s most recent 50 filings')

    edgar_archive_report_url = target_entry['link']

    edgar_archive_request = requests.get(edgar_archive_report_url)

    if not edgar_archive_request.ok:
        raise ValueError('failed to download filing detail at: {}'.format(edgar_archive_report_url))

    soup = BeautifulSoup(edgar_archive_request.text, 'html.parser')

    complete_submission_text_file_element = soup.find('a', href=re.compile('txt'))

    complete_submission_text_file_url = 'https://www.sec.gov{}'\
        .format(complete_submission_text_file_element.attrs['href'])

    complete_submission_text_file_request = requests.get(complete_submission_text_file_url)

    if not complete_submission_text_file_request.ok:
        raise ValueError('failed to download complete submission text file at: {}'
                         .format(complete_submission_text_file_url))

    complete_submission_text_file_content = complete_submission_text_file_request.text

    return complete_submission_text_file_content


if __name__ == '__main__':
    examples = [
        '0000102909',  # vanguard group inc -- has amendments
        '0001166559',  # gates foundation
        '0001350694',  # bridgewater associates lp
        '0001103804',  # VIKING GLOBAL INVESTORS LP,
        '0001067983',  # berkeshire hathaway -- has amendments
        '0001483238',  # montage investments
        '0001625246',  # summit financial strategies
        '0001567755',  # private advisor group
        '0001351903',  # sii investments
        '0001492262'   # national planning corp
    ]

    # attention grader: change the input of this method to test any of the examples above

    generate_report_for_ticker('0000102909', 'output/asdf.tsv')
