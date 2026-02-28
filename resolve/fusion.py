from config import config
from utils import insp_obj

class FusionBridge:
  def __init__(self, timeline):
    self.comp = None
    self.comp_details = None
    self.timeline = timeline
    self.tool = None
    pass

  def find_comp(self, name):
    """
    Locates the Fusion Comp for the associated timeline

    Args:
      name(str): The name of the Fusion Composition

    Returns:
      A Fusion composition if found.
    """

    if self.comp_details:
      print(f"Using cacched comp: {self.comp_details["comp_name"]}")
      return self.comp_details["comp"]

    track_count = self.timeline.GetTrackCount("video")
    comp_name = name if name else "Scoreboard Composition"

    for track_index in range(1, track_count + 1):
      items = self.timeline.GetItemListInTrack("video", track_index)

      for item in items:
        name = item.GetName()
        start = item.GetStart()
        end = item.GetEnd()

        if name == comp_name:
          print(f" Start: {start}, End: {end}, Left Offset: {item.GetSourceStartTime()}")
          comp = item.GetFusionCompByIndex(1)

          if comp:
            print(f"Fusion Comp: {comp_name} has been found at {start}")
            self.comp_details = {
              "comp": comp,
              "comp_name": comp_name,
              "track_idx": track_index,
              "start_frame": float((start-end)/100)
            }
            return comp

    raise RuntimeError(f"Scoreboard Composition: {comp_name} was not found!")

  def find_tool(self, tool_name):
    """
    Locates the node that has the Scoreboard State controls

    Args:
      tool_name(str): The name of the Node to be located

    Returns:
      The node that has the Custom Controls for state.
    """
    if self.tool:
      print(f"Using cached tool: {self.tool.Name}")
      return self.tool

    comp = self.find_comp(config["fusion"]["comp_name"]) if self.comp == None else self.comp
    tool = comp.FindTool(tool_name)

    if tool:
      print(f"Found the tool: {tool_name}")
      self.tool = tool

      return tool

    raise RuntimeError(f"Scoreboard tool {tool_name} was not found!")

  def initialize_controls(self, controls):
    comp = self.find_comp(config["fusion"]["comp_name"])
    tool = self.find_tool(config["fusion"]["tool_name"])

    for control in controls:
      tool[control] = None # Resets Keyframes

      # Sets the control to BezierSpline
      tool[control] = comp.BezierSpline({})

      # Set the initial frame 0.0 to a value of 0
      tool.SetInput(control, 0, 0.0) # Control, Value, Frame
