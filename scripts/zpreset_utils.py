import gradio as gr
import modules.sd_samplers
import modules.scripts as scripts
from modules import shared
import json
import os
import shutil
from pprint import pprint
from modules.ui import gr_show
from collections import namedtuple
from pathlib import Path

update_flag = "preset_manager_update_check"

additional_config_source = "additional_components.json"
additional_config_target = "additional_configs.json"
presets_config_source = "preset_configuration.json"
presets_config_target = "presets.json"

file_path = scripts.basedir() # file_path is basedir
scripts_path = os.path.join(file_path, "scripts")
path_to_update_flag = os.path.join(scripts_path, update_flag)
is_update_available = False
if os.path.exists(path_to_update_flag):
    is_update_available = True
    source_path = os.path.join(file_path, additional_config_source)
    target_path = os.path.join(file_path, additional_config_target)
    if not os.path.exists(target_path):
        shutil.move(source_path, target_path)
        print(f"Created: {additional_config_target}")
    else:
        print(f"Not writing {additional_config_target}: config exists already")
                    
    source_path = os.path.join(file_path, presets_config_source)
    target_path = os.path.join(file_path, presets_config_target)
    if not os.path.exists(target_path):
        shutil.move(source_path, target_path)
        print(f"Created: {presets_config_target}")
    else:
        print(f"Not writing {presets_config_target}: config exists already")
    os.remove(path_to_update_flag)



class PresetManager(scripts.Script):

    BASEDIR = scripts.basedir()

    def update_component_name(self, preset, oldval, newval):
        if preset.get(oldval) is not None:
            preset[newval] = preset.pop(oldval)

    def update_config(self):
        """This is a as per need method that will change per need"""
        component_remap = {
            "Highres. fix": "Hires. fix",
            "Firstpass width": "Upscaler",
            "Firstpass height": "Upscale by",
            "Sampling Steps": "Sampling steps"
            }
        config = self.get_config(self.settings_file)
        for preset in config.values():
            for old_val, new_val in component_remap.items():
                self.update_component_name(preset, old_val, new_val)
                    
        #PresetManager.all_presets = config
        self.save_config(self.settings_file, config)


    def __init__(self, *args, **kwargs):
        
        self.compinfo = namedtuple("CompInfo", ["component", "label", "elem_id", "kwargs"])

        #self.settings_file = "preset_configuration.json"
        self.settings_file = "presets.json"
        #self.additional_settings_file = "additional_components.json"
        self.additional_settings_file = "additional_configs.json"


        self.additional_components_for_presets = self.get_config(self.additional_settings_file) #additionalComponents
        self.available_components = [
            "Prompt",
            "Negative prompt",
            "Sampling steps",
            "Sampling method",
            "Width",
            "Height",
            "Restore faces",
            "Tiling",
            "Hires. fix",#new
            "Highres. fix",#old
            "Upscaler",#new
            "Upscale by",#new
            "Hires. steps",#New
            "Resize width to",#New
            "Resize height to",#New
            "Seed",
            "Extra",
            "Variation seed",
            "Variation strength",
            "Resize seed from width",
            "Resize seed from height",
            "Firstpass width",#old now is upscaler
            "Firstpass height",#old now is upscale by
            "Denoising strength",
            "Batch count",
            "Batch size",
            "CFG Scale",
            "Script",
        ]
        
        if is_update_available:
            self.update_config()

        # components that pass through after_components
        self.all_components = []

        # Read saved settings
        PresetManager.all_presets = self.get_config(self.settings_file)

        # Initialize
        self.component_map = {k: None for k in self.available_components}
        self.additional_components_map = {k:None for k in self.additional_components_for_presets["additionalComponents"]}
        self.additional_components = [x for x in self.additional_components_map] # acts like available_components list for additional components

        # combine defaults and choices
        self.component_map = {**self.component_map, **self.additional_components_map}
        self.available_components = self.available_components + self.additional_components


    
    def fakeinit(self, *args, **kwargs):
        """
        __init__ workaround, since some data is not available during instantiation, such as is_img2img, filename, etc.
        This method is called from .show(), as that's the first method ScriptRunner calls after handing some state dat (is_txt2img, is_img2img2)
        """
        self.elm_prfx = "preset-util"

        # UI elements
        # class level
        # NOTE: Would love to use one component rendered twice, but gradio does not allow rendering twice, so I need one per page
        if self.is_txt2img:
            # quick set tab
            PresetManager.txt2img_preset_dropdown = gr.Dropdown(
                label="",
                choices=list(PresetManager.all_presets.keys()),
                render = False,
                elem_id=f"{self.elm_prfx}_preset_qs_dd"
            )
        # else:
            PresetManager.img2img_preset_dropdown = gr.Dropdown(
                label="Presets",
                choices=list(PresetManager.all_presets.keys()),
                render = False,
                elem_id=f"{self.elm_prfx}_preset_qs_dd"
            )

        self.stackable_check = gr.Checkbox(value=True, label="Stackable", elem_id=f"{self.elm_prfx}_stackable_check", render=False)
        self.save_as = gr.Text(render=False, label="Save", elem_id=f"{self.elm_prfx}_save_qs_txt")
        self.save_button = gr.Button(value="💾", variant="secondary", render=False, visible=True, elem_id=f"{self.elm_prfx}_save_qs_txt")

    def title(self):
        return "Presets"

    def show(self, is_img2img):
        self.fakeinit()
        return True

    def before_component(self, component, **kwargs):
        pass

    def after_component(self, component, **kwargs):
        if hasattr(component, "label") or hasattr(component, "elem_id"):
            self.all_components.append(self.compinfo(
                                                    component=component,
                                                    label=component.label if hasattr(component, "label") else None,
                                                    elem_id=component.elem_id if hasattr(component, "elem_id") else None,
                                                    kwargs=kwargs
                                                    )
                                        )
        label = kwargs.get("label")
        ele = kwargs.get("elem_id")
        if label in self.component_map:
            self.component_map.update({component.label: component})
        

        if ele == "txt2img_clear_prompt" or ele == "img2img_clear_prompt":
            if self.is_txt2img:
                PresetManager.txt2img_preset_dropdown.render()
            else:
                PresetManager.img2img_preset_dropdown.render()
            self._ui()

        if ele == "txt2img_styles" or ele == "img2img_styles":
            self.save_as.render()
            self.save_button.render()
            self._ui2()

    def ui(self, *args):
        pass

    def _ui(self):
        # Conditional for class members
        if self.is_txt2img:
            PresetManager.txt2img_preset_dropdown.change(
                fn=self.preset_dropdown_change,
                inputs=PresetManager.txt2img_preset_dropdown,
                outputs=[],
            )
        else:
            PresetManager.img2img_preset_dropdown.change(
                fn=self.preset_dropdown_change,
                inputs=PresetManager.img2img_preset_dropdown,
                outputs=[],
            )
    def _ui2(self):
        self.save_button.click(
            fn=self.save_config,
            inputs=self.save_as,
            outputs=[]
        )

        self.save_as.change(
            fn = lambda x: gr.update(variant = "primary" if bool(x) else "secondary"),
            inputs = self.save_as,
            outputs = self.save_button
        )

    def run(self, p, *args):
        pass

    #####TODO
    def preset_dropdown_change(self, selector):
        print(selector)
    #####TODO
    def save_config(self, config_name):
        print(config_name)

    def get_config(self, path, open_mode='r'):
        file = os.path.join(PresetManager.BASEDIR, path)
        try:
            with open(file, open_mode) as f:
                as_dict = json.load(f) 
        except FileNotFoundError as e:
            print(f"{e}\n{file} not found, check if it exists or if you have moved it.")
        return as_dict
