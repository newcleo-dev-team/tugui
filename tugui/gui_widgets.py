import os
import tkinter as tk
from tkinter import ttk
from PIL import Image, ImageTk
from typing import Union


class CustomNotebook(ttk.Notebook):
  """
  Class that provides a customization of the ttk.Notebook class that enables
  to build a notebook with tabs presenting a button for closing each one of
  them.
  """
  __initialized: bool = False

  def __init__(self, *args, **kwargs):
    # Initialize the custom style of the notebook, if not yet done
    if not self.__initialized:
      self.__initialize_custom_style()
      CustomNotebook.__initialized = True

    # Store the 'CustomNotebook' style in the arguments to pass to the superclass
    kwargs["style"] = "CustomNotebook"
    # Call the superclass constructor
    ttk.Notebook.__init__(self, *args, **kwargs)
    self._active: Union[bool, None] = None
    # Bind the mouse events to the execution of corresponding methods
    self.bind("<ButtonPress-1>", self.on_close_press, True)
    self.bind("<ButtonRelease-1>", self.on_close_release)

  def on_close_press(self, event: tk.Event) -> Union[str, None]:
    """
    Method that is called when the mouse button is pressed over
    the close button.
    """
    # Get the name of the tab at the event X-Y position
    element = self.identify(event.x, event.y)
    # Handle the case when the event happens on the close button of a tab
    if "close" in element:
      # Get the index of the tab where the event happened
      index = self.index("@%d,%d" % (event.x, event.y))
      # Set the state of the widget
      self.state(['pressed'])
      # Store the index of the tab where the event happened
      self._active = index
      return "break"

  def on_close_release(self, event: tk.Event) -> None:
    """
    Method that is called when the mouse button is released after having
    pressed over the close button.
    """
    # Return immediately if the state is not 'pressed'
    if not self.instate(['pressed']): return
    # Return immediately if the event is related to the user moving the mouse off
    # of the close button
    element =  self.identify(event.x, event.y)
    if "close" not in element: return

    # Get the index of the tab where the event happened
    index = self.index("@%d,%d" % (event.x, event.y))

    if self._active == index:
      print("DELETING TAB FROM CUSTOMNOTEBOOK...", index)
      # Select the tab to delete, given the specified tab index
      self.select(index)
      # Loop over all the tabs of the notebook
      for item in self.winfo_children():
        # Compare each tab string representation with the name of the tab to close
        if str(item)==self.select():
          # Destroy the tab
          print("Deleting plot tab named: ", str(item))
          item.destroy()
          # Exit the loop
          break

      # Generate a virtual event stating the tab closure
      self.event_generate("<<NotebookTabClosed>>")

    # Change the notebook state
    self.state(["!pressed"])
    self._active = None

  def __initialize_custom_style(self) -> None:
    # Declare a new Style instance
    style = ttk.Style()
    # Store the images representing the different states of the close button
    self.images = (
        tk.PhotoImage("img_close", data='''
            R0lGODlhCAAIAMIBAAAAADs7O4+Pj9nZ2Ts7Ozs7Ozs7Ozs7OyH+EUNyZWF0ZWQg
            d2l0aCBHSU1QACH5BAEKAAQALAAAAAAIAAgAAAMVGDBEA0qNJyGw7AmxmuaZhWEU
            5kEJADs='''),
        tk.PhotoImage("img_closeactive", data='''
            R0lGODlhCAAIAMIEAAAAAP/SAP/bNNnZ2cbGxsbGxsbGxsbGxiH5BAEKAAQALAAA
            AAAIAAgAAAMVGDBEA0qNJyGw7AmxmuaZhWEU5kEJADs='''),
        tk.PhotoImage("img_closepressed", data='''
            R0lGODlhCAAIAMIEAAAAAOUqKv9mZtnZ2Ts7Ozs7Ozs7Ozs7OyH+EUNyZWF0ZWQg
            d2l0aCBHSU1QACH5BAEKAAQALAAAAAAIAAgAAAMVGDBEA0qNJyGw7AmxmuaZhWEU
            5kEJADs=''')
    )
    # Create the close element in the current theme
    style.element_create("close", "image", "img_close",
                         ("active", "pressed", "!disabled", "img_closepressed"),
                         ("active", "!disabled", "img_closeactive"),
                         border=8, sticky='')
    # Define the notebook layout for the given style
    style.layout("CustomNotebook", [("CustomNotebook.client", {"sticky": "nswe"})])
    # Define the layout of each single tab for the given style
    style.layout("CustomNotebook.Tab", [
        ("CustomNotebook.tab", {
            "sticky": "nswe",
            "children": [
                ("CustomNotebook.padding", {
                    "side": "top",
                    "sticky": "nswe",
                    "children": [
                        ("CustomNotebook.focus", {
                            "side": "top",
                            "sticky": "nswe",
                            "children": [
                                ("CustomNotebook.label", {"side": "left", "sticky": ''}),
                                ("CustomNotebook.close", {"side": "left", "sticky": ''}),
                            ]
                        })
                    ]
                })
            ]
        })
    ])


class SquareButton(ttk.Frame):
  """
  Class that provides a square button with fixed size by instantiating a square frame
  and adding a button to it. By specifying the frame height and width, the contained
  button assumes the same size of the frame, thus resulting in a button with the same
  dimensions.
  This class includes the possibility to add an image to the button, whose path is
  passed to the constructor.
  """
  def __init__(self, parent, size=None, text="", command=None, style=None, image=None):
    # Call the frame constructor by specifying its height and width
    ttk.Frame.__init__(self, parent, height=size, width=size, style="SquareButton.TFrame")
    # Indicate that the frame must not adapt to its widgets
    self.pack_propagate(0)
    # Instantiate the button as a private attribute
    self._btn = ttk.Button(self, text=text, command=command, style=style, padding=0)

    if image:
      size = self._btn.winfo_pixels('18p')
      print("Size:", size)
      self.image = Image.open(image)
      # assure a RGBA image as foreground color is RGB
      self.image = self.image.convert("RGBA")
      self.image = ImageTk.PhotoImage(self.image.resize((24, 24)))

      self._btn.configure(image=self.image, text="")

    # Place the button in the frame
    self._btn.pack(fill=tk.BOTH, expand=0, ipady=0, ipadx=0)

  def set_text(self, new_text: str):
    """
    Method for setting the text of the button.
    """
    self._btn.configure(text=new_text)


class LabelImage(ttk.Label):
  """
  Class that provides a label filled with an image.
  """
  def __init__(self, container, img_path: str):
    """
    Construct an instance of the 'LabelImage' class by receiving the
    contaniner to put the label into, as well as the path to the
    image file to load and assign to the label.
    """
    # Call the superclass constructor by passing the container
    super().__init__(container)
    # Load the image
    self.label_image = Image.open(img_path)
    self.label_image = ImageTk.PhotoImage(self.label_image)

    # Configure the label by assigning the image to it
    self.configure(image=self.label_image)


class OnOffClickableLabel(ttk.Frame):
  """
  Class that provides a clickable label inserted within a frame object. This label is characterised
  by two images, provided as an input list, that higlight the On-Off states of the label.
  Images are toggled on successive clicks of the mouse on the label that providing the same effect of
  an On-Off button.
  Images can be rotated as well by receiving an integer value indicating the degree the image should
  be rotated by.
  A function object can be passed to the constructor too; this is called whenever a click event on the
  label happens.
  """
  def __init__(self, parent, size=None, command=None, style=None, image: list=None, rotation: int=0):
    # Call the frame constructor by specifying its height and width
    ttk.Frame.__init__(self, parent, height=size, width=size, style="ClickableLabelWithImage.TFrame")
    # Indicate that the frame must adapt to its widgets
    self.pack_propagate(1)
    # Instantiate the label as a private attribute
    self._lbl = ttk.Label(self, style=style, padding=2, anchor=tk.CENTER)
    # Place the label in the frame
    self._lbl.pack(fill=tk.BOTH, expand=0, ipady=0, ipadx=0)

    # Set label default state
    self.on_state = True
    # Store the command to run when the label is clicked
    self.command = command

    # Store the toggle images if two of them are provided
    if len(image) == 2:
      # Rotate the images, if a rotation value has been provided
      self.on_image = Image.open(image[0]).rotate(rotation)
      self.off_image = Image.open(image[1]).rotate(rotation)
      # Assure a RGBA image as foreground color is RGB
      self.on_image = self.on_image.convert("RGBA")
      self.off_image = self.off_image.convert("RGBA")
      # Resize the images to 24px for assuring they are shown in their entirety
      self.on_image = ImageTk.PhotoImage(self.on_image.resize((size, size)))
      self.off_image = ImageTk.PhotoImage(self.off_image.resize((size, size)))

      # Set the default label image to the one representing the ON state
      self._lbl.configure(image=self.on_image)

    # Bind mouse click event to image toggle and input function object call
    self.click_event = self._lbl.bind('<Button-1>', lambda event: self.on_click(event, command))

  def on_click(self, event=None, command=None):
    """
    Method that is called whenever a mouse click event on the label happens.
    Given the current label 'on_state' attribute value, the method switches
    the state to the opposite value and toggles the image not currently shown.
    At the same time, given the input function object, it calls it, if any is
    provided.
    """
    if self.on_state:
      # Switch the state to OFF
      self.on_state = False
      # Change image to the one for the OFF state
      self._lbl.configure(image=self.off_image)
    else:
      # Switch the state to ON
      self.on_state = True
      # Change image to the one for the ON state
      self._lbl.configure(image=self.on_image)

    # Run the function object, if any has been passed
    if command:
      command()

  def activate_label(self):
    """
    Method that allows to activate the clickable label by binding the
    click event to the associated function and setting the label state
    as enabled.
    """
    # Enable the label visually
    self._lbl.configure(state=tk.NORMAL)
    # Enable the binding to the label click
    self.click_event = self._lbl.bind('<Button-1>', lambda event: self.on_click(event, self.command))

  def deactivate_label(self):
    """
    Method that allows to de-activate the clickable label by unbinding the
    click event to the associated function and setting the label state as
    disabled.
    """
    # Disable the label visually
    self._lbl.configure(state=tk.DISABLED)
    # Disable the binding to the label click
    self._lbl.unbind('<Button-1>', self.click_event)


class WidgetTooltip(object):
  """
  Class that provides a tooltip for a given widget passed as argument to
  this class constructor.
  The tooltip text, provided as an argument, is shown whenever the mouse
  enters the borders of the widget and remains active for a specified time
  interval or when the mouse leave the widget area.
  """
  def __init__(self, widget, text='widget info'):
    # Specify the waiting time (in ms) for the tooltip to show
    self.wait_time = 500
    # Specify the dimension (in px) of the tooltip area
    self.wraplength = 180
    # Store the widget the tooltip has to be shown for
    self.widget = widget
    # Store the tooltip text
    self.text = text
    # Bind the mouse enter event, for the given widget, to the method call showing the tooltip
    self.widget.bind("<Enter>", self.enter)
    # Bind the mouse leave event, for the given widget, to the method call removing the tooltip
    self.widget.bind("<Leave>", self.leave)
    # Bind the mouse click event, for the given widget, to the method call removing the tooltip
    self.widget.bind("<ButtonPress>", self.leave)
    # Initialize the tooltip ID
    self.id = None
    # Initialize the tooltip window
    self.tooltip_window = None

  def enter(self, event=None):
    """
    Method that is run whenever the mouse enters the widget area for
    showing its tooltip.
    """
    self.schedule()

  def leave(self, event=None):
    """
    Method that is run whenever the mouse leaves the widget area for
    hiding its tooltip.
    """
    self.unschedule()
    self.hidetip()

  def schedule(self):
    """
    Method that clears any previous tooltip and shows the one for the
    widget after a specific waiting time, i.e. the corresponding method
    is called after the waiting time.
    """
    self.unschedule()
    # Run the method after a waiting time and store its ID
    self.id = self.widget.after(self.wait_time, self.showtip)

  def unschedule(self):
    """
    Method that stops the job that shows the tooltip. The ID of the job
    to stop is retrieved by the corresponding instance attribute.
    """
    id = self.id
    self.id = None
    if id:
      # Cancel the job, given its ID, that shows the tooltip
      self.widget.after_cancel(id)

  def showtip(self, event=None):
    """
    Method that shows the tooltip as a window with a label object inside.
    """
    # Initialize both X-Y coordinates to '0'
    x = y = 0
    # Get the size of the widget
    x, y, cx, cy = self.widget.bbox("insert")
    # Calculate the X-Y coordinates of the tooltip window, so that it is shown
    # below and to the right of the widget
    x += self.widget.winfo_rootx() + 25
    y += self.widget.winfo_rooty() + 20

    # Create a toplevel window
    self.tooltip_window = tk.Toplevel(self.widget)
    # Remove all the OS Window Manager decorations
    self.tooltip_window.wm_overrideredirect(True)
    # Set the window size
    self.tooltip_window.wm_geometry("+%d+%d" % (x, y))
    # Add a label to the window showing the tooltip text
    label = tk.Label(self.tooltip_window,
                     text=self.text,
                     justify='left',
                     background="#ffffff",
                     relief='solid',
                     borderwidth=1,
                     wraplength = self.wraplength)
    label.pack(ipadx=1)

  def hidetip(self):
    """
    Method that hides the tooltip by destroying the Toplevel window that
    contains it.
    """
    tw = self.tooltip_window
    self.tooltip_window = None
    if tw:
      tw.destroy()

# testing ...
if __name__ == '__main__':
  root = tk.Tk()

  #----------------------------
  # Testing the tooltip feature
  #----------------------------
  btn1 = tk.Button(root, text="button 1")
  btn1.pack(padx=10, pady=5)
  button1_ttp = WidgetTooltip(btn1, \
    'Neque porro quisquam est qui dolorem ipsum quia dolor sit amet, '
    'consectetur, adipisci velit. Neque porro quisquam est qui dolorem ipsum '
    'quia dolor sit amet, consectetur, adipisci velit. Neque porro quisquam '
    'est qui dolorem ipsum quia dolor sit amet, consectetur, adipisci velit.')

  btn2 = tk.Button(root, text="button 2")
  btn2.pack(padx=10, pady=5)
  button2_ttp = WidgetTooltip(btn2, \
    "First thing's first, I'm the realest. Drop this and let the whole world "
    "feel it. And I'm still in the Murda Bizness. I could hold you down, like "
    "I'm givin' lessons in  physics. You should want a bad Vic like this.")

  #------------------------------------
  # Testing the clickable label feature
  #------------------------------------
  clickable_lbl = OnOffClickableLabel(
    parent=root,
    command=lambda: print("Execute"),
    size=30,
    image=[os.path.join(os.path.abspath(os.path.dirname(__file__)), "../resources/icons/showtab.png"),
          os.path.join(os.path.abspath(os.path.dirname(__file__)), "../resources/icons/hidetab.png")])
  clickable_lbl.pack()
  WidgetTooltip(clickable_lbl, "Show/hide something")

  #--------------------------------------------------
  # Testing the notebook with tabs that can be closed
  #--------------------------------------------------
  notebook = CustomNotebook(width=200, height=200)
  notebook.pack(side="top", fill="both", expand=True)

  for color in ("red", "orange", "green", "blue", "violet"):
    frame = tk.Frame(notebook, background=color)
    notebook.add(frame, text=color)

  root.mainloop()