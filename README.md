# Códigos da tese — predição da positividade da urocultura (HC-UFMG, 2011–2024)

Códigos de análise da tese de doutorado de **Daniel Henrique Bücker** (Programa de Pós-Graduação em Ciências Aplicadas à Saúde do Adulto, Faculdade de Medicina da UFMG; orientador: Prof. Leonardo de Souza Vasconcellos), sobre o perfil demográfico, o espectro microbiológico e o potencial do exame de urina rotina (EAS) e da bacterioscopia pelo Gram para prever a positividade da urocultura quantitativa.

O aplicativo web PreviTU V6, que usa os modelos congelados gerados aqui, está em um repositório próprio: <https://github.com/danielbucker/previtu>.

## Conteúdo

| Arquivo | O que faz | Seção da tese |
|---|---|---|
| `notebooks/01_quatro_paradigmas_ml_sem_e_com_gram.ipynb` | Compara *Elastic Net*, *Random Forest*, *HistGradientBoosting* e *TabResNet* sem e com Gram; validação cruzada aninhada 5 × 3 agrupada por paciente (2011–2022), validação temporal em pacientes novos (2023–2024), bootstrap pareado, DCA, permutação e SHAP | 4.3 e 5.3 |
| `notebooks/02_escore_linear_e_pontos.ipynb` | Índice linear contínuo (Camada A) e escore de pontos inteiros (Camada B, B = 0,25) | 4.4 e 5.5 |
| `notebooks/03_exportar_modelos_previtu_v6.ipynb` | Treina os dois modelos *HistGradientBoosting* finais (2011–2022), grava os `.joblib`, os *model cards* e o hash SHA-256 | 4.5 e 5.6 |
| `notebooks/04_validacao_externa_taylor_dhanda.ipynb` | Validação externa do modelo congelado sem Gram nas coortes de Taylor et al. (2018) e Dhanda et al. (2023), harmonização do fluxo de microscopia reflexa e recalibração logística local | 4.3 e 5.4 |
| `scripts/gerar_dados_sinteticos.py` | Gera a base artificial de teste | — |
| `dados_sinteticos/base_sintetica_urot_uroc_20000.csv` | 20.000 pedidos **artificiais** no formato da base da tese | — |

## Dados

**A base real do HC-UFMG não é distribuída.** São dados de pacientes, sob aprovação do CEP-UFMG (CAAE 67291423.0.0000.5149), e não podem ser publicados.

Para testar a execução dos notebooks, use o arquivo `dados_sinteticos/base_sintetica_urot_uroc_20000.csv`. Ele tem as mesmas colunas e os mesmos formatos de texto da base real (separador `;`), mas **todas as linhas são inventadas**. Foram sorteadas a partir de distribuições simples, ajustadas apenas a proporções agregadas publicadas na tese (por exemplo, positividade de cerca de 22%). Os resultados obtidos com ela **não reproduzem** os números da tese e não têm interpretação clínica.

Colunas: `NumeroPedido`, `Paciente_ID`, `Ano`, `Idade_anos`, `Sexo`, `Origem` (BC, JAF, LEXT, SAST = ambulatório; PA = pronto-atendimento; HC = internação), `UROT__PH`, `UROT__GRAVID`, `UROT__GLIC`, `UROT__HEMOGL`, `UROT__SEDHEM`, `UROT__SEDLEU`, `UROT__ESTERASE`, `UROT__FLORA`, `UROT__NITRIT`, `Gram_texto`, `Cultura_positiva`.

Para gerar outra base: `python scripts/gerar_dados_sinteticos.py --n 20000 --seed 2026`.

As coortes externas do notebook 04 são públicas e devem ser obtidas nas fontes originais:
- Taylor RA, Moore CL, Cheung KH, Brandt C. *PLOS ONE* 2018;13(3):e0194085, arquivo suplementar S1 (doi:10.1371/journal.pone.0194085);
- Dhanda G et al. *Annals of Family Medicine* 2023;21(1):11–18 (doi:10.1370/afm.2902), conjunto de dados desidentificado de atenção primária.

## Como executar

Os notebooks foram escritos para o Google Colab (GPU opcional, usada pela *TabResNet*) e leem a base de uma pasta do Google Drive. Para rodar com a base sintética:

1. Envie `base_sintetica_urot_uroc_20000.csv` para o seu Drive.
2. Na célula de configuração (`CONFIG["input_path"]`, ou `INPUT_PATH` no notebook 03), troque o caminho pelo do arquivo sintético e ajuste `output_dir` / `OUT_DIR`.
3. Execute todas as células. Versões usadas: Python 3.12, scikit-learn 1.7.2 (necessária para carregar os `.joblib`), PyTorch, SHAP.

Com 20.000 linhas, o notebook 01 leva bem menos tempo que com a base real (cerca de 4 h 40 min em GPU com 148.585 pedidos).

## Nota sobre a escala da flora bacteriana

O laboratório registra a flora como *escassa*, *moderada* ou *aumentada*. Nos notebooks 01 e 03, o termo "aumentada" não consta do dicionário `MAPA_CRUZES` e é convertido em ausente. Como o tratamento foi o mesmo no desenvolvimento, no teste temporal e no PreviTU, as métricas não são afetadas. O indicador de ausência da flora (`missingindicator_UROT__FLORA`) passa a codificar, na prática, **flora aumentada**. Os notebooks são publicados como executados para a tese, para preservar a correspondência com os modelos congelados. No notebook 02 (escore), a conversão foi corrigida na célula 2.1. Detalhes nas Seções 4.3, 5.3 e 5.7 da tese.

## Como citar

BÜCKER, D. H. *Perfil demográfico, espectro microbiológico e potencial preditivo dos testes de urina rotina e bacterioscopia nos resultados de uroculturas ambulatoriais e hospitalares de pacientes assistidos em serviço público de Minas Gerais*. Tese (Doutorado em Ciências Aplicadas à Saúde do Adulto) — Faculdade de Medicina, Universidade Federal de Minas Gerais, Belo Horizonte, 2026.

## Licença

MIT — Copyright (c) 2026 Daniel Henrique Bücker. Ver `LICENSE`.

## Aviso

Material de pesquisa. Não é dispositivo médico e não deve orientar decisões clínicas.
