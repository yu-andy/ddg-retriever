import codecs
import csv
import logging
import os

from ddg.query import Query
from ddg.search_result_list import SearchResultList
from util.exceptions import IllegalArgumentError

logger = logging.getLogger("ddg-retriever_logger")


class QueryList(object):
    """ List of search queries. """

    def __init__(self):
        self.filename = ""
        self.values = []
        self.search_results = SearchResultList()

    def read_from_csv(self, input_file, exact_matches, replace_parentheses, delimiter):
        """
        Read search queries from a CSV file (header required).
        :param replace_parentheses: Replace Wikipedia parentheses in query strings
        :param exact_matches: Only search for exact matches of query strings
        :param input_file: Path to the CSV file.
        :param delimiter: Column delimiter in CSV file (typically ',').
        """

        # read CSV as UTF-8 encoded file (see also http://stackoverflow.com/a/844443)
        with codecs.open(input_file, encoding='utf8') as fp:
            logger.info("Reading search queries from " + input_file + "...")

            reader = csv.reader(fp, delimiter=delimiter)

            # read header
            header = next(reader, None)
            if not header:
                raise IllegalArgumentError("Missing header in CSV file.")

            query = header.index("query")

            # read CSV file
            for row in reader:
                if row:
                    self.values.append(
                        Query(row[query], exact_matches, replace_parentheses)
                    )
                else:
                    raise IllegalArgumentError("Wrong CSV format.")

        self.filename = os.path.basename(input_file)
        logger.info(str(len(self.values)) + " search queries have been imported.")

    def retrieve_search_results(self, max_results, min_wait, max_wait, detect_languages):
        for query in self.values:
            query.retrieve_search_results(max_results, min_wait, max_wait)
            if detect_languages:
                query.search_results.detect_languages()
            for search_result in query.search_results.values:
                self.search_results.values.append(search_result)

    def write_search_results_to_csv(self, output_dir, delimiter, include_language):
        """
        Export search results to a CSV file.
        :param include_language: Add column "language" if tool was configured to detect languages of snippets
        :param output_dir: Target directory for generated CSV file.
        :param delimiter: Column delimiter in CSV file (typically ',').
        """
        self.search_results.write_to_csv(output_dir, delimiter, include_language, self.filename)
