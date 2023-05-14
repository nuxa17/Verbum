"""Custom Widgets.

Custom Tkinter widgets.
"""
from typing import Any
from tkinter import ttk, BooleanVar, END
from tkinter.font import Font, nametofont


def get_default_font(size=9,**options):
    # type: (int, Any) -> Font
    """
    Get copy of tkinter's default font.

    Args:
        `size` (optional): Size of the font.
        Defaults to 9.

        `options`: font configuration parameters.

    Returns:
        `Font`: Default tkinter's font
    """
    font = nametofont("TkTextFont").copy()
    font.configure(size=size,**options)
    return font

class EntryScrollX(ttk.Entry):
    """
    Entry widget with bottom scrollbar.
    """
    def __init__(self, master, view, row=0, column=0, sticky='ew', padx=0, pady=0, columnspan=2, backtext='', **kw):
        ttk.Entry.__init__(self, master, **kw)

        self.view=view
        self.backtext=backtext

        self.default_fg = self.view.style.lookup("TEntry","foreground")
        self.empty = True

        empty_lbl = ttk.Label(master)
        empty_lbl.grid(row=row+1, column=column, columnspan=columnspan)

        self.scroll = ttk.Scrollbar(master, orient='horizontal',command=self.xview)
        self['xscrollcommand'] = self.scroll.set

        self.bind("<FocusIn>", lambda e: self._del_backtext())
        self.bind("<FocusOut>", lambda e: self._set_backtext())

        padsy = [(pady,0), (0,pady)] if isinstance(pady, int) else [(pady[0],0), (0,pady[1])]
        self.grid(
            row=row, column=column, sticky=sticky,
            padx=padx, pady=padsy[0], columnspan=columnspan
        )
        self.scroll.grid(
            row=row+1, column=column, sticky=sticky,
            padx=padx, pady=padsy[1], columnspan=columnspan
        )

    def _del_backtext(self):
        if self.empty:
            self.configure(foreground=self.default_fg, font=self.view.font)
            self.delete(0,END)
            self.empty = False

    def _set_backtext(self):
        if not ttk.Entry.get(self):
            self.configure(foreground='grey', font=self.view.font_i)
            self.insert(0,self.backtext)
            self.icursor(0)
            self.empty=True

    def get(self):
        if self.empty:
            return ''
        return ttk.Entry.get(self)

    def configure(self, cnf=None, **kw):
        self.update_idletasks()
        a = str(self.cget("state"))
        ttk.Entry.configure(self, cnf, **kw)
        self.update_idletasks()
        b = str(self["state"])
        if 'disabled' in a and 'disabled' not in b:
            self._set_backtext()

class NumericEntry(ttk.Entry):
    """
    Entry widget that only allows numbers.
    """
    def __init__(self, master, char_limit=None, from_=None, to=None, **kwargs):
        vcmd = (master.register(self._validate_num), '%P')
        self.from_ = from_
        self.to = to
        ttk.Entry.__init__(self, master,validate="key", validatecommand=vcmd, **kwargs)
        self.char_limit=char_limit

    def _validate_num(self, num):
        if not num:
            return True

        if self.char_limit and len(num) > self.char_limit:
            return False

        if (num.isdigit()
            and self.from_ and self.to
            and (self.from_ <= int(num) <= self.to)
        ):
            return True

        return False

class EmptyCheckbutton(ttk.Checkbutton):
    """
    Empty Checkbutton by default.
    """
    def __init__(self, master, value=False, **kwargs):
        self.var = BooleanVar(value=value)
        ttk.Checkbutton.__init__(self, master, **kwargs, variable=self.var, onvalue=True, offvalue=False, style="TCheckbutton")

class TreeviewScroll(ttk.Treeview):
    """
    Treeview with scrollbars.
    """
    def __init__(self, master, view, **kw):
        ttk.Treeview.__init__(self, master, **kw)
        self.view=view

        self.scrolly = ttk.Scrollbar(master, orient='vertical',command=self.yview)
        self['yscrollcommand'] = self.scrolly.set
        self.scrollx = ttk.Scrollbar(master, orient='horizontal',command=self.xview)
        self['xscrollcommand'] = self.scrollx.set
        self.minwidth=0
        self.column('#0', width=0)
        self._funcid = self.view.bind("<<TSUpdate>>", lambda e:self.update_width(),True)

    def insert(self,parent, index, iid=None, update_width=True,**kw):
        id_inserted = ttk.Treeview.insert(self,parent, index, iid, **kw)
        if update_width:
            self._update_width_on_add(id_inserted)
        return id_inserted

    def delete(self, *items, update_width=True):
        ttk.Treeview.delete(self,*items)
        if update_width:
            self.update_width()

    def _update_width_on_add(self, id_leaf):
        level=0
        while id_leaf:
            id_leaf = self.parent(id_leaf)
            level +=1

        self.minwidth = max(
            self.view.font.measure(self.item(id_leaf)["text"]) + 20*level + 5,
            self.minwidth
        )
        self.column("#0", minwidth=self.minwidth, width=self.minwidth)

    def update_width(self):
        """
        Manually update width of the Treeview.
        """
        self.minwidth = self.winfo_width() - 5
        for child in self.get_children():
            self.minwidth = self._help_iter(child, self.minwidth, 20)
        self.column("#0", minwidth=self.minwidth, width=self.minwidth)

    def _help_iter(self, iid, length, extra):

        length = max(self.view.font.measure(self.item(iid)["text"])+extra+5, length)
        childs = self.get_children(iid)
        for child in childs:
            length = self._help_iter(child, length, extra+20)
        return length

    def destroy(self):
        self.view.unbind("<<TSUpdate>>", self._funcid)
        ttk.Treeview.destroy(self)

    def grid_configure(self, cnf=None, **kw):
        row = kw.pop('row',0)
        column = kw.pop('column',0)
        sticky = kw.pop('sticky',"")
        padx = kw.pop('padx',0)
        pady = kw.pop('pady',0)
        columnspan = kw.pop('columnspan',1)
        rowspan = kw.pop('columnspan',1)

        padsx = [(padx,0), (0,padx)] if isinstance(padx, int) else [(padx[0],0), (0,padx[1])]
        padsy = [(pady,0), (0,pady)] if isinstance(pady, int) else [(pady[0],0), (0,pady[1])]

        ttk.Treeview.grid(self,
            cnf, row=row, column=column, sticky=sticky,
            padx=padsx[0], pady=padsy[0],
            columnspan=columnspan, rowspan=rowspan, **kw
        )
        self.scrolly.grid(
            row=row, column=column+1, sticky='nes',
            padx=padsx[1], pady=padsy[0], rowspan=rowspan
        )
        self.scrollx.grid(
            row=row+1, column=column, sticky='wes',
            padx=padsx[0], pady=padsy[1], columnspan=columnspan
        )
        self.update_width()
