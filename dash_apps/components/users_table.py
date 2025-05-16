from dash import dash_table

KLANDO_RED = "#730200"
KLANDO_BLUEGREY = "#3a4654"

def render_users_table(users_df, columns=None):
    display_columns = [col for col in users_df.columns]
    if columns is None:
        columns = [{"name": col, "id": col} for col in display_columns]
    return dash_table.DataTable(
        id="users-table",
        columns=columns,
        data=users_df.to_dict("records"),
        filter_action='native',
        sort_action='native',
        row_selectable="single",
        selected_rows=[],
        style_table={
            "overflowX": "auto",
            "borderRadius": "10px",
            "border": f"1px solid {KLANDO_BLUEGREY}",
            "marginTop": "10px"
        },
        style_cell={
            "textAlign": "left",
            "fontSize": 14,
            "fontFamily": "Gliker, Arial, sans-serif",
            "color": KLANDO_BLUEGREY,
            "backgroundColor": "#f9f9f9",
            "padding": "8px"
        },
        style_header={
            "backgroundColor": KLANDO_BLUEGREY,
            "color": "white",
            "fontWeight": "bold",
            "fontSize": 16,
            "border": "none",
            "fontFamily": "Gliker, Arial, sans-serif"
        },
        style_data_conditional=[
            {
                "if": {"row_index": "odd"},
                "backgroundColor": "#f1f3fa"
            },
            {
                "if": {"state": "selected"},
                "backgroundColor": KLANDO_RED,
                "color": "white",
                "fontWeight": "bold"
            }
        ],
        page_size=20
    )
