import {connectionErrorToast} from "./modules/uiElements.js"
import * as jsonApi from "./modules/jsonApi.js"
import {formatToUnits, getSuffix, commafy} from "./modules/dataUtils.js"
import {seasons} from "../resources/leaderboards/seasons.js"

const getSeason = (function() {
	const ids = {
		dropdown: "dataset-select"
	}
	const cache = {}
	function init() {
		const dropDown = document.getElementById(ids.dropdown)
		const html = seasons.map(s=>`<option value="${s.id}" >${s.name}</option>`).join("")
		dropDown.innerHTML = html
		dropDown.addEventListener("change", _=> search(dropDown.value) )
		window.addEventListener("popstate", function(e) {
			checkUrl()
		})
		checkUrl()
	}
	function isValidId(id) {
		return seasons.some(a => a.id === id)
	}
	function getLastId() {
		return seasons[seasons.length-1].id
	}
	function checkUrl() {
		// check if url contains ?season=<a valid season>
		const url = new URL(window.location.href)
		let seasonId = url.searchParams.get("season")
		if (!isValidId(seasonId)) {
			seasonId = getLastId()
			history.replaceState(null, "", "?season="+seasonId)
		}
		search(seasonId, false)
	}
	function search(seasonId, pushState = true) {
		if (pushState)history.pushState(null, "", "?season="+seasonId)
		document.getElementById(ids.dropdown).value = seasonId
		//download the season data if not in cache. then proceeds to update the leaderboard
		if (!cache[seasonId]) {
			const seasonUrl = seasons.find(s=> s.id === seasonId).dataUrl
			const options = {
				method: "GET",
				url: seasonUrl
			}
			jsonApi.get("",options)
				.then(d=>{
					cache[seasonId] = d
					leaderboard.update(d)
				})
				.catch(connectionErrorToast)
		} else {
			leaderboard.update(cache[seasonId])
		}
	}
	return {
		init: init
	}
})()


const leaderboard = (function() {
	const ids = {
		table: "leaderboards-table",
		cards: {
			prefix: ["top","left","right"],
			name: "name",
			netWorth: "net-worth",
			netWorthSuffix: "net-worth-suffix",
			profile: "profile"
		}
	}
	const cardElements = {}

	function init() {
		//init card elements
		for (const prefix of ids.cards.prefix) {
			cardElements[prefix] = {
				name: document.getElementById(prefix+"-"+ids.cards.name),
				netWorth: new CountUp(prefix+"-"+ids.cards.netWorth,0, 0, 1),
				netWorthSuffix: document.getElementById(prefix+"-"+ids.cards.netWorthSuffix),
				profile: document.getElementById(prefix+"-"+ids.cards.profile)
			}
		}
	}
	function update(data) {
		renderCards(data)
		renderTable(data)
	}
	function renderTable(obj) {
		let html = ""
		for (let i=3,l=obj.length; i<l;i++) {
			const user = obj[i]
			const badge = user.broke>0 ? `<span class="red bankrupt-badge white-text">${user.broke}</span>`: ""
			html += `<tr>
                     <td>#${i+1}</td>
                     <td><a href="./user.html?account=${user.name}">${user.name} ${badge}</a></td>
                     <td title="${commafy(user.networth)} M&cent;">${formatToUnits(user.networth)}</td>
                     <td>${user.completed}</td>
                  </tr>`
		}
		document.getElementById(ids.table).innerHTML = html  
	}
   
	function updateName(card, data) {
		card.name.innerText = data.name
		setTimeout(removeClass(card), 500)
   }
   
	function removeClass(card) {
		card.name.classList.remove("flip")
	}
   
	function renderCards(obj) {
		for (let i = 0; i < 3; i++) {
			const data = obj[i]
			const card = cardElements[ids.cards.prefix[i]]
			card.name.classList.add("flip")
			setTimeout(updateName(card, data), 240)
			const netWorth = getSuffix(data.networth)
			card.netWorth.update(netWorth.val)
			card.netWorthSuffix.innerText = netWorth.suffix
			card.profile.setAttribute("href", "./user.html?account="+data.name)
		}
	}
	return {
		init: init,
		update: update
	}
})();

(function() {
	document.addEventListener("DOMContentLoaded", function() {
		getSeason.init()
		leaderboard.init()
		document.getElementById("scroll-top").addEventListener("click", _ => scroll(0, 0))
      
	})
})()
