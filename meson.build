project('foco-no-trabalho', 'c')

# Instala o arquivo de esquema do GSettings (salvar configurações)
install_data(
    'org.focodotrabalho.App.gschema.xml',
    install_dir: get_option('datadir') / 'glib-2.0' / 'schemas'
)

# Instala a pasta src inteira (onde estão seus códigos Python)
install_subdir('src', install_dir: get_option('bindir') / 'foco-no-trabalho')

# Gera o executável a partir do arquivo .in
configure_file(
    input: 'foco-no-trabalho.in',
    output: 'foco-no-trabalho',
    install_dir: get_option('bindir'),
    configuration: configuration_data()
)
