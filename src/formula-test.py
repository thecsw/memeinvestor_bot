# Interactive command line tool for performing test calculations for investment return
import argparse
from formula import calculate

def main():
    # == Parse initial and final upvotes from command line
    parser = argparse.ArgumentParser(description='Interactive command line tool for performing test calculations for investment return.')
    parser.add_argument('u_init', metavar='u_init', type=int, help='Post upvotes at time of investment.')
    parser.add_argument('u_final', metavar='u_final', type=int, help='Post upvotes at maturation of investment.')
    parser.add_argument('invested', metavar='invested', type=int, help='MemeCoins Invested in post.')
    args = parser.parse_args()

    print("Starting Upvotes:", args.u_init)
    print("Final Upvotes:", args.u_final)
    print("Amount Invested:", args.invested, "M¢")
    print(">> RETURN:",calculate(args.u_final,args.u_init) * args.invested, "M¢" )

if __name__ == "__main__":
    main
    