from random import choice
from config.cities import data as valid_cities


def domain_builder(search, section, filters, cities=(choice(valid_cities),)):
    """
    Return 0: Array of domains
    Return 1: Array of cities

    Section: 'sss' = all
             'cta' = cars all
             'cto' = cars owner
             'syp' = computer parts
             'sya' = computers
             'ela' = electronics
             'zip' = free stuff
    """

    domains = []
    cities_list = []

    domain_search = '?query={}'.format(search)

    for city in cities:
        domains.append('https://' + city + '.craigslist.org/search/' + section + domain_search + ''.join(filters))
        cities_list.append(city)

    return domains, cities_list
