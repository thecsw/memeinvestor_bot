import {connectionErrorToast} from "./modules/uiElements.js"
import * as jsonApi from "./modules/jsonApi.js"
import {Scheduler} from "./modules/scheduler.js"
import {formatToUnits, getSuffix} from "./modules/dataUtils.js"
import {getFileName, getDescription} from "./modules/badges.js"

var getFirm = (function() {
	function show(device, pushState=true) {
		const url = new URL(window.location.href)
		const firm = url.searchParams.get("firm")
		if (firm.length > 0) {
			if (device === "mobile") {
				//close sidenav
				const elem = document.getElementById("mobile-sidebar")
				const instance = M.Sidenav.getInstance(elem)
				instance.close()
			}
			if (pushState)history.pushState(null, "", "?firm="+firm)
			pageManager.search(firm)
		}
	}
	return {
		show: show
	}
})()

const pageManager = (function() {
	const ids = {
		overlay: "overlay",
		overlayContent: "overlay-content",
		firm: "firm-name",
		rank: "firm-rank",
		size: "firm-size-suffix",
		balance: "firm-balance",
		image: "firm-image"
	}
	let overviewUpdater = undefined
	function init() {
		//nothing to init
	}
	function search(firm) {
		//set overlay to loading 
		document.body.style.overflowY = "hidden"
		document.getElementById(ids.overlay).style.display = "block"
		document.getElementById(ids.overlayContent).innerHTML = 
      `<h4>Searching. </h4>
      <div class="preloader-wrapper big active">
          <div class="spinner-layer spinner-yellow-only">
            <div class="circle-clipper left">
              <div class="circle"></div>
            </div><div class="gap-patch">
              <div class="circle"></div>
            </div><div class="circle-clipper right">
              <div class="circle"></div>
            </div>
          </div>
         </div>`
      //search firm
		jsonApi.get("/firm/"+firm)
			.then(d=> {
				if (d.id == 0) {
					notFound()
				} else {
					display(d)
				}
			})
			.catch(er=>{
				if (er.status == 404) {
					notFound()
				} else {
					connectionErrorToast(er)
				}
			})
	}
	function notFound() {
		document.body.style.overflowY = "hidden"
		document.getElementById(ids.overlay).style.display = "block"
		document.getElementById(ids.overlayContent).innerHTML = 
      "<h5>Firm not found</h5>"
      //kill old overview updater
		if (overviewUpdater)overviewUpdater.stop()
		overviewUpdater = undefined
	}
	function display(data) {
		//remove overlay with animation
		const overlay = document.getElementById(ids.overlay)
		overlay.classList.add("fade-out")
		setTimeout(_=>{
			document.body.style.overflowY = "auto"
			overlay.style.display = "none"
			overlay.classList.remove("fade-out")
		},900)
      
		//update name
		const nameEl = document.getElementById(ids.firm)
		const sizeEl = document.getElementById(ids.size)
		//let imageEl = document.getElementById(ids.image);
		nameEl.innerText = data.name
		const maxSize = Math.pow(2,(data.rank+3))
		sizeEl.innerHTML = maxSize
		overview.update(data)
		//update firm members
		firmMembers.setFirm(data.id,data.size)
		//update firm value
		//firmValue.setFirm(data.firm,data.firm-members);
	}
	return {
		init: init,
		search: search
	}
})()

const overview = (function() {
	let counters = {
		firmBalance: undefined,
		firmRank: undefined,
		firmSize: undefined,
		firmTax: undefined
	}
	function init(data) {
		counters = {
			firmBalance: new CountUp("firm-balance", 0, 0),
			firmRank: new CountUp("firm-rank",0,0),
			firmSize: new CountUp("firm-size", 0, 0),
			firmTax: new CountUp("firm-tax", 0, 0)
		}
		if (data)update(data)
	}
	function update(data) {
		counters.firmBalance.update(data.balance)
		counters.firmRank.update(data.rank)
		counters.firmSize.update(data.size)
		counters.firmTax.update(data.tax)
	}
	return {
		init:init,
		update: update
	}
   
})()

const upgrades = (function() {
	const ids = {
		container: "upgrades-container"
	}
	const amount = 0
	function set(upgrades) {
		render(upgrades)
	}
	function render(upgrades) {
		let html = ""
		for (const upgrade of upgrades) {
			html += `
         <img class="badge z-depth-2 tooltipped" 
         data-position="top" 
         data-tooltip="${getDescription(upgrade)}" 
         src="./resources/badges/${getFileName(upgrade)}"/>
         `
		}
		if (!html)html="<p class=\"grey-text\">This firm doesn't have any upgrades.</p>"
		const container = document.getElementById(ids.container)
		container.innerHTML = html
		const elems = container.querySelectorAll(".tooltipped")
		M.Tooltip.init(elems)
	}
	return {
		set: set
	}
})()


const firmMembers = (function() {
	const ids = {
		table: "investments-table",
		tableOverlay: "investments-table-overlay",
		page: {
			previous: "page-previous",
			indicator: "page-indicator",
			next: "page-next"
		}
	}
	let loading = false
   
	let id = ""

	let showOverlayTimer
	let showingOverlay = false
   
	const perPage = 100
	let pages = 0
	let page = 0
	const tFrom = ""
	const tTo = ""
   
	function init() {
		document.getElementById(ids.page.previous).addEventListener("click",previous)
		document.getElementById(ids.page.next).addEventListener("click",next)
	}
	//initialize the table for a specific user
	function setFirm(firmId,firmSize) {
		id = firmId
		pages = Math.ceil(firmSize/perPage)
		page = 0
		updatePageNumber()
		updateTable()
	}
	function previous() {
		if (!loading) {
			page--
			updatePageNumber()
			updateTable()
		}
	}
	function updatePageNumber() {
		const previousBt = document.getElementById(ids.page.previous).classList
		const nextBt = document.getElementById(ids.page.next).classList
		//increment by one the page number. keep it to zero if there are zero pages
		const pageNonZeroIndexed = pages>0 ? page+1 : page
		document.getElementById(ids.page.indicator).innerText = (pageNonZeroIndexed)+"/"+pages
      
		if (page>0) previousBt.remove("disabled")
		else previousBt.add("disabled")
   
		if ((page+1)<pages) nextBt.remove("disabled")
		else nextBt.add("disabled")
	}
	function next() {
		if (!loading) {
			page++
			updatePageNumber()
			updateTable()
		}
	}
	function updateTable() {
		showOverlay()
		const options = `?per_page=${perPage}&page=${page}&from=${tFrom}&to=${tTo}`
		jsonApi.get(`/firm/${id}/members${options}`)
			.then(d=>{
				if (d.length>0)render(d)
				removeOverlay()
			})
			.catch(er=>{
				connectionErrorToast(er)
			})      
	}
	function showOverlay() {
		console.log(9)
		loading = true
		//set a timer that displays the loading overlay after x milliseconds
		showOverlayTimer = setTimeout(function() {
			console.log(10)
			showingOverlay = true
			document.getElementById(ids.table).style.opacity = 0.4
			document.getElementById(ids.tableOverlay).style.opacity = 1      
		},200//the max millis of time allowed to api calls before the loader overlay is shown
		)
	}
	function removeOverlay() {
		//remove the overlay if it is being shown
		console.log(11)
		if (showingOverlay) {
			console.log(12)
			const overlay = document.getElementById(ids.tableOverlay)
			document.getElementById(ids.table).style.opacity = 1
			overlay.classList.add("pulse-out")
			setTimeout(_=>{
				showingOverlay = false
				loading = false
				overlay.style.opacity = 0
				overlay.classList.remove("pulse-out")
			},400)
		} else {
			loading = false
			//if the overlay is not not being shown (there is a timer that is about to show it)
			//stop the timer 
			clearTimeout(showOverlayTimer)
		}
	}
	function render(data) {
		//console.log(data)
		let html = `
      <thead>
        <tr>
            <th>name</th>
            <th>position</th>
            <th>balance</th>
            <th>completed investments</th>
        </tr>
      </thead>
      <tbody>
      `
		for (const member of data) {
			const balance = getSuffix(member.balance)
			html += `
         <tr>
            <td><a href="./user.html?account=${member.name}">${member.name}</a></td>
            <td>${member.firm_role}</td>
            <td>${balance.val} ${balance.suffix} M¢</td>
            <td>${member.completed} investments</td>
            <td>`
			html += "</td></tr>"
		}
		html += "</tbody>"
		document.getElementById(ids.table).innerHTML = html
	}
	return {
		init: init,
		setFirm: setFirm
	}
})();


(function() {
	document.addEventListener("DOMContentLoaded", function() {
		getFirm.show()
		pageManager.init()
		overview.init()
		firmMembers.init()
	})
})()
