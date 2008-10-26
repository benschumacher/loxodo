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
import platform
import string
import wx

from wxlocale import _

# RecordFrame is a wx.MiniFrame on platforms where this helps usability
_RecordFrameBase = None
if platform.system() in ("Windows", "Microsoft", "Darwin"):
    class _RecordFrameBase(wx.MiniFrame):
        def __init__(self, parent):
            wx.MiniFrame.__init__(self, parent, -1, style=wx.DEFAULT_FRAME_STYLE | wx.TINY_CAPTION_HORIZ)
else:
    class _RecordFrameBase(wx.Frame):
        def __init__(self, parent):
            wx.Frame.__init__(self, parent, -1, style=wx.DEFAULT_FRAME_STYLE)

class RecordFrame(_RecordFrameBase):

    """
    Displays (and lets the user edit) a single Vault Record.
    """

    def __init__(self, parent):
        _RecordFrameBase.__init__(self, parent)
        wx.EVT_CLOSE(self, self._on_frame_close)
        self.Bind(wx.EVT_CHAR_HOOK, self._on_escape)

        self.panel = wx.Panel(self, -1)

        _sz_main = wx.BoxSizer(wx.VERTICAL)
        _sz_fields = wx.FlexGridSizer(5, 2, 5, 5)
        _sz_fields.AddGrowableCol(1)
        _sz_fields.AddGrowableRow(4)
        self._tc_group = self._add_a_textcontrol(_sz_fields, _("Group") + ":", "")
        self._tc_title = self._add_a_textcontrol(_sz_fields, _("Title") + ":", "")
        self._tc_user = self._add_a_textcontrol(_sz_fields, _("Username") + ":", "")
        (self._tc_passwd, self._tc_passwd_alt, self._bt_showhide) = self._add_a_passwdfield(_sz_fields, _("Password") + ":", "")
        self._tc_notes = self._add_a_textbox(_sz_fields, _("Notes") + ":", "")
        _sz_main.Add(_sz_fields, 1, wx.EXPAND | wx.GROW)

        _ln_line = wx.StaticLine(self.panel, -1, size=(20, -1), style=wx.LI_HORIZONTAL)
        _sz_main.Add(_ln_line, 0, wx.GROW|wx.ALIGN_CENTER_VERTICAL|wx.RIGHT|wx.TOP, 5)

        btnsizer = wx.StdDialogButtonSizer()
        btn = wx.Button(self.panel, wx.ID_APPLY)
        wx.EVT_BUTTON(self, wx.ID_APPLY, self._on_apply)
        btnsizer.AddButton(btn)
        btn = wx.Button(self.panel, wx.ID_CANCEL)
        wx.EVT_BUTTON(self, wx.ID_CANCEL, self._on_cancel)
        btnsizer.AddButton(btn)
        btn = wx.Button(self.panel, wx.ID_OK)
        wx.EVT_BUTTON(self, wx.ID_OK, self._on_ok)
        btn.SetDefault()
        btnsizer.AddButton(btn)
        btnsizer.Realize()
        _sz_main.Add(btnsizer, 0, wx.ALIGN_RIGHT | wx.TOP | wx.BOTTOM, 5)

        self.panel.SetSizer(_sz_main)
        _sz_frame = wx.BoxSizer()
        _sz_frame.Add(self.panel, 1, wx.EXPAND | wx.ALL, 5)
        self.SetSizer(_sz_frame)

        self.SetTitle("Loxodo - " + _("Edit Vault Record"))
        self.Layout()

        self.Fit()
        self.SetMinSize(self.GetSize())

        self._tc_passwd.SetFocus()        

        self._vault_record = None
        self.refresh_subscriber = None


    def _add_a_textcontrol(self, parent_sizer, label, default_value, extrastyle=0):
        _label = wx.StaticText(self.panel, -1, label, style=wx.ALIGN_RIGHT)
        parent_sizer.Add(_label, 0, wx.ALIGN_CENTER_VERTICAL|wx.ALIGN_RIGHT|wx.ALL, 5)
        r = wx.TextCtrl(self.panel, -1, default_value, style=extrastyle, size=(128, -1))
        parent_sizer.Add(r, 1, wx.ALIGN_CENTER_VERTICAL|wx.ALIGN_LEFT|wx.ALL|wx.EXPAND, 5)
        return r

    def _add_a_passwdfield(self, parent_sizer, label, default_value, extrastyle=0):
        _label = wx.StaticText(self.panel, -1, label, style=wx.ALIGN_RIGHT)
        parent_sizer.Add(_label, 0, wx.ALIGN_CENTER_VERTICAL|wx.ALIGN_RIGHT|wx.ALL, 5)
        r_container = wx.BoxSizer()
        parent_sizer.Add(r_container, 1, wx.ALIGN_CENTER_VERTICAL|wx.ALIGN_LEFT|wx.ALL|wx.EXPAND, 5)
        r_masked = wx.TextCtrl(self.panel, -1, default_value, style=wx.PASSWORD, size=(128, -1))
        r_container.Add(r_masked, 1, wx.ALIGN_CENTER_VERTICAL|wx.ALIGN_LEFT|wx.EXPAND, 0)
        r_shown = wx.TextCtrl(self.panel, -1, default_value, size=(128, -1))
        r_shown.Hide()
        r_container.Add(r_shown, 1, wx.ALIGN_CENTER_VERTICAL|wx.ALIGN_LEFT|wx.EXPAND, 0)
        r_toggle = wx.Button(self.panel, wx.ID_MORE, _("(un)mask"))
        wx.EVT_BUTTON(self, wx.ID_MORE, self._on_toggle_passwd_mask)
        r_container.Add(r_toggle, 0, wx.ALIGN_CENTER_VERTICAL|wx.ALIGN_LEFT|wx.SHRINK|wx.LEFT, 10)
        r_generate = wx.Button(self.panel, wx.ID_REPLACE, _("generate"))
        wx.EVT_BUTTON(self, wx.ID_REPLACE, self._on_generate_passwd)
        r_container.Add(r_generate, 0, wx.ALIGN_CENTER_VERTICAL|wx.ALIGN_LEFT|wx.SHRINK|wx.LEFT, 10)

        return (r_masked, r_shown, r_toggle)

    def _add_a_textbox(self, parent_sizer, label, default_value):
        _label = wx.StaticText(self.panel, -1, label, style=wx.ALIGN_RIGHT)
        parent_sizer.Add(_label, 0, wx.ALL|wx.ALIGN_TOP|wx.ALIGN_RIGHT, 5)
        control = wx.TextCtrl(self.panel, -1, default_value, style=wx.TE_MULTILINE, size=(128, -1))
        parent_sizer.Add(control, 1, wx.ALIGN_TOP|wx.ALIGN_LEFT|wx.ALL|wx.EXPAND, 5)
        return control

    def _crlf_to_native(self, text):
        text = text.replace("\r\n", "\n")
        text = text.replace("\r", "\n")
        return text

    def _native_to_crlf(self, text):
        text = text.replace("\r\n", "\n")
        text = text.replace("\r", "\n")
        text = text.replace("\n", "\r\n")
        return text

    def Refresh(self):
        """
        Update fields from source

        Extends the base classes' method.
        """
        if (self._vault_record is not None):
            self._tc_group.SetValue(self._vault_record.group)
            self._tc_title.SetValue(self._vault_record.title)
            self._tc_user.SetValue(self._vault_record.user)
            self._tc_passwd.SetValue(self._vault_record.passwd)
            self._tc_notes.SetValue(self._crlf_to_native(self._vault_record.notes))
        wx.Frame.Refresh(self)

    def _on_apply(self, dummy):
        """
        Event handler: Fires when user chooses this button.
        """
        if (not self._vault_record is None):
            self._vault_record.group = self._tc_group.Value
            self._vault_record.title = self._tc_title.Value
            self._vault_record.user = self._tc_user.Value
            self._vault_record.passwd = self._tc_passwd.Value
            self._vault_record.notes = self._native_to_crlf(self._tc_notes.Value)
        if (not self.refresh_subscriber is None):
            self.refresh_subscriber.on_modified()

    def _on_cancel(self, dummy):
        """
        Event handler: Fires when user chooses this button.
        """
        self.Show(False)

    def _on_ok(self, evt):
        """
        Event handler: Fires when user chooses this button.
        """
        self._on_apply(evt)
        self.Show(False)
        
    def _on_toggle_passwd_mask(self, dummy):
        _tmp = self._tc_passwd
        _passwd = _tmp.GetValue()
        self._tc_passwd = self._tc_passwd_alt
        self._tc_passwd_alt = _tmp
        self._tc_passwd.Show()
        self._tc_passwd_alt.Hide()
        self._tc_passwd.GetParent().Layout()
        self._tc_passwd.SetValue(_passwd)
        if (self._tc_passwd_alt.FindFocus() == self._tc_passwd_alt):
            self._tc_passwd.SetFocus()        
   
    def _on_generate_passwd(self, dummy):
        _pwd = self.generate_password()
        self._tc_passwd.SetValue(_pwd)

    def _urandom(self, count):
        try:
            return os.urandom(count)
        except NotImplementedError:
            retval = ""
            for dummy in range(count):
                retval += struct.pack("<B", random.randint(0, 0xFF))
            return retval

    def generate_password(self, alphabet=None, pwd_length=8, allow_reduction=True):
    
        # default alphabet is all alphanumerics characters
        if alphabet is None:
            alphabet = string.ascii_lowercase + string.digits + string.ascii_uppercase
    
        # remove some easy-to-mistake characters
        if allow_reduction:
            for _chr in "0OjlI1":
                alphabet = alphabet.replace(_chr, "")
    
        # iteratively pick one character from this alphabet to assemble password
        last_chr = "x"
        pwd = ""
        for dummy in range(pwd_length):
    
            # temporarily reduce alphabet to avoid easy-to-mistake character pairs
            alphabet2 = alphabet
            if allow_reduction:
                for _chr in ('cl', 'mn', 'nm', 'nn', 'rn', 'vv', 'VV'):
                    if last_chr == _chr[0]:
                        alphabet2 = alphabet.replace(_chr[1],"")
    
            _chr = alphabet2[int(len(alphabet2) / 256.0 * ord(self._urandom(1)))]
            pwd += _chr
            last_chr = _chr
    
        return pwd

    def _on_frame_close(self, dummy):
        """
        Event handler: Fires when user closes the frame
        """
        self.Hide()

    def _on_escape(self, evt):
        """
        Event handler: Fires when user presses a key
        """

        # If "Escape" was pressed, hide the frame
        if evt.GetKeyCode() == wx.WXK_ESCAPE:
            self.Hide()
            return

        # Ignore all other keys
        evt.Skip()

    def set_initial_focus(self):
        self._tc_title.SetFocus()
        self._tc_title.SelectAll()

    def _set_vault_record(self, vault_record):
        self._vault_record = vault_record
        self.Refresh()

    def _get_vault_record(self):
        return self._vault_record

    vault_record = property(_get_vault_record, _set_vault_record)
