import plotly.graph_objects as go

def candlestick_chart(df, title="Candlestick"):
    fig=go.Figure(data=[go.Candlestick(x=df.index,open=df.Open,high=df.High,low=df.Low,close=df.Close)])
    fig.update_layout(title=title, xaxis_rangeslider_visible=False, height=650)
    return fig
