import sys
import socket as s
import time
import threading
import pickle
from collections import defaultdict
from math import inf
import datetime as dt
from typing import Dict, List, Any, Union
import copy

NO_OF_ARGS = 2
F_NAME = 1
NAME_OF_ROUTER = 0
PORT_FOR_PARENT = 1
PORT_FOR_CHILD = 2
DISTANCE = 1
INTERVAL_UPDATE = 1
ROUTER_INTERVAL_UPDATE = 30
NAME_OF_SERVER = 'localhost'


class Router:
    def __init__(self, name, port, nghboring_node_list):
        
        self.name = name
        
        self.port = port
        
        self.nghboring_node = nghboring_node_list
        
        self.msg = None
        
        self.prev_sent_seq= defaultdict(int)
        
        self.globl_time_stamp_for_routing = defaultdict(float)
        
        self.all_globl_routers = defaultdict(list)

    def add_nghbour(self, nghbour):
        
        self.nghboring_node.append(nghbour)
        
        self.all_globl_routers[self.name].append(nghbour)

    def set_msg(self, msg):
        
        self.msg = msg

    def add_prev_seq_for_sent(self, msg):
       
        self.prev_sent_seq[msg.name] = msg.seq_no

    def check_previous_sent_sequence(self, msg):
       
        return self.previous_sent_msgs_sequence[msg.name] != msg.seq_no

    def router_add_timestmp(self, msg):
       
        self.globl_time_stamp_for_routing[msg.name] = msg.tmpstmp

    def check_router_tmpstmp(self, msg):
       
        return self.globl_time_stamp_for_routing[msg.name] != msg.tmpstmp

    def update_all_globl_routers(self, msg):
      
        if len(self.all_globl_routers[msg.name]) > 0:
      
            for nghbour in msg.nghboring_node:
      
                present = False
      
                for present_nghbour in self.all_globl_routers[msg.name]:
      
                    if present_nghbour.port == nghbour.port \
                            and present_nghbour.name == nghbour.name \
                            and present_nghbour.distance == nghbour.distance:
      
                        present = True
      
                if not present:
      
                    self.all_globl_routers[msg.name].append(nghbour)
        else:
      
            for nghbour in msg.nghboring_node:
      
                self.all_globl_routers[msg.name].append(nghbour)

    def neighbor_node_alive_check(self, msg):
        
        for nghbour in msg.nghboring_node:
        
            if nghbour.name == self.name:
        
                present = False
        
                for my_nghbour in self.nghboring_node:
        
                    if my_nghbour.name == msg.name:
        
                        present = True
        
                if not present:
        
                    to_be_added = nghboring_node(msg.name, msg.port, nghbour.distance)
        
                    self.nghboring_node.append(to_be_added)
        
                    self.all_globl_routers[self.name].append(to_be_added)


class msg:
    def __init__(self, sender: Router):
        
        self.port = sender.port
        
        self.name = sender.name
        
        self.nghboring_node = sender.nghboring_node
        
        self.seq_no = 0
        
        self.tmpstmp = dt.datetime.now().timestamp()
        
        self.last_sender = sender.name

    def increment_seq_no(self):
        
        self.seq_no += 1


class nghboring_node:
    def __init__(self, name, port, distance):
        
        self.name = name
        
        self.port = port
        
        self.distance = distance


class Edge:
    def __init__(self, u, v, weight):
        
        self.start = u
        
        self.end = v
        
        self.weight = weight


class grph:
    def __init__(self, all_globl_routers):
        
        self.all_globl_routers = all_globl_routers
        
        self.grph = defaultdict(list)
        
        self.parse(self.all_globl_routers)

    def parse(self, all_globl_routers):
        
        for router, nghboring_node in all_globl_routers.items():
        
            parent = router
        
            for child in nghboring_node:
        
                self.grph[parent].append(Edge(parent, child.name, child.distance))


def calculate_paths_activator():
    while True:
        time.sleep(ROUTER_INTERVAL_UPDATE)
        calculate_paths()


def calculate_paths():
    prnt_router = router_parent_tracker

    weight = 0
    
    status_visited_flag = 1
    
    parent_ = 2

    g = grph(prnt_router.all_globl_routers)

    table_for_calculations: Dict[Any, List[Union[float, bool]]] = {}
    # (name, weight, visited=boolean)
    total_routers = 0
    
    for router in prnt_router.all_globl_routers:
       
        if router != prnt_router.name:
            # filling all the table with name of router
            table_for_calculations[router] = [inf, False, None]
        
        else:
            table_for_calculations[router] = [0.0, True, None]
        total_routers += 1

    c = 0
    
    print(f'Router Name : {prnt_router.name}')
   
    current_router = prnt_router.name
   
    printing_routers = prnt_router.name
   
    printing_list = []
    
    while c != total_routers-1:
        # code for opening up weights
        
        for edge in g.grph[current_router]:
        
            for node, weight_status in table_for_calculations.items():
        
                if node == edge.end and not weight_status[status_visited_flag] and table_for_calculations[node][weight] > table_for_calculations[current_router][weight] + float(edge.weight):
        
                    table_for_calculations[node][weight] = table_for_calculations[current_router][weight] + float(edge.weight)
        
                    table_for_calculations[node][parent_] = edge.start
        
        min_weight = inf
        
        minimum_available_node = ''
        
        for node, weight_status in table_for_calculations.items():
        
            if weight_status[weight] < min_weight and weight_status[status_visited_flag] == False:
        
                minimum_available_node = node
        
                min_weight = weight_status[weight]
        
        if minimum_available_node != '':
        
            table_for_calculations[minimum_available_node][status_visited_flag] = True
        
            current_router = minimum_available_node
        
            c += 1
        
            printing_list.append(minimum_available_node)
        
            printing_routers = printing_routers + minimum_available_node

    for node in printing_list:
        
        hops = node
        
        current_parent = table_for_calculations[node][parent_]
        
        while current_parent is not None:
        
            hops = hops + current_parent
        
            current_parent = table_for_calculations[current_parent][parent_]
        
        print(f'Least cost path available to router {node}:{hops[::-1]} is {table_for_calculations[node][weight]}')


def udp_client(prnt_router: Router):
    
    client_socket = s.socket(s.AF_INET, s.SOCK_DGRAM)
    
    while True:
        
        for child in prnt_router.nghboring_node:
        
            prnt_router.msg.tmpstmp = dt.datetime.now().timestamp()
        
            msg_to_send = pickle.dumps(prnt_router.msg)
        
            server_port = int(child.port)
        
            client_socket.sendto(msg_to_send, (NAME_OF_SERVER, server_port))
        
        time.sleep(INTERVAL_UPDATE)
        
        prnt_router.msg.increment_seq_no()



def check_previous_sent_sequence(msg: msg, prnt_router: Router):

    return prnt_router.previous_sent_msgs_sequence[msg.name] < msg.seq_no


def check_previous_sent_tmpstmp(msg: msg, prnt_router: Router):

    return prnt_router.globl_time_stamp_for_routing[msg.name] < msg.tmpstmp


def udp_server(prnt_router: Router):

    server_port = int(prnt_router.port)

    server_socket = s.socket(s.AF_INET, s.SOCK_DGRAM)

    server_socket.bind((NAME_OF_SERVER, server_port))

    client_socket = s.socket(s.AF_INET, s.SOCK_DGRAM)


    while True:

        msg, client_address = server_socket.recvfrom(2048)

        received_msg: msg = pickle.loads(msg, fix_imports=True, encoding="utf-8", errors="strict")



        last_sender = copy.deepcopy(received_msg.last_sender)

        for nghbour in prnt_router.nghboring_node:

            # dont send to the previous sender

            if last_sender != nghbour.name and check_previous_sent_tmpstmp(received_msg, prnt_router):

                received_msg.last_sender = copy.deepcopy(prnt_router.name)

                client_socket.sendto(pickle.dumps(received_msg), (NAME_OF_SERVER, int(nghbour.port)))

        prnt_router.add_prev_seq_for_sent(received_msg)

        prnt_router.router_add_timestmp(received_msg)

        prnt_router.neighbor_node_alive_check(received_msg)

        prnt_router.update_all_globl_routers(received_msg)



def check_if_nghboring_node_alive(prnt_router: Router):

    nghboring_node_to_remove = None

    for nghbour in prnt_router.nghboring_node:

        if dt.datetime.now().timestamp() - prnt_router.globl_time_stamp_for_routing[nghbour.name] > 3:

            # remove from LSA

            nghboring_node_to_remove = nghbour.name



            # remove from global key

            # remove from global values

    if nghboring_node_to_remove is not None:

        prnt_router.all_globl_routers.pop(nghboring_node_to_remove, None)

        for nghbour in prnt_router.nghboring_node:

            if nghboring_node_to_remove == nghbour.name:

                prnt_router.nghboring_node.remove(nghbour)

                break



def not_my_nghbour(router, prnt_router):
 
    for nghbour in prnt_router.nghboring_node:
  
        if router == nghbour.name:
   
            return False
  
    return True


def check_if_non_nghboring_node_alive(prnt_router: Router):

    router_to_remove = None
  
    for router, all_nghboring_node in prnt_router.all_globl_routers.items():
   
        if not_my_nghbour(router, prnt_router) and router != prnt_router.name:
    
            if dt.datetime.now().timestamp() - prnt_router.globl_time_stamp_for_routing[router] > 12:
     
                router_to_remove = router
  
    if router_to_remove is not None:
     
        prnt_router.all_globl_routers.pop(router_to_remove, None)




def check_alive(prnt_router: Router):
    while True:
        time.sleep(3)
    
        check_if_nghboring_node_alive(prnt_router)
      
        check_if_non_nghboring_node_alive(prnt_router)


if len(sys.argv) == NO_OF_ARGS:
   
    f = open(sys.argv[F_NAME], "r")
    
    ln_c = 0
   
    number_of_nghbour = 0
   
    router_parent_tracker: Router
    
    list_file = []
    
    for ln in f:
    
        list_file.append(ln.split())
   
    for i in range(len(list_file)):
    
        # First ln will always be Parent router
    
        if i == 0:
         
            router_parent_tracker = Router(list_file[i][NAME_OF_ROUTER], list_file[i][PORT_FOR_PARENT], [])

    
        # Second ln will always be the number of nghboring_node
        elif i == 1:
            
            number_of_nghbour = list_file[i]  # TODO not using right now

        # From 3 onwards it will be the child routers
        elif i > 1:
       
            child_router = nghboring_node(list_file[i][NAME_OF_ROUTER], list_file[i][PORT_FOR_CHILD], list_file[i][DISTANCE])
       
            router_parent_tracker.add_nghbour(child_router)
       
        ln_c += 1

    
    router_parent_tracker.set_msg(msg(router_parent_tracker))
    
    thread_client = threading.Thread(target=udp_client, args=(router_parent_tracker,))
    
    thread_server = threading.Thread(target=udp_server, args=(router_parent_tracker,))
    
    thread_calculation = threading.Thread(target=calculate_paths_activator)
   
    check_alive_thread = threading.Thread(target=check_alive, args=(router_parent_tracker,))
    
    thread_client.start()
    
    thread_server.start()
    
    thread_calculation.start()
    
    check_alive_thread.start()
