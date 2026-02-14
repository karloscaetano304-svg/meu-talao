import streamlit as st
import pdfplumber
import re

# Configuração da página para celular
st.set_page_config(page_title="Analisador EDP ES", page_icon="⚡")

def limpar_valor(texto_valor):
    if not texto_valor: return 0.0
    v = texto_valor.replace('.', '').replace(',', '.').strip()
    try: return float(v)
    except: return 0.0

st.title("⚡ Analisador EDP ES")
st.markdown("Suba o PDF da sua conta para uma análise detalhada.")

# --- UPLOAD DO ARQUIVO ---
arquivo_pdf = st.file_uploader("Escolha a fatura PDF", type=["pdf"])

if arquivo_pdf:
    with pdfplumber.open(arquivo_pdf) as pdf:
        texto = pdf.pages[0].extract_text()

        # --- LÓGICA DE EXTRAÇÃO (SEU CÓDIGO ORIGINAL) ---
        
        # Energia
        consumo_match = re.search(r"Energia Ativa - kWh.*?(\d+\.000)", texto)
        consumo_rede = limpar_valor(consumo_match.group(1)) / 1000 if consumo_match else 0.0

        injetada_match = re.search(r"Energia Injetada - k.*?(\d+\.000)", texto)
        energia_injetada = limpar_valor(injetada_match.group(1)) / 1000 if injetada_match else 0.0

        taxa_estimada = 0.35 
        geracao_total_est = energia_injetada / (1 - taxa_estimada)
        simultanea = geracao_total_est - energia_injetada

        # Impostos
        icms_match = re.search(r"TUSD - Energia Ativa.*?17,000\s+([\d,.]+)", texto)
        total_icms = limpar_valor(icms_match.group(1)) if icms_match else 0.0

        valor_cosip_match = re.search(r"Lei Municipal\s+1,0000\s+([\d,.]+)", texto)
        valor_cosip = limpar_valor(valor_cosip_match.group(1)) if valor_cosip_match else 0.0

        pis_match = re.search(r"PIS\s+[\d,.]+\s+[\d,.-]+\s+([\d,.]+)", texto)
        cofins_match = re.search(r"COFINS\s+[\d,.]+\s+[\d,.-]+\s+([\d,.]+)", texto)
        total_pis_cofins = limpar_valor(pis_match.group(1)) + limpar_valor(cofins_match.group(1))

        valor_total_match = re.search(r"TOTAL\s+([\d,.]+)", texto)
        valor_total = valor_total_match.group(1) if valor_total_match else "0,00"

        # --- EXIBIÇÃO NO APP ---
        
        st.subheader("📊 Movimentação de Energia")
        c1, c2 = st.columns(2)
        c1.metric("Consumo Rede", f"{consumo_rede:.0f} kWh")
        c2.metric("Energia Injetada", f"{energia_injetada:.0f} kWh")
        
        st.info(f"**Consumo REAL da Casa:** {consumo_rede + simultanea:.0f} kWh (estimado)")

        st.subheader("💰 Detalhamento Financeiro")
        col_a, col_b = st.columns(2)
        col_a.write(f"**ICMS TUSD:** R$ {total_icms:.2f}")
        col_a.write(f"**PIS/COFINS:** R$ {total_pis_cofins:.2f}")
        col_b.write(f"**Ilum. Pública:** R$ {valor_cosip:.2f}")
        
        st.success(f"### VALOR FINAL: R$ {valor_total}")

        with st.expander("Ver resumo da análise"):
            st.write("Seu sistema solar cobriu todo o seu consumo de ponta, restando apenas taxas obrigatórias e impostos.")

else:
    st.info("Aguardando PDF...")
