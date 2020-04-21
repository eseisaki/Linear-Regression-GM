from statistics import *
import constants as const


###############################################################################
#
#  Safe zone
#
###############################################################################

# safe_zone = error* norm(dot(A_global,D)) + norm(dot(A_global,d)) +
# + norm(dot(A_global,D,w_global))

###############################################################################
#
#  Coordinator
#
###############################################################################
@remote_class("coord")
class Coordinator(Sender):
    def __init__(self):
        pass

    # -------------------------------------------------------------------------
    # REMOTE METHOD
    def alert(self):
        # call send_data()
        pass

    def sync(self):
        # update global estimate
        # call new_estimate()
        pass


###############################################################################
#
#  Site
#
###############################################################################
@remote_class("site")
class Site(Sender):
    def __init__(self):
        pass

    def new_stream(self):
        # update window
        # if safe_zone is violated
        #   call alert()
        pass

    # -------------------------------------------------------------------------
    # REMOTE METHOD
    def new_estimate(self):
        # save received global estimate
        # update last state = current_state
        pass

    def send_data(self):
        # call sync()
        pass


###############################################################################
#
#  Simulation
#
###############################################################################
def configure_system():
    # create a network object
    n = StarNetwork(const.K, site_type=Site, coord_type=Coordinator)

    # add site and coordinator interfaces
    ifc_coord = {"sync": True}
    n.add_interface("coord", ifc_coord)
    ifc_site = {"new_estimate": True}
    n.add_interface("site", ifc_site)

    # create coord and k sites
    n.add_coord("site")
    n.add_sites(n.k, "coord")

    # set up all channels, proxies and endpoints
    n.setup_connections()

    return n
