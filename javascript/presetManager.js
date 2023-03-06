function config_preset_dropdown_change() {
	setTimeout(function() { 
		let hiresFixCheckbox = gradioApp().querySelector("#txt2img_enable_hr > label").firstChild //gets the <input> element next to the "Hires. fix" <span>
		
		let e = document.createEvent("HTMLEvents")
		e.initEvent("change", true, false)
		hiresFixCheckbox.dispatchEvent(e)
		
	}, 200) //50ms is too fast

    return []
}
