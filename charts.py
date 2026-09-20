import plotly.graph_objects as go

DEFAULT_GOOD_COLOR = "#2ECC71"
DEFAULT_BAD_COLOR = "#E74C3C"


def _dark_layout(fig, height=350):
    fig.update_layout(
        paper_bgcolor='rgba(0,0,0,0)',
        plot_bgcolor='rgba(0,0,0,0)',
        font=dict(color='white'),
        height=height,
        margin=dict(l=30, r=30, t=40, b=30),
    )
    return fig


def build_weekly_pie_chart(week_data: dict, good_color: str = DEFAULT_GOOD_COLOR, bad_color: str = DEFAULT_BAD_COLOR):
    good = week_data["good_count"]
    bad = week_data["bad_count"]

    if good == 0 and bad == 0:
        good, bad = 1, 1

    fig = go.Figure(data=[go.Pie(
        labels=["Good", "Bad"],
        values=[good, bad],
        marker=dict(colors=[good_color, bad_color]),
        hole=0.4,
        textinfo="label+percent",
    )])
    fig.update_layout(title=f"Week of {week_data['week_start'].strftime('%d %b %Y')}")
    return _dark_layout(fig)


def build_weekly_bar_chart(weekly_summary: list[dict], good_color: str = DEFAULT_GOOD_COLOR, bad_color: str = DEFAULT_BAD_COLOR):
    week_labels = [w["week_start"].strftime("%d %b") for w in weekly_summary]
    good_counts = [w["good_count"] for w in weekly_summary]
    bad_counts = [w["bad_count"] for w in weekly_summary]

    fig = go.Figure()
    fig.add_trace(go.Bar(x=week_labels, y=good_counts, name="Good", marker_color=good_color))
    fig.add_trace(go.Bar(x=week_labels, y=bad_counts, name="Bad", marker_color=bad_color))

    fig.update_layout(
        barmode="group",
        xaxis_title="Week",
        yaxis_title="Count",
        legend=dict(orientation="h", yanchor="bottom", y=1.02),
    )
    return _dark_layout(fig)


def build_monthly_line_chart(daily_scores: list[dict], line_color: str = "#7C4DFF"):
    dates = [d["date"] for d in daily_scores]
    overalls = [d["overall"] for d in daily_scores]

    fig = go.Figure()
    fig.add_trace(go.Scatter(
        x=dates,
        y=overalls,
        mode="lines+markers",
        line=dict(color=line_color, width=2),
        marker=dict(size=6),
        connectgaps=False,
    ))

    fig.update_layout(
        xaxis_title="Date",
        yaxis_title="Daily Score (%)",
        yaxis=dict(range=[0, 100]),
    )
    return _dark_layout(fig, height=380)