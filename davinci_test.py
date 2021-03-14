import sys
import os
from shutil import copy
import DaVinciResolveScript as bmd

# lib_path = os.getenv('RESOLVE_SCRIPT_LIB')

RESOLVE_LUT_DIR = 'C:/ProgramData/Blackmagic Design/DaVinci Resolve/Support/LUT/Custom'

if not os.path.exists(RESOLVE_LUT_DIR):
    os.makedirs(RESOLVE_LUT_DIR)

resolve = bmd.scriptapp("Resolve")
projectManager = resolve.GetProjectManager()
project = projectManager.GetCurrentProject()
timeline = project.GetCurrentTimeline()

lut_to_load = 'G:/Documents/大学/毕设相关/smart-lut-creator/gen_lut/srgb to ycbcr.cube'
copy(lut_to_load, RESOLVE_LUT_DIR)

current_clip = timeline.GetCurrentVideoItem()
current_clip.SetLUT(1, os.path.join(RESOLVE_LUT_DIR, "srgb to ycbcr.cube"))

# 批量给时间线上的所有片段应用lut
# clips = timeline.GetItemListInTrack('video', 1)
# for clip in clips:
#     clip.SetLUT(1, os.path.join(RESOLVE_LUT_DIR, "Sony SLog2 to Rec709.ilut")) #两个参数，node索引和lut路径