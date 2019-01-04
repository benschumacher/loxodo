#
# Loxodo -- Password Safe V3 compatible Password Vault
# Copyright (C) 2008 Christoph Sommer <mail@christoph-sommer.de>
#
# This program is free software; you can redistribute it and/or
# modify it under the terms of the GNU General Public License
# as published by the Free Software Foundation; either version 2
# of the License, or (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program; if not, write to the Free Software
# Foundation, Inc., 51 Franklin Street, Fifth Floor, Boston, MA  02110-1301, USA.
#

import os
import wx

from .wxlocale import _
from .paths import get_resourcedir

class LoxodoFrame(wx.Frame):
    """
    Displays the "welcome" dialog which lets the user open a Vault.
    """
    def __init__(self, *args, **kwds):
        kwds["style"] = wx.DEFAULT_FRAME_STYLE
        wx.Frame.__init__(self, *args, **kwds)

        filemenu = wx.Menu()
        filemenu.Append(wx.ID_ABOUT, _("&About"))
        wx.EVT_MENU(self, wx.ID_ABOUT, self._on_about)
        filemenu.Append(wx.ID_PREFERENCES, _("&Settings\tCtrl+,"))
        wx.EVT_MENU(self, wx.ID_PREFERENCES, self._on_settings)
        filemenu.AppendSeparator()
        filemenu.Append(wx.ID_EXIT, _("E&xit"))
        wx.EVT_MENU(self, wx.ID_EXIT, self._on_exit)

        mb = wx.MenuBar()
        mb.Append(filemenu, _("&Vault"))

        self._menubar = mb
        self._filemenu = filemenu
        self.SetMenuBar(mb)

    def GetFileMenu(self):
        return self._filemenu

    # def SetFileMenu(self, filemenu):
    #     import copy
    #     self._filemenu = copy.copy(filemenu)
    #     pos = self.GetMenuBar().FindMenu(_("&File"))
    #     self.GetMenuBar().Replace(pos, self._filemenu, _("&File"))

    def _on_about(self, dummy):
        """
        Event handler: Fires when user chooses this menu item.
        """
        gpl_v2 = """This program is free software; you can redistribute it and/or modify it under the
terms of the GNU General Public License as published by the Free Software Foundation;
either version 2 of the License, or (at your option) any later version.

This program is distributed in the hope that it will be useful, but WITHOUT ANY WARRANTY;
without even the implied warranty of MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.
See the GNU General Public License for more details.

You should have received a copy of the GNU General Public License along with this program;
if not, write to the Free Software Foundation, Inc.,
51 Franklin Street, Fifth Floor, Boston, MA  02110-1301, USA."""

        developers = (
                      "Christoph Sommer",
                      "Bjorn Edstrom (Python Twofish)",
                      "Brian Gladman (C Twofish)",
                      "Tim Kuhlman",
                      "David Eckhoff",
                      "Nick Verbeck"
                      )

        about = wx.AboutDialogInfo()
        about.SetIcon(wx.Icon(os.path.join(get_resourcedir(), "loxodo-icon.png"), wx.BITMAP_TYPE_PNG, 128, 128))
        about.SetName("Loxodo")
        about.SetVersion("0.0-git")
        about.SetCopyright("Copyright (C) 2008 Christoph Sommer <mail@christoph-sommer.de>")
        about.SetWebSite("http://www.christoph-sommer.de/loxodo")
        about.SetLicense(gpl_v2)
        about.SetDevelopers(developers)
        wx.AboutBox(about)

    def _on_settings(self, dummy):
        """
        Event handler: Fires when user chooses this menu item.
        """
        settings = Settings(self)
        settings.ShowModal()
        settings.Destroy()
        self._on_close_settings()

    def _on_exit(self, dummy):
        """
        Event handler: Fires when user chooses this menu item.
        """
        self.Close(True)  # Close the frame.

    def _on_close_settings(self):
        pass

from .loadframe import LoadFrame
from .vaultframe import VaultFrame
from .settings import Settings
