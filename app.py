import streamlit as st
st.image("IMG_4881.jpeg")
import pandas as pd
import datetime
from dateutil.relativedelta import relativedelta

# Cấu hình trang Streamlit
st.set_page_config(
    page_title="Công Cụ Tính Lãi Tiết Kiệm",
    page_icon="💰",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Áp dụng giao diện tùy biến với CSS
st.markdown("""
<style>
    .main-header {
        font-size: 2.2rem;
        font-weight: 700;
        color: #1E3A8A;
        margin-bottom: 0.2rem;
    }
    .sub-header {
        font-size: 1rem;
        color: #64748B;
        margin-bottom: 1.5rem;
    }
    .metric-card {
        background: linear-gradient(135deg, #F8FAFC 0%, #EFF6FF 100%);
        border: 1px solid #DBEAFE;
        border-radius: 12px;
        padding: 18px;
        box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.05);
        margin-bottom: 12px;
    }
    .metric-title {
        font-size: 0.9rem;
        font-weight: 600;
        color: #475569;
        text-transform: uppercase;
        letter-spacing: 0.5px;
    }
    .metric-value {
        font-size: 1.6rem;
        font-weight: 700;
        color: #1D4ED8;
        margin-top: 6px;
    }
    .metric-sub {
        font-size: 0.82rem;
        color: #64748B;
        margin-top: 4px;
    }
</style>
""", unsafe_allow_html=True)

def format_vnd(amount: float) -> str:
    """Định dạng số tiền sang định dạng tiền tệ VND dễ đọc."""
    return f"{amount:,.0f} ₫".replace(",", ".")

def calculate_savings(principal: float, term_months: int, annual_rate: float, payout_method: str, start_date: datetime.date):
    """
    Tính toán lãi tiết kiệm theo chuẩn ngân hàng:
    - Cuối kỳ: Tiền lãi = Gốc * (Lãi suất / 100) * (Số tháng / 12)
    - Hàng tháng: Tiền lãi mỗi tháng = Gốc * (Lãi suất / 100) / 12
    - Hàng quý: Tiền lãi mỗi quý (3 tháng) = Gốc * (Lãi suất / 100) * (3 / 12)
    """
    rate_decimal = annual_rate / 100.0
    schedule_data = []

    if payout_method == "Cuối kỳ":
        # Nhận toàn bộ lãi khi đáo hạn
        total_interest = principal * rate_decimal * (term_months / 12.0)
        periodic_interest = total_interest
        periodic_label = f"Nhận 1 lần vào cuối kỳ ({term_months} tháng)"

        maturity_date = start_date + relativedelta(months=term_months)
        schedule_data.append({
            "Kỳ nhận lãi": "Đáo hạn",
            "Ngày nhận dự kiến": maturity_date.strftime("%d/%m/%Y"),
            "Tiền lãi định kỳ": total_interest,
            "Tiền gốc nhận lại": principal,
            "Tổng thực nhận kỳ này": principal + total_interest,
            "Số dư tiền gửi còn lại": 0.0
        })

    elif payout_method == "Hàng tháng":
        # Nhận lãi đều đặn mỗi tháng
        monthly_interest = principal * rate_decimal / 12.0
        periodic_interest = monthly_interest
        periodic_label = "Mỗi tháng"
        total_interest = monthly_interest * term_months

        for month in range(1, term_months + 1):
            payout_date = start_date + relativedelta(months=month)
            is_last = (month == term_months)
            principal_return = principal if is_last else 0.0
            schedule_data.append({
                "Kỳ nhận lãi": f"Tháng {month}",
                "Ngày nhận dự kiến": payout_date.strftime("%d/%m/%Y"),
                "Tiền lãi định kỳ": monthly_interest,
                "Tiền gốc nhận lại": principal_return,
                "Tổng thực nhận kỳ này": monthly_interest + principal_return,
                "Số dư tiền gửi còn lại": 0.0 if is_last else principal
            })

    elif payout_method == "Hàng quý":
        # Nhận lãi định kỳ mỗi 3 tháng
        quarterly_interest = principal * rate_decimal * (3.0 / 12.0)
        periodic_interest = quarterly_interest
        periodic_label = "Mỗi quý (3 tháng)"
        
        full_quarters = term_months // 3
        remainder_months = term_months % 3
        
        # Tiền lãi các quý đủ
        total_interest = quarterly_interest * full_quarters
        
        # Nếu có tháng lẻ dư ra cuối kỳ
        remainder_interest = 0.0
        if remainder_months > 0:
            remainder_interest = principal * rate_decimal * (remainder_months / 12.0)
            total_interest += remainder_interest

        for q in range(1, full_quarters + 1):
            payout_date = start_date + relativedelta(months=q * 3)
            is_final = (q == full_quarters and remainder_months == 0)
            principal_return = principal if is_final else 0.0
            schedule_data.append({
                "Kỳ nhận lãi": f"Quý {q}",
                "Ngày nhận dự kiến": payout_date.strftime("%d/%m/%Y"),
                "Tiền lãi định kỳ": quarterly_interest,
                "Tiền gốc nhận lại": principal_return,
                "Tổng thực nhận kỳ này": quarterly_interest + principal_return,
                "Số dư tiền gửi còn lại": 0.0 if is_final else principal
            })

        if remainder_months > 0:
            payout_date = start_date + relativedelta(months=term_months)
            schedule_data.append({
                "Kỳ nhận lãi": f"Kỳ lẻ ({remainder_months} tháng cuối)",
                "Ngày nhận dự kiến": payout_date.strftime("%d/%m/%Y"),
                "Tiền lãi định kỳ": remainder_interest,
                "Tiền gốc nhận lại": principal,
                "Tổng thực nhận kỳ này": remainder_interest + principal,
                "Số dư tiền gửi còn lại": 0.0
            })

    total_amount = principal + total_interest
    df_schedule = pd.DataFrame(schedule_data)

    return periodic_interest, periodic_label, total_interest, total_amount, df_schedule

st.markdown('<div class="main-header">🏦 Ứng Dụng Tính Lãi Gửi Tiết Kiệm</div>', unsafe_allow_html=True)
st.markdown('<div class="sub-header">Mô phỏng chính xác tiền lãi định kỳ, tổng tiền lãi và lịch dòng tiền nhận lãi ngân hàng.</div>', unsafe_allow_html=True)

# Khung nhập liệu ở Sidebar
with st.sidebar:
    st.header("⚙️ Thông Tin Gửi Tiết Kiệm")

    # 1. Số tiền gửi
    st.subheader("1. Số tiền gốc")
    quick_amount = st.selectbox(
        "Chọn nhanh số tiền (VNĐ):",
        options=[
            "Tùy nhập",
            "50.000.000 đ",
            "100.000.000 đ",
            "200.000.000 đ",
            "500.000.000 đ",
            "1.000.000.000 đ"
        ],
        index=2
    )

    preset_map = {
        "50.000.000 đ": 50_000_000,
        "100.000.000 đ": 100_000_000,
        "200.000.000 đ": 200_000_000,
        "500.000.000 đ": 500_000_000,
        "1.000.000.000 đ": 1_000_000_000,
    }

    if quick_amount == "Tùy nhập":
        principal_input = st.number_input(
            "Nhập số tiền gửi (VNĐ):",
            min_value=1_000_000,
            max_value=100_000_000_000,
            value=100_000_000,
            step=5_000_000,
            format="%d"
        )
    else:
        principal_input = preset_map[quick_amount]
        st.write(f"Số tiền đã chọn: **{format_vnd(principal_input)}**")

    # 2. Kỳ hạn gửi
    st.subheader("2. Kỳ hạn gửi")
    term_type = st.radio("Cách chọn kỳ hạn:", ["Kỳ hạn tiêu chuẩn", "Nhập tháng tùy chọn"], horizontal=True)

    if term_type == "Kỳ hạn tiêu chuẩn":
        term_options = [1, 2, 3, 6, 9, 12, 18, 24, 36]
        term_months = st.selectbox(
            "Chọn kỳ hạn (tháng):",
            options=term_options,
            index=5  # Mặc định 12 tháng
        )
    else:
        term_months = st.number_input("Nhập số tháng gửi:", min_value=1, max_value=120, value=12, step=1)

    # 3. Lãi suất
    st.subheader("3. Lãi suất")
    annual_rate = st.number_input(
        "Lãi suất (% / năm):",
        min_value=0.1,
        max_value=25.0,
        value=5.6,
        step=0.1,
        format="%.2f"
    )

    # 4. Hình thức nhận lãi
    st.subheader("4. Hình thức nhận lãi")
    payout_method = st.selectbox(
        "Phương thức trả lãi:",
        options=["Cuối kỳ", "Hàng tháng", "Hàng quý"],
        index=0
    )

    # 5. Ngày bắt đầu gửi
    start_date = st.date_input("Ngày bắt đầu gửi:", value=datetime.date.today())

periodic_interest, periodic_label, total_interest, total_amount, df_schedule = calculate_savings(
    principal=principal_input,
    term_months=term_months,
    annual_rate=annual_rate,
    payout_method=payout_method,
    start_date=start_date
)

col1, col2, col3, col4 = st.columns(4)

with col1:
    st.markdown(f"""
    <div class="metric-card">
        <div class="metric-title">Tiền Gốc Ban Đầu</div>
        <div class="metric-value">{format_vnd(principal_input)}</div>
        <div class="metric-sub">Kỳ hạn: {term_months} tháng</div>
    </div>
    """, unsafe_allow_html=True)

with col2:
    st.markdown(f"""
    <div class="metric-card">
        <div class="metric-title">Tiền Lãi Định Kỳ</div>
        <div class="metric-value" style="color: #059669;">{format_vnd(periodic_interest)}</div>
        <div class="metric-sub">{periodic_label}</div>
    </div>
    """, unsafe_allow_html=True)

with col3:
    st.markdown(f"""
    <div class="metric-card">
        <div class="metric-title">Tổng Tiền Lãi</div>
        <div class="metric-value" style="color: #D97706;">{format_vnd(total_interest)}</div>
        <div class="metric-sub">Lãi suất: {annual_rate:.2f}% / năm</div>
    </div>
    """, unsafe_allow_html=True)

with col4:
    st.markdown(f"""
    <div class="metric-card">
        <div class="metric-title">Tổng Gốc + Lãi</div>
        <div class="metric-value" style="color: #7C3AED;">{format_vnd(total_amount)}</div>
        <div class="metric-sub">Hình thức: {payout_method}</div>
    </div>
    """, unsafe_allow_html=True)

st.write("---")
tab_summary, tab_schedule, tab_formula = st.tabs(["📊 Tổng Quan & Phân Bổ", "📅 Lịch Chi Tiết Dòng Tiền", "📖 Công Thức & Lưu Ý"])

with tab_summary:
    col_chart1, col_chart2 = st.columns([1, 1])

    with col_chart1:
        st.subheader("Cơ cấu Tổng tiền nhận được")
        pie_df = pd.DataFrame({
            "Khoản mục": ["Tiền gốc", "Tổng tiền lãi"],
            "Số tiền": [principal_input, total_interest]
        })
        st.bar_chart(data=pie_df.set_index("Khoản mục"), y="Số tiền", color="#1D4ED8")
        
        profit_percent = (total_interest / principal_input) * 100
        st.info(f"💡 Tỷ suất sinh lời trên vốn gốc sau **{term_months} tháng** là: **{profit_percent:.2f}%**")

    with col_chart2:
        st.subheader("Thông tin tóm tắt khoản gửi")
        end_date = start_date + relativedelta(months=term_months)
        summary_rows = [
            ("Số tiền gốc gửi", format_vnd(principal_input)),
            ("Kỳ hạn tiết kiệm", f"{term_months} tháng"),
            ("Lãi suất áp dụng", f"{annual_rate:.2f}% / năm"),
            ("Hình thức nhận lãi", payout_method),
            ("Ngày gửi", start_date.strftime("%d/%m/%Y")),
            ("Ngày đáo hạn", end_date.strftime("%d/%m/%Y")),
            ("Tiền lãi định kỳ", f"{format_vnd(periodic_interest)} ({periodic_label})"),
            ("Tổng lãi nhận được", format_vnd(total_interest)),
            ("Tổng số tiền nhận về", format_vnd(total_amount))
        ]
        summary_df = pd.DataFrame(summary_rows, columns=["Chỉ tiêu", "Giá trị"])
        st.table(summary_df)

with tab_schedule:
    st.subheader(f"Lịch chi trả tiền lãi ({len(df_schedule)} kỳ nhận)")
    
    # Hiển thị bảng định dạng tiền VND
    df_display = df_schedule.copy()
    for col in ["Tiền lãi định kỳ", "Tiền gốc nhận lại", "Tổng thực nhận kỳ này", "Số dư tiền gửi còn lại"]:
        df_display[col] = df_display[col].apply(format_vnd)

    st.dataframe(df_display, use_container_width=True, hide_index=True)

    # Nút tải file bảng biểu CSV
    csv_data = df_schedule.to_csv(index=False).encode('utf-8-sig')
    st.download_button(
        label="📥 Tải lịch trả lãi về máy (.CSV)",
        data=csv_data,
        file_name=f"lich_tra_lai_{principal_input}_{term_months}thang.csv",
        mime="text/csv"
    )

with tab_formula:
    st.subheader("Công thức tính lãi suất ngân hàng hiện hành")
    st.markdown("""
    **1. Nhận lãi cuối kỳ:**
    $$\\text{Tiền lãi} = \\frac{\\text{Số tiền gửi} \\times \\text{Lãi suất (\\%/năm)} \\times \\text{Số tháng gửi}}{12}$$

    **2. Nhận lãi hàng tháng:**
    $$\\text{Lãi mỗi tháng} = \\frac{\\text{Số tiền gửi} \\times \\text{Lãi suất (\\%/năm)}}{12}$$
    $$\\text{Tổng lãi} = \\text{Lãi mỗi tháng} \\times \\text{Số tháng gửi}$$

    **3. Nhận lãi hàng quý (3 tháng/lần):**
    $$\\text{Lãi mỗi quý} = \\frac{\\text{Số tiền gửi} \\times \\text{Lãi suất (\\%/năm)} \\times 3}{12}$$

    *Lưu ý:* Thông thường ở các ngân hàng thương mại, cùng một kỳ hạn thì phương thức nhận lãi **hàng tháng** hoặc **hàng quý** sẽ có lãi suất công bố thấp hơn so với nhận lãi **cuối kỳ**.
    """)
