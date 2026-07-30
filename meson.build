project(
    'foco-no-trabalho',
    'c',
    version: '1.1.0'
)

gnome = import('gnome')

# 1. Instala o atalho no Menu do Linux (.desktop)
install_data(
    'org.focodotrabalho.App.desktop',
    install_dir: get_option('datadir') / 'applications'
)

# 2. Instala o ícone oficial da aplicação (PNG)
install_data(
    'data/org.focodotrabalho.App.png',
    install_dir: get_option('datadir') / 'icons/hicolor/512x512/apps'
)

# 3. Instala o esquema do GSettings
install_data(
    'org.focodotrabalho.App.gschema.xml',
    install_dir: get_option('datadir') / 'glib-2.0' / 'schemas'
)

# 4. Instala as pastas de código e dados em /app/share/foco-no-trabalho
install_subdir('src', install_dir: get_option('datadir') / 'foco-no-trabalho')
install_subdir('data', install_dir: get_option('datadir') / 'foco-no-trabalho')

# Compila os esquemas do GSettings automaticamente
gnome.post_install(glib_compile_schemas: true)

# Gera o executável com permissão de execução
configure_file(
    input: 'foco-no-trabalho.in',
    output: 'foco-no-trabalho',
    install_dir: get_option('bindir'),
    configuration: configuration_data(),
    install_mode: 'rwxr-xr-x'
)
