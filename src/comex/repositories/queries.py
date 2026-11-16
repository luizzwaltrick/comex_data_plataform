# Upsert pela chave natural: reprocessar o mesmo arquivo não duplica linhas e só gera
# evento de CDC (update) para o que realmente mudou.
UPSERT_OPERACAO = """
INSERT INTO operacao (fluxo, ano, mes, co_ncm, co_pais, sg_uf, co_via, co_urf,
                      kg_liquido, vl_fob, vl_frete, vl_seguro)
VALUES (%(fluxo)s, %(ano)s, %(mes)s, %(co_ncm)s, %(co_pais)s, %(sg_uf)s, %(co_via)s, %(co_urf)s,
        %(kg_liquido)s, %(vl_fob)s, %(vl_frete)s, %(vl_seguro)s)
ON CONFLICT (fluxo, ano, mes, co_ncm, co_pais, sg_uf, co_via, co_urf) DO UPDATE
SET kg_liquido = EXCLUDED.kg_liquido, vl_fob = EXCLUDED.vl_fob,
    vl_frete = EXCLUDED.vl_frete, vl_seguro = EXCLUDED.vl_seguro, atualizado = now()
WHERE (operacao.kg_liquido, operacao.vl_fob, operacao.vl_frete, operacao.vl_seguro)
      IS DISTINCT FROM
      (EXCLUDED.kg_liquido, EXCLUDED.vl_fob, EXCLUDED.vl_frete, EXCLUDED.vl_seguro)
"""
