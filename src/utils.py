from investor import *

data_folder = "./data/"

def write_investors(investors):
    length = len(investors)
    keys = list(investors.keys())
    values = list(investors.values())
    
    with open(data_folder + "investors.txt", "w") as w:
        w.writelines(str(length) + "\n")
        for i in range(len(keys)):
            # Just the name
            investor = keys[i]
            w.writelines(investor + "\n")
            # Array of Investor objects
            data = values[i]
            w.writelines(str(data.get_name()) + "\n")
            w.writelines(str(data.get_balance()) + "\n")
            w.writelines(str(data.get_active()) + "\n")
            w.writelines(str(data.get_completed()) + "\n")

            invests = data.get_invests()
            investments = len(invests)
            w.writelines(str(investments))
            for j in range(investments):
                w.writelines(str(invests[j].get_post()) + "\n")
                w.writelines(str(invests[j].get_name()) + "\n")
                w.writelines(str(invests[j].get_amount()) + "\n")
                w.writelines(str(invests[j].get_done()) + "\n")
                w.writelines(str(invests[j].get_time()) + "\n")
                w.writelines(str(invests[j].get_head()) + "\n")
                w.writelines(str(invests[j].get_post_upvotes()) + "\n")
                
                gr = invests[j].get_growth()
                grl = len(gr)
                w.writelines(str(grl) + "\n")
                for k in range(grl):
                    w.writelines(str(gr[k]) + "\n")
    w.close()

def read_investors():
    investors = {}
    with open(data_folder + "investors.txt", "r") as r:
        invs = r.readlines()
        for _ in range(invs):
            investor = r.readlines()
            investors[investor] = Investor(investor, starter)
            investors[investor].set_name(r.readlines())
            investors[investor].set_balance(r.readlines())
            investors[investor].set_active(r.readlines())
            investors[investor].set_completed(r.readlines())

            number_of_investments = r.readlines()
            
            for _ in range(number_of_investments):
                investors[investor].invest()
