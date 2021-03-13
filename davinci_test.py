import sys
import imp
import os
import DaVinciResolveScript as bmd

# lib_path = os.getenv('RESOLVE_SCRIPT_LIB')

RESOLVE_LUT_DIR = 'C:/ProgramData/Blackmagic Design/DaVinci Resolve/Support/LUT'

resolve = bmd.scriptapp("Resolve")
projectManager = resolve.GetProjectManager()
project = projectManager.GetCurrentProject()
timeline = project.GetCurrentTimeline()

current_clip = timeline.GetCurrentVideoItem()
current_clip.SetLUT(1, os.path.join(RESOLVE_LUT_DIR, "Sony SLog2 to Rec709.ilut"))

# 批量给时间线上的所有片段应用lut
# clips = timeline.GetItemListInTrack('video', 1)
# for clip in clips:
#     clip.SetLUT(1, os.path.join(RESOLVE_LUT_DIR, "Sony SLog2 to Rec709.ilut")) #两个参数，node索引和lut路径