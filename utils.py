import sys
import inspect

RESOLVE_SCRIPT_PATH = "/Library/Application Support/Blackmagic Design/DaVinci Resolve/Developer/Scripting/Modules/"
if RESOLVE_SCRIPT_PATH not in sys.path:
  sys.path.insert(0, RESOLVE_SCRIPT_PATH)

#-----
#
# Get Davinci "Resolve" object"
#
#-----
def get_resolve():
  """
  Imports the DaVinciResolveScipting API

  Returns:
    An instance of the Resolve API

  """
  try:
    import DaVinciResolveScript as bmd
  except ImportError:
    print("Unable to find module DaVinciResolveScript from $PYTHONPATH - trying default locations")
    try:
      import imp
      bmd = imp.load_source('DaVinciResolveScript', RESOLVE_SCRIPT_PATH+"DaVinciResolveScript.py")
    except ImportError:
      # No Fallback
      print("Unable to find module DaVinciResolveSCript")
      print(f"For a DaVinci Resolve installation, the module is expected to be located in: {RESOLVE_SCRIPT_PATH}")

  return bmd.scriptapp("Resolve")

def get_core_resolve_objects():
  """Gets the Core Resolve Objects used throughout the process

  Returns:
    An array of objects [resolve, project_manager, project, timeline]
  """

  resolve = get_resolve()

  project_manager = resolve.GetProjectManager()
  if not project_manager:
    print("Project Manager not avaialable")
    raise RuntimeError

  project = project_manager.GetCurrentProject()
  if not project:
    print("No current project found")
    raise RuntimeError

  timeline = project.GetCurrentTimeline()
  if not timeline:
    print("No current timeline found")
    raise RuntimeError

  return resolve, project_manager, project, timeline

#-----
#
# Converts Timecode to Frames
#
# @timecode: string format hh:mm:ss:ff
# @fps: Frames Per Second
#
#-----
def timecode_to_frame(timecode, fps):
  """
  Converts the timecode to frame

  Args:
    timecode(str): The Timecode that will be converted
    fps(int): Frames Per Second to calculate the frame

  Returns:
    (int)
  """
  hh, mm, ss, ff = map(int, timecode.split(':'))

  total_frames = ((hh * 3600) + (mm * 60) + ss) * fps + ff

  return total_frames

def frame_to_timecode(frame, fps):
  """
  Converts the frame number to timecode

  Args:
    frame(int): The frame number that will be converted
    fps(int): Frames Per Second to calculate the timecode

  Returns:
    (str)
  """
  total_seconds = int(frame // fps)
  ff = int(round(frame % fps))

  hh = total_seconds // 3600
  mm = (total_seconds % 3600) // 60
  ss = total_seconds % 60

  return f"{hh:02}:{mm:02}:{ss:02}:{ff:02}"

def insp_obj(obj, header=""):
  print(f"----{header}----  type: {type(obj)}")
  for attr in sorted(dir(obj)):
    try:
      value = getattr(obj, attr)

      if callable(value):
        sig = None
        # try direct signature
        try:
          sig = inspect.signature(value)
        except (ValueError, TypeError):
          # try to get signature from the attribute on the object's class
          try:
            cls_attr = getattr(type(obj), attr, None)
            if cls_attr:
              sig = inspect.signature(cls_attr)
          except (ValueError, TypeError, AttributeError):
            sig = None

        doc = inspect.getdoc(value) or getattr(value, "__doc__", None)
        if sig:
          print(f"  {attr}{sig}")
          if doc:
            first = doc.splitlines()[0]
            print(f"    doc: {first}")
        elif doc:
          first = doc.splitlines()[0]
          print(f"  {attr}: {first}")
        else:
          # fallback: print repr for native/bound methods
          print(f"  {attr}: <callable (no signature/doc available)>")
      else:
        # non-callable attribute
        print(f"  {attr}: {repr(value)}")
    except Exception as e:
      print(f"  {attr}: <error retrieving value: {e}>")
