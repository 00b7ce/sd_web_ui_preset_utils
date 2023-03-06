function config_preset_dropdown_change() {

    // const root = gradioApp()

    // const prompt          = root.querySelector('#txt2img_prompt').querySelector('label').querySelector('textarea');
    // const neg_prompt      = root.querySelector('#txt2img_neg_prompt').querySelector('label').querySelector('textarea');
    // const sampler         = root.querySelector('#txt2img_sampling').querySelector('label').querySelector('select');
    // const steps           = root.querySelector('#txt2img_steps').querySelector('input');
    // const is_restore_face = root.querySelector('#txt2img_restore_faces').querySelector('input');
    // const is_tiling       = root.querySelector('#txt2img_tiling').querySelector('input');
    // const is_hires_fix    = root.querySelector('#txt2img_enable_hr').querySelector('input');
    // const hires_sampler   = root.querySelector('#txt2img_hr_upscaler').querySelector('input');
    // const hires_steps     = root.querySelector('#txt2img_hires_steps').querySelector('input');
    // const hires_denoising = root.querySelector('#txt2img_denoising_strength').querySelector('input');
    // const hires_upscale   = root.querySelector('#txt2img_hr_scale').querySelector('input');
    // const hires_width     = root.querySelector('#txt2img_hr_resize_x').querySelector('input');
    // const hires_height    = root.querySelector('#txt2img_hr_resize_y').querySelector('input');
    // const img_width       = root.querySelector('#txt2img_width').querySelector('input');
    // const img_height      = root.querySelector('#txt2img_height').querySelector('input');
    // const batch_count     = root.querySelector('#txt2img_batch_count').querySelector('input');
    // const batch_size      = root.querySelector('#txt2img_batch_size').querySelector('input');
    // const cfg_scale       = root.querySelector('#txt2img_cfg_scale').querySelector('input');

	setTimeout(function() { 
		let hiresFixCheckbox = gradioApp().querySelector("#txt2img_enable_hr > label").firstChild //gets the <input> element next to the "Hires. fix" <span>
		
		let e = document.createEvent("HTMLEvents")
		e.initEvent("change", true, false)
		hiresFixCheckbox.dispatchEvent(e)
		
		//console.log("hiresFixCheckbox="+hiresFixCheckbox)
		//console.log("e="+e)
	}, 200) //50ms is too fast

    return []
}



// class PresetManagerDropdownComponent{
//     constructor(component){
//         this.component = gradioApp().getElementById(component)
//     }
//     updateDropdown(selection){
//         //getElementById("preset-util_preset_ds_dd").querySelector("select").querySelectorAll("option")[1].selected = true;
//         //Array.from(this.component.querySelector("select").querySelectorAll("option")).find( e => e.value.includes(selection)).selected = true;
//         this.getDropDownOptions().find( e => e.value.includes(selection)).selected = true;
//         this.component.querySelector("select").dispatchEvent(new Event("change"));
//     }
//     getDropDownOptions(asValues=false){
//         if (asValues){
//             let temp = new Array;
//             Array.from(this.component.querySelector("select").querySelectorAll("option")).forEach( opt => temp.push(opt.value))
//             return temp
//         }
//         else{
//             return Array.from(this.component.querySelector("select").querySelectorAll("option"))
//         }
//     }
//     getCurrentSelection(){
//         return this.component.querySelector("select").value
//     }
// }

// class PresetManagerCheckboxGroupComponent{
//     constructor(component){
//         this.component = gradioApp().getElementById(component);
//         this.checkBoxes = new Object;
//         this.setCheckBoxesContainer()
//     }
//     setCheckBoxesContainer(){
//         Array.from(this.component.querySelectorAll("input")).forEach( _input => this.checkBoxes[_input.nextElementSibling.innerText] = _input)
//     }
//     getCheckBoxes(){
//         let response = new Array;
//         for (let _component in this.checkBoxes){
//             response.push([_component, this.checkBoxes[_component]])
//         }
//         return response
//     }
//     setCheckBoxesValues(iterable){
//         for (let _componentText in this.checkBoxes){
//             this.conditionalToggle(false, this.checkBoxes[_componentText])
//         }
//         if (iterable instanceof Array){
//             setTimeout( () =>
//             iterable.forEach( _label => this.conditionalToggle(true, this.checkBoxes[_label])),
//             2)
//         }
//     }
//     conditionalToggle(desiredVal, _component){
//         //This method behaves like 'set this value to this'
//         //Using element.checked = true/false, does not register the change, even if you called change afterwards,
//         //  it only sets what it looks like in our case, because there is no form submit, a person then has to click on it twice.
//         //Options are to use .click() or dispatch an event
//         if (desiredVal != _component.checked){
//             _component.dispatchEvent(new Event("change"))//using change event instead of click, in case browser ad-blockers blocks the click method
//         }
//     }
// }
// class PresetManagerMover{
//     constructor(self, target, onLoadHandler){
//         this.presetManager = gradioApp().getElementById(self)
//         this.target = gradioApp().getElementById(target)
//         this.handler = gradioApp().getElementById(onLoadHandler)
//     }
//     move(adjacentAt='afterend'){
//         /*
//         'beforebegin'
//             <ele>
//             'afterbegin'
//                 <otherele>
//             'beforeend'
//             </ele>
//         'afterend'
//         */
         
//         this.target.insertAdjacentElement(adjacentAt, this.presetManager)
//     }
//     updateTarget(new_target){
//         this.target = gradioApp().getElementById(new_target)
//     }
// }
