{
    "name": "GlobeTrotter",
    "version": "19.0.1.0.0",
    "summary": "Personalized Multi-City Travel Planning",
    "description": """
GlobeTrotter - Personalized Travel Planning Platform

Core functionality:
- Create and manage multi-city trips
- Manage trip stops and travel dates
- Explore cities and activities
- Plan itineraries
- Track trip budgets and expenses
- Provide travel recommendations
- Share trip plans
    """,
    "category": "Travel",
    "author": "GlobeTrotter Team",
    "license": "LGPL-3",
    "depends": [
        "base",
        "web",
    ],
    "data": [
        "security/security_groups.xml",
        "security/ir.model.access.csv",
        "security/record_rules.xml",
        "data/city_data.xml",
        "data/activity_data.xml",
        "data/cron.xml",
        "views/menus.xml",
        "views/trip_views.xml",
        "views/trip_stop_views.xml",
        "views/city_views.xml",
        "views/activity_views.xml",
        "views/itinerary_views.xml",
        "views/expense_views.xml",
        "views/budget_views.xml",
        "views/recommendation_views.xml",
        "views/dashboard_views.xml",
        "views/profile_views.xml",
        "reports/trip_report.xml",
        "reports/trip_report_template.xml",
    ],
    "demo": [
        "demo/demo_data.xml",
    ],
    "assets": {
        "web.assets_backend": [
            "globetrotter/static/src/scss/*.scss",
            "globetrotter/static/src/js/*.js",
        ],
    },
    "installable": True,
    "application": True,
    "auto_install": False,
}