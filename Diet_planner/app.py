import dash
from dash import dcc
from dash import html
from dash.dependencies import Input, Output, State
import dash_bootstrap_components as dbc
import os
from dotenv import load_dotenv
import traceback
import re
import plotly.graph_objects as go
from datetime import datetime
import time
from crewai import Crew, Process


from agents.meal_planner_agent import meal_planner_agent, generate_meal_plan_task, prepare_inputs
from agents.tracker_agent import tracker_agent, track_progress_task
from agents.motivation_agent import motivation_agent, motivate_user_task

load_dotenv(dotenv_path="./.env")

app = dash.Dash(__name__,
                external_stylesheets=[dbc.themes.BOOTSTRAP],
                suppress_callback_exceptions=True,
                meta_tags=[{'name': 'viewport',
                            'content': 'width=device-width, initial-scale=1.0'}])
server = app.server 


PAGE_ORDER = ['/', '/meal-planner', '/tracker', '/motivation']


def create_nav_buttons(current_path):
    current_index = PAGE_ORDER.index(current_path)
    buttons = []

    if current_index > 0:
        buttons.append(
            dbc.Button("السابق", id="prev-page-button", color="secondary", className="me-2")
        )

    if current_index < len(PAGE_ORDER) - 1:
        buttons.append(
            dbc.Button("التالي", id="next-page-button", color="primary", className="ms-2")
        )

    if current_path == '/motivation':
        buttons.append(
            dcc.Link(dbc.Button("الذهاب للقائمة الرئيسية", color="info", className="ms-auto"), href="/")
        )

    return html.Div(buttons, className="d-flex justify-content-between mt-4 navigation-buttons-container")


CONTAINER_STYLE = {
    'background-color': 'rgba(255, 255, 255, 0.9)',
    'border-radius': '15px',
    'padding': '30px',
    'box-shadow': '0 4px 12px rgba(0,0,0,0.15)',
    'margin': 'auto',
    'max-width': '950px',
    'min-height': 'calc(100vh - 80px)',
    'display': 'flex',
    'flex-direction': 'column',
    'justify-content': 'flex-start',
    'align-items': 'center',
    'text-align': 'right',
    'direction': 'rtl',
    'gap': '20px'
}

PAGE_BACKGROUND_STYLE = {
    'min-height': '100vh',
    'padding': '20px',
    'direction': 'rtl',
    'text-align': 'right',
    'display': 'flex',
    'justify-content': 'center',
    'align-items': 'flex-start',
}



def get_main_layout():
    return html.Div(
        style=PAGE_BACKGROUND_STYLE,
        children=[
            dbc.Container(
                style=CONTAINER_STYLE,
                children=[
                    html.H1("مرحباً بك في مساعد النظام الغذائي", className="text-center my-4", id="welcome-message"),
                    html.Hr(style={'border-top': '1px solid rgba(255,255,255,0.5)'}),

                    dbc.Row([
                        dbc.Col(
                            dbc.Card(
                                dbc.CardBody([
                                    html.H3("تخطيط الوجبات", className="card-title text-primary"),
                                    html.P("احصل على خطة وجبات مخصصة بناءً على أهدافك واحتياجاتك الصحية.", className="card-text"),
                                    dcc.Link(
                                        dbc.Button("اذهب إلى مخطط الوجبات", color="primary", className="mt-3"),
                                        href="/meal-planner"
                                    )
                                ]),
                                className="mb-4",
                                style={'background-color': 'rgba(255,255,255,0.7)', 'border-radius': '10px'}
                            ),
                            md=4
                        ),
                        dbc.Col(
                            dbc.Card(
                                dbc.CardBody([
                                    html.H3("تقييم الالتزام", className="card-title text-success"),
                                    html.P("قيّم مدى التزامك بخطتك الغذائية اليومية.", className="card-text"),
                                    dcc.Link(
                                        dbc.Button("اذهب إلى التقييم", color="success", className="mt-3"),
                                        href="/tracker"
                                    )
                                ]),
                                className="mb-4",
                                style={'background-color': 'rgba(255,255,255,0.7)', 'border-radius': '10px'}
                            ),
                            md=4
                        ),
                        dbc.Col(
                            dbc.Card(
                                dbc.CardBody([
                                    html.H3("التحفيز", className="card-title text-info"),
                                    html.P("احصل على تحفيز ونصائح لمواصلة رحلتك الصحية.", className="card-text"),
                                    dcc.Link(
                                        dbc.Button("اذهب إلى التحفيز", color="info", className="mt-3"),
                                        href="/motivation"
                                    )
                                ]),
                                className="mb-4",
                                style={'background-color': 'rgba(255,255,255,0.7)', 'border-radius': '10px'}
                            ),
                            md=4
                        )
                    ]),
                    html.Div([
                        html.H3("تقريرك الشامل", className="text-center my-4"),
                        dbc.Button("تحميل تقرير شامل (HTML)", id="download-report-button", color="warning", className="w-100 mb-4"),
                        dcc.Download(id="download-html-report"),
                        html.Div(id="download-report-status",
                                     style={'color': 'white', 'text-align': 'center', 'margin-top': '10px'})
                    ], style={'background-color': 'rgba(0,0,0,0.4)', 'padding': '20px', 'border-radius': '10px'}),
                ]
            )
        ]
    )


meal_planner_layout = html.Div(
    style=PAGE_BACKGROUND_STYLE,
    children=[
        dbc.Container(
            style=CONTAINER_STYLE,
            children=[
                html.H2("تخطيط الوجبات", className="text-center my-4"),
                dbc.Card(
                    dbc.CardBody([
                        dbc.Form([
                            dbc.Row([
                                dbc.Col(dbc.Label("الاسم:", className="form-group"), width=3),
                                dbc.Col(dbc.Input(id="name-input", type="text", placeholder="أدخل اسمك", className="form-control"), width=9)
                            ], className="mb-3"),
                            dbc.Row([
                                dbc.Col(dbc.Label("الوزن (كجم):", className="form-group"), width=3),
                                dbc.Col(dbc.Input(id="weight-input", type="number", placeholder="مثال: 75", className="form-control"), width=9)
                            ], className="mb-3"),
                            dbc.Row([
                                dbc.Col(dbc.Label("الطول (سم):", className="form-group"), width=3),
                                dbc.Col(dbc.Input(id="height-input", type="number", placeholder="مثال: 170", className="form-control"), width=9)
                            ], className="mb-3"),
                            dbc.Row([
                                dbc.Col(dbc.Label("العمر:", className="form-group"), width=3),
                                dbc.Col(dbc.Input(id="age-input", type="number", placeholder="مثال: 30", className="form-control"), width=9)
                            ], className="mb-3"),
                            dbc.Row([
                                dbc.Col(dbc.Label("الجنس:", className="form-group"), width=3),
                                dbc.Col(dcc.Dropdown(
                                    id="sex-input",
                                    options=[
                                        {'label': 'ذكر', 'value': 'ذكر'},
                                        {'label': 'أنثى', 'value': 'أنثى'}
                                    ],
                                    placeholder="اختر الجنس",
                                    className="dash-dropdown"
                                ), width=9)
                            ], className="mb-3"),
                            dbc.Row([
                                dbc.Col(dbc.Label("مستوى النشاط:", className="form-group"), width=3),
                                dbc.Col(dcc.Dropdown(
                                    id="activity-level-input",
                                    options=[
                                        {'label': 'كسول', 'value': 'كسول'},
                                        {'label': 'خفيف', 'value': 'خفيف'},
                                        {'label': 'متوسط', 'value': 'متوسط'},
                                        {'label': 'نشط', 'value': 'نشط'},
                                        {'label': 'نشط جدًا', 'value': 'نشط جدًا'}
                                    ],
                                    placeholder="اختر مستوى النشاط",
                                    className="dash-dropdown"
                                ), width=9)
                            ], className="mb-3"),
                            dbc.Row([
                                dbc.Col(dbc.Label("الهدف:", className="form-group"), width=3),
                                dbc.Col(dcc.Dropdown(
                                    id="goal-input",
                                    options=[
                                        {'label': 'فقدان الوزن', 'value': 'فقدان الوزن'},
                                        {'label': 'زيادة الوزن', 'value': 'زيادة الوزن'},
                                        {'label': 'الحفاظ على الوزن', 'value': 'الحفاظ على الوزن'}
                                    ],
                                    placeholder="اختر الهدف",
                                    className="dash-dropdown"
                                ), width=9)
                            ], className="mb-3"),
                            dbc.Row([
                                dbc.Col(dbc.Label("نوع النظام الغذائي:", className="form-group"), width=3),
                                dbc.Col(dbc.Input(id="diet-type-input", type="text", placeholder="مثال: عادي، كيتو، نباتي", className="form-control"), width=9)
                            ], className="mb-3"),
                            dbc.Row([
                                dbc.Col(dbc.Label("الحساسيات الغذائية (افصل بفاصلة):", className="form-group"), width=3),
                                dbc.Col(dbc.Input(id="allergy-input", type="text", placeholder="مثال: جلوتين، لاكتوز", className="form-control"), width=9)
                            ], className="mb-3"),
                            dbc.Row([
                                dbc.Col(dbc.Label("الحالات الطبية (افصل بفاصلة):", className="form-group"), width=3),
                                dbc.Col(dbc.Input(id="conditions-input", type="text", placeholder="مثال: سكري، ضغط", className="form-control"), width=9)
                            ], className="mb-3"),
                            dbc.Button("توليد خطة الوجبات", id="generate-meal-plan-button", color="primary", className="mt-3 w-100")
                        ]),
                        html.Hr(),
                        html.Div(id="meal-plan-output", style={'white-space': 'pre-wrap', 'direction': 'rtl', 'text-align': 'right', 'color': '#333'}),
                        html.Div(id="meal-plan-error-output", style={'color': 'red', 'white-space': 'pre-wrap', 'direction': 'rtl', 'text-align': 'right', 'marginTop': '10px'})
                    ]),
                    style={'background-color': 'rgba(255,255,255,0.85)', 'border-radius': '10px'}
                ),
                create_nav_buttons('/meal-planner')
            ])
        ]
    )


tracker_layout = html.Div(
    style=PAGE_BACKGROUND_STYLE,
    children=[
        dbc.Container(
            style=CONTAINER_STYLE,
            children=[
                html.H2("تقييم الالتزام", className="text-center my-4"),
                dbc.Card(
                    dbc.CardBody([
                        dbc.Label("الخطة الغذائية المقترحة (ملخص):", className="form-group"),
                        dcc.Textarea(id="planned-meal-input", style={'width': '100%', 'height': 150}, placeholder="سيتم ملء الخطة الغذائية المقترحة تلقائيًا هنا.", className="dcc-textarea"),
                        dbc.Label("ما تم تناوله فعليًا خلال اليوم:", className="form-group"),
                        dcc.Textarea(id="eaten-meal-input", style={'width': '100%', 'height': 150}, placeholder="اذكر ما تناولته فعليًا خلال اليوم (مثال: إفطار: بيض، غداء: دجاج وأرز...).", className="dcc-textarea"),
                        dbc.Label("العوامل الخارجية التي أثرت على التزامك (اختياري):", className="form-group"),
                        dcc.Textarea(id="external-factors-input", style={'width': '100%', 'height': 100}, placeholder="مثال: ضغط عمل، مناسبات اجتماعية...", className="dcc-textarea"),
                        dbc.Button("تقييم الالتزام", id="evaluate-commitment-button", color="success", className="mt-3 w-100")
                    ]),
                    style={'background-color': 'rgba(255,255,255,0.85)', 'border-radius': '10px'}
                ),
                html.Hr(),
                dcc.Graph(id='commitment-pie-chart', config={'displayModeBar': False}),
                html.Div(id="tracker-output", style={'white-space': 'pre-wrap', 'direction': 'rtl', 'text-align': 'center', 'color': '#333', 'font-size': '1.8em', 'font-weight': 'bold', 'marginTop': '10px'}),
                html.Div(id="tracker-error-output", style={'color': 'red', 'white-space': 'pre-wrap', 'direction': 'rtl', 'text-align': 'right', 'marginTop': '10px'}),
                create_nav_buttons('/tracker')
            ]),
        ]
    )


motivation_layout = html.Div(
    style=PAGE_BACKGROUND_STYLE,
    children=[
        dbc.Container(
            style=CONTAINER_STYLE,
            children=[
                html.H2("التحفيز", className="text-center my-4"),
                dbc.Card(
                    dbc.CardBody([
                        dbc.Button("احصل على تحفيز", id="get-motivation-button", color="info", className="mt-3 w-100"),
                        html.Hr(),
                        html.Div(id="motivation-output", style={'white-space': 'pre-wrap', 'direction': 'rtl', 'text-align': 'right', 'color': '#333'}),
                        html.Div(id="motivation-error-output", style={'color': 'red', 'white-space': 'pre-wrap', 'direction': 'rtl', 'text-align': 'right', 'marginTop': '10px'})
                    ]),
                    style={'background-color': 'rgba(255,255,255,0.85)', 'border-radius': '10px'}
                ),
                create_nav_buttons('/motivation')
            ])
        ]
    )


app.layout = html.Div([
    dcc.Location(id='url', refresh=False),
    dcc.Store(id='meal-plan-data-store', data={}),
    dcc.Store(id='tracker-summary-store', data={'summary': '', 'commitment_percentage': 0}),
    dcc.Store(id='user-inputs-store', data={}),
    dcc.Store(id='motivation-data-store', data={}),
    html.Div(id='page-content'),
])

# Callbacks
@app.callback(
    Output('page-content', 'children'),
    [Input('url', 'pathname')]
)
def display_page(pathname):
    if pathname == '/meal-planner':
        return meal_planner_layout
    elif pathname == '/tracker':
        return tracker_layout
    elif pathname == '/motivation':
        return motivation_layout
    else:
        return get_main_layout()

@app.callback(
    Output('welcome-message', 'children'),
    [Input('user-inputs-store', 'data')]
)
def update_welcome_message(user_data):
    name = user_data.get('name') if user_data and user_data.get('name') else 'الزائر'
    return f"مرحباً بك يا {name} في مساعد النظام الغذائي"

@app.callback(
    Output('url', 'pathname', allow_duplicate=True),
    [Input('next-page-button', 'n_clicks')],
    [State('url', 'pathname'),
     State('user-inputs-store', 'data'),
     State('meal-plan-data-store', 'data')],
    prevent_initial_call=True
)
def navigate_next(n_clicks, current_path, user_data, meal_data):
    if not n_clicks: return dash.no_update
    if current_path == '/meal-planner':
        required_fields = ["weight", "height", "age", "sex", "activity_level", "goal"]
        if not user_data: return dash.no_update
        missing_fields = [field for field in required_fields if not user_data.get(field)]
        if missing_fields: return f"الحقول التالية مطلوبة: {', '.join(missing_fields)}"
        if not meal_data or 'meal_plan_text' not in meal_data: return "يجب توليد خطة الوجبات أولاً"
    current_index = PAGE_ORDER.index(current_path)
    if current_index < len(PAGE_ORDER) - 1:
        time.sleep(0.3)
        return PAGE_ORDER[current_index + 1]
    return dash.no_update

@app.callback(
    Output('url', 'pathname', allow_duplicate=True),
    [Input('prev-page-button', 'n_clicks')],
    [State('url', 'pathname')],
    prevent_initial_call=True
)
def navigate_prev(n_clicks, current_path):
    if n_clicks:
        current_index = PAGE_ORDER.index(current_path)
        if current_index > 0: return PAGE_ORDER[current_index - 1]
    return dash.no_update

@app.callback(
    Output('meal-plan-error-output', 'children', allow_duplicate=True),
    [Input('next-page-button', 'n_clicks')],
    [State('url', 'pathname'),
     State('user-inputs-store', 'data'),
     State('meal-plan-data-store', 'data')],
    prevent_initial_call=True
)
def show_navigation_errors(n_clicks, current_path, user_data, meal_data):
    if n_clicks and current_path == '/meal-planner':
        required_fields = ["weight", "height", "age", "sex", "activity_level", "goal"]
        if not user_data: return "الرجاء ملء جميع البيانات الأساسية"
        missing_fields = [field for field in required_fields if not user_data.get(field)]
        if missing_fields: return f"الحقول التالية مطلوبة: {', '.join(missing_fields)}"
        if not meal_data or 'meal_plan_text' not in meal_data: return "يجب توليد خطة الوجبات أولاً"
    return ""

@app.callback(
    Output('user-inputs-store', 'data'),
    [Input(f"{field}-input", "value") for field in [
        "name", "weight", "height", "age", "sex",
        "activity-level", "goal", "diet-type",
        "allergy", "conditions"
    ]],
    [State('user-inputs-store', 'data')]
)
def update_user_data(name, weight, height, age, sex, activity, goal, diet, allergy, conditions, current):
    updated = current.copy() if current else {}
    if name is not None: updated['name'] = name
    if weight is not None: updated['weight'] = weight
    if height is not None: updated['height'] = height
    if age is not None: updated['age'] = age
    if sex is not None: updated['sex'] = sex
    if activity is not None: updated['activity_level'] = activity
    if goal is not None: updated['goal'] = goal
    if diet is not None: updated['diet_type'] = diet or "عادي"
    if allergy is not None: updated['allergy'] = allergy or "لا يوجد"
    if conditions is not None: updated['conditions'] = conditions or "لا يوجد"
    return updated

@app.callback(
    [Output("meal-plan-output", "children"),
     Output("meal-plan-data-store", "data"),
     Output("meal-plan-error-output", "children")],
    [Input("generate-meal-plan-button", "n_clicks")],
    [State(f"{field}-input", "value") for field in [
        "name", "weight", "height", "age", "sex",
        "activity-level", "goal", "diet-type",
        "allergy", "conditions"
    ]],
    prevent_initial_call=True
)
def generate_meal_plan(n_clicks, name, weight, height, age, sex, activity_level, goal, diet_type, allergy, conditions):
    if not n_clicks: return dash.no_update, dash.no_update, dash.no_update
    required_fields = ["weight", "height", "age", "sex", "activity_level", "goal"]
    user_inputs = {
        "name": name if name else "الزائر", "weight": weight, "height": height, "age": age, "sex": sex,
        "activity_level": activity_level, "goal": goal, "diet_type": diet_type if diet_type else "عادي",
        "allergy": allergy if allergy else "لا يوجد", "conditions": conditions if conditions else "لا يوجد"
    }
    if not all(user_inputs.get(field) for field in required_fields):
        return "", {}, "الرجاء ملء جميع البيانات الأساسية (الوزن، الطول، العمر، الجنس، مستوى النشاط، الهدف)"
    try:
        prepared_inputs = prepare_inputs(user_inputs)
        meal_planner_crew = Crew(
            agents=[meal_planner_agent], tasks=[generate_meal_plan_task], process=Process.sequential, verbose=False
        )
        meal_plan_result = meal_planner_crew.kickoff(inputs=prepared_inputs)
        meal_plan_data = {
            'meal_plan_text': meal_plan_result.raw, 'user_inputs': user_inputs, 'timestamp': datetime.now().isoformat()
        }
        return meal_plan_result.raw, meal_plan_data, ""
    except Exception as e:
        error_msg = f"حدث خطأ أثناء توليد خطة الوجبات: {str(e)}"
        traceback.print_exc()
        return "", {}, error_msg

@app.callback(
    Output("meal-plan-output", "children", allow_duplicate=True),
    [Input("meal-plan-data-store", "data")],
    prevent_initial_call=True
)
def update_meal_plan_display(stored_data):
    if stored_data and 'meal_plan_text' in stored_data: return stored_data['meal_plan_text']
    return ""

@app.callback(
    Output("planned-meal-input", "value"),
    [Input("url", "pathname")],
    [State("meal-plan-data-store", "data")],
    prevent_initial_call=False
)
def update_planned_meal(pathname, stored_data):
    if pathname == '/tracker' and stored_data and 'meal_plan_text' in stored_data: return stored_data['meal_plan_text']
    return ""

@app.callback(
    [Output("tracker-output", "children"),
     Output("tracker-summary-store", "data"),
     Output("commitment-pie-chart", "figure"),
     Output("tracker-error-output", "children")],
    [Input("evaluate-commitment-button", "n_clicks")],
    [State("planned-meal-input", "value"),
     State("eaten-meal-input", "value"),
     State("external-factors-input", "value"),
     State("user-inputs-store", "data")],
    prevent_initial_call=True
)
def evaluate_commitment(n_clicks, planned_meal, eaten_meal, external_factors, user_inputs):
    if not n_clicks: return "", dash.no_update, go.Figure(), ""
    if not planned_meal or not eaten_meal:
        return "الرجاء إدخال الخطة الغذائية وما تم تناوله فعليًا.", dash.no_update, go.Figure(), "خطأ: الرجاء ملء حقول الخطة الغذائية وما تم تناوله فعليًا."
    try:
        tracker_crew = Crew(
            agents=[tracker_agent], tasks=[track_progress_task], process=Process.sequential, verbose=False
        )
        tracker_inputs = {
            "username": user_inputs.get("name", "الزائر"), "planned_meal": planned_meal,
            "eaten_meal": eaten_meal, "external_factors": external_factors if external_factors else "لا توجد عوامل خارجية"
        }
        tracker_result = tracker_crew.kickoff(inputs=tracker_inputs)
        raw_output = tracker_result.raw
        percentage = 0
        percentage_match = re.search(r'(\d+)%', raw_output)
        if percentage_match: percentage = int(percentage_match.group(1))
        else:
            num_match = re.match(r'^\s*(\d+)', raw_output)
            if num_match: percentage = int(num_match.group(1))
        display_output = f"نسبة الالتزام: {percentage}%\n\n" + raw_output

        # Set chart color based on percentage
        if percentage >= 85: chart_color = '#28a745'
        elif percentage >= 70: chart_color = '#ffc107'
        elif percentage >= 50: chart_color = '#fd7e14'
        else: chart_color = '#dc3545'

        # Create pie chart
        fig = go.Figure(
            data=[go.Pie(
                labels=['الالتزام', 'المتبقي'], values=[percentage, 100 - percentage],
                hole=.7, marker_colors=[chart_color, 'lightgray'], textinfo='none', hoverinfo='label+percent'
            )]
        )
        fig.update_layout(
             margin=dict(t=0, b=0, l=0, r=0), showlegend=False, height=200,
             xaxis=dict(showgrid=False, zeroline=False, showticklabels=False),
             yaxis=dict(showgrid=False, zeroline=False, showticklabels=False),
             annotations=[dict(
                 text=f'{percentage}%', x=0.5, y=0.5, font_size=30, showarrow=False, font_color='black'
             )]
        )
        return display_output, {'summary': display_output, 'commitment_percentage': percentage}, fig, ""
    except Exception as e:
        error_msg = f"حدث خطأ أثناء تقييم الالتزام: {str(e)}"
        traceback.print_exc()
        return "", {'summary': 'خطأ في التقييم', 'commitment_percentage': 0}, go.Figure(), error_msg

@app.callback(
    [Output("motivation-output", "children"),
     Output("motivation-error-output", "children")],
    [Input("get-motivation-button", "n_clicks")],
    [State("tracker-summary-store", "data"),
     State("user-inputs-store", "data")],
    prevent_initial_call=True
)
def get_motivation(n_clicks, tracker_data, user_data):
    if not n_clicks: return "", ""
    tracker_summary = tracker_data.get('summary') if tracker_data else None
    commitment_percentage = tracker_data.get('commitment_percentage', 0) if tracker_data else 0
    username = user_data.get("name") if user_data and user_data.get("name") else "الزائر"
    if not tracker_summary: return "الرجاء تقييم التزامك أولاً للحصول على تحفيز مخصص.", "خطأ: الرجاء تقييم الالتزام أولاً."
    try:
        motivation_crew = Crew(
            agents=[motivation_agent], tasks=[motivate_user_task], process=Process.sequential, verbose=False
        )
        motivation_inputs = {
            "tracker_summary": tracker_summary, "username": username, "commitment_percentage": commitment_percentage
        }
        motivation_result = motivation_crew.kickoff(inputs=motivation_inputs)
        return dcc.Markdown(motivation_result.raw), ""
    except Exception as e:
        error_msg = f"حدث خطأ أثناء الحصول على التحفيز: {str(e)}"
        traceback.print_exc()
        return "", error_msg

@app.callback(
    Output("motivation-data-store", "data"),
    [Input("motivation-output", "children")],
    [State("motivation-data-store", "data")],
    prevent_initial_call=True
)
def store_motivation_data(motivation_text_component, current_data):
    if motivation_text_component:
        if isinstance(motivation_text_component, dcc.Markdown):
            motivation_text = motivation_text_component.children
        else:
            motivation_text = motivation_text_component
        return {
            'motivation_text': motivation_text, 'timestamp': datetime.now().isoformat()
        }
    return current_data

def generate_html_report_content(report_data):
    try:
        username = report_data.get("username")
        username_display = username if username and username != "الزائر" else "العميل"
            
        meal_plan = report_data.get("meal_plan", "لا توجد خطة وجبات متاحة.").replace('\n', '<br>')
        tracker_summary = report_data.get("tracker_summary", "لا يوجد تقييم التزام متاح.").replace('\n', '<br>')
        motivation = report_data.get("motivation", "لا يوجد تحفيز متاح.").replace('\n', '<br>')
        user_profile = report_data.get("user_profile", {})
        report_date = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

        html_content = f"""
        <!DOCTYPE html>
        <html lang="ar" dir="rtl">
        <head>
            <meta charset="UTF-8">
            <meta name="viewport" content="width=device-width, initial-scale=1.0">
            <title>تقرير النظام الغذائي - {username_display}</title>
            <style>
                body {{
                    font-family: 'Arial', sans-serif; line-height: 1.6; color: #333;
                    max-width: 800px; margin: 0 auto; padding: 20px;
                    background-color: #f4f4f4; border: 1px solid #ddd;
                    box-shadow: 0 0 10px rgba(0,0,0,0.1);
                    direction: rtl; text-align: right;
                }}
                h1, h2, h3 {{ color: #2c3e50; text-align: center; }}
                .container {{
                    background-color: #fff; padding: 30px; border-radius: 8px; margin-top: 20px;
                }}
                .section-title {{
                    font-size: 24px; color: #34495e; border-bottom: 2px solid #34495e;
                    padding-bottom: 10px; margin-bottom: 20px; text-align: right;
                }}
                .content-box {{
                    background-color: #f9f9f9; border: 1px solid #eee; border-radius: 5px;
                    padding: 15px; margin-bottom: 15px; white-space: pre-wrap;
                    text-align: right; word-wrap: break-word;
                }}
                .user-profile-table {{ width: 100%; border-collapse: collapse; margin-bottom: 20px; }}
                .user-profile-table th, .user-profile-table td {{ border: 1px solid #ddd; padding: 8px; text-align: right; }}
                .user-profile-table th {{ background-color: #e9ecef; width: 30%; }}
                .footer {{ text-align: center; margin-top: 40px; font-size: 0.9em; color: #777; }}
            </style>
        </head>
        <body>
            <div class="container">
                <h1>تقرير النظام الغذائي الشامل</h1>
                <h3>تاريخ التقرير: {report_date}</h3>
                <hr>

                <h2 class="section-title">بيانات المستخدم</h2>
                <table class="user-profile-table">
                    <tr><th>الاسم</th><td>{user_profile.get("name", "غير متوفر")}</td></tr>
                    <tr><th>الوزن</th><td>{user_profile.get("weight", "غير متوفر")} كجم</td></tr>
                    <tr><th>الطول</th><td>{user_profile.get("height", "غير متوفر")} سم</td></tr>
                    <tr><th>العمر</th><td>{user_profile.get("age", "غير متوفر")} سنة</td></tr>
                    <tr><th>الجنس</th><td>{user_profile.get("sex", "غير متوفر")}</td></tr>
                    <tr><th>مستوى النشاط</th><td>{user_profile.get("activity_level", "غير متوفر")}</td></tr>
                    <tr><th>الهدف</th><td>{user_profile.get("goal", "غير متوفر")}</td></tr>
                    <tr><th>نوع النظام الغذائي</th><td>{user_profile.get("diet_type", "غير متوفر")}</td></tr>
                    <tr><th>الحساسيات الغذائية</th><td>{user_profile.get("allergy", "لا يوجد")}</td></tr>
                    <tr><th>الحالات الطبية</th><td>{user_profile.get("conditions", "لا يوجد")}</td></tr>
                </table>

                <h2 class="section-title">خطة الوجبات</h2>
                <div class="content-box">{meal_plan}</div>

                <h2 class="section-title">ملخص تقييم الالتزام</h2>
                <div class="content-box">{tracker_summary}</div>

                <h2 class="section-title">التحفيز والنصائح</h2>
                <div class="content-box">{motivation}</div>

                <div class="footer">تم إنشاء هذا التقرير بواسطة مساعد النظام الغذائي الذكي الخاص بك.</div>
            </div>
        </body>
        </html>
        """
        return html_content
    except Exception as e:
        traceback.print_exc()
        return "خطأ في توليد التقرير."


@app.callback(
    Output("download-html-report", "data"),
    Output("download-report-status", "children"),
    [Input("download-report-button", "n_clicks")],
    [State("meal-plan-data-store", "data"),
     State("tracker-summary-store", "data"),
     State("motivation-data-store", "data"),
     State("user-inputs-store", "data")],
    prevent_initial_call=True
)
def download_report(n_clicks, meal_data, tracker_data, motivation_data, user_inputs):
    if not n_clicks: return dash.no_update, ""
    if not meal_data or not meal_data.get('meal_plan_text'): return None, "الرجاء توليد خطة الوجبات أولاً."
    if not tracker_data or not tracker_data.get('summary'): return None, "الرجاء تقييم الالتزام أولاً."
    if not motivation_data or not motivation_data.get('motivation_text'): return None, "الرجاء الحصول على التحفيز أولاً."
    if not user_inputs or not user_inputs.get('name'): return None, "الرجاء إدخال بيانات المستخدم (خاصة الاسم) أولاً."
    report_data = {
        "username": str(user_inputs.get("name", "الزائر")),
        "meal_plan": str(meal_data.get("meal_plan_text", "لا توجد خطة وجبات متاحة.")),
        "tracker_summary": str(tracker_data.get("summary", "لا يوجد تقييم التزام متاح.")),
        "motivation": str(motivation_data.get("motivation_text", "لا يوجد تحفيز متاح.")),
        "user_profile": user_inputs
    }
    try:
        html_content = generate_html_report_content(report_data)
        output_filename = f"تقرير_النظام_الغذائي_{report_data['username']}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.html"
        return dcc.send_bytes(html_content.encode('utf-8'), output_filename, type='text/html'), "تم إنشاء التقرير بنجاح!"
    except Exception as e:
        error_msg = f"حدث خطأ أثناء توليد ملف HTML: {str(e)}"
        traceback.print_exc()
        return None, error_msg

if __name__ == "__main__":
    app.run(debug=True, host="0.0.0.0", port=7860)
