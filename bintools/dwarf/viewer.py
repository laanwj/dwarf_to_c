"""
Copyright (c) 2010, Cambridge Silicon Radio Ltd.
Written by Emilio Monti <emilmont@gmail.com>
"""
from bintools.dwarf import DWARF
from bintools.dwarf.info import CU, DIE
import wx


class Info_Frame(wx.Frame):
    def __init__(self, dwarf):
        wx.Frame.__init__(self, None, title="DWARF Viewer", size=(520,1000))
        self.dwarf = dwarf
        self.node_names = {}
        
        # Search
        self.search_text = wx.TextCtrl(self)
        self.Bind(wx.EVT_TEXT_ENTER, self.notify_search, self.search_text)
        self.search_button = wx.Button(self,wx.ID_ANY,label = 'Search')
        self.Bind(wx.EVT_BUTTON, self.notify_search, self.search_button)
        
        # Tree
        self.tree = wx.TreeCtrl(self, size=(520,200))
        self.root = self.tree.AddRoot(".debug_info")
        for cu in dwarf.info.cus:
            cu_node = self.add_node(self.root, cu.short_description())
            self.tree.SetItemData(cu_node, wx.TreeItemData(cu))
            self.add_die(cu_node, cu.root)
        self.Bind(wx.EVT_TREE_SEL_CHANGED, self.OnSelChanged, self.tree)
        
        # Info Text Box
        self.die_text = wx.TextCtrl(self, size=(520,200), style=wx.TE_MULTILINE)
        
        # Layout
        self.hbox = wx.BoxSizer()
        self.hbox.Add(self.search_text  , proportion=1, border=0)
        self.hbox.Add(self.search_button, proportion=0, border=0)
        
        self.vbox= wx.BoxSizer(wx.VERTICAL)
        self.vbox.Add(self.hbox    , proportion=0, border=1, flag=wx.EXPAND|wx.ALL)
        self.vbox.Add(self.tree    , proportion=1, border=1, flag=wx.EXPAND|wx.ALL)
        self.vbox.Add(self.die_text, proportion=0, border=1, flag=wx.EXPAND|wx.ALL)
        self.SetSizer(self.vbox)
        
        self.tree.EnsureVisible(self.root)
        self.Show()
    
    def add_node(self, parent, description):
        node = self.tree.AppendItem(parent, description)
        self.node_names[description] = node
        return node
    
    def add_die(self, parent, die):
        new_node = self.add_node(parent, die.short_description())
        self.tree.SetItemData(new_node, wx.TreeItemData(die))
        for c in die.children:
            self.add_die(new_node, c)
    
    def OnSelChanged(self, evt):
        item = self.tree.GetItemData(evt.GetItem()).GetData()
        description = ''
        if isinstance(item, CU):
            description = item.short_description()
        elif isinstance(item, DIE):
            description = str(item)
        self.die_text.SetValue(description)
    
    def notify_search(self, evt):
        text = self.search_text.GetValue()
        self.matching_nodes = []
        for name, node in list(self.node_names.items()):
            if text in name:
                self.matching_nodes.append(node)
        
        # For the moment focus on the first one:
        if self.matching_nodes:
            self.tree.SelectItem(self.matching_nodes[0])
            self.tree.EnsureVisible(self.matching_nodes[0])
        else:
            print('Unable to find any match of the string: %s'%(text))


class Viewer:
    def __init__(self, dwarf):
        app = wx.PySimpleApp(None)
        frame = Info_Frame(dwarf)
        frame.Show()
        app.MainLoop()
