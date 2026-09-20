import plotly.graph_objects as go

def _hex_to_rgba(hex_color: str, alpha: float) -> str:
    hex_color = hex_color.lstrip('#')
    r, g, b = int(hex_color[0:2], 16), int(hex_color[2:4], 16), int(hex_color[4:6], 16)
    return f'rgba({r}, {g}, {b}, {alpha})'

def build_radar_chart(categories: list[dict], color: str = "#7C4DFF"):
    """
    Builds a single combined radar/spider chart from the user's categories.
    """
    names = [c["name"] for c in categories]
    scores = [c["score"] for c in categories]
    types = [c["type"] for c in categories]

    names_closed = names + [names[0]] if names else []
    scores_closed = scores + [scores[0]] if scores else []

    hover_text = [
        f"{n} ({'Good' if t == 'good' else 'Bad'}): {s:.0f}%"
        for n, s, t in zip(names, scores, types)
    ]
    hover_text_closed = hover_text + [hover_text[0]] if hover_text else []

    fig = go.Figure()

    fig.add_trace(go.Scatterpolar(
        r=scores_closed,
        theta=names_closed,
        fill='toself',
       fillcolor=_hex_to_rgba(color, 0.3),
        line=dict(color=color, width=2),
        marker=dict(size=8, color=color),
        hovertext=hover_text_closed,
        hoverinfo='text',
        name='Your Axis'
    ))

    fig.update_layout(
        polar=dict(
            bgcolor='rgba(0,0,0,0)',
            radialaxis=dict(
                visible=True,
                range=[0, 100],
                showticklabels=False,
                gridcolor='rgba(255,255,255,0.15)',
            ),
            angularaxis=dict(
                gridcolor='rgba(255,255,255,0.15)',
                tickfont=dict(color='white', size=13),
            ),
        ),
        showlegend=False,
        paper_bgcolor='rgba(0,0,0,0)',
        plot_bgcolor='rgba(0,0,0,0)',
        font=dict(color='white'),
        margin=dict(l=40, r=40, t=40, b=40),
        height=450,
    )

    return fig