# Elise Bourgoignie 
# Mats Valgaeren
from maya import cmds

class ArnoldSubdUI:
    """
    Maya tool for batch-editing Arnold Subdivision attributes on multiple mesh objects.
    Provides a simple UI to set subdivision type and iteration count for selected meshes.
    """

    def __init__(self):
        # Set up window title and unique window name for the UI
        self.window_title = "Set Arnold Subdivision"
        self.tool_window = self.window_title.replace(" ", "_").casefold()

        # Ensure any previous UI instance is closed and preferences are reset, then build the UI
        self.window_cleaner()
        self.build_ui()

    def build_ui(self):
        """
        Creates the main UI window and all its controls for the Arnold subdivision tool.
        """
        # Create the main window
        self.tool_window = cmds.window(
            self.tool_window,
            title=self.window_title,
            resizeToFitChildren=True
        )

        # Set up the main vertical layout
        cmds.columnLayout(adjustableColumn=True, rowSpacing=10)

        # Container for all UI elements
        self.mainLayout = cmds.columnLayout(w=300, h=150, adjustableColumn=True)

        # Add the title label at the top of the window
        cmds.text(
            label="Arnold Subdivisions",
            w=250, h=50, fn="boldLabelFont",
            bgc=(0.15, 0.15, 0.15)
        )
        cmds.separator(h=10, style="none")  # Spacer for visual separation

        # Create a row layout for subdivision type and iteration input
        self.rowLayout = cmds.rowColumnLayout(
            nc=3,
            cw=[(1, 150), (2, 60), (3, 50)],
            adjustableColumn=True
        )

        # Dropdown menu for selecting subdivision type
        self.subOptionMenu = cmds.optionMenuGrp(
            "subOptionMenu",
            label="Sub Type",
            cal=[1, "left"],
            cw=(1, 62)
        )
        cmds.menuItem(label="none")
        cmds.menuItem(label="catclark")
        cmds.menuItem(label="linear")
        # Set 'catclark' as the default selection (index 2)
        cmds.optionMenuGrp(self.subOptionMenu, e=1, sl=2)

        # Add a label and input field for the number of subdivision iterations
        self.iterationNumbtext = cmds.text(label="Iterations", fn="plainLabelFont")
        self.iterationNumb = cmds.intField(
            "iterationNumb",
            minValue=0,
            maxValue=100,
            value=2,
            w=1
        )

        cmds.separator(h=10, style="none")  # Spacer for layout

        # Add the main action button to apply the settings to the selection
        self.subBtn = cmds.button(
            label="Set Subdivisions",
            w=250, h=50,
            parent=self.mainLayout,
            command=self.set_subdiv_and_iterations
        )

        # Display the UI window
        cmds.showWindow(self.tool_window)

    def window_cleaner(self):
        """
        Closes any existing window with the same name and removes its preferences.
        This ensures only one instance of the tool can be open at a time and resets window size/position.
        """
        # Delete the window if it already exists
        if cmds.window(self.tool_window, exists=True):
            cmds.deleteUI(self.tool_window)

        # Try to remove window preferences (size, position), ignore error if none exist
        try:
            cmds.windowPref(self.tool_window, remove=True)
        except RuntimeError:
            pass

    def set_subdiv_and_iterations(self, *args):
        """
        Applies the selected subdivision type and iteration count to all selected mesh objects.
        Only mesh shapes with Arnold subdivision attributes are updated.
        """
        # Get the user's current selection in the scene
        self.selection = cmds.ls(sl=True, long=True)

        # Warn the user if nothing is selected
        if not self.selection:
            cmds.warning("No objects selected. Please select one or more objects and try again.")
            return

        # Get the subdivision type from the dropdown (optionMenuGrp is 1-based, Arnold expects 0-based)
        sub_type = cmds.optionMenuGrp(self.subOptionMenu, q=True, sl=True) - 1

        # Get the number of iterations from the input field
        iteration_count = cmds.intField(self.iterationNumb, q=True, v=True)

        updated_objects = 0  # Counter for successfully updated meshes

        for obj in self.selection:
            # Get the shape node(s) of the selected transform
            shape = cmds.listRelatives(obj, shapes=True, fullPath=True)

            # Only proceed if the shape exists and is a mesh
            if shape and cmds.nodeType(shape[0]) == "mesh":
                try:
                    # Only update if Arnold subdivision attributes exist on the mesh
                    if cmds.attributeQuery("aiSubdivType", node=shape[0], exists=True):
                        cmds.setAttr(shape[0] + ".aiSubdivType", sub_type)
                        cmds.setAttr(shape[0] + ".aiSubdivIterations", iteration_count)
                        updated_objects += 1
                    else:
                        cmds.warning(f"{obj} does not have Arnold attributes. Skipping.")
                except Exception as e:
                    cmds.warning(f"Failed to set attributes for {obj}: {e}")

        # Provide feedback to the user about the operation
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
