
export const badgesList = {
   'top-beta': [
      'Billionaire during the first beta',
      'top-beta.png'
   ],
   'top-investor': [
      'the richest investor on memeEconomy',
      'top-investor.png'
   ],
   'contributorz': [
      'contributed in the development of memeInvestor',
      'laurel.png'
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