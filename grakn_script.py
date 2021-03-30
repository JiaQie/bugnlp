from grakn.client import GraknClient
import csv

def load_data_into_grakn(inputs, session):
    items = parse_data_to_dictionaries(inputs)
    for item in items:
        with session.transaction().write() as transaction:
            graql_insert_query = inputs["template"](item)
            print("Executing Graql Query: " + graql_insert_query)
            transaction.query(graql_insert_query)
            transaction.commit()

    print("\nInserted " + str(len(items)) + " items from [ " + inputs["data_path"] + "] into Grakn.\n")

def build_bug_graph(inputs):
    with GraknClient(uri = 'localhost:48555') as client:
        with client.session(keyspace = 'bug_graph3') as session:
            for input in inputs:
                print('Loading from [' + input['data_path'] + '] into Grakn ... ')
                load_data_into_grakn(input,session)

def bigram_template(bigram):
    return 'insert $bigram isa bigram, has name "' + bigram['name'] + '";'

#to insert instances of "conincidence" where bigram_one and bigram_two conincide in the same bug report description
def coincide_template(coincide):
    # match caller
    graql_insert_query = 'match $bigram_one isa bigram, has name "' + coincide["bigram_one"] + '";'
    # match callee
    graql_insert_query += ' $bigram_two isa bigram, has name "' + coincide["bigram_two"] + '";'
    # insert call
    graql_insert_query += ' insert $coincide(bigram_one: $bigram_one, bigram_two: $bigram_two) isa coincide; $coincide has count ' + coincide["count"] + ';'
    return graql_insert_query


def parse_data_to_dictionaries(input):
    items = []
    with open(input["data_path"] + ".csv") as data: # 1
        for row in csv.DictReader(data, skipinitialspace = True):
            item = { key: value for key, value in row.items() }
            items.append(item) # 2
    return items

inputs = [
        {"data_path":"bigrams",
         "template":bigram_template
                },
         {"data_path":"coincide",
         "template":coincide_template
                 }
        ]

build_bug_graph(inputs)
