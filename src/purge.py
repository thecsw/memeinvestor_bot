# Data folder
data_folder = "./data/"

# File to store all investors
investors_file = "investors.txt"

# File to store all awaiting investments
awaiting_file = "awaiting.txt"

# File to store all done investments
done_file = "done.txt"

# File to store checked comments
checked_file = "checked_comments.txt"

with open(data_folder + investors_file, "w") as w:
    w.write("0\n")
    w.close()

with open(data_folder + awaiting_file, "w") as w:
    w.write("0\n")
    w.close()

with open(data_folder + done_file, "w") as w:
    w.write("0\n")
    w.close()
    
with open(data_folder + checked_file, "w") as w:
    w.write("0\n")
    w.close()
