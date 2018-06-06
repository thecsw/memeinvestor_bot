# u/MemeInvestor_bot Documentation

## Contents

- [Welcome to meme investment!](#welcome-to-meme-investment)
- [Contributing](#contributing)
- [Investment behaviour](#investment-behaviour)
- [Commands](#commands)
- [Getting started](#getting-started)
- [Prerequisites](#prerequisites)
- [Installation and configuration](#installation-and-configuration)
- [Deployment](#deployment)
- [Source code](#source-code)
- [Authors](#authors)
- [License](#license)

## Welcome to meme investment!

Welcome to the source code repository of [u/MemeInvestor_bot](https://www.reddit.com/user/MemeInvestor_bot). 
This bot has been developed exclusively for [r/MemeEconomy](https://reddit.com/r/MemeEconomy/). It allows users
to create investment accounts with fictional MemeCoins, invest those MemeCoins in specific memes, and automatically
evaluate meme performance resulting in positive or negative returns.

The README below is a bit outdated. New version will be soon.

## Contributing

If you want to contribute, please do so! Check the [Issues](https://github.com/MemeInvestor/memeinvestor_bot/issues) list and help meme investments thrive!

## Investment behaviour

To calculate the investment return, the bot performs a two-step procedure.

### First step

The bot calculates an initial growth factor, `y`, using a power function of the form `y = x^m`,
where `m` is a constant (`m=1/3`) and `x` is the relative change in
upvotes on the post since the investment was made as a proportion of the upvotes 
at the time of investment:  
`x=1+(final_upvotes - initial_upvotes)/initial_upvotes`.  
The 1/3 power function (cube root) behaviour was chosen so that the overall behavior
of the investment return function is a steep rise which levels off at higher upvote
growth. The reasoning behind this is to prevent a small handful of investors who get lucky
and invest in one or more posts that 'blow up' from earning so many MemeCoins that they
dominate the market from then on. This helps keep the playing field somewhat more
level for new investors. 
  
![Investment Return Initial Growth Factor](./data/investment_return_multiplier.png)
*Investment Return Initial Growth Factor*

### Second step

Unlike real stocks, reddit post upvotes typically either grow or don't grow; posts
don't usually get mass-downvoted by an appreciable amount and if they do, they quickly 
get buried, reducing the potential for downvoting. In light of this, so that investments aren't
risk-free, a graduated threshold is applied to the the factor calculated by the power function in the
first step. If the post grows such that this factor `y` is above the success threshold, `thresh = 1.2`,
the investment return is simply `invested_amount * y`. If the post grows (`y>1`) but the factor is at or
below 1.2, the investor only gets back `invested_amount * (y-1)/(thresh - 1)`. If the post doesn't grow
or is downvoted (`y<=1`), the investor gets back nothing.

![Investment Return Final Return Multiplier](./data/investment_return_multiplier_thresholding.png)
*Investment Return Final Return Multiplier vs Initial Growth Factor*

*Note:* The investment behaviour has already been through several design iterations
and may well be revised again in the future.

## Commands

The bot has the following commands:

- `!create` - creates a bank account for you with a new balance of 1000
  MemeCoins.
- `!invest AMOUNT` - invests AMOUNT in the meme (post). 4 hours after the
  investment, the meme growth will be evaluated and your investment can profit
  you or make you bankrupt. Minimum possible investment is 100 MemeCoins.
- `!balance` - returns your current balance.
- `!active` - returns a number of active investments.
- `!broke` - only if your balance is less than 100 MemeCoins and you do not have
  any active investments, declares bankruptcy on your account and sets your
  balance to 100 MemeCoins (minimum possible investment). 
- `!market` - gives an overview for the whole Meme market.
- `!top` - gives a list of the users with the largest account balances.
- `!ignore` - ignores the whole message.
- `!help` - returns this help message.

To invoke a command, reply to either the top-level u/MemeInvestor_bot comment in the comment section of any
r/MemeEconomy post or to one of its subsequent replies to your command comment.

## Getting started 

These instructions will get you a copy of the project up and running on your
local machine for development and testing purposes. See deployment for notes on
how to deploy the project on a live system. 

### Prerequisites

### Installation and configuration

### Deployment

## Authors

 - *Sagindyk Urazayev* - Core back-end developer. Initial work & SQLite. - [thecsw](https://github.com/thecsw)
 - *Dimitris Zervas* - Main back-end developer. MySQL, Docker, API and overall support. - [dzervas](https://github.com/dzervas)
 - *jimbobur* - Our math guy. Can make really pretty graphs. - [jimbobur](https://github.com/jimbobur)
 - *Alberto Ventafridda* - Main front-end and web developer. - [robalb](https://github.com/robalb)
 - *rickles42* - Heavy outside contributor. - [rickles42](https://github.com/rickles42)
 - *TwinProduction* - Heavy outside contributor. - [TwinProduction](https://github.com/TwinProduction)
 - *ggppjj* - Minor fixes - [ggppjj](https://github.com/ggppjj)

## License

This project is licensed under the The GNU General Public License (see the
[LICENSE.md](https://github.com/thecsw/prequelmemes_bot/blob/master/LICENSE) file for details), it explains everything pretty well. 
