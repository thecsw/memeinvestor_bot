# Interactive command line tool for performing test calculations for investment return
import argparse
import matplotlib.pyplot as plt
from formula import calculate

def main():
    # == Parse initial and final upvotes from command line
    parser = argparse.ArgumentParser(description='Interactive command line tool for performing test calculations for investment return.')
    parser.add_argument('u_init', metavar='u_init', type=int, help='Post upvotes at time of investment.')
    parser.add_argument('u_final', metavar='u_final', type=int, help='Post upvotes at maturation of investment.')
    parser.add_argument('invested', metavar='invested', type=int, help='MemeCoins Invested in post.')
    parser.add_argument('net_worth', metavar='net_worth', type=int, help='Account\'s net worth.')
    parser.add_argument("-s", "--save-img", help="Save generated plot to file 'investment_performance.png'", action="store_true")
    args = parser.parse_args()

    print("Starting Upvotes:", args.u_init)
    print("Final Upvotes:", args.u_final)
    print("Amount Invested:", args.invested, "M¢")
    print("Net worth:", args.net_worth, "M¢")
    inv_return = calculate(args.u_final, args.u_init, args.net_worth) * args.invested
    profit = inv_return - args.invested
    print(">> RETURN:", inv_return, "M¢ (Profit:", profit, "M¢)")

    #Generate data for performance plot
    olds = list(range(args.u_init, args.u_final * 2, args.net_worth))# + list(range(args.u_final, args.u_final * 2, 10))
    x = []
    x2 = []
    y = []
    y2 = []
    for i in olds:
        x.append(i)
        result = calculate(i, args.u_init, args.net_worth) * args.invested
        y.append(result)
        if i <= args.u_final:
            x2.append(i)
            y2.append(result)

    #Generate performance plot
    fig = plt.figure(figsize=(7,7))
    plt.grid(color='k', alpha=0.15, which='major')
    plt.title('Investment Performance',fontsize='18')
    plt.xlabel('Upvotes',fontsize='14')
    plt.ylabel('Return / M¢',fontsize='14')
    plt.plot(x,y,label='Return curve')
    plt.plot(x2,y2,label='Meme Performance',color='r')
    plt.plot(args.u_final, inv_return, color='r', marker='X', markersize=8, linestyle='none', label='Return: %i M¢ (Profit: %i M¢)' %(inv_return,profit))
    plt.legend(fontsize='12')

    #Interactive show plot
    plt.show()

    #Optional save plot
    if args.save_img:
        out_filename = 'investment_performance.png'
        print ("Saving image to: '",out_filename,"'")
        fig.savefig(out_filename)

if __name__ == "__main__":
    main()
