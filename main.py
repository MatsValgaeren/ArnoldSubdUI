# Elise Bourgoignie 
# Mats Valgaeren
from maya import cmds

class ArnoldSubdUI:
    """
    Maya tool for batch-editing Arnold Subdivision attributes on multiple mesh objects.
    Provides a simple UI to set subdivision type and iteration count for selected meshes.
    """

    def __init__(self):
        # Window title and unique window name (lowercase, underscores)
        self.window_title = "Set Arnold Subdivision"
        self.tool_window = self.window_title.replace(" ", "_").casefold()

        # Ensure previous instances are cleaned up, then build the UI
        self.window_cleaner()
        self.build_ui()

    def build_ui(self):
        """
        Constructs the UI window and its controls.
        """
        # Create main window
        self.tool_window = cmds.window(
            self.tool_window,
            title=self.window_title,
            resizeToFitChildren=True
        )

        # Main layout: vertical column
        cmds.columnLayout(adjustableColumn=True, rowSpacing=10)

        # Container for all UI elements
        self.mainLayout = cmds.columnLayout(w=300, h=150, adjustableColumn=True)

        # Title label
        cmds.text(
            label="Arnold Subdivisions",
            w=250, h=50, fn="boldLabelFont",
            bgc=(0.15, 0.15, 0.15)
        )
        cmds.separator(h=10, style="none")  # Spacer

        # Row layout: Subdivision type and iterations input
        self.rowLayout = cmds.rowColumnLayout(
            nc=3,
            cw=[(1, 150), (2, 60), (3, 50)],
            adjustableColumn=True
        )

        # Dropdown for subdivision type
        self.subOptionMenu = cmds.optionMenuGrp(
            "subOptionMenu",
            label="Sub Type",
            cal=[1, "left"],
            cw=(1, 62)
        )
        cmds.menuItem(label="none")
        cmds.menuItem(label="catclark")
        cmds.menuItem(label="linear")
        # Set 'catclark' as default (index 2)
        cmds.optionMenuGrp(self.subOptionMenu, e=1, sl=2)

        # Iteration count input
        self.iterationNumbtext = cmds.text(label="Iterations", fn="plainLabelFont")
        self.iterationNumb = cmds.intField(
            "iterationNumb",
            minValue=0,
            maxValue=100,
            value=2,
            w=1
        )

        cmds.separator(h=10, style="none")  # Spacer

        # Main action button
        self.subBtn = cmds.button(
            label="Set Subdivisions",
            w=250, h=50,
            parent=self.mainLayout,
            command=self.set_subdiv_and_iterations
        )

        # Show the window
        cmds.showWindow(self.tool_window)

    def window_cleaner(self):
        """
        Closes and removes preferences for any previous window with this name.
        Prevents multiple instances of the UI.
        """
        # Delete the window if it exists
        if cmds.window(self.tool_window, exists=True):
            cmds.deleteUI(self.tool_window)

        # Safely remove window preferences (ignore errors if none exist)
        try:
            cmds.windowPref(self.tool_window, remove=True)
        except RuntimeError:
            pass  # No preferences to remove

    def set_subdiv_and_iterations(self, *args):
        """
        Applies the selected subdivision type and iteration count to all selected mesh objects.
        Only valid mesh shapes with Arnold attributes are updated.
        """
        # Get current selection
        self.selection = cmds.ls(sl=True, long=True)

        if not self.selection:
            cmds.warning("No objects selected. Please select one or more objects and try again.")
            return

        # Get subdivision type from dropdown (optionMenuGrp is 1-based, Arnold expects 0-based)
        sub_type = cmds.optionMenuGrp(self.subOptionMenu, q=True, sl=True) - 1
        # Get iteration count from intField
        iteration_count = cmds.intField(self.iterationNumb, q=True, v=True)

        updated_objects = 0  # Counter for successful updates

        for obj in self.selection:
            # Get shape node(s) for the transform
            shape = cmds.listRelatives(obj, shapes=True, fullPath=True)

            # Only proceed if shape exists and is a mesh
            if shape and cmds.nodeType(shape[0]) == "mesh":
                try:
                    # Check if Arnold subdivision attributes exist
                    if cmds.attributeQuery("aiSubdivType", node=shape[0], exists=True):
                        cmds.setAttr(shape[0] + ".aiSubdivType", sub_type)
                        cmds.setAttr(shape[0] + ".aiSubdivIterations", iteration_count)
                        updated_objects += 1
                    else:
                        cmds.warning(f"{obj} does not have Arnold attributes. Skipping.")
                except Exception as e:
                    cmds.warning(f"Failed to set attributes for {obj}: {e}")

        # Feedback to user
        if updated_objects > 0:
            cmds.inViewMessage(
                amg=f"<hl>{updated_objects} object(s) updated with new subdivision settings!</hl>",
                pos="topCenter",
                fade=True
            )
        else:
            cmds.warning("No valid mesh objects found in the selection.")

# Instantiate and show the UI
ArnoldSubdUI()
