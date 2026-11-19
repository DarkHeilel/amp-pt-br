# AMP — locale PT-BR e guia técnico

Material comunitário em português brasileiro para estudar e localizar partes da interface do AMP da CubeCoders. Não é um produto oficial da CubeCoders.

## Conteúdo

- `locale/pt.json` — locale PT-BR adaptado; cobertura parcial.
- `scripts/install_amp_pt_br.py` — locale e ajustes opcionais específicos para AMP 2.8.0.10, incluindo reaplicação a textos dinâmicos e renovação do cache dos arquivos modificados. Cria backups e interrompe sem alterar arquivos quando os marcadores esperados não correspondem.
- `docs/guia-amp-pt-br.md` — referência técnica com fontes oficiais e relatos do fórum identificados.
- `docs/tutorial-locale-pt-br.md` — instalação, verificação e reversão.

## Segurança e privacidade

Este repositório contém somente os arquivos selecionados para distribuição. Capturas, logs, backups, configurações de host, endereços, usuários e credenciais foram deixados de fora. O locale omite valores coletados em tempo de execução que poderiam identificar o ambiente original, como informações de hardware, versão do sistema, fuso horário, plugins instalados e nomes configurados pela comunidade.

O instalador modifica arquivos da interface AMP e não é um mecanismo oficial de localização. Use somente na versão descrita no tutorial, mantenha os backups e revise-o antes de qualquer atualização. A configuração depende do operador do servidor; não inclua credenciais nos comandos, issues ou commits.

## Fontes

O guia aponta para a documentação e os fóruns da CubeCoders. A estrutura do locale segue o formato descrito no repositório oficial [AMPTranslations](https://github.com/CubeCoders/AMPTranslations); este projeto não é afiliado à CubeCoders.
