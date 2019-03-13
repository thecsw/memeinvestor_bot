# MemeInvestor_bot API Documentation

Hello there! Thank you for visiting our documentation and I hope you will find it useful.

This page is dividid into several sections, depending on the table you are requesting.

Before that, general request variables will be explained.

**NOTE:** Only `https` requests are served. You can play with the api using `$ curl https://memes.market/api/`

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
 $ curl 'https://memes.market/api/coins/invested'
 
 {
	 "coins":262013065167
 }
 ```
 
 - `/coins/total`

 The number of all meme coins owned by investors.

_Example:_
 ``` bash
 $ curl 'https://memes.market/api/coins/total'
 
 {
	 "coins":150568744453
 }
 ```

## 3. Investments

**NOTE:** All `/investments` handlers support request variables listed above.

 - `/investments`
 
 An array of json investment formatted objects.
 
 _Example:_
 ``` bash
 $ curl 'https://memes.market/api/investments?page=10&per_page=1'
 
 [
	 {
		"id":"21",
		"post":"aidfua",
		"upvotes":10,
		"comment":"eemwpr7",
		"name":"Weam86",
		"amount":100,
		"time":1548098074,
		"done":true,
		"response":"eemwqbe",
		"final_upvotes":38,
		"profit":-86
	 }
 ]
 ```
 
 - `/investments/active`
 
 Number of active investments.
 
 ``` bash
 $ curl 'https://memes.market/api/investments/active'
 
 {
	 "investments":374
 }
 ```
 
 - `/investments/total`
 
 Number of all investments
 
 ``` bash
 $ curl 'https://memes.market/api/investments/total'
 
 {
	 "investments":116784
 }
 ```
 
 - `/investments/amount`
 
 Number of meme coins invested in investments.
 
 ``` bash
 $ curl 'https://memes.market/api/investments/amount?from=1551654000&to=1551740400'
 
 {
	 "coins":153164238060
 }
 ```
 
 - `/investments/post/{post}`

All investments invested in the specified post. The post string is sanitized with regex. `[a-z0-9]{6}`

 ``` bash
 $ curl 'https://memes.market/api/investments/post/aibu3z?per_page=1&page=0'
 
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
 $ curl 'https://memes.market/api/investor/Thecsw'
 
 {
	 "id":"9072",
	 "name":"thecsw",
	 "balance":11000,
	 "badges":"[\"contributor\"]"
 }
 ```

 **NOTE:** as of 03/12/19, the bodges is unmarshalled. The ETA is several days, maybe weeks.

- `/investor/{name}/investments`

Returns an array of investments made by that user. Request variables are supported.

``` bash
$ curl 'https://memes.market/api/investor/mappum/investments?per_page=1&page=0'

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
$ curl 'https://memes.market/api/investor/DyspraxicRob/active?per_page=1&page=0'

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
$ curl 'https://memes.market/api/investors/top?per_page=3'

[
	{
		"id":"65277",
		"name":"lukenamop",
		"completed":167,
		"badges":"[]",
		"firm":51,
		"firm_role":"ceo",
		"networth":77252593483
	},
	{
		"id":"67546",
		"name":"EverythingTittysBoii",
		"balance":67258973992,
		"completed":121,
		"badges":"[]",
		"firm":1,
		"firm_role":"ceo",
		"networth":67258973992
	},
	{
		"id":"10400"
		"name":"youngmemeguy"
		"balance":1,
		"completed":249,
		"badges":"[\"top-s1\"]",
		"firm":51,
		"firm_role":"exec",
		"networth":54868148817
	}
]
```

## 6. Summary
