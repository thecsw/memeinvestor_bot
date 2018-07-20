
export const badgesList = {
   'top-beta': [
      'Billionaire during the first beta',
      'top-beta.png'
   ],
   'top-investor': [
      'the richest investor on memeEconomy',
      'top-investor.png'
   ],
   'dev': [
      'developers for memeInvestor inc.',
      'dev.png'
   ],
   'test': [
      'this is a test badge',
      'test.png'
   ]
}
export function getFileName(badge){
   return badgesList[badge][1]
}
export function getDescription(badge){
   return badgesList[badge][0]
}