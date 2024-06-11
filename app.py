import streamlit as st
import plotly.express as px
import plotly.graph_objects as go
import pandas as pd
import json

# Import data
with open('data_cache/Indonesia_provinces.geojson', 'r') as geojson_file:
    geojson_data = json.load(geojson_file)

shipping = pd.read_pickle('data_input/shipping_clean')

# Menghitung Total Pesanan
total_pesanan = shipping['order_id'].count()

# Menghitung Completed rate
completed_rate = (shipping[shipping['status'] == 'Completed']['order_id'].count() / total_pesanan)*100

# Menghitung Rata-rata Waktu Pengiriman
delivery_time = shipping['day_to_arv'].mean()

# Plotly figures
province_data = shipping.pivot_table(
    index='province',
    values='order_id',
    aggfunc='count'
).reset_index()

fig_map = px.choropleth(province_data,
                   geojson=geojson_data,
                   locations='province',
                   color='order_id',
                   color_continuous_scale=['#ffc107', '#fd7e14', '#dc3545', '#e83e8c', '#6f42c1'],
                   featureidkey='properties.NAME_1',
                   title='Peta Pengiriman Paket Ke Seluruh Provinsi di Indonesia',
                   hover_name='province',
                   template='plotly_white',
                   projection='equirectangular',
                   labels={'order_id': 'Jumlah Pesanan',
                           'province': 'Provinsi'}
                   )

fig_map = fig_map.update_geos(fitbounds='locations', visible=False)

# Donut chart
ship_mode = shipping.pivot_table(
    index='ship_mode',
    values='order_id',
    aggfunc='count'
).reset_index()

fig_donut = px.pie(
    ship_mode,
    values = 'order_id',
    names = 'ship_mode',
    hole = 0.4,
    color_discrete_sequence=['#ffc107', '#e83e8c', '#6f42c1'],
    title = 'Jumlah Pengiriman Disetiap Status Pengiriman',
    labels = {
        'ship_mode': 'Mode Pengiriman',
        'order_id': 'Jumlah Pengiriman'
    },
    template = 'plotly_white',
)

# Streamlit layout

st.set_page_config(page_title='Dashboard Pengiriman COD', page_icon='📦')
st.title('Dashboard Pengiriman COD 📦')

st.markdown('---')
# Choropleth map
st.header('Peta Pengiriman Paket 📍')
st.plotly_chart(fig_map)

st.markdown('---')

# Layout with two columns
col1, col2 = st.columns(2)

with col1:
    # Info cards
    # st.header('Informasi Pengiriman')
    # st.info(f"### Total Pengiriman\n{total_pesanan:,}")
    # st.info(f"### Persentase Pengiriman Selesai\n{completed_rate:.2f}%")
    # st.info(f"### Rata-rata Waktu Pengiriman\n{delivery_time:.0f} hari")

    
    st.markdown(f"""
        <div style="padding: 10px; border-radius: 5px; background-color: #f1f3f4;">
            <p>Total Pengiriman</p>
            <h3>{total_pesanan:,}</h3>
        </div>
        <br>
        """, unsafe_allow_html=True)


    st.markdown(f"""
        <div style="padding: 10px; border-radius: 5px; background-color: #f1f3f4;">
            <p>Persentase Pengiriman Selesai</p>
            <h3>{completed_rate:.2f}%</h3>
        </div>
        <br>
        """, unsafe_allow_html=True)

    st.markdown(f"""
        <div style="padding: 10px; border-radius: 5px; background-color: #f1f3f4;">
            <p>Rata-rata Waktu Pengiriman</p>
            <h3>{delivery_time:.0f} hari</h3>
        </div>
        """, unsafe_allow_html=True)

with col2:
    # st.header('Analisis Mode Pengiriman')
    st.plotly_chart(fig_donut)

st.markdown('---')


# Tabs for lineplot and heatmap
st.header('Pergerakan Harian dan Jumlah Pengiriman Harian')
selected_mode = st.selectbox('Pilih Mode Pengiriman', options=shipping['ship_mode'].unique())
tab1, tab2 = st.tabs(['📈 Pergerakan Harian', '📋 Jumlah Pengiriman Harian'])

with tab1:
    # Update line plot
    standard = shipping[shipping['ship_mode'] == selected_mode]
    line_agg = standard.pivot_table(
        index='creation_date',
        values='order_id',
        aggfunc='count'
    ).reset_index()
    fig_line = px.line(
        line_agg,
        x = 'creation_date',
        y = 'order_id',
        color_discrete_sequence=['#6f42c1'],
        title = 'Pergerakan Pengiriman Paket Harian',
        template='plotly_white',
        labels = {
            'order_id': 'Jumlah Pengiriman',
            'creation_date': ''
        }
    )
    st.plotly_chart(fig_line)

with tab2:
    # Update heatmap
    data_agg1 = standard.pivot_table(
        values='order_id',
        index='order_day',
        columns='order_hour',
        aggfunc='count',
    ).reindex(['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday'])
    fig_heatmap = px.imshow(
        data_agg1,
        color_continuous_scale=['#ffc107', '#fd7e14', '#dc3545', '#e83e8c', '#6f42c1'],
        template='plotly_white',
        title='Jumlah Pengiriman Harian'
    )
    fig_heatmap.update_xaxes(title_text='Waktu Pesanan', dtick=1)
    fig_heatmap.update_yaxes(title_text='Hari Pesanan')
    st.plotly_chart(fig_heatmap)
