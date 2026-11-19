# Tutorial: locale PT-BR no AMP 2.8.0.10

Este tutorial instala o locale PT-BR e os ajustes necessários para textos dinâmicos, a aba “Monitoramento e métricas” e o aviso de incompatibilidade no AMP 2.8.0.10. O instalador preserva `v=2.8.0.10` e usa `ptbr=1` em separado para renovar o cache dos dois scripts; aceita o AMP original e o estado já corrigido. Não use em outra versão.

## O que será alterado

- `Locale/pt.json` — tradução PT-BR parcial, incluindo o aviso de incompatibilidade.
- `Scripts/AMP.js` — traduz o nome da aba antes de inserir espaços não separáveis e localiza o aviso de incompatibilidade.
- `Scripts/Locale.js` — observa texto e elementos adicionados ao DOM e reaplica as traduções quando o AMP monta partes dinâmicas da interface.
- `AMP.html` — renova o cache de `AMP.js` e `Locale.js` sem alterar a versão que o AMP compara com o servidor.

Se `Locale/pt.json` já existir, o instalador preserva chaves extras e aplica as traduções do projeto; se não existir, cria o arquivo. Faz backups dos arquivos existentes, valida o JSON e a sintaxe JavaScript e confere os trechos esperados antes e depois da instalação.

## Pré-requisitos

- AMP 2.8.0.10.
- Acesso administrativo ao host.
- O caminho absoluto do `WebRoot` correto, contendo `AMP.html`, `Scripts/AMP.js`, `Scripts/Locale.js` e a pasta `Locale`.

## Instalação

No terminal do host, cole o bloco abaixo. Substitua o caminho de exemplo pelo `WebRoot` correto da sua instalação:

```sh
bash -c 'set -e
TMP_DIR="$(mktemp -d)"
cleanup(){ rm -rf "$TMP_DIR"; }
trap cleanup EXIT
curl -fL "https://github.com/DarkHeilel/amp-pt-br/archive/refs/heads/main.tar.gz" -o "$TMP_DIR/repo.tar.gz"
tar -xzf "$TMP_DIR/repo.tar.gz" -C "$TMP_DIR"
sudo env AMP_WEBROOT="/caminho/absoluto/para/WebRoot" python3 "$TMP_DIR/amp-pt-br-main/scripts/install_amp_pt_br.py"'
```

Leia a saída: ela informa os backups. Se disser “Parado sem alterar nada”, interrompa e não force a edição. Depois, recarregue o painel uma vez com `Ctrl+F5`. Confirme que a aba aparece como **Monitoramento e métricas**, que os textos gerados ao abrir páginas (por exemplo, nomes e descrições de configurações) também ficam em português e que o painel abre sem o aviso de incompatibilidade. O locale é parcial; nomes próprios, conteúdo fornecido por serviços externos e frases que ainda não tenham uma chave continuarão no idioma original.

## Reversão

Use somente os backups exatos impressos na saída da instalação. Restaure `AMP.html`, `Scripts/AMP.js` e `Scripts/Locale.js` a partir dos respectivos backups. Se o instalador criou `Locale/pt.json` porque não existia antes, remova esse arquivo criado; se ele atualizou um `pt.json` existente, restaure o backup correspondente. Não use curingas. Mantenha os backups até confirmar que a versão anterior voltou.

## Atualizações futuras

Uma atualização do AMP pode substituir os arquivos modificados ou alterar os trechos que o instalador reconhece. Antes de repetir, confirme a versão e revise os arquivos; o instalador deve recusar estruturas inesperadas. Não remova essas verificações para fazê-lo continuar.
