/*
CONSULTAS SQL — ANÁLISE CPGF 2024
Banco: cpgf_2024.db (SQLite, 141.048 registros)
Ferramenta: DBeaver
*/


/* 1 - TOP 10 ÓRGÃOS POR GASTO TOTAL */

SELECT nome_orgao_superior,
       SUM(valor_transacao) AS total_gasto
FROM cpgf
GROUP BY nome_orgao_superior
ORDER BY total_gasto DESC
LIMIT 10;


/* 2 - DISTRIBUIÇÃO POR TIPO DE TRANSAÇÃO */

SELECT transacao,
       SUM(valor_transacao) AS total_gasto,
       COUNT(*) AS qtd_transacoes,
       ROUND(SUM(valor_transacao) * 100.0 / (SELECT SUM(valor_transacao) FROM cpgf), 2) AS pct_total
FROM cpgf
GROUP BY transacao
ORDER BY total_gasto DESC;


/* 3 - SAZONALIDADE MENSAL */

SELECT mes_extrato,
       SUM(valor_transacao) AS total_gasto,
       COUNT(*) AS qtd_transacoes,
       ROUND(AVG(valor_transacao), 2) AS media_transacao
FROM cpgf
GROUP BY mes_extrato
ORDER BY mes_extrato;


/* 4 - TOP 10 PORTADORES (excluindo sigilosos) */

SELECT nome_portador,
       SUM(valor_transacao) AS total_gasto,
       COUNT(*) AS qtd_transacoes
FROM cpgf
WHERE nome_portador != 'Sigiloso'
GROUP BY nome_portador
ORDER BY total_gasto DESC
LIMIT 10;


/* 5 - TOP 10 FAVORECIDOS (excluindo sigilosos e sem identificação) */

SELECT nome_favorecido,
       SUM(valor_transacao) AS total_gasto,
       COUNT(*) AS qtd_transacoes
FROM cpgf
WHERE nome_favorecido NOT IN ('Sigiloso', 'NAO SE APLICA', 'SEM INFORMACAO')
GROUP BY nome_favorecido
ORDER BY total_gasto DESC
LIMIT 10;


/* 6 - TICKET MÉDIO POR ÓRGÃO (mínimo 50 transações) */

SELECT nome_orgao_superior,
       SUM(valor_transacao) AS total_gasto,
       COUNT(*) AS qtd_transacoes,
       ROUND(SUM(valor_transacao) / COUNT(*), 2) AS ticket_medio
FROM cpgf
GROUP BY nome_orgao_superior
HAVING qtd_transacoes >= 50
ORDER BY ticket_medio DESC
LIMIT 10;