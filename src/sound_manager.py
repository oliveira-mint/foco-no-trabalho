import gi
gi.require_version('Gst', '1.0')

from gi.repository import Gst, GLib
import os

class SoundManager:
    def __init__(self):
        Gst.init(None)
        self.players = {}

        # Caminho para desenvolvimento local
        local_path = os.path.abspath(
            os.path.join(os.path.dirname(__file__), '..', 'data', 'sounds')
        )

        # Caminho padrão gerado pelo Meson/Flatpak
        system_path = '/app/share/foco-no-trabalho/sounds'

        if os.path.exists(local_path):
            self.base_path = local_path
        elif os.path.exists(system_path):
            self.base_path = system_path
        else:
            self.base_path = local_path

    def _get_file_path(self, sound_id):
        for ext in ['.mp3', '.ogg', '.wav']:
            path = os.path.join(self.base_path, f"{sound_id}{ext}")
            if os.path.exists(path):
                return path
        return None

    def play_sound(self, sound_id, volume):
        if sound_id in self.players:
            return

        file_path = self._get_file_path(sound_id)
        if not file_path:
            print(f"Aviso: Arquivo de som para '{sound_id}' não encontrado.")
            return

        pipeline_str = f'filesrc location="{file_path}" ! decodebin ! audioconvert ! volume name=vol ! autoaudiosink'

        try:
            pipeline = Gst.parse_launch(pipeline_str)
            if pipeline is None:
                print(f"Erro: Não foi possível criar a pipeline para '{sound_id}'")
                return

            volume_element = pipeline.get_by_name('vol')
            if volume_element:
                volume_element.set_property('volume', volume)
            else:
                print(f"Erro: Elemento de volume não encontrado para '{sound_id}'")
                return

            bus = pipeline.get_bus()
            bus.add_signal_watch()
            bus.connect('message::eos', self._on_eos, sound_id)
            bus.connect('message::error', self._on_error, sound_id)
            bus.connect('message::state-changed', self._on_state_changed, sound_id)

            pipeline.set_state(Gst.State.PLAYING)

            self.players[sound_id] = {
                'pipeline': pipeline,
                'volume_element': volume_element,
                'retry_count': 0,
                'current_volume': volume
            }
        except Exception as e:
            print(f"Erro ao iniciar o som '{sound_id}': {e}")

    def _on_state_changed(self, bus, message, sound_id):
        if message.src == self.players.get(sound_id, {}).get('pipeline'):
            old_state, new_state, pending_state = message.parse_state_changed()
            if new_state == Gst.State.NULL and pending_state == Gst.State.VOID_PENDING:
                if sound_id in self.players and self.players[sound_id]['retry_count'] < 3:
                    self.players[sound_id]['retry_count'] += 1
                    print(f"Reiniciando {sound_id} (tentativa {self.players[sound_id]['retry_count']})")
                    GLib.timeout_add(500, self._retry_sound, sound_id)

    def _retry_sound(self, sound_id):
        if sound_id in self.players:
            volume = self.players[sound_id].get('current_volume', 0.2)
            self.stop_sound(sound_id)
            self.play_sound(sound_id, volume)
        return False

    def resume_sound(self, sound_id):
        player_data = self.players.get(sound_id)
        if player_data:
            player_data['pipeline'].set_state(Gst.State.PLAYING)

    def _on_eos(self, bus, message, sound_id):
        player_data = self.players.get(sound_id)
        if player_data:
            player_data['pipeline'].seek_simple(Gst.Format.TIME, Gst.SeekFlags.FLUSH, 0)

    def _on_error(self, bus, message, sound_id):
        err, debug = message.parse_error()
        print(f"Erro GStreamer para '{sound_id}': {err.message}")
        if sound_id in self.players and self.players[sound_id]['retry_count'] < 3:
            self.players[sound_id]['retry_count'] += 1
            GLib.timeout_add(1000, self._retry_sound, sound_id)

    def pause_sound(self, sound_id):
        player_data = self.players.get(sound_id)
        if player_data:
            player_data['pipeline'].set_state(Gst.State.PAUSED)

    def stop_sound(self, sound_id):
        player_data = self.players.pop(sound_id, None)
        if player_data:
            player_data['pipeline'].set_state(Gst.State.NULL)

    def stop_all(self):
        for sound_id in list(self.players.keys()):
            self.stop_sound(sound_id)

    def pause_all(self):
        for player_data in self.players.values():
            player_data['pipeline'].set_state(Gst.State.PAUSED)

    def resume_all(self):
        for player_data in self.players.values():
            player_data['pipeline'].set_state(Gst.State.PLAYING)

    def set_volume(self, sound_id, volume):
        player_data = self.players.get(sound_id)
        if player_data:
            player_data['volume_element'].set_property('volume', volume)
            player_data['current_volume'] = volume
