from investor import *

def strn(arg):
    return f"{str(arg)}\n"

def addl(w, arg):
    w.writelines(strn(arg))

def write_investors(file_name, investors):
    length = len(investors)
    keys = list(investors.keys())
    values = list(investors.values())
    
    with open(file_name, "w") as w:
        # Number of Investors
        addl(w, length)

        for i in range(length):
            # Investor instance
            ivi = values[i]
            
            addl(w, ivi.get_name())
            addl(w, ivi.get_balance())
            addl(w, ivi.get_active())
            addl(w, ivi.get_completed())

            # Array of Investments
            arr = ivi.get_invests()
            arrl = len(arr)

            addl(w, arrl)
            # For each investment
            for j in range(arrl):
                addl(w, arr[j].get_ID())
                addl(w, arr[j].get_comment())
                addl(w, arr[j].get_upvotes())
                addl(w, arr[j].get_name())
                addl(w, arr[j].get_amount())
                addl(w, arr[j].get_time())
        w.close()
        
    return True

def read_investors(file_name):
    with open(file_name, "r") as r:
        data = r.readlines()
        data = [x.replace("\n", "") for x in data]
        arr = {}

        # Number of investors
        nofinv = int(float(data.pop(0)))

        for _ in range(nofinv):
            name = data.pop(0)
            balance = int(float(data.pop(0)))
            active = int(float(data.pop(0)))
            completed = int(float(data.pop(0)))

            arr[name] = Investor(name, balance)
            arr[name].set_active(active)
            arr[name].set_completed(completed)

            # Invests
            invs = int(float(data.pop(0)))
            
            for _ in range(invs):
                post_ID = data.pop(0)
                commentID = data.pop(0)
                post_upvotes = int(float(data.pop(0)))
                inv_name = data.pop(0)
                inv_amount = int(float(data.pop(0)))
                inv_time = int(float(data.pop(0)))

                arr[name].add_investment(Investment(post_ID,
                                                    commentID,
                                                    post_upvotes,
                                                    inv_name,
                                                    inv_amount))
                arr[name].invests[-1].set_time(inv_time)
        r.close()
        
    return arr

def write_investments(file_name, arr):
    invl = len(arr)
    with open(file_name, "w") as w:
        
        addl(w, invl)
        
        for i in range(invl):
            addl(w, arr[i].get_ID())
            addl(w, arr[i].get_upvotes())
            addl(w, arr[i].get_name())
            addl(w, arr[i].get_amount())
            addl(w, arr[i].get_time())

        w.close()

def read_investments(file_name):

    arr = []
    with open(file_name, "r") as r:
        data = r.readlines()
        data = [x.replace("\n", "") for x in data]

        num = int(float(data.pop(0)))

        for _ in range(num):
            post_ID = data.pop(0)
            post_upvotes = int(float(data.pop(0)))
            inv_name = data.pop(0)
            inv_amount = int(float(data.pop(0)))
            inv_time = int(float(data.pop(0)))

            arr.append(Investment(post_ID,
                                  post_upvotes,
                                  inv_name,
                                  inv_amount))
            arr[-1].set_time(inv_time)
        r.close()

    return arr

def write_array(file_name, arr):
    with open(file_name, "w") as w:
        for i in arr:
            w.writelines(f"{str(i)}\n")
    w.close
    return True
    
def read_array(file_name):
    arr = []
    with open(file_name, "r") as r:
        arr = r.readlines()
        arr = [x.replace("\n", "") for x in arr]
        r.close()
    return arr
