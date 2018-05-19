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
                w.writelines(str(invests[j].get_post().get_ID()) + "\n")
                w.writelines(str(invests[j].get_post().get_upvotes()) + "\n")
                w.writelines(str(invests[j].get_name()) + "\n")
                w.writelines(str(invests[j].get_amount()) + "\n")
                w.writelines(str(invests[j].get_done()) + "\n")
                w.writelines(str(invests[j].get_time()) + "\n")
                w.writelines(str(invests[j].get_head()) + "\n")
                
                gr = invests[j].get_growth()
                grl = len(gr)
                w.writelines(str(grl) + "\n")
                for k in range(grl):
                    w.writelines(str(gr[k]) + "\n")
    w.close()

c = 0
def read_lines(array):
    global c
    elem = array[c]
    c += 1
    return elem
    
def read_investors():
    investors = {}
    with open(data_folder + "investors.txt", "r") as r:
        file_data = r.readlines()
        file_data = [x.replace("\n", "") for x in file_data]
        invs = int(float(read_lines(file_data)))
        for _ in range(invs):
            investor = read_lines(file_data)
            investors[investor] = Investor(investor, 1000)
            investors[investor].set_name(read_lines(file_data))
            investors[investor].set_balance(read_lines(file_data))
            investors[investor].set_active(read_lines(file_data))
            investors[investor].set_completed(read_lines(file_data))

            number_of_investments = int(float(read_lines(file_data)))
            
            for _ in range(number_of_investments):

                post_ID = read_lines(file_data)
                post_upvotes = int(float(read_lines(file_data)))
                amount = int(float(read_lines(file_data)))
                done = int(float(read_lines(file_data)))
                time = int(float(read_lines(file_data)))
                head = int(float(read_lines(file_data)))

                investors[investor].append(Investment(post_ID,
                                                      post_upvotes,
                                                      investor,
                                                      amount))

                investor[investor].invests[-1].set_done(done)
                investor[investor].invests[-1].set_time(time)
                investor[investor].invests[-1].set_head(head)

                growth_length = int(float(read_lines(file_data)))

                for _ in range(growth_length):
                    investor[investor].invests[-1].growth.append(int(float(read_lines(file_data))))

    return investors
