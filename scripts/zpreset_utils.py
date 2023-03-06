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

presets_config_target = "presets.json"

file_path = scripts.basedir() # file_path is basedir
scripts_path = os.path.join(file_path, "scripts")
path_to_update_flag = os.path.join(scripts_path, update_flag)
is_update_available = False
if os.path.exists(path_to_update_flag):
    is_update_available = True
                    
class PresetManager(scripts.Script):

    BASEDIR = scripts.basedir()

    def update_component_name(self, preset, oldval, newval):
        if preset.get(oldval) is not None:
            preset[newval] = preset.pop(oldval)

    def __init__(self, *args, **kwargs):
        
        self.compinfo = namedtuple("CompInfo", ["component", "label", "elem_id", "kwargs"])

        self.settings_file = "presets.json"

        self.available_components = [
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
        
        # components that pass through after_components
        self.all_components = []

        # Read saved settings
        PresetManager.all_presets = self.get_config(self.settings_file)

        # Initialize
        self.component_map = {k: None for k in self.available_components}

    def fakeinit(self, *args, **kwargs):
        """
        __init__ workaround, since some data is not available during instantiation, such as is_img2img, filename, etc.
        This method is called from .show(), as that's the first method ScriptRunner calls after handing some state dat (is_txt2img, is_img2img2)
        """
        self.elm_prfx = "preset-util"

        if self.is_txt2img:
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

    #####TODO
    def preset_dropdown_change(self, selection, *comps_vals):
        print(self.component_map.keys())

    def _ui(self):
        if self.is_txt2img:
            PresetManager.txt2img_preset_dropdown.change(
                fn=self.preset_dropdown_change,
                inputs=[],
                outputs=[],
            )
            PresetManager.txt2img_preset_dropdown.change(
                fn=None,
                inputs=[],
                outputs=[],
                _js="config_preset_dropdown_change",
            )
        else:
            PresetManager.img2img_preset_dropdown.change(
                fn=self.preset_dropdown_change,
                inputs=[],
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
    def save_config(self, config_name):
        print(config_name)

    def f_b_syncer(self):
        """
        ?Front/Backend synchronizer?
        Not knowing what else to call it, simple idea, rough to figure out. When updating choices on the front-end, back-end isn't updated, make them both match
        https://github.com/gradio-app/gradio/discussions/2848
        """
        self.inspect_dd.choices = [str(x) for x in self.all_components]
        return [gr.update(choices=[str(x) for x in self.all_components]), gr.Button.update(visible=False)]

    def get_config(self, path, open_mode='r'):
        file = os.path.join(PresetManager.BASEDIR, path)
        try:
            with open(file, open_mode) as f:
                as_dict = json.load(f) 
        except FileNotFoundError as e:
            print(f"{e}\n{file} not found, check if it exists or if you have moved it.")
        return as_dict
