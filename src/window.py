import gi
gi.require_version('Gtk', '4.0')
gi.require_version('Adw', '1')
gi.require_version('Gio', '2.0')

from gi.repository import Gtk, Adw, Gio, Gdk
from sound_manager import SoundManager

SOUND_KEYS = {
    'chuva':     ('chuva-volume',     'chuva-playing'),
    'trovao':    ('trovao-volume',    'trovao-playing'),
    'cafeteria': ('cafeteria-volume', 'cafeteria-playing'),
    'lareira':   ('lareira-volume',   'lareira-playing'),
    'lofi':      ('lofi-volume',      'lofi-playing'),
    'passaros':  ('passaros-volume',  'passaros-playing'),
    'riacho':    ('riacho-volume',    'riacho-playing'),
    'teclado':   ('teclado-volume',   'teclado-playing'),
    'vento':     ('vento-volume',     'vento-playing'),
}

PRESETS_DATA = [
    {
        "id": "chuva_trovao",
        "name": "Chuva & Trovão",
        "icon": "weather-storm-symbolic",
        "sounds": {"chuva": 60, "trovao": 30}
    },
    {
        "id": "cafe",
        "name": "Um_Cafézinho",
        "icon": "system-users-symbolic",
        "sounds": {"cafeteria": 50, "lofi": 40, "teclado": 20}
    },
    {
        "id": "natureza",
        "name": "Natureza",
        "icon": "weather-showers-scattered-symbolic",
        "sounds": {"passaros": 40, "riacho": 50, "vento": 25}
    }
]

class FocoNoTrabalhoWindow(Adw.ApplicationWindow):
    def __init__(self, settings, **kwargs):
        super().__init__(**kwargs)
        self.set_title("Foco no Trabalho")
        self.set_default_size(520, 780)
        self.set_resizable(True)

        self.settings = settings  # Gio.Settings
        self.sound_manager = SoundManager()
        self.globally_paused = True
        self.sound_widgets = {}

        self.active_preset_id = None
        self.preset_buttons = {}

        self._create_ui()
        self._setup_keyboard_shortcuts()
        self._load_persistent_state()

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
        # CONTROLES SUPERIORES
        # =========================================================
        controls_box = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=8)

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
        self.action_stack.set_visible_child(self.resume_button)

        controls_box.append(self.action_stack)

        # Botão "Atalhos"
        self.shortcuts_button = Gtk.Button(label="Atalhos")
        self.shortcuts_button.add_css_class("suggestion-action")
        self.shortcuts_button.add_css_class("compact")
        self.shortcuts_button.connect("clicked", self._on_shortcuts_clicked)
        controls_box.append(self.shortcuts_button)

        controls_box.append(Gtk.Box(hexpand=True))
        main_box.append(controls_box)

        # =========================================================
        # SEÇÃO DE PRESETS (MODOS RÁPIDOS)
        # =========================================================
        preset_group = Adw.PreferencesGroup()
        preset_group.set_title("Modos Rápidos")
        preset_group.set_description("Ative uma combinação pré-definida de sons")

        preset_box = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=8)
        preset_box.set_margin_top(8)
        preset_box.set_margin_bottom(8)
        preset_box.set_margin_start(12)
        preset_box.set_margin_end(12)
        preset_box.set_homogeneous(True)

        for preset in PRESETS_DATA:
            btn = Gtk.Button()
            btn_box = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=6)
            btn_box.set_halign(Gtk.Align.CENTER)

            icon = Gtk.Image.new_from_icon_name(preset["icon"])
            label = Gtk.Label(label=preset["name"])

            btn_box.append(icon)
            btn_box.append(label)
            btn.set_child(btn_box)

            btn.connect("clicked", self._on_preset_clicked, preset["id"])
            preset_box.append(btn)
            self.preset_buttons[preset["id"]] = btn

        preset_group.add(preset_box)
        main_box.append(preset_group)

        # =========================================================
        # CARDS DE SONS INDIVIDUAIS
        # =========================================================
        sounds_data = [
            ("Chuva",     "chuva",     "weather-showers-symbolic"),
            ("Trovão",    "trovao",    "weather-storm-symbolic"),
            ("Cafeteria", "cafeteria", "system-users-symbolic"),
            ("Lareira",   "lareira",   "night-light-symbolic"),
            ("Lofi",      "lofi",      "audio-headphones-symbolic"),
            ("Pássaros",  "passaros",  "audio-speakers-symbolic"),
            ("Riacho",    "riacho",    "weather-showers-scattered-symbolic"),
            ("Teclado",   "teclado",   "input-keyboard-symbolic"),
            ("Vento",     "vento",     "weather-windy-symbolic"),
        ]

        group = Adw.PreferencesGroup()
        group.set_title("Sons ambientais")
        group.set_description("Selecione e ajuste o volume de cada som")

        for name, sound_id, icon_name in sounds_data:
            row = self._create_sound_row(name, sound_id, icon_name)
            group.add(row)

        scrolled_window = Gtk.ScrolledWindow()
        scrolled_window.set_vexpand(True)
        scrolled_window.set_policy(Gtk.PolicyType.NEVER, Gtk.PolicyType.AUTOMATIC)
        scrolled_window.set_kinetic_scrolling(True)
        scrolled_window.set_min_content_height(350)
        scrolled_window.add_css_class("no-scrollbar")
        scrolled_window.set_child(group)

        main_box.append(scrolled_window)
        toolbar_view.set_content(main_box)
        self.set_content(toolbar_view)

    def _create_sound_row(self, name, sound_id, icon_name):
        row = Adw.ActionRow()
        row.set_title(name)

        icon = Gtk.Image.new_from_icon_name(icon_name)
        icon.add_css_class("icon")
        row.add_prefix(icon)

        controls_box = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=8)

        play_button = Gtk.Button()
        play_icon = Gtk.Image.new_from_icon_name("media-playback-start-symbolic")
        play_button.set_child(play_icon)
        play_button.add_css_class("circular")
        play_button.set_tooltip_text(f"Tocar {name}")
        play_button.set_valign(Gtk.Align.CENTER)
        controls_box.append(play_button)

        volume_scale = Gtk.Scale(orientation=Gtk.Orientation.HORIZONTAL)
        volume_scale.set_adjustment(Gtk.Adjustment(lower=0, upper=100, step_increment=1))
        volume_scale.set_value(20)
        volume_scale.set_draw_value(False)
        volume_scale.add_css_class("volume-scale")
        volume_scale.set_size_request(150, -1)
        controls_box.append(volume_scale)

        row.add_suffix(controls_box)

        self.sound_widgets[sound_id] = {
            "name": name,
            "row": row,
            "play_button": play_button,
            "play_icon": play_icon,
            "volume_scale": volume_scale,
            "is_playing": False
        }

        play_button.connect("clicked", self._on_play_pause, sound_id)
        volume_scale.connect("value-changed", self._on_volume_changed, sound_id)

        return row

    def _set_sound_playing_state(self, sound_id, is_playing):
        """Atualiza a interface do card e botão de um som ativo/pausado."""
        widget_data = self.sound_widgets[sound_id]
        widget_data["is_playing"] = is_playing

        if is_playing:
            widget_data["play_icon"].set_from_icon_name("media-playback-pause-symbolic")
            widget_data["row"].add_css_class("active-sound")
        else:
            widget_data["play_icon"].set_from_icon_name("media-playback-start-symbolic")
            widget_data["row"].remove_css_class("active-sound")

    # =========================================================
    # LÓGICA DOS PRESETS
    # =========================================================
    def _on_preset_clicked(self, button, preset_id):
        if self.active_preset_id == preset_id:
            # Se clicou no preset ativo -> Desativa ele
            self._deactivate_preset(preset_id)
        else:
            # Se havia outro preset ativo -> Desativa o antigo primeiro
            if self.active_preset_id:
                self._deactivate_preset(self.active_preset_id)

            self._activate_preset(preset_id)

        self._update_global_state()

    def _activate_preset(self, preset_id):
        preset = next(p for p in PRESETS_DATA if p["id"] == preset_id)
        self.active_preset_id = preset_id

        # Marca o botão do preset com VERDE (success)
        self.preset_buttons[preset_id].add_css_class("success")

        for sound_id, target_vol in preset["sounds"].items():
            widget_data = self.sound_widgets[sound_id]

            widget_data["volume_scale"].set_value(target_vol)
            self.sound_manager.set_volume(sound_id, target_vol / 100.0)

            if not widget_data["is_playing"]:
                if sound_id in self.sound_manager.players:
                    self.sound_manager.resume_sound(sound_id)
                else:
                    self.sound_manager.play_sound(sound_id, target_vol / 100.0)

            self._set_sound_playing_state(sound_id, True)

            # Bloqueia o botão manual do som enquanto o preset estiver ativo
            widget_data["play_button"].set_sensitive(False)
            widget_data["play_button"].set_tooltip_text(f"Gerenciado pelo preset '{preset['name']}'")

    def _deactivate_preset(self, preset_id):
        preset = next(p for p in PRESETS_DATA if p["id"] == preset_id)

        # Remove a marcação verde
        self.preset_buttons[preset_id].remove_css_class("success")

        for sound_id in preset["sounds"]:
            widget_data = self.sound_widgets[sound_id]

            self.sound_manager.pause_sound(sound_id)
            self._set_sound_playing_state(sound_id, False)

            # Desbloqueia o botão manual
            widget_data["play_button"].set_sensitive(True)
            widget_data["play_button"].set_tooltip_text(f"Tocar {widget_data['name']}")

        self.active_preset_id = None

    # =========================================================
    # PERSISTÊNCIA (GSettings)
    # =========================================================
    def _load_persistent_state(self):
        """Carrega os volumes salvos, mas garante que o app inicie totalmente silenciado/pausado."""
        for sound_id, widget_data in self.sound_widgets.items():
            vol_key, _ = SOUND_KEYS[sound_id]
            volume = self.settings.get_int(vol_key)

            widget_data["volume_scale"].set_value(volume)

            self.sound_manager.play_sound(sound_id, volume / 100.0)
            self.sound_manager.pause_sound(sound_id)

            self._set_sound_playing_state(sound_id, False)

        self._update_global_state()

    def _save_state(self, sound_id):
        """Salva o volume e estado de um som específico."""
        vol_key, play_key = SOUND_KEYS[sound_id]
        widget_data = self.sound_widgets[sound_id]
        volume = int(widget_data["volume_scale"].get_value())
        playing = widget_data["is_playing"]
        self.settings.set_int(vol_key, volume)
        self.settings.set_boolean(play_key, playing)

    def _save_all_states(self):
        """Salva todos os sons ao fechar o app."""
        for sound_id in self.sound_widgets:
            self._save_state(sound_id)

    def close_request(self):
        self._save_all_states()
        return super().close_request()

    # =========================================================
    # ESTADO GLOBAL DA INTERFACE
    # =========================================================
    def _update_global_state(self):
        """Atualiza dinamicamente se há áudios tocando e altera o botão do topo."""
        any_playing = any(w["is_playing"] for w in self.sound_widgets.values())
        self.globally_paused = not any_playing
        self._update_buttons_visibility(is_playing=any_playing)

    def _update_buttons_visibility(self, is_playing):
        if is_playing:
            self.action_stack.set_visible_child(self.stop_button)
        else:
            self.action_stack.set_visible_child(self.resume_button)

    # =========================================================
    # ATALHOS DE TECLADO
    # =========================================================
    def _setup_keyboard_shortcuts(self):
        controller = Gtk.EventControllerKey.new()
        controller.connect("key-pressed", self._on_key_pressed)
        self.add_controller(controller)

    def _on_key_pressed(self, controller, keyval, keycode, state):
        return False

    # =========================================================
    # DIÁLOGO DE ATALHOS
    # =========================================================
    def _on_shortcuts_clicked(self, button):
        window = Adw.Window(transient_for=self, modal=True)
        window.set_title("Atalhos de teclado")
        window.set_default_size(320, 100)
        window.set_resizable(False)

        header = Adw.HeaderBar()
        header.set_show_end_title_buttons(True)

        toolbar_view = Adw.ToolbarView()
        toolbar_view.add_top_bar(header)

        box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=12)
        box.set_margin_top(16)
        box.set_margin_bottom(16)
        box.set_margin_start(16)
        box.set_margin_end(16)

        no_shortcuts_label = Gtk.Label(label="Nenhum atalho configurado.")
        no_shortcuts_label.add_css_class("dim-label")
        box.append(no_shortcuts_label)

        toolbar_view.set_content(box)
        window.set_content(toolbar_view)
        window.present()

    # =========================================================
    # LÓGICA DE ÁUDIO INDIVIDUAL
    # =========================================================
    def _on_play_pause(self, button, sound_id):
        widget_data = self.sound_widgets[sound_id]
        if widget_data["is_playing"]:
            self.sound_manager.pause_sound(sound_id)
            self._set_sound_playing_state(sound_id, False)
        else:
            if sound_id in self.sound_manager.players:
                self.sound_manager.resume_sound(sound_id)
            else:
                volume = widget_data["volume_scale"].get_value() / 100.0
                self.sound_manager.play_sound(sound_id, volume)
            self._set_sound_playing_state(sound_id, True)

        self._update_global_state()
        self._save_state(sound_id)

    def _on_volume_changed(self, scale, sound_id):
        volume = scale.get_value() / 100.0
        self.sound_manager.set_volume(sound_id, volume)
        self._save_state(sound_id)

    def _on_stop_all(self, button):
        if self.active_preset_id:
            self._deactivate_preset(self.active_preset_id)

        self.sound_manager.pause_all()
        for sound_id in self.sound_widgets:
            self._set_sound_playing_state(sound_id, False)
        self._update_global_state()
        self._save_all_states()

    def _on_resume_all(self, button):
        self.sound_manager.resume_all()
        for sound_id in self.sound_widgets:
            self._set_sound_playing_state(sound_id, True)
        self._update_global_state()
        self._save_all_states()
