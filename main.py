#!/usr/bin/python3
import gi
import subprocess
gi.require_version("Gtk", "3.0")
gi.require_version("AppIndicator3", "0.1")
from gi.repository import Gtk as gtk, AppIndicator3 as appindicator
import gettext

el = gettext.translation('suse-prime', localedir='locales')
el.install()
_ = el.gettext

gpu_mode = ""
exit_mode = ""
gpu_icon = ""
gpu_sure_text = ""

def ChangeGpuDialog():
  dialog = gtk.MessageDialog(
            transient_for=None,
            flags=0,
            message_type=gtk.MessageType.WARNING,
            buttons=gtk.ButtonsType.YES_NO,
            text=_("Are you sure?"),
        )
  dialog.format_secondary_text(
      gpu_sure_text + "\n" +  _("This operation will terminate your session")
  )
  dialog.set_position(gtk.WindowPosition.CENTER_ALWAYS )
  response = dialog.run()
  dialog.destroy()
  return response

def load_gpu_label():
    global gpu_mode, gpu_icon
    output_glxinfo = subprocess.check_output('glxinfo | grep "OpenGL vendor string"', shell=True)
    if output_glxinfo.decode("UTF-8").find("Intel") >= 0:
        gpu_mode = "hybrid"
        gpu_icon = "power-profile-power-saver-symbolic"
    elif output_glxinfo.decode("UTF-8").find("NVIDIA") >= 0:
        gpu_mode = "nvidia"
        gpu_icon = "power-profile-performance-symbolic"

def load_graphical_interface():
  global exit_mode
  output_graphical = subprocess.check_output('echo $XDG_CURRENT_DESKTOP', shell=True)
  if(output_graphical.decode("UTF-8").find("GNOME") >= 0):
    exit_mode = "gnome-session-quit --logout --no-prompt"
  elif(output_graphical.decode("UTF-8").find("XFCE") >= 0):
    exit_mode = "xfce4-session-logout --logout"
  else:
    exit_mode = "loginctl terminate-user $USER"
    

def main():
  load_gpu_label()
  load_graphical_interface()
  indicator = appindicator.Indicator.new("customtray", gpu_icon, appindicator.IndicatorCategory.APPLICATION_STATUS)
  indicator.set_status(appindicator.IndicatorStatus.ACTIVE)
  indicator.set_menu(menu())
  gtk.main()

def menu():
  menu = gtk.Menu()
  
  switch_label = ""

  if(gpu_mode=="hybrid"):
    switch_label = _("NVIDIA Graphics")
  elif(gpu_mode=="nvidia"):
    switch_label = _("Hybrid Graphics")

  command_one = gtk.MenuItem(label=_('Switch to ') + switch_label)
  command_one.connect('activate', switch_gpu)
  menu.append(command_one)

  exittray = gtk.MenuItem(label=_('Quit'))
  exittray.connect('activate', quit)
  menu.append(exittray)
  
  menu.show_all()
  return menu
  
def switch_gpu(z):
  global gpu_sure_text, exit_mode
  
  quit_app = False
  if(gpu_mode == 'hybrid'):
    gpu_sure_text = _('Are you sure you want to change to a ') + _('NVIDIA Graphics') + "?"
    response = ChangeGpuDialog()
    if(response == gtk.ResponseType.YES):
      quit_app = True
      subprocess.call("pkexec /usr/sbin/prime-select nvidia", shell=True)
  elif(gpu_mode == 'nvidia'):
    gpu_sure_text = _('Are you sure you want to change to a ') + _('Hybrid Graphics') + "?"
    response = ChangeGpuDialog()
    if(response == gtk.ResponseType.YES):
      quit_app = True
      subprocess.call("pkexec /usr/sbin/prime-select offload", shell=True)
  if quit_app:
    subprocess.call(exit_mode, shell=True)
    gtk.main_quit()

if __name__ == "__main__":
  main()