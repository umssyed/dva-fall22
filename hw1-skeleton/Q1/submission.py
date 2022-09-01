import http.client
import json
import csv
import urllib.request


#############################################################################################################################
# cse6242 
# All instructions, code comments, etc. contained within this notebook are part of the assignment instructions.
# Portions of this file will auto-graded in Gradescope using different sets of parameters / data to ensure that values are not
# hard-coded.
#
# Instructions:  Implement all methods in this file that have a return
# value of 'NotImplemented'. See the documentation within each method for specific details, including
# the expected return value
#
# Helper Functions:
# You are permitted to write additional helper functions/methods or use additional instance variables within
# the `Graph` class or `TMDbAPIUtils` class so long as the originally included methods work as required.
#
# Use:
# The `Graph` class  is used to represent and store the data for the TMDb co-actor network graph.  This class must
# also provide some basic analytics, i.e., number of nodes, edges, and nodes with the highest degree.
#
# The `TMDbAPIUtils` class is used to retrieve Actor/Movie data using themoviedb.org API.  We have provided a few necessary methods
# to test your code w/ the API, e.g.: get_movie_cast(), get_movie_credits_for_person().  You may add additional
# methods and instance variables as desired (see Helper Functions).
#
# The data that you retrieve from the TMDb API is used to build your graph using the Graph class.  After you build your graph using the
# TMDb API data, use the Graph class write_edges_file & write_nodes_file methods to produce the separate nodes and edges
# .csv files for use with the Argo-Lite graph visualization tool.
#
# While building the co-actor graph, you will be required to write code to expand the graph by iterating
# through a portion of the graph nodes and finding similar artists using the TMDb API. We will not grade this code directly
# but will grade the resulting graph data in your Argo-Lite graph snapshot.
#
#############################################################################################################################


class Graph:

    # Do not modify
    def __init__(self, with_nodes_file=None, with_edges_file=None):
        """
        option 1:  init as an empty graph and add nodes
        option 2: init by specifying a path to nodes & edges files
        """
        self.nodes = []
        self.edges = []
        if with_nodes_file and with_edges_file:
            nodes_CSV = csv.reader(open(with_nodes_file))
            nodes_CSV = list(nodes_CSV)[1:]
            self.nodes = [(n[0], n[1]) for n in nodes_CSV]

            edges_CSV = csv.reader(open(with_edges_file))
            edges_CSV = list(edges_CSV)[1:]
            self.edges = [(e[0], e[1]) for e in edges_CSV]

    def add_node(self, id: str, name: str) -> None:
        """
        add a tuple (id, name) representing a node to self.nodes if it does not already exist
        The graph should not contain any duplicate nodes
        """
        node = (id, name)
        if node not in self.nodes:
            self.nodes.append(node)

        return None

    def add_edge(self, source: str, target: str) -> None:
        """
        Add an edge between two nodes if it does not already exist.
        An edge is represented by a tuple containing two strings: e.g.: ('source', 'target').
        Where 'source' is the id of the source node and 'target' is the id of the target node
        e.g., for two nodes with ids 'a' and 'b' respectively, add the tuple ('a', 'b') to self.edges
        """
        edge = (source, target)
        if edge not in self.edges:
            self.edges.append(edge)

        return None

    def total_nodes(self) -> int:
        """
        Returns an integer value for the total number of nodes in the graph
        """
        print(f"Total Nodes: {len(self.nodes)}")
        return len(self.nodes)

    def total_edges(self) -> int:
        """
        Returns an integer value for the total number of edges in the graph
        """
        print(f"Total Edges: {len(self.edges)}")
        return len(self.edges)

    def max_degree_nodes(self) -> dict:
        """
        Return the node(s) with the highest degree
        Return multiple nodes in the event of a tie
        Format is a dict where the key is the node_id and the value is an integer for the node degree
        e.g. {'a': 8}
        or {'a': 22, 'b': 22}

        https://stackoverflow.com/questions/38555385/removing-duplicate-edges-from-graph-in-python-list
        """

        # Initialize highest degree to zero
        # Set max_degree_nodes to empty dict
        highest_degree = 0
        max_degree_nodes = {}

        # 1. Clean the edge list with no duplicates - count only one direction. Store in r_edge
        r_edge = []
        for edge in self.edges:
            if (edge[1], edge[0]) in r_edge:
                continue
            r_edge.append((edge[0], edge[1]))
        print(f"r_edge: {r_edge}")
        # 2. Create a new dict 'g' skeleton with all target nodes. 'target node':['source nodes']
        g = {edge[1]: [] for edge in r_edge}

        # 3. Populate graph. 'target node':['source nodes']
        #    Check if graph[target] has highest number of source nodes. Compare against highest_degree
        for edge in r_edge:
            source = edge[0]
            target = edge[1]
            g[target].append(source)
            if len(g[target]) > highest_degree:
                highest_degree = len(g[target])

        print(f"incident node graph g: {g}")
        # 4. Append target id with degree of nodes to max_deg_nodes dict
        max_degree_nodes = {id: len(g[id]) for id in g if len(g[id]) == highest_degree}
        return max_degree_nodes

    def print_nodes(self):
        """
        No further implementation required
        May be used for de-bugging if necessary
        """
        print(self.nodes)

    def print_edges(self):
        """
        No further implementation required
        May be used for de-bugging if necessary
        """
        print(self.edges)

    # Do not modify
    def write_edges_file(self, path="edges.csv") -> None:
        """
        write all edges out as .csv
        :param path: string
        :return: None
        """
        edges_path = path
        edges_file = open(edges_path, 'w', encoding='utf-8')

        edges_file.write("source" + "," + "target" + "\n")

        for e in self.edges:
            edges_file.write(e[0] + "," + e[1] + "\n")

        edges_file.close()
        print("finished writing edges to csv")

    # Do not modify
    def write_nodes_file(self, path="nodes.csv") -> None:
        """
        write all nodes out as .csv
        :param path: string
        :return: None
        """
        nodes_path = path
        nodes_file = open(nodes_path, 'w', encoding='utf-8')

        nodes_file.write("id,name" + "\n")
        for n in self.nodes:
            nodes_file.write(n[0] + "," + n[1] + "\n")
        nodes_file.close()
        print("finished writing nodes to csv")


class TMDBAPIUtils:

    # Do not modify
    def __init__(self, api_key: str):
        self.api_key = api_key

    def get_movie_cast(self, movie_id: str, limit: int = None, exclude_ids: list = None) -> list:
        """
        Get the movie cast for a given movie id, with optional parameters to exclude an cast member
        from being returned and/or to limit the number of returned cast members
        documentation url: https://developers.themoviedb.org/3/movies/get-movie-credits

        :param integer movie_id: a movie_id
        :param list exclude_ids: a list of ints containing ids (not cast_ids) of cast members  that should be excluded from the returned result
            e.g., if exclude_ids are [353, 455] then exclude these from any result.
        :param integer limit: maximum number of returned cast members by their 'order' attribute
            e.g., limit=5 will attempt to return the 5 cast members having 'order' attribute values between 0-4
            If after excluding, there are fewer cast members than the specified limit, then return the remaining members (excluding the ones whose order values are outside the limit range). 
            If cast members with 'order' attribute in the specified limit range have been excluded, do not include more cast members to reach the limit.
            If after excluding, the limit is not specified, then return all remaining cast members."
            e.g., if limit=5 and the actor whose id corresponds to cast member with order=1 is to be excluded,
            return cast members with order values [0, 2, 3, 4], not [0, 2, 3, 4, 5]
        :rtype: list
            return a list of dicts, one dict per cast member with the following structure:
                [{'id': '97909' # the id of the cast member
                'character': 'John Doe' # the name of the character played
                'credit_id': '52fe4249c3a36847f8012927' # id of the credit, ...}, ... ]
                Note that this is an example of the structure of the list and some of the fields returned by the API.
                The result of the API call will include many more fields for each cast member.

        """
        cast_members = []
        API_BASE_URL = f'https://api.themoviedb.org/3/movie/{movie_id}/credits?api_key={self.api_key}&language=en-US'

        # 1. Using urllib, fetch JSON data to the API_BASE_URL
        request = urllib.request.Request(API_BASE_URL)
        with urllib.request.urlopen(request) as response:
            res = response.read().decode('utf-8')
            data = json.loads(res)

        # 2. Filter JSON data by cast and store it to cast_data
        cast_data = data["cast"]

        # 3. Using the above restrictions, populate the list cast_members with dicts
        for cast in cast_data:
            if limit is None:
                if exclude_ids is None:
                    cast_members.append(cast)
                else:
                    if cast['id'] in exclude_ids:
                        continue
                    else:
                        cast_members.append(cast)
            else:
                if exclude_ids is None:
                    if cast['order'] < limit:
                        cast_members.append(cast)
                else:
                    if cast['order'] < limit:
                        if cast['id'] in exclude_ids:
                            continue
                        else:
                            cast_members.append(cast)
                    else:
                        continue



        return cast_members

    def get_movie_credits_for_person(self, person_id: str, vote_avg_threshold: float = None) -> list:
        """
        Using the TMDb API, get the movie credits for a person serving in a cast role
        documentation url: https://developers.themoviedb.org/3/people/get-person-movie-credits

        :param string person_id: the id of a person
        :param vote_avg_threshold: optional parameter to return the movie credit if it is >=
            the specified threshold.
            e.g., if the vote_avg_threshold is 5.0, then only return credits with a vote_avg >= 5.0
        :rtype: list
            return a list of dicts, one dict per movie credit with the following structure:
                [{'id': '97909' # the id of the movie credit
                'title': 'Long, Stock and Two Smoking Barrels' # the title (not original title) of the credit
                'vote_avg': 5.0 # the float value of the vote average value for the credit}, ... ]

                https://api.themoviedb.org/3/person/8/movie_credits?api_key=edc3f4b783865a2e79f271e73c1522ad&language=en-US
        """

        movies = []
        API_BASE_URL = f'https://api.themoviedb.org/3/person/{person_id}/movie_credits?api_key={self.api_key}&language=en-US'

        # 1. Using urllib, fetch JSON data to the API_BASE_URL
        request = urllib.request.Request(API_BASE_URL)
        with urllib.request.urlopen(request) as response:
            res = response.read().decode('utf-8')
            actor_data = json.loads(res)

        # 2. Using the above restrictions, populate the list movies with dicts, check vote_avg_threshold if it is not None
        for movie in actor_data['cast']:
            vote_average = movie['vote_average']
            if vote_avg_threshold == None:
                movies.append(movie)
            else:
                if vote_average >= vote_avg_threshold:
                    movies.append(movie)
        #print(f"Movies by id: {person_id}: {movies}")
        return movies


#############################################################################################################################
#
# BUILDING YOUR GRAPH
#
# Working with the API:  See use of http.request: https://docs.python.org/3/library/http.client.html#examples
#
# Using TMDb's API, build a co-actor network for the actor's/actress' highest rated movies
# In this graph, each node represents an actor
# An edge between any two nodes indicates that the two actors/actresses acted in a movie together
# i.e., they share a movie credit.
# e.g., An edge between Samuel L. Jackson and Robert Downey Jr. indicates that they have acted in one
# or more movies together.
#
# For this assignment, we are interested in a co-actor network of highly rated movies; specifically,
# we only want the top 3 co-actors in each movie credit of an actor having a vote average >= 8.0.
# Build your co-actor graph on the actor 'Laurence Fishburne' w/ person_id 2975.
#
# You will need to add extra functions or code to accomplish this.  We will not directly call or explicitly grade your
# algorithm. We will instead measure the correctness of your output by evaluating the data in your argo-lite graph
# snapshot.
#
# GRAPH SIZE
# With each iteration of your graph build, the number of nodes and edges grows approximately at an exponential rate.
# Our testing indicates growth approximately equal to e^2x.
# Since the TMDB API is a live database, the number of nodes / edges in the final graph will vary slightly depending on when
# you execute your graph building code. We take this into account by rebuilding the solution graph every few days and
# updating the auto-grader.  We establish a bound for lowest & highest encountered numbers of nodes and edges with a
# margin of +/- 100 for nodes and +/- 150 for edges.  e.g., The allowable range of nodes is set to:
#
# Min allowable nodes = min encountered nodes - 100
# Max allowable nodes = max allowable nodes + 100
#
# e.g., if the minimum encountered nodes = 507 and the max encountered nodes = 526, then the min/max range is 407-626
# The same method is used to calculate the edges with the exception of using the aforementioned edge margin.
# ----------------------------------------------------------------------------------------------------------------------
# BEGIN BUILD CO-ACTOR NETWORK
#
# INITIALIZE GRAPH
#   Initialize a Graph object with a single node representing Laurence Fishburne
#
# BEGIN BUILD BASE GRAPH:
#   Find all of Laurence Fishburne's movie credits that have a vote average >= 8.0
#   FOR each movie credit:
#   |   get the movie cast members having an 'order' value between 0-2 (these are the co-actors)
#   |
#   |   FOR each movie cast member:
#   |   |   using graph.add_node(), add the movie cast member as a node (keep track of all new nodes added to the graph)
#   |   |   using graph.add_edge(), add an edge between the Laurence Fishburne (actress) node
#   |   |   and each new node (co-actor/co-actress)
#   |   END FOR
#   END FOR
# END BUILD BASE GRAPH
#
#
# BEGIN LOOP - DO 2 TIMES:
#   IF first iteration of loop:
#   |   nodes = The nodes added in the BUILD BASE GRAPH (this excludes the original node of Laurence Fishburne!)
#   ELSE
#   |    nodes = The nodes added in the previous iteration:
#   ENDIF
#
#   FOR each node in nodes:
#   |  get the movie credits for the actor that have a vote average >= 8.0
#   |
#   |   FOR each movie credit:
#   |   |   try to get the 3 movie cast members having an 'order' value between 0-2
#   |   |
#   |   |   FOR each movie cast member:
#   |   |   |   IF the node doesn't already exist:
#   |   |   |   |    add the node to the graph (track all new nodes added to the graph)
#   |   |   |   ENDIF
#   |   |   |
#   |   |   |   IF the edge does not exist:
#   |   |   |   |   add an edge between the node (actor) and the new node (co-actor/co-actress)
#   |   |   |   ENDIF
#   |   |   END FOR
#   |   END FOR
#   END FOR
# END LOOP
#
# Your graph should not have any duplicate edges or nodes
# Write out your finished graph as a nodes file and an edges file using:
#   graph.write_edges_file()
#   graph.write_nodes_file()
#
# END BUILD CO-ACTOR NETWORK
# ----------------------------------------------------------------------------------------------------------------------

# Exception handling and best practices
# - You should use the param 'language=en-US' in all API calls to avoid encoding issues when writing data to file.
# - If the actor name has a comma char ',' it should be removed to prevent extra columns from being inserted into the .csv file
# - Some movie_credits may actually be collections and do not return cast data. Handle this situation by skipping these instances.
# - While The TMDb API does not have a rate-limiting scheme in place, consider that making hundreds / thousands of calls
#   can occasionally result in timeout errors. If you continue to experience 'ConnectionRefusedError : [Errno 61] Connection refused',
#   - wait a while and then try again.  It may be necessary to insert periodic sleeps when you are building your graph.


def return_name() -> str:
    """
    Return a string containing your GT Username
    e.g., gburdell3
    Do not return your 9 digit GTId
    """
    return 'msyed46'


def return_argo_lite_snapshot() -> str:
    """
    Return the shared URL of your published graph in Argo-Lite
    """
    url = "https://poloclub.github.io/argo-graph-lite/#76b9359e-f9a2-47d6-be1d-408dabb66053"
    return url

def list_to_dict(list_item):

    d = {item:value for item, value in list_item}
    print(f"d is : {d}")
    return d

def build_base_graph():
    movies = tmdb_api_utils.get_movie_credits_for_person(person_id='2975', vote_avg_threshold=8.0)

    for each_movie in movies:
        movie_id = each_movie['id']
        movie_cast_members = tmdb_api_utils.get_movie_cast(movie_id=movie_id, limit=3, exclude_ids=[2975])
        for cast_member in movie_cast_members:
            target_id = str(cast_member['id'])
            target_name = str(cast_member['name'])

            if target_id == '2975':
                continue
            graph.add_node(id=target_id, name=target_name)
            graph.add_edge(source='2975', target=target_id)

    count = 1

    node_dict = list_to_dict(graph.nodes)
    int_list_of_node_ids = [int(node[0]) for node in graph.nodes]
    print(f"LIST OF NODE IDS: {int_list_of_node_ids}")

    while count < 3:
        if count == 1:
            nodes = [node for node in graph.nodes if node[0] != '2975']
        else:
            pass

        # Find Highest rated movies for each actor in the nodes
        for node in nodes:
            actor_id = node[0]
            actor_name = node[1]
            #print('\n---------------------------------------------------')
            #print(f"For the actor: {actor_name} with actor_id: {actor_id}")
            highest_rated_movies = tmdb_api_utils.get_movie_credits_for_person(person_id=actor_id,
                                                                               vote_avg_threshold=8.0)

            # For each highest rated movie, find co-actors with order limit 3. Exclude starting actor.
            for movie in highest_rated_movies:
                #print(f"\nFor Highest Rated Movie: {movie['original_title']}")
                movie_id = str(movie['id'])
                cast_members = tmdb_api_utils.get_movie_cast(movie_id=movie_id, limit=3, exclude_ids=[int(actor_id)])

                for co_actor in cast_members:
                    unwanted_char = ","
                    if unwanted_char in co_actor['original_name']:
                        name = co_actor['original_name'].replace(unwanted_char, "")
                        co_actor['original_name'] = name
                        print(f"New name: {co_actor['original_name']}")

                    #print(f"ACTOR: {actor_name}, CO-ACTOR: {co_actor['name']}, CO-ACTOR ORDER: {co_actor['order']}, CO_ACTOR ID: {co_actor['id']}")
                    if co_actor['id'] not in int_list_of_node_ids:
                        #print(f"ADDING {co_actor['original_name']}")
                        graph.add_node(id=str(co_actor['id']), name=co_actor['original_name'])

                    edge = (str(actor_id), str(co_actor['id']))
                    if edge not in graph.edges:
                        #print(f"ADDING NEW EDGE {actor_name} and {co_actor['original_name']}")
                        graph.add_edge(source=str(actor_id), target=str(co_actor['id']))

        count += 1

    print(f"\nPrinting NODES: {nodes} \n and length {len(nodes)}")
    print(f"\n\nBASE GRAPH NODES:")
    graph.print_nodes()
    print(f"\nBASE GRAPH EDGES:")
    graph.print_edges()

    print("Total Nodes:", graph.total_nodes())
    print("Total Edges:", graph.total_edges())

def test_graph_nodes():
    graph.add_node(id="6384", name="Keanu Reeves")
    graph.add_node(id="110380", name="Colin Powell")
    graph.add_node(id="3087", name="Robert Duvall")
    graph.add_node(id="5139", name="Robert Englund")
    graph.add_node(id="5141", name="Heather Langenkamp")
    graph.add_node(id="74611", name="Tracee Ellis Ross")

    graph.add_edge(source="74611", target="6384")
    graph.add_edge(source="6384", target="110380")
    graph.add_edge(source="5139", target="74611")
    graph.add_edge(source="5139", target="6384")
    graph.add_edge(source="5139", target="5141")
    graph.add_edge(source="110380", target="5139")
    graph.add_edge(source="110380", target="5141")
    graph.add_edge(source="110380", target="2975")
    graph.add_edge(source="5141", target="2975")
    graph.add_edge(source="5141", target="3087")
    graph.add_edge(source="3087", target="2975")

    graph.add_edge(source="110380", target="6384")
    graph.add_edge(source="5141", target="110380")
    graph.add_edge(source="5141", target="6384")
    graph.add_edge(source="6384", target="5141")
    graph.add_edge(source="2975", target="110380")
    graph.add_edge(source="2975", target="5141")
    graph.add_edge(source="2975", target="3087")

    print("NODES:")
    graph.print_nodes()
    graph.total_nodes()
    print("\nEDGES:")
    graph.print_edges()
    graph.total_edges()
    max_deg = graph.max_degree_nodes()
    print(f"\nMax Degree Nodes: {max_deg}")

def test_graph():
    graph.add_node(id="1000", name="Colin Powell")
    graph.add_node(id="2000", name="Robert Duvall")
    graph.add_node(id="3000", name="Robert Englund")

    graph.add_edge(source="2975", target="3000")
    graph.add_edge(source="1000", target="3000")
    graph.add_edge(source="2000", target="3000")

    graph.add_edge(source="3000", target="2000")
    graph.add_edge(source="2975", target="2000")

    graph.add_edge(source="1000", target="2975")
    graph.add_edge(source="2000", target="2975")
    graph.add_edge(source="3000", target="2975")


    print("\nNODES:")
    graph.print_nodes()
    graph.total_nodes()
    print("\nEDGES:")
    graph.print_edges()
    graph.total_edges()
    max_deg = graph.max_degree_nodes()
    print(f"\nMax Degree Nodes: {max_deg}")

def TMDB_test_functions(id):
    movie_cast = tmdb_api_utils.get_movie_cast(movie_id=str(id), limit=5, exclude_ids=[8, 569, 651, 652])

    print(f"Cast Members: {movie_cast}")
    print(f"The lenght of movie cast is: {len(movie_cast)}")
    for member in movie_cast:
        print(f"Actor Name: {member['original_name']}, Actor ID: {member['id']}, Order: {member['order']}")


# You should modify __main__ as you see fit to build/test your graph using  the TMDBAPIUtils & Graph classes.
# Some boilerplate/sample code is provided for demonstration. We will not call __main__ during grading.

if __name__ == "__main__":

    graph = Graph()
    graph.add_node(id='2975', name='Laurence Fishburne')

    tmdb_api_utils = TMDBAPIUtils(api_key='edc3f4b783865a2e79f271e73c1522ad')



    # call functions or place code here to build graph (graph building code not graded)
    # Suggestion: code should contain steps outlined above in BUILD CO-ACTOR NETWORK
    build_base_graph()
    graph.write_edges_file()
    graph.write_nodes_file()

    # If you have already built & written out your graph, you could read in your nodes & edges files
    # to perform testing on your graph.
    # graph = Graph(with_edges_file="edges.csv", with_nodes_file="nodes.csv")

    #test_graph_nodes()
    #test_graph()
    # TMDB_test_functions(80)