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


BASEDIR = scripts.basedir()
CONFIG_T2I_FILENAME = "t2i_presets.json"
CONFIG_I2I_FILENAME = "i2i_presets.json"

class QuickPreset(scripts.Script):

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.t2i_component_ids = [
            "txt2img_prompt",
            "txt2img_neg_prompt",
            "txt2img_sampling",
            "txt2img_steps",
            "txt2img_restore_faces",
            "txt2img_tiling",
            "txt2img_enable_hr",
            "txt2img_hr_upscaler",
            "txt2img_hires_steps",
            "txt2img_denoising_strength",
            "txt2img_hr_scale",
            "txt2img_hr_resize_x",
            "txt2img_hr_resize_y",
            "txt2img_width",
            "txt2img_height",
            "txt2img_batch_count",
            "txt2img_batch_size",
            "txt2img_cfg_scale",
        ]

        self.i2i_component_ids = [
            "img2img_prompt",
            "img2img_neg_prompt",
            "img2img_sampling",
            "img2img_steps",
            "img2img_restore_faces",
            "img2img_tiling",
            "img2img_width",
            "img2img_height",
            "img2img_denoising_strength",
            "img2img_batch_count",
            "img2img_batch_size",
            "img2img_cfg_scale",
        ]

        self.t2i_component_map = {k: None for k in self.t2i_component_ids}
        self.i2i_component_map = {k: None for k in self.i2i_component_ids}

        # text2img
        try:
            with open(f"{BASEDIR}/{CONFIG_T2I_FILENAME}") as f:
                self.t2i_presets = json.load(f)
        except FileNotFoundError:
            self.t2i_presets = {
                "Reset": {
                    "txt2img_prompt": "",
                    "txt2img_neg_prompt": "",
                    "txt2img_sampling": "Euler a",
                    "txt2img_steps": 20,
                    "txt2img_restore_faces": False,
                    "txt2img_tiling": False,
                    "txt2img_enable_hr": False,
                    "txt2img_width": 512,
                    "txt2img_height": 512,
                    "txt2img_batch_count": 1,
                    "txt2img_batch_size": 1,
                    "txt2img_cfg_scale": 7,
                },
            }
            json_object = json.dumps(self.t2i_presets, indent=4)
            with open(f"{BASEDIR}/{CONFIG_T2I_FILENAME}", "w") as f:
                f.write(json_object)

        # img2img
        try:
            with open(f"{BASEDIR}/{CONFIG_I2I_FILENAME}") as f:
                self.i2i_presets = json.load(f)
        except FileNotFoundError:
            self.i2i_presets = {
                "Reset": {
                    "img2img_prompt": "",
                    "img2img_neg_prompt": "",
                    "img2img_sampling": "Euler a",
                    "img2img_steps": 20,
                    "img2img_restore_faces": False,
                    "img2img_tiling": False,
                    "img2img_width": 512,
                    "img2img_height": 512,
                    "img2img_denoising_strength": 0.7,
                    "img2img_batch_count": 1,
                    "img2img_batch_size": 1,
                    "img2img_cfg_scale": 7,
                },
            }
            json_object = json.dumps(self.i2i_presets, indent=4)
            with open(f"{BASEDIR}/{CONFIG_I2I_FILENAME}", "w") as f:
                f.write(json_object)


    def fakeinit(self, *args, **kwargs):
        self.elm_prfx = "quick_preset"

        if self.is_txt2img:
            QuickPreset.t2i_dropdown = gr.Dropdown(
                label="",
                choices=list(self.t2i_presets.keys()),
                render = False,
                elem_id=f"{self.elm_prfx}_preset_dd"
            )
        else:
            QuickPreset.i2i_dropdown = gr.Dropdown(
                label="",
                choices=list(self.i2i_presets.keys()),
                render = False,
                elem_id=f"{self.elm_prfx}_preset_dd"
            )
        self.save_as     = gr.Text(render=False, label="Save", elem_id=f"{self.elm_prfx}_save")
        self.save_button = gr.Button(value="💾", variant="secondary", render=False, visible=True, elem_id=f"{self.elm_prfx}_save")

    def title(self):
        return "Quick Preset"
    
    def show(self, is_img2img):
        self.fakeinit()
        return scripts.AlwaysVisible
    
    def after_component(self, component, **kwargs):

        self.component_map    = None
        self.component_ids    = None
        self.config_file_name = None

        if self.is_txt2img:
            self.component_map    = self.t2i_component_map
            self.component_ids    = self.t2i_component_ids
            self.config_file_name = CONFIG_T2I_FILENAME
            self.config_presets   = self.t2i_presets
        else:
            self.component_map    = self.i2i_component_map
            self.component_ids    = self.i2i_component_ids
            self.config_file_name = CONFIG_I2I_FILENAME
            self.config_presets   = self.i2i_presets

        if component.elem_id in self.component_map:
            self.component_map[component.elem_id] = component

        # Setting
        if component.elem_id == "txt2img_generation_info_button" or component.elem_id == "img2img_generation_info_button":
            for component_name, component in self.component_map.items():
                if component is None:
                    print(f"[ERROR][Config-Presets] The component '{component_name}' no longer exists in the Web UI. Try updating the Config-Presets extension. This extension will not work until this issue is resolved.")
                    return

            self.index_type_components = []
            for component in self.component_map.values():
                if getattr(component, "type", "No type attr") == "index":
                    self.index_type_components.append(component.elem_id)
            self._ui()

        # presets
        # self.config_presets = self.t2i_presets

        # UI 
        if component.elem_id == "txt2img_clear_prompt" or component.elem_id == "img2img_clear_prompt":
            if self.is_txt2img:
                QuickPreset.t2i_dropdown.render()
            else:
                QuickPreset.i2i_dropdown.render()
        if component.elem_id == "txt2img_styles" or component.elem_id == "img2img_styles":
            self.save_as.render()
            self.save_button.render()

    # Change dropdown event
    def preset_dropdown_change(self, selector, *components):
        config_preset = self.config_presets[selector]
        current_components = dict(zip(self.component_map.keys(), components))
        current_components.update(config_preset)

        for component_name, component_value in current_components.items():
            if component_name in self.index_type_components and type(component_value) == int:
                current_components[component_name] = self.component_map[component_name].choices[component_value]

        return list(current_components.values())

    # UI configuration
    def _ui(self):
        components = list(self.component_map.values())
        if self.is_txt2img:
            QuickPreset.t2i_dropdown.change(
                fn = self.preset_dropdown_change,
                show_progress = False,
                inputs = [QuickPreset.t2i_dropdown, *components],
                outputs = components
            )
            QuickPreset.t2i_dropdown.change(
                fn = None,
                show_progress = False,
                inputs = [],
                outputs = [],
                _js = "config_preset_dropdown_change()"
            )
            self.save_button.click(
                fn=save_config(self.config_presets, self.component_map, self.config_file_name),
                show_progress=False,
                inputs=[self.save_as] + [self.component_map[comp_name] for comp_name in self.component_ids if self.component_map[comp_name] is not None],
                outputs=[self.save_as, QuickPreset.t2i_dropdown]
            )
        else:
            QuickPreset.i2i_dropdown.change(
                fn = self.preset_dropdown_change,
                show_progress = False,
                inputs = [QuickPreset.i2i_dropdown, *components],
                outputs = components
            )
            QuickPreset.i2i_dropdown.change(
                fn = None,
                show_progress = False,
                inputs = [],
                outputs = [],
                _js = "config_preset_dropdown_change()"
            )
            self.save_button.click(
                fn=save_config(self.config_presets, self.component_map, self.config_file_name),
                show_progress=False,
                inputs=[self.save_as] + [self.component_map[comp_name] for comp_name in self.component_ids if self.component_map[comp_name] is not None],
                outputs=[self.save_as, QuickPreset.i2i_dropdown]
            )
        self.save_as.change(
            fn = lambda x: gr.update(variant = "primary" if bool(x) else "secondary"),
            inputs = self.save_as,
            outputs = self.save_button
        )


def save_config(config_presets, component_map, config_file_name):
    def func(new_setting_name, *new_setting):

        if new_setting_name == "":
            return gr.Dropdown.update(), ""

        new_setting_map = {}
        for i, component_id in enumerate(component_map.keys()):
            if component_map[component_id] is not None:
                new_value = new_setting[i]  # this gives the index when the component is a dropdown
                if component_id == "txt2img_sampling":
                    new_setting_map[component_id] = modules.sd_samplers.samplers[new_value].name
                elif component_id == "img2img_sampling":
                    new_setting_map[component_id] = modules.sd_samplers.samplers_for_img2img[new_value].name
                else:
                    new_setting_map[component_id] = new_value

        config_presets.update({new_setting_name: new_setting_map})
        write_config_presets_to_file(config_presets, config_file_name)

        return '', gr.Dropdown.update(value=new_setting_name, choices=list(config_presets.keys()))

    return func

def load_config(path):
    file = os.path.join(BASEDIR, path)
    try:
        with open(file) as f:
            as_dict = json.load(f) 
    except FileNotFoundError as e:
        print(f"{e}\n{file} not found, check if it exists or if you have moved it.")
    return as_dict 


def write_config_presets_to_file(config_presets, config_file_name: str):
    json_object = json.dumps(config_presets, indent=4)
    with open(f"{BASEDIR}/{config_file_name}", "w") as outfile:
        outfile.write(json_object)