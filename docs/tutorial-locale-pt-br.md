# Tutorial: locale PT-BR no AMP 2.8.0.10

Este tutorial instala uma tradução parcial e uma correção de compatibilidade da interface, preparada e verificada para AMP 2.8.0.10. O AMP compara a versão da interface com a do backend; por isso o instalador mantém `v=2.8.0.10` intacto e usa `ptbr=1` como parâmetro separado de cache. Não use este instalador em outra versão.

## O que será alterado

O instalador atualiza somente estes três arquivos no `WebRoot` escolhido:

- `Locale/pt.json` — locale PT-BR, incluindo o aviso de incompatibilidade.
- `Scripts/AMP.js` — traduz o nome da aba antes de inserir espaços não separáveis e localiza o aviso de incompatibilidade.
- `AMP.html` — referências ao script com parâmetro de versão compatível e um parâmetro separado para renovar o cache.

Antes da gravação, ele cria cópias com sufixo `.bak.DATA-HORA`, valida o JSON e a sintaxe JavaScript, e confere os marcadores esperados. Se a versão/estrutura não corresponder, ele deve parar sem alterar os arquivos.

## Pré-requisitos

- AMP 2.8.0.10.
- Acesso administrativo ao host da instância.
- O caminho absoluto do `WebRoot` correto. Ele deve conter `AMP.html`, `Scripts/AMP.js` e `Locale/pt.json`.
- Uma cópia segura dos arquivos atuais, além dos backups que o instalador cria.

Não cole senhas, tokens, endereços privados ou saída de configuração em issues ou no repositório. Não publique capturas ou logs do host.

## Instalação

1. Baixe/clône este repositório no host ou transfira os dois arquivos necessários por um canal seguro. Não altere o caminho do AMP até confirmar que corresponde à instância pretendida.
2. Defina `AMP_WEBROOT` como o caminho absoluto do diretório `WebRoot`, sem substituir os sinais de `<` e `>` por texto literal:

   ```sh
   AMP_WEBROOT="/caminho/absoluto/para/WebRoot"
   ```

3. Execute o instalador como administrador, passando a variável explicitamente:

   ```sh
   sudo env AMP_WEBROOT="/caminho/absoluto/para/WebRoot" python3 scripts/install_amp_pt_br.py
   ```

4. Leia a saída. Ela deve confirmar o parâmetro de versão intacto e informar os caminhos dos backups. Se aparecer “Parado sem alterar nada”, interrompa: não force a edição nem repita em outra versão.
5. Recarregue a interface com `Ctrl+F5`. Se houver proxy reverso ou cache intermediário, limpe também esse cache. O aviso de incompatibilidade continua em inglês até o locale PT-BR carregar.
6. Confirme que a aba aparece como **Monitoramento e métricas** e que o painel abre sem o aviso “AMP Version Mismatch”.

## Reversão

Use os caminhos de backup impressos pelo instalador; escolha o conjunto da execução que deseja desfazer. Substitua cada marcador pelo caminho exato, sem usar curingas:

```sh
WEBROOT="/caminho/absoluto/para/WebRoot"
sudo cp -a "$WEBROOT/AMP.html.bak.DATA-HORA" "$WEBROOT/AMP.html"
sudo cp -a "$WEBROOT/Scripts/AMP.js.bak.DATA-HORA" "$WEBROOT/Scripts/AMP.js"
sudo cp -a "$WEBROOT/Locale/pt.json.bak.DATA-HORA" "$WEBROOT/Locale/pt.json"
```

Depois, recarregue a interface e limpe caches intermediários. Não remova os backups até confirmar que a versão anterior voltou.

## Atualizações futuras

Uma atualização do AMP pode substituir os arquivos modificados ou alterar os trechos que o instalador reconhece. Não execute o instalador novamente só porque uma tela mudou: primeiro confirme a versão instalada e revise as notas da release e os arquivos atuais. O instalador foi preparado para recusar estruturas inesperadas; não remova essas verificações para fazê-lo continuar.
