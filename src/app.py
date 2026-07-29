import gi
import os
import sys

gi.require_version('Gtk', '4.0')
gi.require_version('Adw', '1')

from gi.repository import Gtk, Adw, Gio, Gdk
from window import FocoNoTrabalhoWindow

class FocoNoTrabalhoApp(Adw.Application):
    def __init__(self):
        super().__init__(
            application_id='org.focodotrabalho.App',
            flags=Gio.ApplicationFlags.FLAGS_NONE
        )
        self.window = None

    def do_activate(self):
        if self.window:
            self.window.present()
            return
        self.window = FocoNoTrabalhoWindow(application=self)
        self.window.present()

    def do_startup(self):
        Gtk.Application.do_startup(self)
        Adw.StyleManager.get_default().set_color_scheme(Adw.ColorScheme.PREFER_DARK)

        css_provider = Gtk.CssProvider()
        css_path = os.path.join(os.path.dirname(__file__), 'style.css')

        try:
            css_provider.load_from_path(css_path)
        except Exception as e:
            print(f"Erro ao carregar CSS local: {e}")

        Gtk.StyleContext.add_provider_for_display(
            Gdk.Display.get_default(),
            css_provider,
            Gtk.STYLE_PROVIDER_PRIORITY_APPLICATION
        )
