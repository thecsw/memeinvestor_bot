# MemeInvestor_bot API Documentation

Hello there! Thank you for visiting our documentation and I hope you will find it useful.

This page is dividid into several sections, depending on the table you are requesting.

Before that, general request variables will be explained.

**NOTE:** Only `https` requests are served. You can play with the api using `$ curl https://meme.market/api/`

**ANOTHER NOTE:** All successful requests have `OK HEADER 200` in the header of the return.

## 1. General request variables

We support 4 optional variables when you request a json collection of investment entries:
 - from
 
 This should be a valid UNIX timestamp. Lower boundary for investment's time. The fallback value is 0.
 
 - to
 
 This should be a valid UNIX timestamp. Upper boundary for investment's time. The fallback value is `4294967295`.
 
 - page
 
 This is a [pagination](https://en.wikipedia.org/wiki/Pagination) variable. Starts from 0. The fallback value is 0.
 
 - per_page

 This is a [pagination](https://en.wikipedia.org/wiki/Pagination) variable. Starts from 1 to 100. The fallback value is 100.

## 2. Coins

 - `/coins/invested`
 
 The number of all currently invested coins.
 
 _Example:_
 ``` bash
 $ curl 'https://meme.market/api/coins/invested'
 
 {
  "coins": 993204860096
 }
 ```
 
 - `/coins/total`

 The number of all meme coins owned by investors.

_Example:_
 ``` bash
 $ curl 'https://meme.market/api/coins/total'
 
 {
  "coins": 272792228967
 }
```

## 3. Investments

**NOTE:** All `/investments` handlers support request variables listed above.

 - `/investments`
 
 An array of json investment formatted objects.
 
 _Example:_
 ``` bash
 $ curl 'https://meme.market/api/investments?page=10&per_page=1'
 
 [
  {
   "id": 133559,
   "post": "b2wa7l",
   "upvotes": 105,
   "comment": "eivt96u",
   "name": "xuebinz",
   "amount": 100,
   "time": 1553008527,
   "done": false,
   "response": "eivt9wu",
   "final_upvotes": -1,
   "success": false,
   "profit": 0
  }
 ]
 ```
 
 - `/investments/active`
 
 Number of active investments.
 
 ``` bash
 $ curl 'https://meme.market/api/investments/active'
 
 {
  "investments":374
 }
 ```
 
 - `/investments/total`
 
 Number of all investments
 
 ``` bash
 $ curl 'https://meme.market/api/investments/total'
 
 {
  "investments":116784
 }
 ```
 
 - `/investments/amount`
 
 Number of meme coins invested in investments.
 
 ``` bash
 $ curl 'https://meme.market/api/investments/amount?from=1551654000&to=1551740400'
 
 {
  "coins":153164238060
 }
 ```
 
 - `/investments/post/{post}`

All investments invested in the specified post. The post string is sanitized with regex. `[a-z0-9]{6}`

 ``` bash
 $ curl 'https://meme.market/api/investments/post/aibu3z?per_page=1&page=0'
 
 [
  {
   "id":"1",
   "post":"aibu3z",
   "upvotes":3,
   "comment":"eemjre5",
   "name":"Noerdy",
   "amount":100,
   "time":1548089163,
   "done":true,
   "response":"eemjs3d",
   "final_upvotes":9,
   "profit":-94
  }
 ]
 ```

## 4. Investor

 - `/investor/{name}`

 Returns a json object of Investor.
 
 ``` bash
 $ curl 'https://meme.market/api/investor/Thecsw'
 
 {
  "id": 9072,
  "name": "thecsw",
  "balance": 11000,
  "completed": 0,
  "broke": 0,
  "badges": [
   "contributor"
  ],
  "firm": 0,
  "firm_role": "",
  "networth": 11000,
  "rank": 1
 }
 ```

- `/investor/{name}/investments`

Returns an array of investments made by that user. Request variables are supported.

``` bash
$ curl 'https://meme.market/api/investor/mappum/investments?per_page=1&page=0'

[
 {
  "id":"912",
  "post":"aio25g",
  "upvotes":308,
  "comment":"eephr20",
  "name":"mappum",
  "amount":1000,
  "time":1548181211,
  "done":true,
  "response":"eephrsx",
  "final_upvotes":10137,
  "success":true,
  "profit":25
 }
]
```

- `/investor/{name}/active`

Returns an array of active investments made by that user. Request variables are supported.

``` bash
$ curl 'https://meme.market/api/investor/DyspraxicRob/active?per_page=1&page=0'

[
 {
  "id":"116818",
  "post":"b0770b",
  "upvotes":13308,
  "comment":"eie1a84",
  "name":"DyspraxicRob",
  "amount":5000,
  "time":1552432030,
  "response":"eie1anw",
  "final_upvotes":-1
 }
]
```

**NOTE:** final_upvotes is -1 because the entry does not exist and all `NULL` values in the table are replaced with -1

## 5. Investors

- `/investors/top`

Returns an array of investor objects + networth. All the entries are ordered by their networth.

``` bash
$ curl 'https://meme.market/api/investors/top?per_page=3'

[
 {
  "id": 65277,
  "name": "lukenamop",
  "balance": 0,
  "completed": 190,
  "broke": 0,
  "badges": [
   "top-s1"
  ],
  "firm": 51,
  "firm_role": "cfo",
  "networth": 228915997569
 },
 {
  "id": 6699,
  "name": "organic_crystal_meth",
  "balance": 0,
  "completed": 336,
  "broke": 0,
  "badges": [
   "top-s1",
   "top-s1"
  ],
  "firm": 51,
  "firm_role": "ceo",
  "networth": 185692230751
 },
 {
  "id": 10400,
  "name": "youngmemeguy",
  "balance": 0,
  "completed": 277,
  "broke": 0,
  "badges": [
   "top-s1"
  ],
  "firm": 51,
  "firm_role": "exec",
  "networth": 171326457546
 }
]
```

## 6. Summary

Returns a summary of basic meme market stats. This is used for the main page and website-specific.

``` bash
$ curl 'https://meme.market/api/summary?per_page=3'

{
 "coins": {
  "invested": {
   "coins": 993142784335
  },
  "total": {
   "coins": 272859664573
  }
 },
 "investments": {
  "active": {
   "investments": 650
  }
 },
 "investors": {
  "top": [
   {
    "id": 65277,
    "name": "lukenamop",
    "balance": 0,
    "completed": 190,
    "broke": 0,
    "badges": [
     "top-s1"
    ],
    "firm": 51,
    "firm_role": "cfo",
    "networth": 228915997569
   },
   {
    "id": 6699,
    "name": "organic_crystal_meth",
    "balance": 0,
    "completed": 336,
    "broke": 0,
    "badges": [
     "top-s1",
     "top-s1"
    ],
    "firm": 51,
    "firm_role": "ceo",
    "networth": 185692230751
   },
   {
    "id": 10400,
    "name": "youngmemeguy",
    "balance": 0,
    "completed": 277,
    "broke": 0,
    "badges": [
     "top-s1"
    ],
    "firm": 51,
    "firm_role": "exec",
    "networth": 171326457546
   }
  ]
 }
}
```

## 7. Firm

By providing a firm id, you can get general info about thefirm. ID should pass `^[0-9]+$` regex.

- `/firm/{id}`

``` bash
$ curl 'https://meme.market/api/firm/10'

{
 "id": 10,
 "name": "FENIX GLOBALS",
 "balance": 387820,
 "size": 10,
 "execs": 3,
 "assocs": 0,
 "coo": 1,
 "cfo": 1,
 "tax": 10,
 "rank": 1,
 "private": false,
 "last_payout": 1552687503
}
```

- `/firm/{id}/members`

Returns all members of the firm. Returns full Investor objects.

**NOTE** It probably will be changed in the future where it would return just an array of investors' names. Keep checking this page if we do.

``` bash
$ curl 'https://meme.market/api/firm/10/members?per_page=2

[
 {
  "id": 12312,
  "name": "Upvote4Isles",
  "balance": 166932,
  "completed": 2,
  "broke": 0,
  "badges": [],
  "firm": 10,
  "firm_role": "",
  "networth": 0
 },
 {
  "id": 42232,
  "name": "LL22-",
  "balance": 160316,
  "completed": 13,
  "broke": 0,
  "badges": [],
  "firm": 10,
  "firm_role": "",
  "networth": 0
 }
]
```

- `/firm/{id}/members/top`

Returns all top members of the firm sorted by networth. Returns full Investor objects.

``` bash
$ curl 'https://meme.market/api/firm/10/members/top?per_page=2'

[
 {
  "id": 71341,
  "name": "London_Dry",
  "balance": 6883470,
  "completed": 116,
  "broke": 0,
  "badges": [],
  "firm": 10,
  "firm_role": "ceo",
  "networth": 6883470
 },
 {
  "id": 73360,
  "name": "sobuchh",
  "balance": 4950307,
  "completed": 169,
  "broke": 0,
  "badges": [],
  "firm": 10,
  "firm_role": "exec",
  "networth": 4950307
 }
]
```

## 8. Firms

- `/firms/top`

Returns an array of firms sorted by their balance.

``` bash
$ curl 'https://meme.market/api/firms/top?per_page=2'

[
 {
  "id": 51,
  "name": "The Iron Bank",
  "balance": 61092366993,
  "size": 65,
  "execs": 6,
  "tax": 5,
  "rank": 4,
  "private": true,
  "last_payout": 1552687503
 },
 {
  "id": 57,
  "name": "Mahogany And Sons",
  "balance": 8950351429,
  "size": 14,
  "execs": 1,
  "tax": 5,
  "rank": 1,
  "private": true,
  "last_payout": 1552687503
 }
]
```
