# Tutorial: locale PT-BR no AMP 2.8.0.10

Este tutorial instala o locale PT-BR e os ajustes de compatibilidade testados para AMP 2.8.0.10. O idioma da página é selecionado com `?lang=pt`; o instalador mantém a versão AMP intacta e renova separadamente o cache de `AMP.js` e `Locale.js`. Não use o instalador em outra versão sem revisar e testar os trechos esperados.

## Abrir o AMP em português

Acrescente `?lang=pt` ao fim do endereço completo da página que você quer abrir. Por exemplo:

- Página inicial: `https://amp.exemplo.org/?lang=pt`
- Tela de implantação: `https://amp.exemplo.org/configuration/instancedeployment?lang=pt`

O parâmetro vem depois do caminho. Não coloque `?lang=pt` entre o domínio e o caminho, como em `https://amp.exemplo.org?lang=pt/configuration/instancedeployment`. Se o endereço já tiver um `?` com outros parâmetros, acrescente `&lang=pt` ao fim. Para voltar ao inglês, use `lang=en` no lugar de `lang=pt`.

`?lang=pt` escolhe o idioma da interface; `ptbr=1` nos endereços dos scripts é apenas um parâmetro de renovação de cache inserido pelo instalador, não substitui o seletor de idioma. O locale é parcial, então chaves sem tradução e alguns textos de módulos/serviços podem continuar em inglês.

## O que será alterado

- `Locale/pt.json` — locale PT-BR do projeto; inclui as seis frases de configuração inicial e preserva chaves extras locais que já existam.
- `Scripts/AMP.js` — localiza o nome da aba “Monitoring and Metrics” e o aviso de incompatibilidade de versão.
- `Scripts/Locale.js` — observa mudanças na página e reaplica traduções; normaliza o contexto recebido para aceitar seletores, objetos jQuery e elementos DOM.
- `AMP.html` — renova o cache dos dois scripts sem mudar o parâmetro `v=2.8.0.10` que o AMP compara com o servidor.

Cada instalação AMP serve seus próprios arquivos. Se houver mais de um host/painel, execute a instalação separadamente para cada `WebRoot` que você quer corrigir. O pareamento Controller/Target não compartilha esses arquivos entre máquinas. O instalador cria backups dos arquivos alterados, valida o JSON e a sintaxe JavaScript e interrompe sem editar se encontrar uma estrutura inesperada.

## Pré-requisitos

- AMP 2.8.0.10 e Linux com `bash`, `curl`, `tar`, Python 3 e `sudo`.
- Acesso administrativo ao host.
- O caminho absoluto do `WebRoot` correto, contendo `AMP.html`, `Scripts/AMP.js`, `Scripts/Locale.js` e `Locale/`.

## Instalar ou atualizar

No terminal do host cujo painel você quer corrigir, substitua `/caminho/absoluto/para/WebRoot` pelo caminho real. O comando usa Bash mesmo quando seu shell interativo é Fish:

```sh
bash -c 'set -e
TMP_DIR="$(mktemp -d)"
cleanup(){ rm -rf "$TMP_DIR"; }
trap cleanup EXIT
curl -fL "https://github.com/DarkHeilel/amp-pt-br/archive/refs/heads/main.tar.gz" -o "$TMP_DIR/repo.tar.gz"
tar -xzf "$TMP_DIR/repo.tar.gz" -C "$TMP_DIR"
sudo env AMP_WEBROOT="/caminho/absoluto/para/WebRoot" python3 "$TMP_DIR/amp-pt-br-main/scripts/install_amp_pt_br.py"'
```

Leia a saída e guarde os caminhos exatos dos backups. Se aparecer “Parado sem alterar nada”, não force a edição: confirme a versão do AMP e revise os arquivos antes de tentar novamente. Depois da instalação, abra a página com `?lang=pt` no fim do endereço e faça uma recarga forçada (`Ctrl+F5`).

## Verificar

Confira que a página abre, que os controles estáticos e os textos inseridos dinamicamente aparecem em português, e que as seis mensagens de configuração inicial estão traduzidas:

- `AMP First Time Setup` → `Configuração inicial do AMP`
- `Welcome to` → `Bem-vindo ao`
- `Please click Next >> to continue setup.` → `Clique em Avançar >> para continuar a configuração.`
- `Next >>` → `Avançar >>`
- `Default Authentication Server` → `Servidor de autenticação padrão`
- `Re-run Setup` → `Executar a configuração novamente`

O locale é parcial. Nomes próprios, conteúdo fornecido por serviços externos, extensões e frases ainda sem chave podem continuar no idioma original; isso não significa necessariamente que `?lang=pt` falhou.

## Reversão

Use somente os backups exatos impressos pelo instalador. Restaure `AMP.html`, `Scripts/AMP.js`, `Scripts/Locale.js` e `Locale/pt.json` a partir dos respectivos backups. Se o locale não existia antes, remova apenas o arquivo que o instalador criou. Não use curingas e mantenha os backups até confirmar que a interface voltou ao estado anterior.

## Atualizações futuras

Uma atualização do AMP pode substituir os arquivos modificados ou mudar os trechos reconhecidos pelo instalador. Confirme a versão, revise os arquivos e faça backup antes de repetir o procedimento. Não remova as verificações do instalador para fazê-lo continuar.
