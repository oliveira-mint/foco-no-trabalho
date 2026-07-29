import gi
gi.require_version('Gtk', '4.0')
gi.require_version('Adw', '1')

from gi.repository import Gtk, Adw
from sound_manager import SoundManager

class FocoNoTrabalhoWindow(Adw.ApplicationWindow):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.set_title("Foco no Trabalho")
        self.set_default_size(480, 720)
        self.set_resizable(False)

        self.sound_manager = SoundManager()
        self.globally_paused = False
        self.sound_widgets = {}

        self.connect('realize', self._on_realize)
        self._create_ui()

    def _on_realize(self, widget):
        self._start_all_sounds()

    def _create_ui(self):
        toolbar_view = Adw.ToolbarView()

        header_bar = Adw.HeaderBar()
        subtitle = Gtk.Label(label="Ambiente sonoro para concentração")
        subtitle.add_css_class("dim-label")
        header_bar.set_title_widget(subtitle)
        toolbar_view.add_top_bar(header_bar)

        main_box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=12)
        main_box.set_margin_top(12)
        main_box.set_margin_bottom(12)
        main_box.set_margin_start(12)
        main_box.set_margin_end(12)

        # =========================================================
        # LINHA DE CONTROLES (Botões superiores)
        # =========================================================
        controls_box = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=8)

        # Botões dinâmicos dentro de uma Stack (garante que o Sobre nunca saia do lugar)
        self.action_stack = Gtk.Stack()
        self.action_stack.set_transition_type(Gtk.StackTransitionType.NONE)
        self.action_stack.set_halign(Gtk.Align.START)

        self.stop_button = Gtk.Button(label="Parar tudo")
        self.stop_button.add_css_class("destructive-action")
        self.stop_button.add_css_class("compact")
        self.stop_button.connect("clicked", self._on_stop_all)

        self.resume_button = Gtk.Button(label="Continuar tudo")
        self.resume_button.add_css_class("success")
        self.resume_button.add_css_class("compact")
        self.resume_button.connect("clicked", self._on_resume_all)

        self.action_stack.add_child(self.stop_button)
        self.action_stack.add_child(self.resume_button)
        self.action_stack.set_visible_child(self.stop_button)

        controls_box.append(self.action_stack)

        # Botão Sobre (Agora está perfeitamente fixo aqui, ao lado da stack)
        self.about_button = Gtk.Button(label="Sobre")
        self.about_button.add_css_class("suggestion-action")
        self.about_button.add_css_class("compact")
        self.about_button.connect("clicked", self._on_about_clicked)
        controls_box.append(self.about_button)

        controls_box.append(Gtk.Box(hexpand=True))
        main_box.append(controls_box)
        # =========================================================

        sounds_data = [
            ("Chuva", "chuva", "🌧️"),
            ("Trovão", "trovao", "⚡"),
            ("Cafeteria", "cafeteria", "☕"),
            ("Lareira", "lareira", "🔥"),
            ("Lofi", "lofi", "🎧"),
            ("Pássaros", "passaros", "🐦"),
            ("Riacho", "riacho", "💧"),
            ("Teclado", "teclado", "⌨️"),
            ("Vento", "vento", "🌬️"),
        ]

        group = Adw.PreferencesGroup()
        group.set_title("Sons ambientais")
        group.set_description("Selecione e ajuste o volume de cada som")

        for name, sound_id, emoji in sounds_data:
            row = self._create_sound_row(name, sound_id, emoji)
            group.add(row)

        scrolled_window = Gtk.ScrolledWindow()
        scrolled_window.set_vexpand(True)
        scrolled_window.set_policy(Gtk.PolicyType.NEVER, Gtk.PolicyType.AUTOMATIC)
        scrolled_window.set_kinetic_scrolling(True)
        scrolled_window.set_min_content_height(400)
        scrolled_window.add_css_class("no-scrollbar")
        scrolled_window.set_child(group)

        main_box.append(scrolled_window)
        toolbar_view.set_content(main_box)
        self.set_content(toolbar_view)

    def _start_all_sounds(self):
        default_volume = 20
        for sound_id, widget_data in self.sound_widgets.items():
            widget_data["volume_scale"].set_value(default_volume)
            volume = default_volume / 100.0
            self.sound_manager.play_sound(sound_id, volume)
            self.sound_manager.pause_sound(sound_id)
            widget_data["play_icon"].set_from_icon_name("media-playback-start-symbolic")
            widget_data["is_playing"] = False

        self.globally_paused = True
        self._update_buttons_visibility(is_playing=False)

    def _update_buttons_visibility(self, is_playing):
        # Troca os botões na Stack sem alterar o espaço físico do layout
        if is_playing:
            self.action_stack.set_visible_child(self.stop_button)
        else:
            self.action_stack.set_visible_child(self.resume_button)

    def _create_sound_row(self, name, sound_id, emoji):
        play_button = Gtk.Button()
        play_icon = Gtk.Image.new_from_icon_name("media-playback-start-symbolic")
        play_button.set_child(play_icon)
        play_button.add_css_class("circular")
        play_button.set_tooltip_text(f"Tocar {name}")
        play_button.set_valign(Gtk.Align.CENTER)

        volume_scale = Gtk.Scale(orientation=Gtk.Orientation.HORIZONTAL)
        volume_scale.set_adjustment(Gtk.Adjustment(lower=0, upper=100, step_increment=1))
        volume_scale.set_value(20)
        volume_scale.set_draw_value(False)
        volume_scale.add_css_class("volume-scale")
        volume_scale.set_size_request(200, -1)

        row = Gtk.ListBoxRow()
        row_box = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=12)
        row_box.set_margin_top(12)
        row_box.set_margin_bottom(12)
        row_box.set_margin_start(12)
        row_box.set_margin_end(12)

        icon = Gtk.Label(label=emoji)
        icon.add_css_class("title")

        label = Gtk.Label(label=name)
        label.set_xalign(0)
        label.add_css_class("title")

        controls_box = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=8)

        scroll_controller = Gtk.EventControllerScroll.new(Gtk.EventControllerScrollFlags.BOTH_AXES)
        scroll_controller.set_propagation_phase(Gtk.PropagationPhase.CAPTURE)
        scroll_controller.connect('scroll', lambda c, dx, dy: False)
        controls_box.add_controller(scroll_controller)

        controls_box.append(play_button)
        controls_box.append(volume_scale)

        spacer = Gtk.Box(hexpand=True)

        row_box.append(icon)
        row_box.append(label)
        row_box.append(controls_box)
        row_box.append(spacer)
        row.set_child(row_box)

        self.sound_widgets[sound_id] = {
            "name": name,
            "play_button": play_button,
            "play_icon": play_icon,
            "volume_scale": volume_scale,
            "is_playing": False
        }

        play_button.connect("clicked", self._on_play_pause, sound_id)
        volume_scale.connect("value-changed", self._on_volume_changed, sound_id)

        return row

    def _on_play_pause(self, button, sound_id):
        if self.globally_paused:
            self.globally_paused = False
            self._update_buttons_visibility(is_playing=True)

        widget_data = self.sound_widgets[sound_id]
        if widget_data["is_playing"]:
            self.sound_manager.pause_sound(sound_id)
            widget_data["play_icon"].set_from_icon_name("media-playback-start-symbolic")
            widget_data["is_playing"] = False
        else:
            if sound_id in self.sound_manager.players:
                self.sound_manager.resume_sound(sound_id)
            else:
                volume = widget_data["volume_scale"].get_value() / 100.0
                self.sound_manager.play_sound(sound_id, volume)
            widget_data["play_icon"].set_from_icon_name("media-playback-pause-symbolic")
            widget_data["is_playing"] = True

    def _on_volume_changed(self, scale, sound_id):
        volume = scale.get_value() / 100.0
        self.sound_manager.set_volume(sound_id, volume)

    def _on_stop_all(self, button):
        self.sound_manager.pause_all()
        self.globally_paused = True
        for widget_data in self.sound_widgets.values():
            widget_data["play_icon"].set_from_icon_name("media-playback-start-symbolic")
            widget_data["is_playing"] = False
        self._update_buttons_visibility(is_playing=False)

    def _on_resume_all(self, button):
        self.sound_manager.resume_all()
        self.globally_paused = False
        for widget_data in self.sound_widgets.values():
            widget_data["play_icon"].set_from_icon_name("media-playback-pause-symbolic")
            widget_data["is_playing"] = True
        self._update_buttons_visibility(is_playing=True)

    # =========================================================
    # DIÁLOGO DO SOBRE (AGORA APENAS "EM BREVE")
    # =========================================================
    def _on_about_clicked(self, button):
        dialog = Adw.Dialog()
        dialog.set_title("Sobre")

        # Define um tamanho fixo para o diálogo não ficar minúsculo
        dialog.set_default_size(300, 200)

        # Cria uma caixa para centralizar o texto
        box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=10)
        box.set_valign(Gtk.Align.CENTER)
        box.set_halign(Gtk.Align.CENTER)

        label = Gtk.Label(label="EM BREVE")
        label.add_css_class("title-1") # Fonte grande e destacada

        box.append(label)

        # CORREÇÃO DO ERRO ANTERIOR: Adw.Dialog usa .set_child() e não .set_content()
        dialog.set_child(box)

        dialog.present(self)
