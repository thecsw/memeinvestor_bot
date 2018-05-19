import matplotlib.pyplot as plt

file_name = "temp.png"

def make_graph(growth):
    obs = range(len(growth))
    plt.plot(obs, growth)
