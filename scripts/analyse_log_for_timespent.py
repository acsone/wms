#!/usr/bin/env python
import re
import sys
from collections import namedtuple

ModuleInfo = namedtuple("ModuleInfo", ["name", "time_spent", "number_of_queries"])


def get_time_by_addon(log_file_path):
    """Get the time in minutes spent to load each addon.

    We only consider
    the time where it exceeds 1 minute.

    We search in the log file for the following pattern:

    2023-03-23 07:19:36,355 286521 INFO alcyon-16-postmig odoo.modules.loading: Module product_state loaded in 193.30s, 70440 queries (+70440 other)

    where:
    * the time spent is: 193.30s
    * the number of queries is: 70440
    * the module name is: product_state
    We return a list of tuples (module_name, time_spent, number_of_queries)
    ordered by time spent. (highest first)
    """
    # we define a regex to extract all the information we need
    regex = re.compile(
        r".* odoo\.modules\.loading: Module (?P<module_name>\w+) loaded in (?P<time_spent>\d+\.\d+)s, (?P<number_of_queries>\d+) queries.*"
    )
    # read the log file
    with open(log_file_path) as log_file:
        lines = log_file.readlines()
        module_infos = []
        for line in lines:
            # We check if the line matches the pattern we are looking for
            match = regex.match(line)
            if match:
                # We have a line with the pattern we are looking for
                # We extract the module name
                module_name = match.group("module_name")
                # We extract the time spent
                time_spent = float(match.group("time_spent"))
                # We transform the time spent in minutes
                time_spent = time_spent / 60
                if time_spent < 1:
                    # We do not consider the time spent if it is less than 1 minute
                    continue
                # We extract the number of queries
                number_of_queries = int(match.group("number_of_queries"))
                module_infos.append(
                    ModuleInfo(module_name, time_spent, number_of_queries)
                )
        # We sort the list by time spent (highest first)
        module_infos.sort(key=lambda x: x.time_spent, reverse=True)
        return module_infos


if __name__ == "__main__":
    # get file path from command line
    log_file_path = sys.argv[1]
    # get the time spent by addon
    module_infos = get_time_by_addon(log_file_path)
    # print the result
    for module_info in module_infos:
        print(
            f"{module_info.name}: {module_info.time_spent:.2f} minutes, {module_info.number_of_queries} queries"
        )
