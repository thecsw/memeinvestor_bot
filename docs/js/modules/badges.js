
export const badgesList = {
   'top-beta': [
      'Beta Billionaire: Earned a billion MemeCoins or more during the beta',
      'top-beta.png'
   ],
   'top-s1': [
      'S1 Top Investor: Reached the height of riches in Season 1',
      'top-investor.png'
   ],
   'contributor': [
      'Contributor: Made at least one commit to the MemeInvestor_bot project on GitHub',
      'contributor.png'
   ],
   'overflow': [
      'Overflow: \'The value of his bank account is too damn high!\'',
      'overflow.png'
   ],
   'donor': [
      'Donor: Supported the bot on Patreon and is generally an awesome person',
      'donor.png'
   ],
   'unknown': [
      'unknown badge',
      'laurel.png'
   ]
}
export function getFileName(badge){
   if(!badgesList.hasOwnProperty(badge)){
      badge = 'unknown'
   }
   return badgesList[badge][1]
}
export function getDescription(badge){
   if(!badgesList.hasOwnProperty(badge)){
      badge = 'unknown'
   }
   return badgesList[badge][0]
}