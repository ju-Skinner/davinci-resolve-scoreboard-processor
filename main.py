from utils import get_core_resolve_objects
from config import config

from resolve.fusion import FusionBridge

resolve, project_manager, project, timeline = get_core_resolve_objects()

print(config["fusion"]["comp_name"])
comp_name = config["fusion"]["comp_name"]
tool_name = config["fusion"]["tool_name"]

bridge = FusionBridge(timeline)
comp = bridge.find_comp(comp_name)
tool = bridge.find_tool(tool_name)
comp_start_frame = bridge.comp_details["start_frame"]

print(f"Comp Start Frame: {comp_start_frame}")
controls = config["controls"].values()
bridge.initialize_controls(controls)


### Get Markers
def get_markers(timeline):
  """
  Gets all the markers from the timeline

  Args:
    timeline: The timeline that will have markers

  Returns:
    markers: A collection of markers
  """
  markers = timeline.GetMarkers()

  results = []

  for frame, marker in markers.items():
    results.append({
      "frame": float(frame),
      "color": marker["color"],
      "name": marker["name"],
      "note": marker["note"]
    })

  results.sort(key=lambda x: x["frame"])

  return results

markers = get_markers(timeline)

home_score_key_frames = {}
away_score_key_frames = {}

home_timeout_key_frames = {}
away_timeout_key_frames = {}

home_score = 0
home_timeouts = 0

away_score = 0
away_timeouts = 0

epsilon = 1e-9


for marker in markers:
  frame = marker["frame"]
  color = marker["color"]
  frame_w_offset = abs(float(frame + comp_start_frame))
  step_in_frame = float(frame_w_offset + epsilon)

  # print(f"Processing marker {color} at {frame}, offset: {offset} w/offset: {frame + offset}")

  if color == config["markers"]["away_score"]:
    away_score += 1

    away_score_key_frames[frame_w_offset] = {
        1: away_score
      }

    away_score_key_frames[step_in_frame] = {
        1: away_score,
        "Flags": {"StepIn": True}
      }
  elif color == config["markers"]["home_score"]:
    home_score += 1
    home_score_key_frames[frame_w_offset] = {
        1: home_score
      }

    home_score_key_frames[step_in_frame] = {
        1: home_score,
        "Flags": {"StepIn": True}
      }
  elif color == config["markers"]["home_timeout"]:
    home_timeouts += 1
    home_timeout_key_frames[frame_w_offset] = {
        1: home_timeouts
      }

    home_timeout_key_frames[step_in_frame] = {
        1: home_timeouts,
        "Flags": {"StepIn": True}
      }
  elif color == config["markers"]["away_timeout"]:
    away_timeouts += 1
    away_timeout_key_frames[frame_w_offset] = {
        1: away_timeouts
      }

    away_timeout_key_frames[step_in_frame] = {
        1: away_timeouts,
        "Flags": {"StepIn": True}
      }

    # print(f"Key Frames: {away_score_key_frames}")
    # key = {
    #   frame: {
    #     1: away_score
    #   },
    #   (frame + epsilon): {
    #     1: away_score,
    #     "Flags": {"StepIn": True}
    #   }
    # }

spline_out = tool["AwayScore"].GetConnectedOutput()
spline = spline_out.GetTool()
spline.SetKeyFrames(away_score_key_frames)

spline_out = tool["AwayTimeouts"].GetConnectedOutput()
spline = spline_out.GetTool()
spline.SetKeyFrames(away_timeout_key_frames)

spline_out = tool["HomeScore"].GetConnectedOutput()
spline = spline_out.GetTool()
spline.SetKeyFrames(home_score_key_frames)

spline_out = tool["HomeTimeouts"].GetConnectedOutput()
spline = spline_out.GetTool()
spline.SetKeyFrames(home_timeout_key_frames)


# print(f"Markers: {markers}")

# ### Build out Spline

# spline_data = spline.GetKeyFrames()


# key_frames = {
#     0.0: {
#         1: 0,
#         "Flags": {"Linear": True}
#     },

#     40.0: {
#         1: 0
#     },

#     40.000000001: {
#         1: 10,
#         "Flags": {"StepIn": True}
#     },

#     838.0: {
#         1: 20,
#         "Flags": {"StepIn": True}
#     }
# }
# spline.SetKeyFrames(key_frames)

# tool.ConnectInput(
#     control,
#     spline,
#     "Value"
# )





#--- NOT USED --- ###
# def create_state_spline(comp, name):

#     spline = comp.AddTool("BezierSpline", -32768, -32768)

#     spline.SetAttrs({
#         "TOOLS_Name": name
#     })

#     return spline

# def write_keyframes(spline, key_data):

#     spline_input = spline["Value"]

#     spline_input.SetAttrs({
#         "TOOLS_KeyFrames": key_data
#     })


# comp.Lock()
# comp.StartUndo("Create Scoreboard State")
# home_score = create_state_spline(
#     comp,
#     "ScoreboardStateHomeScore"
# )

# write_keyframes(home_score, key_frames)
# tool.ConnectInput(
#     "HomeScore",
#     home_score,
#     "Value"
# )
# comp.EndUndo(True)
# comp.Unlock()
