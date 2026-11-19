# AMP da CubeCoders — guia técnico de estudo (PT-BR)

## Escopo e revisão

**Revisado em 19 de novembro de 2026** · foco em conceitos e leitura do painel, não em intervenção no servidor.

> **Escopo:** esta referência cobre AMP 2.2.1 ou posterior, com atenção à linha 2.8.0.10. É um guia técnico baseado nas fontes citadas, não uma inspeção ao vivo de qualquer instalação; confirme versão, caminho e estado antes de aplicar procedimentos.

### Como ler as evidências

- **Documentação/publicação CubeCoders:** página do produto ou notas oficiais de versão.
- **Base de conhecimento do fórum CubeCoders:** guias “How To” e respostas de suporte publicados no fórum. São úteis e frequentemente mantidos por desenvolvedores/moderadores, mas nem todo artigo é uma especificação formal; a autoria e a data importam.
- **Relato comunitário:** experiência de um usuário em uma situação particular; serve como pista, não como prova de comportamento geral.
- **Dependente de versão / incerto:** verificar na versão exata antes de aplicar.

## 1. O que é AMP — escopo AMP 2

AMP significa **Application Management Panel**. É um painel web auto-hospedado que administra instâncias de aplicações, sobretudo servidores de jogos. O fabricante descreve uma estrutura modular: módulos e extensões implementam funções e, para jogos compatíveis, automatizam configurações e argumentos de inicialização. O AMP não é o jogo nem o serviço de distribuição do jogo; cada servidor de jogo/aplicação atualiza-se por seu próprio mecanismo. [1][2]

Este material cobre **AMP 2.2.1+**. A documentação consultada confirma a localização por arquivos JSON a partir de 2.2.1.0; os guias operacionais citados aplicam-se à linha AMP 2 e precisam ser cotejados com a versão concreta. [29]



A linha AMP 2 usa **ADS** (Application Deployment Service) como painel de gestão e **`ampinstmgr`** como gerenciador de instâncias. Os componentes e as aplicações têm ciclos de atualização distintos; veja a seção 4. [2][3]

**Regra prática para estudar:** manter os nomes originais de controles ao lado das traduções, distinguir configurações do ADS das configurações de cada instância e conferir notas da versão antes de aplicar qualquer procedimento.

## 2. Arquitetura e conceitos centrais (AMP 2)

### Vocabulário

- **AMP instance / instance (instância AMP):** processo/painel AMP com uma função e configuração próprias. Uma instância pode ser o painel de administração ou um servidor de jogo.
- **ADS — Application Deployment Service:** módulo/painel central que lista, cria e administra instâncias e controla autenticação e implantação.
- **`ampinstmgr` (AMP Instance Manager):** ferramenta de gestão do sistema usada para instalar/configurar/atualizar instâncias. Não é a interface web.
- **Generic Module (Módulo Genérico):** módulo usado pela maioria dos templates de jogos; o template diz ao AMP como obter, configurar e iniciar aquela aplicação. O jogo/aplicação tem seu próprio ciclo de atualização. [2]
- **Template (modelo):** definição de uma aplicação/servidor e seus parâmetros. Templates oficiais ficam no repositório CubeCoders/AMPTemplates; repositórios externos podem adicionar outros modelos. Um template pode ter requisitos de versão mínima do AMP, dependências e configurações diferentes.
- **Controller / Target (controlador / alvo):** papéis de ADS para gerenciar vários computadores.

### Modos ADS

O guia do fórum lista quatro modos: [6]

| Nome original | Tradução / ideia | O que significa no AMP 2 |
|---|---|---|
| **Standalone** | Independente | Um único computador/VPS; o ADS administra instâncias locais. É o modo inicial indicado para uma máquina só. |
| **Controller** | Controlador | Centraliza autenticação e gestão de máquinas **Target**; delega criação de instâncias remotas. O guia diz que não cria instâncias locais comuns, salvo instâncias de template. |
| **Target** | Alvo | Máquina que hospeda instâncias locais sob orientação de um Controller; depende dele para autenticação e gestão. |
| **Hybrid** | Híbrido | Combina funções de Controller e Target; o próprio guia geralmente desaconselha esse modo. |

Em Controller/Target, a comunicação é **bidirecional**: não basta o controlador alcançar o alvo; cada lado precisa conseguir estabelecer a conexão necessária. Se o controlador fica indisponível, uma instância dependente pode continuar rodando e executar agendamentos, mas o usuário pode perder o acesso ao painel/API para administrá-la até o controlador voltar. [6]

### Um painel global não é a mesma coisa que configuração global

No ADS existem controles de implantação/defaults; dentro de cada instância existem configurações do jogo, tarefas, backups e permissões locais. Um default de implantação serve para orientar **novas** instâncias; não conclua que editar um default altera as que já existem. Essa diferença entre ADS e “Manage” da instância é uma fonte recorrente de confusão relatada por usuários. [7][8]

## 3. Instalação: o que o instalador faz e o que precisa ser decidido

A página de instalação oficial oferece rotas para Linux e Windows; para Linux descreve o instalador GetAMP como responsável por dependências, usuário de sistema e instância inicial do painel. As escolhas podem incluir Java para Minecraft, dependências de 32 bits para jogos/SteamCMD, contêineres e HTTPS. Consulte a página no dia da instalação, pois sistemas suportados e opções evoluem. [9][10]

**Conceitos de escolha, sem prescrever alteração agora:**

- **Nativo vs. contêiner:** o contêiner pode isolar a instância do host e reduzir o alcance de uma falha, especialmente quando usuários não confiáveis terão acesso; tem requisitos próprios de armazenamento e rede. O guia oficial de contêineres AMP 2 afirma que o ADS/gerenciador não roda dentro do mesmo tipo de contêiner que ele precisa criar. Linux pode usar Docker ou Podman conforme suporte; o modo de rede altera quais portas ficam acessíveis. [11]
- **HTTPS:** configure no desenho da instalação (ou com uma rota documentada posteriormente), não suponha que o painel esteja protegido só por usar uma senha. Para Enterprise, HTTPS é requisito. O guia recomenda reverse proxy Nginx em Linux em cenários apropriados; exige domínio/subdomínio com DNS e acessibilidade de portas 80/443 para emissão/renovação conforme o método. [12]
- **Ambiente e domínio:** o assistente pode abrir portas ou integrar regras de firewall. Isso não prova que o roteador, NAT/CGNAT, DNS ou firewall externo esteja correto. [9][12]
- **Múltiplos nós:** Controller/Target é uma arquitetura AMP 2; adiciona dependências de rede e autenticação. Não a escolha apenas porque há mais de um computador: entenda antes quem precisa iniciar conexões para quem. [6]

A documentação de GetAMP também descreve instalações automatizadas via variáveis e comandos do instalador. Esse material é para automação planejada, não deve ser copiado para um host desconhecido sem identificar sistema, versão e estado. [10]

## 4. Instâncias, templates e atualizações: quatro camadas distintas

O material oficial separa explicitamente componentes que podem ser confundidos: [2]

1. **Gerenciador AMP (`ampinstmgr`)** — ferramentas do host.
2. **Instâncias AMP** — ADS e painéis de cada aplicação.
3. **Configuração do Generic Module/template** — definição do comportamento do servidor; pode atualizar independentemente do AMP.
4. **Aplicação gerenciada** — o servidor de jogo/software, com seu próprio botão/ciclo de atualização.

Atualizar uma dessas camadas **não implica** automaticamente atualizar as outras. O guia oficial alerta que atualizar AMP pela aba “Support and Updates” da instância não atualiza a configuração do template Generic Module; em alguns jogos, depois de atualizar o template/configuração, ainda é necessário atualizar separadamente a aplicação. [2]

A documentação de atualização traz compatibilidade específica por linha de versões (por exemplo, certos patches 2.6.x podiam interoperar enquanto 2.6.3.0 não; não extrapole essa regra para saltos maiores). O lançamento 2.8.0.6 exigiu que as ferramentas de sistema fossem atualizadas antes de o novo botão da interface funcionar; 2.8.0.8 corrigiu um problema de inicialização após reinício em Linux. A 2.8.0.10 pediu seguir o guia de atualização e informou correções de vulnerabilidades relacionadas ao .NET e imagens de contêiner. Portanto, leia as notas da versão de origem e destino, não apenas o botão disponível. [2][3]

### Templates e versões

- A lista de jogos depende dos repositórios de configuração carregados; o repositório oficial é **CubeCoders/AMPTemplates**. Guias antigos descrevem buscar/sincronizar esses templates no ADS. [13]
- Um template pode exigir versão mínima do AMP. Um relato de suporte documentou erro de criação porque o ADS era mais antigo que o mínimo requerido pelo template; isso é um caso particular, mas ilustra por que verificar compatibilidade importa. [14]
- Templates de terceiros podem funcionar, mas passam a ter seu próprio mantenedor e ciclo de atualização. O fato de aparecer no catálogo não garante suporte oficial da CubeCoders.
- Não trate “clonar/duplicar instância” como cópia completa de tudo: verifique dados, configuração, portas, credenciais e arquivos próprios do jogo separadamente.

## 5. Usuários e permissões (AMP 2)

O guia de permissões descreve controle por **roles (papéis)**, com usuários e papéis configurados em dois escopos: **ADS** e **instância individual**. O ADS controla ações de gestão (por exemplo, criar ou administrar instâncias); o painel de cada aplicação controla ações daquele servidor (por exemplo, iniciar/parar, agendar e fazer backup). Em alguns cenários é necessário conceder permissões nos dois níveis, mas “ver o painel” não deveria significar “administrar todo o ADS”. [15]

No controle deslizante descrito pelo guia: **vermelho** = negar expressamente; **cinza** = não conceder nem negar naquele nível; **verde** = permitir expressamente, mas uma negação em outro nível ainda pode prevalecer. Usuários/papéis criados no ADS podem ser aplicados também a outras instâncias; os criados apenas numa instância ficam restritos a ela. O usuário inicial de superadmin é necessário ao gerenciador e o guia diz para não modificar nem apagar o papel **Super Admins**. [15]

**Princípio seguro de estudo:** comece pelo menor conjunto de permissões e teste com usuário de teste; observe cada escopo. A configuração de acesso ao ADS e a configuração dentro da instância são controles diferentes. Não conceda acesso a arquivos, configurações de rede, console administrativo ou gestão de usuários se a pessoa precisa só administrar jogadores/servidor. A advertência é especialmente importante para hospedagem de terceiros. [15][16]

## 6. Agendamentos e automação

No AMP 2, **Schedule (Agendamento)** organiza **triggers (gatilhos)** e tarefas associadas. Um gatilho pode ser temporal ou ligado a eventos/estado, conforme o módulo e a versão; a tarefa define a ação. A base de conhecimento documenta variáveis globais de agendamento desde AMP 2.5 com a sintaxe original `{@Key}`, incluindo `InstanceName`, `InstanceId`, `Uptime`, `State`, `StartTime`, `ApplicationName`, `RAMUsage`, `CPUUsage`, `MaxUsers`, `UserCount`, `TriggerId` e `TriggerName`. [17]

**Limitações que não se deve adivinhar:** o próprio tópico de suporte mostra usuários perguntando unidade/semântica de valores como `Uptime` e `State`; o artigo lista nomes, mas não detalha todos os tipos/valores. Não dependa de cálculo ou interpretação de variável que não esteja documentada para a versão em uso. [17]

AMP 2.5.1 permitiu escolher fuso horário do Scheduler; a nota afirma que os gatilhos já existentes não são reescritos quando essa configuração muda. Isso torna importante comparar horário exibido, timezone do painel/host e gatilhos existentes. [18]

Relatos comunitários sobre “schedule” e auto-updates variam por jogo, template e versão. Um tópico de usuários iniciantes (junho de 2024) descreve confusão entre ADS e configuração local, além de casos em que tarefas/atualizações pareciam inconsistentes. É uma experiência localizada, não prova de defeito geral. Faça um teste controlado e confira histórico/log do gatilho e ação antes de depender de automação crítica. [8]

## 7. Backups e restauração

### O que o AMP 2.8 mudou

As notas do **2.8 Proteus** reformularam o processo para reduzir risco de copiar arquivos enquanto o jogo ainda os altera. **Quiesce** (pausa lógica das gravações em disco enquanto o jogo continua) é suportado pelo material consultado para Minecraft Java e Bedrock; outras aplicações podem precisar ser paradas para gerar cópia consistente. O novo controle é **Backup While Running** (“Fazer backup enquanto está em execução”), substituindo **Shutdown for Backups**. As notas alertam que fora dos jogos com suporte a quiesce há risco de arquivos mudarem simultaneamente e de backup ficar inconsistente. [3]

O AMP prepara/stageia arquivos e depois comprime a cópia; a implementação de staging mudou (incluindo a remoção de uma abordagem de hardlinks no Linux). O lançamento 2.8.0.8 também corrigiu checagem de espaço em disco em alguns caminhos e passou a falhar explicitamente se faltar espaço durante staging, em vez de concluir com arquivos ausentes. Em 2.8.0.10, novos servidores Minecraft passaram a ter `Backup While Running` ligado por padrão por suportarem quiesce; não generalize esse padrão para outros jogos/versões. [3]

### Local, S3 e caminhos de armazenamento

O guia de caminhos de backup exige que o usuário que executa a instância tenha acesso ao destino, recomenda diretório separado por instância e documenta o rótulo `Storage.StorePath`. Para instâncias em Docker/Podman, um caminho interno ao contêiner não é automaticamente uma pasta no host: precisa de um volume/mount correspondente. Compartilhar um diretório amplo pode expor backups de outras instâncias também. [19]

O painel também oferece armazenamento compatível com S3 em versões/documentações consultadas. O artigo de 2023 é um ponto de partida comunitário, não uma receita universal para todo provedor; endpoint, região, política IAM, limites, retenção e custos variam. Em 2.8.0.8 houve correções explícitas para serviços anônimos S3 compatíveis e erros de espaço. Confirme suporte e configuração na release atual e no provedor de storage. [20][3]

### Restore não é sinônimo de migração integral

Um backup de arquivos do jogo não deve ser tratado como cópia completa do ADS, de todas as instâncias e de toda a configuração do host. Relatos de migração no fórum descrevem dificuldades em fazer arquivos copiados aparecerem no seletor de restore e em preservar permissões/configurações; um usuário conseguiu restaurar ao mover também metadados locais, mas precisou recuperar configurações do servidor separadamente. São relatos individuais e versões específicas, não uma instrução oficial geral. [21][22]

**Conclusão prática:** um arquivo de backup só é confiável depois de confirmar que terminou, que está no destino esperado e que um restore de teste funciona. Para recuperação total, planeje separadamente dados do jogo, cadastro/configuração de AMP, permissões, versões/template, dependências, portas e chaves/segredos. Não presuma que cópia “offsite” ou manifesto isolado prove que o conteúdo do mundo está preservado. [3][21]

## 8. Rede e segurança

### Separar painel, servidor do jogo e arquivos

Há pelo menos três fluxos diferentes: navegador ↔ painel AMP; jogador ↔ porta(s) do jogo; e, quando usados, transferência/gestão de arquivos e comunicação Controller↔Target. O endereço e a porta exibidos para o painel não identificam automaticamente as portas do jogo. A documentação de suporte cita **8080 como porta padrão do ADS** em exemplos, mas a porta real precisa ser lida do painel/diagnóstico instalado. [23]

Cada template informa portas e protocolo (TCP/UDP); o roteador e o firewall precisam encaminhar exatamente o que o jogo pede. AMP pode administrar regras locais, mas não configura magicamente roteador, NAT ou CGNAT. A página de diagnóstico oficial recomenda confirmar se o processo escuta nas portas e comparar as regras locais; para hospedagem residencial, testar na LAN ajuda a separar um problema do servidor/firewall de um problema de encaminhamento externo. Essa é orientação diagnóstica, não evidência de que qualquer porta específica esteja aberta aqui. [24]

### HTTPS, contêineres e exposição

O guia oficial recomenda HTTPS e indica Nginx reverse proxy no Linux como rota comum; Enterprise exige HTTPS. Um certificado/TLS protege a conexão web, mas não substitui senha forte, atualização, controle de acesso, regras de firewall nem proteção das portas do jogo. [12]

O guia AMP 2 de Docker/Podman recomenda evitar **Use Host Networking for new Containers** em contextos em que usuários podem não ser confiáveis, porque o modo padrão pode restringir a publicação às portas atribuídas à instância. Há trade-off: isolamento e controles de portas versus requisitos de conectividade e configuração. A versão do runtime, host e instâncias precisam ser avaliados juntos. [11]

Não exponha console administrativo, SFTP ou portas de gestão “por garantia”. Abra apenas o necessário ao serviço identificado e confira cada protocolo. Este guia não fornece inventário de portas de uma instalação específica.

## 9. Licenças e edições

A página de produto apresenta **Standard**, **Professional**, **Advanced** e **Enterprise**. Ela lista Professional com até 15 App Instances e usuários de painel ilimitados; Advanced com até 50 App Instances, suporte prioritário e recursos como analytics/geofiltering, branding/SSO e deployment templates conforme a geração; Enterprise é para revenda/uso comercial com limites flexíveis e recursos de implantação/integração. A página afirma que licenças AMP de consumo não são travadas a hardware/IP e podem ser movidas dentro do limite de instâncias; licenças do mesmo tipo podem empilhar limites. [1]

A FAQ de licenças (24 fev. 2026) descreve contagem de ativações como limite “soft”, que ativações antigas caem ao longo do tempo e que não é necessário esperar a contagem cair para mover a licença. Isso não elimina o limite de instâncias nem autoriza revenda comercial. [25]

**Preço exige confirmação na página de compra:** a tabela comparativa do fórum contém valores mais antigos e conflita com trechos atuais da página de produto. Por isso não reproduzo aqui um preço como vigente. Enterprise é uma assinatura e a página atual anuncia preço inicial, sujeito a região/condições. Confira o preço e a licença exatos antes de comprar. [1][26]

## 10. Diagnóstico sem “chutar” configuração

Uma sequência de leitura segura, baseada nas telas/guias consultados:

1. **Identificar versão e canal** de cada peça relevante; diferenciar `ampinstmgr`, ADS, a instância da aplicação e o template.
2. **No ADS:** conferir se a instância aparece e seu estado. Não inferir que “não aparece” significa que os dados desapareceram; há relatos de índices/arquivos e versões desalinhados. [28]
3. **Dentro da instância:** olhar **Metrics and Status**, a aba **Support / Diagnostics** e os logs da instância; guardar trechos com horário, versão, módulo e erro exato. A página de diagnóstico sugere usar os dados do próprio AMP e confirmar qual porta/processo escuta. [2][24]
4. **Para conexão:** separar acesso local, LAN e internet; verificar endereço, porta, protocolo e destino de encaminhamento. Se funciona pela LAN mas não de fora, investigação muda para roteador/ISP/CGNAT; se falha também na LAN, olhar servidor e firewall local. Não assumir causa antes do teste. [24]
5. **Para falha de criação/template:** comparar versão mínima, origem do template e log de implantação. Uma lista incompleta pode ser problema de sincronização/repositório ou requisito da versão, não prova de perda do AMP. [13][14]
6. **Para atualização/restauração:** conferir o guia e notas da release e preservar os dados antes de qualquer tentativa. Os relatos mostram que alterar permissões recursivamente ou mover pastas sem plano pode piorar a recuperação; não “corrija” ownership/permissões às cegas. [2][21][28]

### O que ainda é incerto sem uma inspeção autorizada

- versão e canal realmente instalados em cada componente AMP relevante;
- se os painéis e instâncias descritos ainda estão ativos e se correspondem à versão mostrada nas capturas;
- modo ADS, instalação nativa/contêiner e seus mounts;
- estado de backup, local de armazenamento, retenção e se algum restore foi testado;
- portas, protocolos, firewalls, DNS, roteador, NAT/CGNAT e alcance público;
- papéis/licença e configurações atuais.

Nenhum desses itens é preenchido por um relato antigo ou por este guia.

## 11. Resumo de bolso

- AMP administra aplicações; ADS é a camada de gestão no AMP 2; `ampinstmgr`, instâncias, templates e jogo são componentes/versionamentos diferentes.
- No AMP 2, diferencie Standalone, Controller, Target e Hybrid; a arquitetura de múltiplos nós depende de conexões nos dois sentidos.
- **Manage** de uma instância e configuração do ADS são escopos diferentes. Defaults de implantação não são prova de alteração em instâncias existentes.
- Atualização segura é uma cadeia: ferramenta → instâncias AMP → template/configuração → aplicação do jogo, conforme notas da versão.
- No AMP 2.8, backup ao vivo só tem consistência assegurada onde há suporte a quiesce; as notas atuais citam Minecraft Java/Bedrock. Backup local/S3 e restore precisam de teste real.
- HTTPS protege o painel web, não abre nem protege automaticamente as portas do jogo. Use porta/protocolo realmente documentados para aquela instância.
- Relato comunitário gera hipótese; versão, logs e testes daquele host determinam o diagnóstico.

## Fontes consultadas

### Produto e publicações de versão CubeCoders

[1] AMP — página de produto e edições: https://cubecoders.com/AMP

[3] AMP “Proteus” 2.8.0 release notes (inclui atualizações de 2.8.0.6/.8/.10): https://discourse.cubecoders.com/t/amp-proteus-2-8-0-release-notes/40953

### Base de conhecimento / guias CubeCoders

[2] Como atualizar os componentes do AMP: https://discourse.cubecoders.com/t/how-to-update-amp-to-the-latest-version/2297

[6] Modos de implantação do ADS: https://discourse.cubecoders.com/t/ads-deployment-modes/2245

[9] Instalação oficial: https://cubecoders.com/AMPInstall

[10] GetAMP unattended installations: https://discourse.cubecoders.com/t/getamp-unattended-installations/2294

[11] Docker/Podman para instâncias AMP: https://discourse.cubecoders.com/t/configuring-amp-to-use-docker-podman-for-instances/1957

[12] HTTPS seguro com AMP: https://discourse.cubecoders.com/t/setting-up-secure-http-https-with-amp/2305

[13] Templates indisponíveis/sincronização: https://discourse.cubecoders.com/t/missing-some-templates-when-creating-an-instance/2314

[15] Gestão de usuários e permissões: https://discourse.cubecoders.com/t/managing-user-permissions-in-amp/2301

[16] Configuração Enterprise/Advanced (contexto de segurança e templates): https://discourse.cubecoders.com/t/configuring-amp-for-enterprise-or-advanced-usage/1830

[17] Variáveis globais do Scheduler, desde AMP 2.5: https://discourse.cubecoders.com/t/scheduler-global-variables/10601

[18] AMP 2.5.1 release notes e timezone do Scheduler: https://discourse.cubecoders.com/t/amp-callisto-2-5-1-release-notes/14472

[19] Caminhos de backup local e mounts de contêiner: https://discourse.cubecoders.com/t/how-to-change-backup-locations/2783

[20] S3 backup configuration (guia de usuário no fórum, 2023): https://discourse.cubecoders.com/t/s3-backup-configuration/3241

[23] Como conectar ao painel remotamente (8080 é exemplo/padrão documentado): https://discourse.cubecoders.com/t/how-to-connect-to-amp-remotely/3731

[24] Diagnóstico de conectividade/portas: https://discourse.cubecoders.com/t/diagnosing-connectivity-issues/2290

[25] Licenças e ativações, FAQ de 24 fev. 2026: https://discourse.cubecoders.com/t/licencing-and-activations-faq/38539

### Relatos comunitários — experiências localizadas, não especificações

[7][8] Confusão com escopos, papéis e agendamentos (jun. 2024): https://discourse.cubecoders.com/t/challenges-getting-started-with-amp/14132

[14] Requisito mínimo de versão de template, caso de suporte: https://discourse.cubecoders.com/t/application-deployment-this-task-could-not-be-completed-create-instance/35412

[21] Restore/migração de backup para novo servidor (discussão, 2022): https://discourse.cubecoders.com/t/restore-backup-on-new-server/2865

[22] Dificuldades de restauração com AMP 2.5.1.6 / Windows Server 2019 (relato de 16 ago. 2024): https://discourse.cubecoders.com/t/backup-restore-issues/16085

[26] Tabela de edições antiga; os preços divergem da página de produto consultada: https://discourse.cubecoders.com/t/editions-comparison-sheet/2247

[28] Caso de instâncias que desapareceram após atualização AMP 2.4.0.0 (Debian 11, jan. 2025): https://discourse.cubecoders.com/t/after-update-with-application-deployment-all-instances-have-disappeared-like-a-fresh-install/22334

---

**Status do material:** este repositório inclui um locale PT-BR e um instalador opcional de compatibilidade testado para AMP 2.8.0.10. O instalador altera arquivos da interface e cria backups; veja o tutorial, confirme a versão e não o reutilize após uma atualização do AMP sem revisar os arquivos esperados.

## 12. Prioridade: interface em português brasileiro

### Resposta curta

**AMP 2 tem suporte documentado a arquivos de localização**, mas a documentação consultada não confirma um pacote pt-BR pronto nem um seletor oficial de português brasileiro incluído. Desde AMP 2.2.1.0, a CubeCoders documenta arquivos de idioma JSON em `WebRoot/Locale`; o repositório oficial `CubeCoders/AMPTranslations` recebe contribuições. O README pede um código de idioma de **duas letras ISO 639-1**: para português, a forma documentada seria `pt`, não `pt-BR`. Isso não prova que a variante regional brasileira seja rejeitada em toda versão, mas `pt-BR` não é o formato descrito. [29]

A listagem pública atual do repositório oficial mostra `da.json`, `de.json`, `es.json`, `fr.json`, `ko.json` e `template.json`; não lista `pt.json` nem `pt-BR.json`. Isso confirma que não há um locale português publicado na listagem principal consultada, mas não exclui arquivos fora dela ou traduções privadas. [29]

### Opções oficiais e o que cada uma entrega

| Caminho | O que é documentado | O que não garante |
|---|---|---|
| **Arquivo de localização AMP 2 (`WebRoot/Locale/*.json`)** | O README oficial descreve estrutura, chaves em inglês, objeto `Strings`, nome/código do locale e listas de meses/dias. Strings que faltarem permanecem em inglês. O teste documentado usa `?lang=xx`; `?lang=en` volta ao inglês. | Não é automaticamente uma tradução completa, revisada ou empacotada pela CubeCoders. O idioma do painel AMP também não traduz o jogo ou o conteúdo de cada servidor. |
| **Traduzir e contribuir ao `CubeCoders/AMPTranslations`** | Pull request; CubeCoders revê e pode pedir validação comunitária. Tradução considerada precisa/de qualidade pode ser aceita no próprio AMP. Ao contribuir, o autor autoriza inclusão no software comercial. | A aceitação e o prazo não são garantidos. O formato público descrito é ISO de duas letras; tratamento específico de `pt-BR` precisa confirmação. |
| **Theme / tema CSS** | É uma camada visual CSS. O guia do fórum diz que arquivos de tema são preservados entre atualizações e podem ser trocados sem reiniciar, com atualização da página; a aparência atinge todos os usuários e instâncias administradas que compartilham a interface. [30] | **Tema não é tradução:** cores, fontes e layout não traduzem rótulos/strings. CSS pode ocultar ou rearranjar elementos, não substitui localização acessível. |
| **Strings de módulos/plugins** | O repositório avisa que AMP tem muitos módulos e plugins e recomenda testar a tradução em mais de um jogo; notas AMP 2.4.3.2 mencionam expansão das strings localizáveis e 2.4.3.4 melhoria de localização em todo o núcleo e interface. [31] | Não prova cobertura completa de todo módulo, plugin, diálogo, texto do jogo ou integração; faltas seguem em inglês e cada extensão pode ter seu próprio comportamento. |

O repositório público contém um `template.json` com **658 strings** na versão consultada. Seu nome/código segue o formato do README. O template traz a propriedade `LongDaysOfWeeek` com três “e”; embora o README a escreva `LongDaysOfWeek`, um rascunho baseado nesse arquivo deve preservar literalmente o nome da propriedade observado até que a versão do painel seja comparada. [29]

### Glossário inicial PT-BR — proposta de consistência

Esta tabela é um primeiro vocabulário, não um mapeamento completo validado de todos os rótulos presentes na instalação. A forma original continua sendo a chave técnica do JSON e deve acompanhar a tradução nas notas/documentação; as traduções abaixo são uma proposta a revisar com contexto real de tela.

| Rótulo original | Tradução PT-BR proposta | Uso consistente |
|---|---|---|
| `Instance` / `AMP instance` | Instância / instância AMP | Processo/ambiente gerenciado; não chamar de “servidor” quando também pode ser o ADS. |
| `Application` | Aplicação | Programa gerenciado; reservar “jogo” ao jogo. |
| `Application Deployment` | Implantação de aplicações | Área/função do ADS. |
| `Controller` / `Target` | Controlador / alvo | Preservar o original ao explicar papéis e topologia. |
| `Template` | Template (modelo) | Manter “template” junto de “modelo” por ser termo frequente da interface e comunidade. |
| `Manage` | Gerenciar | Ação para abrir a gestão da instância. |
| `Configuration` / `Settings` | Configuração / configurações | “Configuração” para seção; “configurações” para opções. |
| `User` / `Role` | Usuário / papel | Preferir “papel”, não “função”, para o mecanismo de permissões. |
| `Schedule` / `Trigger` / `Task` | Agendamento / gatilho / tarefa | Não misturar o gatilho que dispara com a tarefa executada. |
| `Backup` / `Restore Backup` | Backup / restaurar backup | Preserva o uso corrente em PT-BR; explicar como cópia de segurança na primeira ocorrência. |
| `File Manager` / `Datastore` | Gerenciador de arquivos / armazenamento | Não traduzir `Datastore` por “banco de dados”. |
| `Start` / `Stop` / `Restart` | Iniciar / parar / reiniciar | Verbos curtos de controles. |
| `Update` / `Upgrade` | Atualizar / atualizar versão | Em notas técnicas, distinguir atualização de aplicação e upgrade do AMP quando necessário. |
| `Running` / `Stopped` / `Suspended` | Em execução / parado / suspenso | Vocabulário de estado, sem indicar causa. |
| `Permissions` / `Audit Log` | Permissões / registro de auditoria | Termos de segurança. |

### Riscos de edição e atualização

- **Mais seguro é usar o mecanismo de locale separado**, não editar executáveis, arquivos internos do AMP, strings originais nem JavaScript. O procedimento oficial descreve um arquivo de idioma adicional; não documenta alteração de código-fonte da instalação.
- **A preservação de temas não comprova a preservação de locales personalizados.** A página de temas diz explicitamente que temas sobrevivem a atualizações; não achei garantia equivalente para um `pt.json` criado à parte. Faça cópia do arquivo fora da pasta do AMP antes de atualizar e confira se continua disponível depois; não conclua que a atualização apagou ou preservou até verificar.
- **Tradução parcial ou comprida** pode deixar inglês misturado, quebrar espaçamento ou exigir ajuste de termos. O README reconhece que, em alguns casos, o layout pode precisar de adaptação. Um tema CSS não deve ser usado para esconder controles cuja tradução esteja faltando.
- **Teste primeiro sem afetar o uso normal:** use o fluxo oficial de `?lang=xx` numa sessão de navegador de teste; confira login, ADS e algumas instâncias/jogos, inclusive extensões relevantes. Mantenha o caminho de volta `?lang=en`. Antes de colocar arquivo novo no host, confirme versão/caminho, guarde cópia e prefira um teste isolado/staging se existir.
- **Contribuição pública tem condição de licença:** o projeto informa que enviar uma tradução concede à CubeCoders permissão para incluí-la em software comercial. Quem abrir um PR deve revisar a tradução e aceitar essa condição antes do envio. [29]

### Implementação PT-BR incluída neste projeto

O diretório `locale/pt.json` reúne a tradução PT-BR preparada para esta interface e inclui as mensagens de incompatibilidade de versão. A cobertura é parcial: extensões, módulos e textos do jogo podem continuar em inglês.

O instalador opcional dá suporte somente ao AMP 2.8.0.10 com os trechos de interface esperados. Ele preserva o parâmetro de versão que o AMP compara com o backend, adiciona um parâmetro separado para renovar o cache e cria backups antes de substituir arquivos. É uma adaptação local, não um recurso oficial da CubeCoders; confira o tutorial e não aplique após uma atualização sem revalidar a versão.

## 13. Resumo de bolso (localização)

- AMP 2.2.1+ documenta locales JSON e `?lang=xx`; a convenção publicada é ISO 639-1 de duas letras (`pt`), não `pt-BR`.
- A listagem principal atual do repositório oficial tem `da`, `de`, `es`, `fr`, `ko` e `template.json`; não inclui locale português.
- O locale deste projeto é uma adaptação parcial; textos de módulos, plugins e jogos podem continuar em inglês.
- Tema CSS altera aparência, não traduz texto. Locale incompleto mantém o inglês nas chaves faltantes; traduções longas podem afetar layout.
- O instalador opcional é específico para AMP 2.8.0.10 e modifica arquivos da interface com backups; consulte o tutorial antes de usar.



### Fontes adicionais sobre localização

[29] Repositório oficial de arquivos de tradução AMP; README informa AMP 2.2.1.0+, formato de locale JSON, ISO 639-1, `?lang=xx`, fallback em inglês, fluxo de revisão e condição de licença: https://github.com/CubeCoders/AMPTranslations · listagem principal atual: `da.json`, `de.json`, `es.json`, `fr.json`, `ko.json`, `template.json`.

[33] Template JSON do repositório oficial (658 strings na versão lida): https://raw.githubusercontent.com/CubeCoders/AMPTranslations/main/template.json

[30] Guia de temas AMP (publicado em 25 out. 2022; atualizado no fórum em 16 out. 2026): CSS, diretório de temas e preservação entre atualizações: https://discourse.cubecoders.com/t/using-amp-themes/2288

[31] Notas oficiais AMP “Decadeus” 2.4.3: localização ampliada em 2.4.3.2 e suporte melhorado no núcleo/interface em 2.4.3.4 (abr.–mai. 2023): https://discourse.cubecoders.com/t/amp-decadeus-2-4-3-release-notes/3319

[32] Discussão do fórum CubeCoders sobre pedido de idioma, com resposta apontando ao repositório de traduções: https://discourse.cubecoders.com/t/giv-1-language/12008
