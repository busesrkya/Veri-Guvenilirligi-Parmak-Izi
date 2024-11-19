from __future__ import annotations

from pathlib import Path
import sys

import pandas as pd
import plotly.express as px
import streamlit as st

PROJECT_ROOT = Path(__file__).resolve().parents[1]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from src.database import connect, test_connection
from src.data_loader import load_csv
from src.fingerprint import analyze_dataset
from src.repository import AnalysisRepository
from src.sensor_analysis import analyze_sensor_consistency

st.set_page_config(page_title="Data Reliability Fingerprint", layout="wide")
st.title("Data Reliability Fingerprint")
st.caption("Bağlama duyarlı veri güvenilirliği analizi. Skorlar açıklanabilir proje varsayımlarıdır; evrensel bir güvence değildir.")

uploaded = st.sidebar.file_uploader("CSV dosyası yükle", type="csv")
default_path = PROJECT_ROOT / "data" / "sample_data.csv"
if uploaded is not None:
    frame = load_csv(uploaded)
    dataset_name = uploaded.name
elif default_path.exists():
    frame = load_csv(default_path)
    dataset_name = default_path.name
    st.sidebar.info("Üretilen örnek veri seti kullanılıyor.")
else:
    st.info("Bir CSV yükleyin veya önce `python data/generate_dataset.py` komutunu çalıştırın.")
    st.stop()

candidate_contexts = [c for c in frame.columns if frame[c].nunique(dropna=True) <= 60]
if "temperature" in frame.columns:
    candidate_contexts.append("temperature_range")
if "machine_load" in frame.columns:
    candidate_contexts.append("machine_load_range")
default_contexts = [c for c in ["machine_id", "sensor_id", "shift", "operating_status", "temperature_range", "machine_load_range"] if c in candidate_contexts]
contexts = st.sidebar.multiselect("Bağlam kolonları", candidate_contexts, default=default_contexts)
timestamp_options = ["<none>"] + list(frame.columns)
timestamp_default = timestamp_options.index("timestamp") if "timestamp" in timestamp_options else 0
timestamp_choice = st.sidebar.selectbox("Zaman damgası kolonu", timestamp_options, index=timestamp_default)
timestamp_column = None if timestamp_choice == "<none>" else timestamp_choice

result = analyze_dataset(
    frame,
    dataset_name=dataset_name,
    context_columns=contexts,
    timestamp_column=timestamp_column,
    key_columns=["record_id"] if "record_id" in frame else None,
)

pages = ["Genel Bakış", "Veri Profilleme", "Bağlam Analizi", "Zamansal Analiz", "ML Deneyleri", "Analiz Geçmişi"]
page = st.sidebar.radio("Sayfa", pages)

if page == "Genel Bakış":
    c1, c2, c3 = st.columns(3)
    c1.metric("Satır", f"{len(frame):,}")
    c2.metric("Kolon", len(frame.columns))
    c3.metric("Genel skor", "Hesaplanamadı" if result["overall_score"] is None else f"{result['overall_score']:.1f}")
    chart_data = pd.DataFrame(
        [{"metric": name.replace("_", " ").title(), "score": score} for name, score in result["metrics"].items() if score is not None]
    )
    if not chart_data.empty:
        fig = px.bar(chart_data, x="score", y="metric", orientation="h", range_x=[0, 100], text_auto=".1f")
        fig.update_layout(yaxis_title="", xaxis_title="Skor (0–100)")
        st.plotly_chart(fig, use_container_width=True)
    unavailable = result["unavailable_metrics"]
    if unavailable:
        st.warning("Hesaplanamayan metrikler: " + ", ".join(unavailable))
    with st.expander("Yöntem ayrıntıları ve sınırlamalar"):
        st.json(result["metric_details"])
        for limitation in result["limitations"]:
            st.write(f"- {limitation}")

elif page == "Veri Profilleme":
    profile_columns = pd.DataFrame(result["profile"]["columns"])
    st.dataframe(profile_columns, use_container_width=True)
    if not profile_columns.empty:
        st.plotly_chart(px.bar(profile_columns, x="column", y="missing_rate", title="Özelliklere göre eksik değer oranı"), use_container_width=True)
    st.subheader("Doğrulama kuralları")
    st.dataframe(result["validation_results"], use_container_width=True)
    st.subheader("Sensör tutarlılığı")
    st.json(analyze_sensor_consistency(frame))

elif page == "Bağlam Analizi":
    context = result["context_results"]
    if context.empty:
        st.info("Bir veya daha fazla bağlam kolonu seçin.")
    else:
        st.dataframe(context, use_container_width=True)
        fig = px.bar(
            context,
            x="context_value",
            y="reliability_score",
            color="context_column",
            facet_row="context_column",
            hover_data=["sample_size", "sufficient_sample", "missing_rate"],
            range_y=[0, 100],
        )
        st.plotly_chart(fig, use_container_width=True)

elif page == "Zamansal Analiz":
    temporal = result["temporal_results"]
    if temporal.empty:
        st.info("Geçerli bir zaman damgası kolonu ve gözlemler olmadan zamansal analiz hesaplanamaz.")
    else:
        st.dataframe(temporal, use_container_width=True)
        melted = temporal.melt("period_start", value_vars=["completeness", "validity", "reliability_score"], var_name="metric", value_name="score")
        st.plotly_chart(px.line(melted, x="period_start", y="score", color="metric", markers=True, range_y=[0, 100]), use_container_width=True)

elif page == "ML Deneyleri":
    if st.button("Kontrollü ML deneylerini çalıştır", type="primary"):
        with st.spinner("Logistic Regression ve Random Forest modelleri eğitiliyor..."):
            from src.ml_experiments import run_experiments

            st.session_state["experiments"] = run_experiments(frame)
    experiments = st.session_state.get("experiments")
    if experiments is None:
        st.info("Gözlenen veri ile kontrollü bozulma senaryolarını karşılaştırmak için deneyleri çalıştırın.")
    else:
        st.dataframe(experiments, use_container_width=True)
        st.plotly_chart(px.bar(experiments, x="scenario", y="f1_score", color="model", barmode="group"), use_container_width=True)
        st.plotly_chart(px.scatter(experiments, x="reliability_score", y="f1_score", color="model", symbol="scenario"), use_container_width=True)

else:
    connected, message = test_connection()
    if not connected:
        st.warning(message)
        st.caption("Hiçbir sonuç kaydedilmiş gibi gösterilmez. Kalıcı kayıt için `.env` dosyasında SQL Server bağlantısını yapılandırın.")
    else:
        st.success(message)
        with connect() as connection:
            repository = AnalysisRepository(connection)
            st.dataframe(repository.analysis_history(), use_container_width=True)
            if st.button("Geçerli analizi kaydet"):
                run_id = repository.save_analysis(dataset_name, "uploaded_csv" if uploaded else "synthetic_csv", result)
                experiments = st.session_state.get("experiments")
                if experiments is not None:
                    repository.save_experiments(run_id, experiments)
                st.success(f"{run_id} numaralı analiz çalışması kaydedildi.")
