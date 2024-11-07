import os
import re
import tkinter as tk
from tkinter import ttk
from tkinter import messagebox
from PIL import Image, ImageTk
from typing import Callable, List, Union


class EntryVariable:
  """
  Class defining a variable having a corresponding Entry object. Its value
  is validated when set.
  """
  def __init__(self, frame: tk.Frame, width: int, col: int, row: int,
               end: str, validation: Callable) -> None:
    """
    Constructor requiring the Frame object onto which putting the Entry.
    The Entry width, as well as the column and row indices are passed to
    configure the Entry object within the frame.
    """
    # Instantiate the string variable
    self.var: tk.StringVar = tk.StringVar()
    # Instantiate the entry field
    self.entry: ttk.Entry = ttk.Entry(frame, width = width, textvariable=self.var)
    # Place the entry in the frame grid
    self.entry.grid(column = col, row = row, sticky = 'ew')

    # Register the validation funtion of the Entry widget
    valid_entry = (self.entry.register(self.validate), '%P')
    self.validation_func: Callable = validation
    # Configure the entry for checking the validity of its content when the
    # widget looses focus
    self.entry.configure(validate='focusout', validatecommand=valid_entry)

    # Entry file extension
    self.entry_extension: str = end

  def validate(self, entry_txt: str = "") -> bool:
    """
    Method that checks if the entry is valid.
    """
    # Return if the entry is empty
    if not entry_txt:
      return True
    # Check the entry value according to the validation function
    try:
      self.validation_func(entry_txt, self.entry_extension)
      # FIXME: to add the following message into the log file
      print("The entry is valid!")
      self.entry.configure(foreground="#343638")
      # Generate a virtual event stating that the entry is valid
      self.entry.event_generate("<<Valid-Entry>>")
      return True
    except Exception as e:
      # Handle the invalid case
      self.on_invalid(str(e))
      return False

  def on_invalid(self, error_message: str) -> None:
    """
    Show the error message if the data is not valid.
    """
    # FIXME: to add the following message to the log file
    print(error_message)
    # Highlight the entry color in red
    self.entry.configure(foreground="red")
    # Show the error message as a pop-up window
    messagebox.showerror("Error", error_message)


class StatusBar(ttk.Frame):
  """
  Class describing a Frame where a label is shown. This represents a status bar
  that provides useful log to the user.
  """
  def __init__(self, container: tk.Misc) -> None:
    # Initialize the Style object
    s: ttk.Style = ttk.Style()
    # Configure the style for the status bar frame
    s.configure('self.TFrame', border=1, borderwidth=1, relief=tk.GROOVE)
    # Configure the style for the status bar label
    s.configure('self.TLabel')

    # Call the superclass initializer passing the built style
    super().__init__(container, style='self.TFrame')

    # Declare an empty label providing the status messages
    self.label: ttk.Label = ttk.Label(self, text="", style='self.TLabel')
    # Align the label on the left
    self.label.pack(side=tk.LEFT, padx=3, pady=3)

    # Configure the status bar in order to fill all the space in the horizontal direction
    self.grid(sticky='ew')

  def set_text(self, new_text: str) -> None:
    """
    Method that allow the modification of the status bar text.
    """
    self.label.configure(text=new_text)

  def clear_label(self) -> None:
    """
    Method that clears any text already present in the label status bar.
    """
    self.set_text("")


class CustomNotebook(ttk.Notebook):
  """
  Class that provides a customization of the ttk.Notebook class that enables
  to build a notebook with tabs presenting a button for closing each one of
  them.
  """
  __initialized: bool = False

  def __init__(self, *args, **kwargs) -> None:
    # Initialize the custom style of the notebook, if not yet done
    if not self.__initialized:
      self.__initialize_custom_style()
      CustomNotebook.__initialized = True

    # Store the 'CustomNotebook' style in the arguments to pass to the superclass
    kwargs["style"] = "CustomNotebook"
    # Call the superclass constructor
    ttk.Notebook.__init__(self, *args, **kwargs)
    self._active: Union[int, None] = None
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
      # Get and store the index of the tab where the event happened
      self._active = self.index("@%d,%d" % (event.x, event.y))
      # Set the state of the widget
      self.state(['pressed'])
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
  def __init__(self, parent: Union[tk.Misc, None],
               size: Union[int, None] = None, text: str = "",
               command: Union[Callable, None] = None,
               style: Union[str, None] = None,
               image: Union[str, None] = None) -> None:
    # Call the frame constructor by specifying its height and width
    ttk.Frame.__init__(self, parent, height=size, width=size, style="SquareButton.TFrame")
    # Indicate that the frame must not adapt to its widgets
    self.pack_propagate(0)
    # Instantiate the button as a private attribute
    self._btn: ttk.Button = ttk.Button(self, text=text, command=command, style=style, padding=0)

    if image:
      size = self._btn.winfo_pixels('18p')
      print("Size:", size)
      self.image: Union[Image.Image, ImageTk.PhotoImage] = Image.open(image)
      # assure a RGBA image as foreground color is RGB
      self.image = self.image.convert("RGBA")
      self.image = ImageTk.PhotoImage(self.image.resize((24, 24)))

      self._btn.configure(image=self.image, text="")

    # Place the button in the frame
    self._btn.pack(fill=tk.BOTH, expand=0, ipady=0, ipadx=0)

  def set_text(self, new_text: str) -> None:
    """
    Method for setting the text of the button.
    """
    self._btn.configure(text=new_text)


def provide_label_image(container: tk.Misc, img_path: str) -> ttk.Label:
  """
  Function that provides a label filled with an image. It builds an instance
  of the 'ttk.Label' class by receiving the contaniner to put the label
  into, as well as the path to the image file to load and assign to the
  label.
  The loaded image is added as an attribute to the 'ttk.Label' instance so
  to keep a reference to it and prevent it to be garbage collected, thus
  allowing to be correctly shown.
  """
  # Instantiate the 'ttk.Label' class
  label = ttk.Label(container)
  # Load the image
  label_image = Image.open(img_path)
  label_image = ImageTk.PhotoImage(label_image)
  # Configure the label by assigning the image to it
  label.configure(image=label_image)
  # Add an attribute to the label to keep a reference to the image and prevent it
  # from being garbage collected
  label.image = label_image

  # Return the label
  return label


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
  def __init__(self, parent: Union[tk.Misc, None],
               size: Union[int, None] = None,
               command: Union[Callable, None] = None,
               style: Union[str, None] = None,
               image: Union[List[str], None] = None,
               rotation: int = 0) -> None:
    # Call the frame constructor by specifying its height and width
    ttk.Frame.__init__(self, parent, height=size, width=size, style="ClickableLabelWithImage.TFrame")
    # Indicate that the frame must adapt to its widgets
    self.pack_propagate(1)
    # Instantiate the label as a private attribute
    self._lbl: ttk.Label = ttk.Label(self, style=style, padding=2, anchor=tk.CENTER)
    # Place the label in the frame
    self._lbl.pack(fill=tk.BOTH, expand=0, ipady=0, ipadx=0)

    # Set label default state
    self.on_state: bool = True
    # Store the command to run when the label is clicked
    self.command: Union[Callable, None] = command

    # Store the toggle images if two of them are provided
    if len(image) == 2:
      # Rotate the images, if a rotation value has been provided
      self.on_image: Union[Image.Image, ImageTk.PhotoImage] = Image.open(image[0]).rotate(rotation)
      self.off_image: Union[Image.Image, ImageTk.PhotoImage] = Image.open(image[1]).rotate(rotation)
      # Assure a RGBA image as foreground color is RGB
      self.on_image = self.on_image.convert("RGBA")
      self.off_image = self.off_image.convert("RGBA")
      # Resize the images to 24px for assuring they are shown in their entirety
      self.on_image = ImageTk.PhotoImage(self.on_image.resize((size, size)))
      self.off_image = ImageTk.PhotoImage(self.off_image.resize((size, size)))

      # Set the default label image to the one representing the ON state
      self._lbl.configure(image=self.on_image)

    # Bind mouse click event to image toggle and input function object call
    self.click_event: str = self._lbl.bind('<Button-1>', lambda event: self.on_click(event, command))

  def on_click(self, event: Union[tk.Event, None] = None,
               command: Union[Callable, None] = None) -> None:
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

  def activate_label(self) -> None:
    """
    Method that allows to activate the clickable label by binding the
    click event to the associated function and setting the label state
    as enabled.
    """
    # Enable the label visually
    self._lbl.configure(state=tk.NORMAL)
    # Enable the binding to the label click
    self.click_event = self._lbl.bind('<Button-1>', lambda event: self.on_click(event, self.command))

  def deactivate_label(self) -> None:
    """
    Method that allows to de-activate the clickable label by unbinding the
    click event to the associated function and setting the label state as
    disabled.
    """
    # Disable the label visually
    self._lbl.configure(state=tk.DISABLED)
    # Disable the binding to the label click
    self._lbl.unbind('<Button-1>', self.click_event)


class WidgetTooltip():
  """
  Class that provides a tooltip for a given widget passed as argument to
  this class constructor.
  The tooltip text, provided as an argument, is shown whenever the mouse
  enters the borders of the widget and remains active for a specified time
  interval or when the mouse leave the widget area.
  """
  def __init__(self, widget: tk.Widget, text: str = 'widget info') -> None:
    # Specify the waiting time (in ms) for the tooltip to show
    self.wait_time: int = 500
    # Specify the dimension (in px) of the tooltip area
    self.wraplength: int = 180
    # Store the widget the tooltip has to be shown for
    self.widget: tk.Widget = widget
    # Store the tooltip text
    self.text: str = text
    # Bind the mouse enter event, for the given widget, to the method call showing the tooltip
    self.widget.bind("<Enter>", self.enter)
    # Bind the mouse leave event, for the given widget, to the method call removing the tooltip
    self.widget.bind("<Leave>", self.leave)
    # Bind the mouse click event, for the given widget, to the method call removing the tooltip
    self.widget.bind("<ButtonPress>", self.leave)
    # Initialize the tooltip ID
    self.id: Union[str, None] = None
    # Initialize the tooltip window
    self.tooltip_window: Union[tk.Toplevel, None] = None

  def enter(self, event: Union[tk.Event, None] = None) -> None:
    """
    Method that is run whenever the mouse enters the widget area for
    showing its tooltip.
    """
    self.schedule()

  def leave(self, event: Union[tk.Event, None] = None) -> None:
    """
    Method that is run whenever the mouse leaves the widget area for
    hiding its tooltip.
    """
    self.unschedule()
    self.hidetip()

  def schedule(self) -> None:
    """
    Method that clears any previous tooltip and shows the one for the
    widget after a specific waiting time, i.e. the corresponding method
    is called after the waiting time.
    """
    self.unschedule()
    # Run the method after a waiting time and store its ID
    self.id = self.widget.after(self.wait_time, self.showtip)

  def unschedule(self) -> None:
    """
    Method that stops the job that shows the tooltip. The ID of the job
    to stop is retrieved by the corresponding instance attribute.
    """
    id = self.id
    self.id = None
    if id:
      # Cancel the job, given its ID, that shows the tooltip
      self.widget.after_cancel(id)

  def showtip(self, event: Union[tk.Event, None] = None) -> None:
    """
    Method that shows the tooltip as a window with a label object inside.
    """
    # Initialize both X-Y coordinates to '0'
    x = y = 0
    # Get the size of the widget
    x, y, _, _ = self.widget.bbox("insert")
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

  def hidetip(self) -> None:
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
  root: tk.Tk = tk.Tk()

  #----------------------------
  # Testing the tooltip feature
  #----------------------------
  btn1: tk.Button = tk.Button(root, text = "button 1")
  btn1.pack(padx=10, pady=5)
  button1_ttp: WidgetTooltip = WidgetTooltip(btn1, \
    'Neque porro quisquam est qui dolorem ipsum quia dolor sit amet, '
    'consectetur, adipisci velit. Neque porro quisquam est qui dolorem ipsum '
    'quia dolor sit amet, consectetur, adipisci velit. Neque porro quisquam '
    'est qui dolorem ipsum quia dolor sit amet, consectetur, adipisci velit.')

  btn2: tk.Button = tk.Button(root, text="button 2")
  btn2.pack(padx=10, pady=5)
  button2_ttp: WidgetTooltip = WidgetTooltip(btn2, \
    "First thing's first, I'm the realest. Drop this and let the whole world "
    "feel it. And I'm still in the Murda Bizness. I could hold you down, like "
    "I'm givin' lessons in  physics. You should want a bad Vic like this.")

  #------------------------------------
  # Testing the clickable label feature
  #------------------------------------
  clickable_lbl: OnOffClickableLabel = OnOffClickableLabel(
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
  notebook: CustomNotebook = CustomNotebook(width=200, height=200)
  notebook.pack(side="top", fill="both", expand=True)

  for color in ("red", "orange", "green", "blue", "violet"):
    frame = tk.Frame(notebook, background=color)
    notebook.add(frame, text=color)

  root.mainloop()