project('foco-no-trabalho',
  version: '0.1.0',
  meson_version: '>= 0.59.0'
)

python = import('python').find_installation('python3')

pkgdatadir = join_paths(get_option('prefix'), 'share', meson.project_name())
moduledir = join_paths(pkgdatadir, 'src')

install_data(
  'src/app.py',
  'src/main.py',
  'src/sound_manager.py',
  'src/style.css',
  'src/window.py',
  install_dir: moduledir
)

install_subdir('data/sounds', install_dir: pkgdatadir)

install_data(
  'bin/foco-no-trabalho',
  install_dir: get_option('bindir')
)

install_data(
  'data/org.focodotrabalho.App.desktop',
  install_dir: join_paths(get_option('prefix'), 'share', 'applications')
)

install_data(
  'data/org.focodotrabalho.App.metainfo.xml',
  install_dir: join_paths(get_option('prefix'), 'share', 'metainfo')
)

install_data(
  'data/org.focodotrabalho.App.png',
  install_dir: join_paths(get_option('prefix'), 'share', 'icons', 'hicolor', 'scalable', 'apps')
)
