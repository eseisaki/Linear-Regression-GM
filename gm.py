from statistics import *
import constants as const
import numpy as np
import time
from colorama import Fore, Back, Style
import winsound
import sys


###############################################################################
#
#  Coordinator
#
###############################################################################
@remote_class("coord")
class Coordinator(Sender):
    def __init__(self, net, nid, ifc):
        super().__init__(net, nid, ifc)
        self.A_global = np.zeros((const.FEATURES + 1, const.FEATURES + 1))
        self.c_global = np.zeros((const.FEATURES + 1, 1))
        self.w_global = None
        self.counter = 0
        self.sub_counter = -10 * const.K
        self.sync_counter = 0
        self.round_counter = 0

    def update_counter(self):
        self.counter += 1

    # -------------------------------------------------------------------------
    # REMOTE METHOD

    def alert(self):
        if self.sub_counter <= self.counter < self.sub_counter + const.K:
            if const.DEBUG: print(Fore.RED + "Coordinator ignores this alert",
                                  Style.RESET_ALL)
        else:
            self.sync_counter += 1
            self.sub_counter = self.counter
            if const.DEBUG: print(Back.RED, Fore.BLACK, "SYNC",
                                  self.sync_counter, "--SYNC "
                                                     "TIME:",
                                  self.counter, "--",
                                  Style.RESET_ALL)
            if const.DEBUG: print(Fore.GREEN + "Coordinator asks data from "
                                               "every node",
                                  Style.RESET_ALL)
            self.send("send_data", None)

    def sync(self, msg):
        D, d = msg
        self.incoming_channels += 1
        if const.DEBUG: print(Fore.YELLOW, "Coordinator aggregates "
                                           "estimate.", Style.RESET_ALL)

        self.A_global = np.add(self.A_global, D / const.K)
        self.c_global = np.add(self.c_global, d / const.K)

        if self.incoming_channels == const.K:
            self.round_counter += 1
            # compute coefficients
            self.w_global = np.linalg.pinv(self.A_global).dot(self.c_global)
            w_train = self.w_global.reshape(1, -1)
            w_train = np.insert(w_train, w_train.shape[1], self.counter,
                                axis=1)
            # save coefficients
            np.savetxt(f1, w_train, delimiter=',', newline='\n')

            self.incoming_channels = 0
            if const.DEBUG: print(Fore.GREEN, "Coordinator sends new "
                                              "estimate.",
                                  Style.RESET_ALL)
            self.send("new_estimate", (self.A_global, self.w_global))


###############################################################################
#
#  Site
#
###############################################################################
@remote_class("site")
class Site(Sender):
    def __init__(self, net, nid, ifc):
        super().__init__(net, nid, ifc)
        self.D = np.zeros((const.FEATURES + 1, const.FEATURES + 1))
        self.d = np.zeros((const.FEATURES + 1, 1))

        self.A_global = None
        self.w_global = None
        self.win = Window(size=const.SIZE, step=const.STEP,
                          points=const.POINTS * const.EPOCH)
        self.init = True

    def new_stream(self, stream):
        np.set_printoptions(precision=2, suppress=True)

        if const.DEBUG: print("Node", self.nid, "takes a new (x,y) pair.",
                              stream)

        # update window
        try:
            res = self.win.update(stream)
            # batch = next(res)
            new, old = next(res)

            # update drift
            self.update_drift(new, old)

            if const.DEBUG: print("Local drift ", self.d)
            if self.init is True:
                if const.DEBUG: print(Fore.RED + "Node", self.nid,
                                      "sends an alert msg.", Style.RESET_ALL)
                self.send("alert", None)
                self.init = False

            A_in = np.linalg.pinv(self.A_global)
            norm = np.linalg.norm
            a1 = norm(np.dot(A_in, self.D))
            a2 = norm(np.dot(A_in, self.d))
            a3 = norm(np.dot((np.dot(A_in, self.D)), self.w_global))
            if const.DEBUG: print(Fore.YELLOW, "Node constraint:",
                                  const.ERROR * a1 + a2 + a3, Style.RESET_ALL)
            if const.ERROR * a1 + a2 + a3 > const.ERROR:
                if const.DEBUG: print(Fore.RED + "Node", self.nid,
                                      "sends an alert msg.", Style.RESET_ALL)
                self.send("alert", None)

        except StopIteration:
            pass

    def update_drift(self, new, old):
        if const.DEBUG: print("Node", self.nid,
                              "updates local state and local drift.")

        for x, y in new:
            x = x.reshape(-1, 1)
            ml1 = x.dot(x.T)
            self.D = np.add(self.D, ml1)
            ml2 = x.dot(y)
            self.d = np.add(self.d, ml2)

        for x, y in old:
            x = x.reshape(-1, 1)
            ml1 = x.dot(x.T)
            self.D = np.subtract(self.D, ml1)
            ml2 = x.dot(y)
            self.d = np.subtract(self.d, ml2)

    # -------------------------------------------------------------------------
    # REMOTE METHOD
    def new_estimate(self, msg):
        A_global, w_global = msg
        if const.DEBUG: print(Fore.CYAN, "Node", self.nid,
                              "saves new global estimate and nullifies "
                              " local drift", Style.RESET_ALL)
        # save received global estimate
        self.A_global = A_global
        self.w_global = w_global

    def send_data(self):
        # send local state
        if const.DEBUG: print(Fore.BLUE, "Node", self.nid,
                              "sends its local drift.", Style.RESET_ALL)
        self.send("sync", (self.D, self.d))
        if const.DEBUG: print(Fore.BLUE, "Node", self.nid,
                              "initializes local state.", Style.RESET_ALL)
        # drift = 0
        self.D = np.zeros((const.FEATURES + 1, const.FEATURES + 1))
        self.d = np.zeros((const.FEATURES + 1, 1))


###############################################################################
#
#  Simulation
#
###############################################################################
def configure_system():
    # create a network object
    n = StarNetwork(const.K, site_type=Site, coord_type=Coordinator)

    # add site and coordinator interfaces
    ifc_coord = {"alert": True, "sync": True}
    n.add_interface("coord", ifc_coord)
    ifc_site = {"new_estimate": True, "send_data": True}
    n.add_interface("site", ifc_site)

    # create coord and k sites
    n.add_coord("site")
    n.add_sites(n.k, "coord")

    # set up all channels, proxies and endpoints
    n.setup_connections()

    return n


def start_synthetic_simulation():
    net = configure_system()

    f2 = open("tests/synthetic.csv", "r")
    lines = f2.readlines()

    # setup toolbar
    bar_percent = 0
    line_counter = 0

    j = 0
    for line in lines:

        # update the bar
        line_counter += 1
        tmp_percent = int((line_counter / (const.POINTS * const.EPOCH)) * 100)
        if tmp_percent > bar_percent:
            bar_percent = tmp_percent
            sys.stdout.write('\r')
            sys.stdout.write(
                "[%-100s] %d%%" % ('=' * bar_percent, bar_percent))
            sys.stdout.flush()

        if j == const.K:
            j = 0
        tmp = np.fromstring(line, dtype=float, sep=',')
        x_train = tmp[0:const.FEATURES + 1]
        y_train = tmp[const.FEATURES + 1]

        net.coord.update_counter()
        net.sites[j].new_stream([(x_train, y_train)])
        j += 1

    f2.close()

    print("\n------------ RESULTS --------------")
    print("ROUNDS:", net.coord.sync_counter)


if __name__ == "__main__":
    start_time = time.time()
    print("Start running, wait until finished:")

    f1 = open("tests/gm.csv", "w")
    start_synthetic_simulation()
    f1.close()

    print("SECONDS: %s" % (time.time() - start_time))
    duration = 2000  # milliseconds
    freq = 440  # Hz
    winsound.Beep(freq, duration)
