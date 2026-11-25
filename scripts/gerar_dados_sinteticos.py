"""Gera uma base ARTIFICIAL de 20.000 pedidos com o mesmo formato da base usada na tese.

Nenhuma linha vem de paciente real. Os valores são sorteados a partir de distribuições
simples, calibradas apenas por proporções agregadas publicadas na tese (positividade
global ~22%, distribuição por origem e faixas plausíveis de cada parâmetro do EAS).
A base serve para testar a execução dos notebooks, não para reproduzir os resultados.

Uso:
    python scripts/gerar_dados_sinteticos.py --n 20000 --seed 2026 \
        --saida dados_sinteticos/base_sintetica_urot_uroc_20000.csv
"""
from __future__ import annotations

import argparse
from pathlib import Path

import numpy as np
import pandas as pd


def _cruzes(nivel: np.ndarray, rotulos: list[str]) -> np.ndarray:
    nivel = np.clip(nivel, 0, len(rotulos) - 1).astype(int)
    return np.array(rotulos, dtype=object)[nivel]


def gerar(n: int = 20000, seed: int = 2026) -> pd.DataFrame:
    rng = np.random.default_rng(seed)

    # Pacientes com pedidos repetidos (média ~2,4 pedidos por paciente)
    n_pac = int(n / 2.4)
    pac_ids = rng.integers(0, n_pac, size=n)
    pac_ids = np.array([f"SINT{p:06d}" for p in pac_ids])

    # Ano: pacientes com primeiro pedido tardio garantem pacientes novos em 2023–2024
    ano_base = rng.integers(2011, 2025, size=n_pac)
    idx_pac = np.array([int(p[4:]) for p in pac_ids])
    ano = np.clip(ano_base[idx_pac] + rng.integers(0, 2, size=n), 2011, 2024)

    sexo = np.where(rng.random(n_pac) < 0.64, "F", "M")[idx_pac]
    idade = np.clip(rng.gamma(2.2, 22.0, size=n_pac), 0, 105)[idx_pac]
    idade = np.round(idade + rng.random(n) * 0.5, 1)

    origem = rng.choice(["BC", "JAF", "LEXT", "SAST", "PA", "HC"], size=n,
                        p=[0.48, 0.05, 0.03, 0.03, 0.21, 0.20])

    # Estado latente de infecção (~22% de positividade)
    logit = (-2.0 + 0.25 * (sexo == "F") + 0.012 * np.maximum(idade - 50, 0)
             + 0.35 * np.isin(origem, ["PA", "HC"]))
    infec = rng.random(n) < 1 / (1 + np.exp(-logit))

    # Parâmetros do EAS condicionados ao estado latente
    leu = np.where(infec, rng.lognormal(3.4, 1.2, n), rng.lognormal(1.3, 1.0, n))
    hem = np.where(infec, rng.lognormal(1.9, 1.3, n), rng.lognormal(1.0, 1.1, n))
    leu_txt = np.where(leu > 100, "NUMEROSOS", np.round(leu).astype(int).astype(str))
    hem_txt = np.where(hem > 100, "NUMEROSAS", np.round(hem).astype(int).astype(str))

    esterase = _cruzes(np.where(infec, rng.poisson(2.0, n), rng.poisson(0.3, n)),
                       ["NEGATIVO", "TRAÇOS", "+", "++", "+++"])
    nitrito = np.where(infec & (rng.random(n) < 0.45), "POSITIVO",
                       np.where(rng.random(n) < 0.03, "POSITIVO", "NEGATIVO"))
    flora = _cruzes(np.where(infec, 1 + rng.poisson(1.0, n), rng.poisson(0.6, n)),
                    ["ESCASSA", "ESCASSA", "MODERADA", "AUMENTADA"])
    hemogl = _cruzes(np.where(infec, rng.poisson(1.0, n), rng.poisson(0.4, n)),
                     ["NEGATIVO", "TRAÇOS", "+", "++", "+++"])
    glic = _cruzes(rng.poisson(0.1, n), ["NEGATIVO", "+", "++", "+++"])
    ph = np.clip(np.round(rng.normal(6.0, 0.7, n) * 2) / 2, 5.0, 8.5)
    dens = np.clip(np.round(rng.normal(1.016, 0.007, n), 3), 1.000, 1.040)
    dens_txt = np.where(rng.random(n) < 0.5, (dens * 1000).astype(int).astype(str),
                        np.char.replace(dens.astype(str), ".", ","))

    # Bacterioscopia pelo Gram em gota de urina não centrifugada
    r = rng.random(n)
    gram = np.select(
        [infec & (r < 0.62), infec & (r < 0.80), infec & (r < 0.86), infec,
         ~infec & (r < 0.12), ~infec & (r < 0.20)],
        ["BACILOS GRAM-NEGATIVOS", "COCOS GRAM-POSITIVOS", "LEVEDURAS",
         "NÃO FORAM OBSERVADAS BACTÉRIAS", "BACILOS GRAM-POSITIVOS",
         "BACILOS GRAM-NEGATIVOS"],
        default="NÃO FORAM OBSERVADAS BACTÉRIAS",
    )

    # Desfecho: urocultura positiva (com ruído de classificação)
    y = np.where(rng.random(n) < 0.94, infec, ~infec).astype(int)

    df = pd.DataFrame({
        "NumeroPedido": [f"PED{i:07d}" for i in range(n)],
        "Paciente_ID": pac_ids,
        "Ano": ano,
        "Idade_anos": idade,
        "Sexo": sexo,
        "Origem": origem,
        "UROT__PH": ph,
        "UROT__GRAVID": dens_txt,
        "UROT__GLIC": glic,
        "UROT__HEMOGL": hemogl,
        "UROT__SEDHEM": hem_txt,
        "UROT__SEDLEU": leu_txt,
        "UROT__ESTERASE": esterase,
        "UROT__FLORA": flora,
        "UROT__NITRIT": nitrito,
        "Gram_texto": gram,
        "Cultura_positiva": y,
    })

    # Ausências esporádicas (~1%), como em dados reais
    for col in ["UROT__PH", "UROT__GRAVID", "UROT__SEDHEM", "UROT__SEDLEU", "UROT__FLORA"]:
        df.loc[rng.random(n) < 0.01, col] = np.nan
    return df.sort_values(["Ano", "NumeroPedido"]).reset_index(drop=True)


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("--n", type=int, default=20000)
    ap.add_argument("--seed", type=int, default=2026)
    ap.add_argument("--saida", default="dados_sinteticos/base_sintetica_urot_uroc_20000.csv")
    a = ap.parse_args()
    d = gerar(a.n, a.seed)
    Path(a.saida).parent.mkdir(parents=True, exist_ok=True)
    d.to_csv(a.saida, sep=";", index=False)
    print(f"{len(d):,} linhas gravadas em {a.saida}; positividade = {d['Cultura_positiva'].mean():.1%}")
